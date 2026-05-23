from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, List, Optional

from .config import RuntimeConfig
from .explanation_engine import ExplanationEngine
from .medframework_ingest import MedframeworkIngestor
from .node_mesh import NodeMeshStore
from .ollama_client import OllamaClient
from .pattern_engine import RecursivePatternEngine
from .types import DiscoveryResult, MedDocument, PatternReport
from .utils import extract_json_object, trim_text


class DiscoveryAgent:
    def __init__(self, config: Optional[RuntimeConfig] = None) -> None:
        self.config = config or RuntimeConfig()
        self.config.ensure_runtime_dirs()
        self.pattern_engine = RecursivePatternEngine()
        self.mesh_store = NodeMeshStore(self.config.mesh_store_path)
        self.ollama = OllamaClient(base_url=self.config.ollama_base_url)
        self.explainer = ExplanationEngine()

    def index_medframework(
        self,
        medframework_root: Optional[Path] = None,
        max_files: Optional[int] = None,
    ) -> Dict[str, Any]:
        source_root = medframework_root or self.config.medframework_root
        max_file_count = max_files or self.config.max_files
        ingestor = MedframeworkIngestor(
            root=source_root,
            max_files=max_file_count,
            max_file_bytes=self.config.max_file_bytes,
        )
        documents = ingestor.collect_documents()
        patterns = self.pattern_engine.build(documents)
        self.mesh_store.rebuild(documents, patterns)
        self.mesh_store.save()
        return {"documents": documents, "patterns": patterns}

    def _build_prompt(self, query: str, documents: List[MedDocument], patterns: PatternReport) -> str:
        doc_context = []
        for doc in documents[:12]:
            doc_context.append(
                {
                    "endpoint_url": doc.endpoint_url,
                    "preview": trim_text(doc.text, 240),
                }
            )
        context = {
            "query": query,
            "document_count": len(documents),
            "top_terms": patterns.top_terms[:20],
            "recursive_signals": patterns.recursive_signals[:20],
            "document_samples": doc_context,
        }
        schema = {
            "working_result": {
                "result_type": "analysis|protocol|code",
                "title": "short title",
                "content": "usable technical output",
                "assumptions": ["..."],
                "validation_steps": ["..."],
                "limitations": ["..."],
            },
            "optimal_discovery_process": [
                {"step": 1, "action": "what to do", "why": "why this step is optimal"}
            ],
            "explanation": {
                "summary": "high-level explanation for lab professionals",
                "mechanistic_rationale": ["..."],
                "safety_and_quality_notes": ["..."],
            },
            "evidence_endpoints": ["file://..."],
        }
        return (
            "You are a biomedical discovery assistant for lab-grade professionals.\n"
            "Use the provided medframework context and produce JSON only.\n"
            "Do not claim certainty; include validation and limitations.\n\n"
            f"CONTEXT:\n{context}\n\n"
            f"OUTPUT_SCHEMA:\n{schema}"
        )

    def _normalize_payload(
        self,
        query: str,
        model: str,
        model_payload: Dict[str, Any],
        patterns: PatternReport,
        documents: List[MedDocument],
    ) -> Dict[str, Any]:
        working_result = model_payload.get("working_result", {})
        if not isinstance(working_result, dict):
            working_result = {"result_type": "analysis", "title": "Generated result", "content": str(working_result)}

        explanation_module = self.explainer.build(
            query=query,
            model_payload=model_payload,
            patterns=patterns,
            documents=documents,
        )

        evidence_endpoints = model_payload.get("evidence_endpoints", [])
        if not isinstance(evidence_endpoints, list) or not evidence_endpoints:
            evidence_endpoints = [doc.endpoint_url for doc in documents[:10]]

        process = model_payload.get("optimal_discovery_process", [])
        if not isinstance(process, list) or not process:
            process = [
                {"step": 1, "action": "Ingest medframework context", "why": "Ground response in local domain data"},
                {"step": 2, "action": "Extract recursive patterns", "why": "Identify cross-file biological signals"},
                {"step": 3, "action": "Generate candidate output", "why": "Produce usable result for lab workflows"},
                {"step": 4, "action": "Apply validation plan", "why": "Ensure reproducible and safe next steps"},
            ]

        return {
            "working_result": working_result,
            "optimal_discovery_process": process,
            "model_explanation": model_payload.get("explanation", {}),
            "explanation_module": explanation_module,
            "pattern_snapshot": patterns.to_dict(),
            "evidence_endpoints": evidence_endpoints,
            "knowledge_stats": {
                "documents_indexed": len(documents),
                "mesh_store_path": str(self.config.mesh_store_path),
                "ollama_endpoint": self.config.ollama_base_url,
            },
        }

    def run_discovery(
        self,
        query: str,
        model: str,
        medframework_root: Optional[Path] = None,
        max_files: Optional[int] = None,
    ) -> DiscoveryResult:
        snapshot = self.index_medframework(medframework_root=medframework_root, max_files=max_files)
        documents: List[MedDocument] = snapshot["documents"]
        patterns: PatternReport = snapshot["patterns"]

        prompt = self._build_prompt(query=query, documents=documents, patterns=patterns)
        response = self.ollama.chat(
            model=model,
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You provide rigorous and interpretable biomedical outputs for expert users. "
                        "Return strict JSON only."
                    ),
                },
                {"role": "user", "content": prompt},
            ],
            options={"temperature": 0.2},
        )
        content = response.get("message", {}).get("content", "")
        decoded = extract_json_object(content)
        if decoded is None:
            decoded = {
                "working_result": {
                    "result_type": "analysis",
                    "title": "Model output (non-JSON fallback)",
                    "content": content.strip(),
                    "assumptions": [],
                    "validation_steps": ["Review with domain expert before execution."],
                    "limitations": ["Model response was not emitted as valid JSON."],
                },
                "optimal_discovery_process": [],
                "explanation": {"summary": "Fallback response wrapper", "mechanistic_rationale": []},
                "evidence_endpoints": [doc.endpoint_url for doc in documents[:8]],
            }

        payload = self._normalize_payload(
            query=query,
            model=model,
            model_payload=decoded,
            patterns=patterns,
            documents=documents,
        )
        return DiscoveryResult(query=query, model=model, payload=payload)

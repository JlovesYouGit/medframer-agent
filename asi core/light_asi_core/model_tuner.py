from __future__ import annotations

import json
import subprocess
from pathlib import Path
from typing import Any, Dict, List, Optional

from .config import RuntimeConfig
from .medframework_ingest import MedframeworkIngestor
from .pattern_engine import RecursivePatternEngine
from .types import MedDocument, PatternReport


class ModelTuner:
    """Fine-tunes Ollama models using medframework data and patterns."""

    def __init__(self, config: Optional[RuntimeConfig] = None) -> None:
        self.config = config or RuntimeConfig()
        self.config.ensure_runtime_dirs()

    def _generate_training_data(
        self, documents: List[MedDocument], patterns: PatternReport
    ) -> List[Dict[str, Any]]:
        """Generate training examples from medframework data."""
        training_examples = []

        # Create question-answer pairs from document content
        for doc in documents[:50]:  # Limit to prevent overwhelming
            text = doc.text.strip()
            if len(text) < 100:
                continue

            # Extract key terms from patterns
            doc_terms = [t["term"] for t in patterns.top_terms if t["term"] in text.lower()]
            if not doc_terms:
                continue

            # Create training example
            example = {
                "system": "You are a biomedical discovery assistant with expertise in medical research and biological data analysis.",
                "user": f"Analyze the following biological data focusing on: {', '.join(doc_terms[:5])}\n\nData: {text[:500]}",
                "assistant": f"Based on the data, I can identify patterns related to {', '.join(doc_terms[:3])}. The document contains structured information that can be used for biological discovery and analysis. Key signals include recursive patterns across the dataset.",
            }
            training_examples.append(example)

        return training_examples

    def _create_modelfile(
        self, base_model: str, training_data: List[Dict[str, Any]]
    ) -> str:
        """Create an Ollama Modelfile for fine-tuning."""
        modelfile_content = f"""FROM {base_model}

# Parameters
PARAMETER temperature 0.2
PARAMETER top_p 0.9
PARAMETER num_ctx 4096

# System prompt
SYSTEM You are a specialized biomedical discovery assistant for lab-grade professionals. You have deep knowledge of medical research, biological data analysis, and compound structures. You provide precise, testable outputs with proper validation steps.

# Training data integration
TEMPLATE """
        # Add training examples as few-shot examples
        for i, example in enumerate(training_data[:10]):  # Limit examples
            modelfile_content += f"\nExample {i+1}:\nUser: {example['user']}\nAssistant: {example['assistant']}\n"

        modelfile_content += """
{{- if .System }}
System: {{ .System }}
{{- end }}

{{- if .Prompt }}
User: {{ .Prompt }}
{{- end }}

Assistant: {{ .Response }}
"""
        return modelfile_content

    def create_custom_model(
        self,
        base_model: str,
        custom_name: str,
        medframework_root: Optional[Path] = None,
        max_files: int = 100,
    ) -> Dict[str, Any]:
        """Create a custom fine-tuned model from medframework data."""
        # Ingest medframework data
        source_root = medframework_root or self.config.medframework_root
        ingestor = MedframeworkIngestor(
            root=source_root, max_files=max_files, max_file_bytes=self.config.max_file_bytes
        )
        documents = ingestor.collect_documents()

        # Extract patterns
        pattern_engine = RecursivePatternEngine()
        patterns = pattern_engine.build(documents)

        # Generate training data
        training_data = self._generate_training_data(documents, patterns)

        # Create Modelfile
        modelfile_content = self._create_modelfile(base_model, training_data)

        # Write Modelfile to temp location
        modelfile_path = self.config.model_store_path / f"{custom_name}_Modelfile"
        modelfile_path.write_text(modelfile_content, encoding="utf-8")

        # Create custom model using Ollama
        try:
            result = subprocess.run(
                ["ollama", "create", custom_name, "-f", str(modelfile_path)],
                capture_output=True,
                text=True,
                timeout=600,
            )

            if result.returncode == 0:
                return {
                    "success": True,
                    "model_name": custom_name,
                    "base_model": base_model,
                    "training_examples": len(training_data),
                    "documents_used": len(documents),
                    "modelfile_path": str(modelfile_path),
                    "message": f"Custom model '{custom_name}' created successfully",
                }
            else:
                return {
                    "success": False,
                    "error": result.stderr,
                    "message": f"Failed to create custom model: {result.stderr}",
                }

        except subprocess.TimeoutExpired:
            return {"success": False, "error": "Model creation timed out", "message": "Model creation took too long"}
        except FileNotFoundError:
            return {"success": False, "error": "Ollama not found", "message": "Ollama CLI not available"}

    def list_custom_models(self) -> List[str]:
        """List all custom models created by MedFramer."""
        try:
            result = subprocess.run(
                ["ollama", "list"], capture_output=True, text=True, timeout=30
            )
            if result.returncode == 0:
                lines = result.stdout.split("\n")
                custom_models = [
                    line.split()[0] for line in lines[1:] if line.strip() and "medframer" in line.lower()
                ]
                return custom_models
        except (subprocess.TimeoutExpired, FileNotFoundError):
            pass
        return []

    def remove_custom_model(self, model_name: str) -> Dict[str, Any]:
        """Remove a custom model."""
        try:
            result = subprocess.run(
                ["ollama", "rm", model_name], capture_output=True, text=True, timeout=60
            )
            if result.returncode == 0:
                return {"success": True, "message": f"Model '{model_name}' removed successfully"}
            else:
                return {"success": False, "error": result.stderr}
        except (subprocess.TimeoutExpired, FileNotFoundError) as e:
            return {"success": False, "error": str(e)}

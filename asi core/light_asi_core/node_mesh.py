from __future__ import annotations

import json
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List

from .types import MedDocument, PatternReport
from .utils import sha1_hex, tokenize


class NodeMeshStore:
    def __init__(self, path: Path) -> None:
        self.path = path
        self.data = self._blank_data()
        self.load()

    def _blank_data(self) -> Dict[str, Any]:
        return {
            "version": "1.0",
            "updated_at": None,
            "nodes": {},
            "edges": {},
            "metadata": {"documents_indexed": 0, "terms_indexed": 0},
        }

    def load(self) -> None:
        if not self.path.exists():
            self.data = self._blank_data()
            return
        try:
            self.data = json.loads(self.path.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            self.data = self._blank_data()

    def rebuild(self, documents: List[MedDocument], patterns: PatternReport) -> None:
        self.data = self._blank_data()
        nodes: Dict[str, Dict[str, Any]] = self.data["nodes"]
        edges: Dict[str, Dict[str, Any]] = self.data["edges"]

        term_seen = set()
        for doc in documents:
            doc_id = f"doc:{sha1_hex(str(doc.path))[:16]}"
            nodes[doc_id] = {
                "kind": "document",
                "path": str(doc.path),
                "endpoint_url": doc.endpoint_url,
                "checksum": doc.checksum,
            }

            terms = [term for term, _ in Counter(tokenize(doc.text)).most_common(14)]
            for term in terms:
                term_id = f"term:{term}"
                term_seen.add(term)
                if term_id not in nodes:
                    nodes[term_id] = {"kind": "term", "label": term}
                edge_id = f"contains:{doc_id}:{term_id}"
                edges[edge_id] = {"source": doc_id, "target": term_id, "kind": "contains", "weight": 1}

        for pair in patterns.co_occurrence:
            a = pair["a"]
            b = pair["b"]
            weight = pair["weight"]
            a_id = f"term:{a}"
            b_id = f"term:{b}"
            if a_id not in nodes:
                nodes[a_id] = {"kind": "term", "label": a}
                term_seen.add(a)
            if b_id not in nodes:
                nodes[b_id] = {"kind": "term", "label": b}
                term_seen.add(b)
            edge_id = f"co:{a_id}:{b_id}"
            edges[edge_id] = {"source": a_id, "target": b_id, "kind": "co_occurs", "weight": weight}

        self.data["updated_at"] = datetime.now(timezone.utc).isoformat()
        self.data["metadata"] = {
            "documents_indexed": len(documents),
            "terms_indexed": len(term_seen),
            "co_edges_indexed": len(patterns.co_occurrence),
        }

    def save(self) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.path.write_text(json.dumps(self.data, indent=2, ensure_ascii=False), encoding="utf-8")

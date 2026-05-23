from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List


@dataclass
class MedDocument:
    path: Path
    endpoint_url: str
    text: str
    checksum: str

    def preview(self, max_chars: int = 260) -> str:
        chunk = self.text.strip().replace("\n", " ")
        if len(chunk) <= max_chars:
            return chunk
        return chunk[: max_chars - 3] + "..."

    def to_dict(self) -> Dict[str, Any]:
        return {
            "path": str(self.path),
            "endpoint_url": self.endpoint_url,
            "checksum": self.checksum,
            "preview": self.preview(),
        }


@dataclass
class PatternReport:
    top_terms: List[Dict[str, Any]] = field(default_factory=list)
    co_occurrence: List[Dict[str, Any]] = field(default_factory=list)
    recursive_signals: List[Dict[str, Any]] = field(default_factory=list)
    document_count: int = 0

    def to_dict(self) -> Dict[str, Any]:
        return {
            "top_terms": self.top_terms,
            "co_occurrence": self.co_occurrence,
            "recursive_signals": self.recursive_signals,
            "document_count": self.document_count,
        }


@dataclass
class DiscoveryResult:
    query: str
    model: str
    payload: Dict[str, Any]

    def to_dict(self) -> Dict[str, Any]:
        data = dict(self.payload)
        data["query"] = self.query
        data["model"] = self.model
        return data

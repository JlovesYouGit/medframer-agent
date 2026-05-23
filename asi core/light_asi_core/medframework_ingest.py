from __future__ import annotations

from pathlib import Path
from typing import Iterable, List, Optional, Set

from .types import MedDocument
from .utils import read_text_limited, sha1_hex


class MedframeworkIngestor:
    DEFAULT_SUFFIXES: Set[str] = {".py", ".md", ".txt", ".json", ".yaml", ".yml", ".csv", ".toml"}
    SKIP_PARTS: Set[str] = {"venv", ".venv", "__pycache__", ".git", "node_modules", "installed_models", "model_env"}

    def __init__(
        self,
        root: Path,
        max_files: int = 300,
        max_file_bytes: int = 1_048_576,
        include_suffixes: Optional[Iterable[str]] = None,
    ) -> None:
        self.root = root
        self.max_files = max_files
        self.max_file_bytes = max_file_bytes
        self.include_suffixes = set(s.lower() for s in (include_suffixes or self.DEFAULT_SUFFIXES))

    def _is_valid(self, path: Path) -> bool:
        if path.suffix.lower() not in self.include_suffixes:
            return False
        parts = {part.lower() for part in path.parts}
        return not bool(parts & self.SKIP_PARTS)

    def collect_documents(self) -> List[MedDocument]:
        if not self.root.exists():
            return []

        files: List[Path] = []
        for path in self.root.rglob("*"):
            if not path.is_file():
                continue
            if self._is_valid(path):
                files.append(path)
        files.sort(key=lambda p: str(p))

        documents: List[MedDocument] = []
        for path in files[: self.max_files]:
            text = read_text_limited(path, self.max_file_bytes)
            if not text.strip():
                continue
            endpoint = path.resolve().as_uri()
            checksum = sha1_hex(text)
            documents.append(
                MedDocument(path=path.resolve(), endpoint_url=endpoint, text=text, checksum=checksum)
            )
        return documents

from __future__ import annotations

import os
from dataclasses import dataclass, field
from pathlib import Path


def _repo_root() -> Path:
    # .../BIO/asi core/light_asi_core/config.py -> .../BIO
    return Path(__file__).resolve().parents[2]


@dataclass
class RuntimeConfig:
    repo_root: Path = field(default_factory=_repo_root)
    medframework_root: Path = field(
        default_factory=lambda: Path(os.getenv("MEDFRAMEWORK_ROOT", str(_repo_root() / "medframeworks")))
    )
    model_store_path: Path = field(
        default_factory=lambda: Path(os.getenv("OLLAMA_MODELS", str(_repo_root() / "models_store")))
    )
    mesh_store_path: Path = field(
        default_factory=lambda: Path(os.getenv("NODE_MESH_PATH", str(_repo_root() / "node_mesh" / "mesh_store.json")))
    )
    ollama_base_url: str = field(default_factory=lambda: os.getenv("OLLAMA_BASE_URL", "http://127.0.0.1:11434"))
    max_files: int = field(default_factory=lambda: int(os.getenv("MEDFRAMEWORK_MAX_FILES", "300")))
    max_file_bytes: int = field(default_factory=lambda: int(os.getenv("MEDFRAMEWORK_MAX_FILE_BYTES", "1048576")))

    def ensure_runtime_dirs(self) -> None:
        self.model_store_path.mkdir(parents=True, exist_ok=True)
        self.mesh_store_path.parent.mkdir(parents=True, exist_ok=True)

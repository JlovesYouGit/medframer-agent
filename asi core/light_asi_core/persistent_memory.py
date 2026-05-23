from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

from .config import RuntimeConfig


class PersistentMemory:
    """Persistent memory system for cross-session recall and learning."""

    def __init__(self, config: Optional[RuntimeConfig] = None) -> None:
        self.config = config or RuntimeConfig()
        self.memory_path = self.config.repo_root / "memory_store" / "persistent_memory.json"
        self.memory_path.parent.mkdir(parents=True, exist_ok=True)
        self.memory_data = self._load_memory()

    def _load_memory(self) -> Dict[str, Any]:
        """Load persistent memory from disk."""
        if not self.memory_path.exists():
            return self._blank_memory()
        try:
            return json.loads(self.memory_path.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            return self._blank_memory()

    def _blank_memory(self) -> Dict[str, Any]:
        """Create blank memory structure."""
        return {
            "version": "1.0",
            "created_at": datetime.now(timezone.utc).isoformat(),
            "updated_at": None,
            "sessions": [],
            "knowledge_graph": {
                "entities": {},
                "relationships": [],
                "patterns": [],
            },
            "discovery_history": [],
            "model_interactions": [],
            "learned_weights": {},
        }

    def save(self) -> None:
        """Save persistent memory to disk."""
        self.memory_data["updated_at"] = datetime.now(timezone.utc).isoformat()
        self.memory_path.write_text(json.dumps(self.memory_data, indent=2, ensure_ascii=False), encoding="utf-8")

    def add_session(self, session_id: str, query: str, model: str, result_summary: str) -> None:
        """Add a discovery session to memory."""
        session = {
            "session_id": session_id,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "query": query,
            "model": model,
            "result_summary": result_summary,
        }
        self.memory_data["sessions"].append(session)
        self.save()

    def add_discovery_result(self, query: str, patterns: List[str], evidence_count: int) -> None:
        """Add a discovery result to history."""
        discovery = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "query": query,
            "patterns_found": patterns,
            "evidence_count": evidence_count,
        }
        self.memory_data["discovery_history"].append(discovery)
        self.save()

    def add_entity(self, entity_name: str, entity_type: str, properties: Dict[str, Any]) -> None:
        """Add an entity to the knowledge graph."""
        entity_id = f"{entity_type}:{entity_name}"
        self.memory_data["knowledge_graph"]["entities"][entity_id] = {
            "name": entity_name,
            "type": entity_type,
            "properties": properties,
            "first_seen": datetime.now(timezone.utc).isoformat(),
            "access_count": 0,
        }
        self.save()

    def add_relationship(self, source: str, target: str, relationship_type: str, weight: float = 1.0) -> None:
        """Add a relationship to the knowledge graph."""
        relationship = {
            "source": source,
            "target": target,
            "type": relationship_type,
            "weight": weight,
            "created_at": datetime.now(timezone.utc).isoformat(),
        }
        self.memory_data["knowledge_graph"]["relationships"].append(relationship)
        self.save()

    def add_learned_pattern(self, pattern: str, frequency: int, contexts: List[str]) -> None:
        """Add a learned pattern to memory."""
        pattern_entry = {
            "pattern": pattern,
            "frequency": frequency,
            "contexts": contexts,
            "learned_at": datetime.now(timezone.utc).isoformat(),
        }
        self.memory_data["knowledge_graph"]["patterns"].append(pattern_entry)
        self.save()

    def update_model_weights(self, model_name: str, weight_adjustments: Dict[str, float]) -> None:
        """Update learned model weights based on patterns."""
        if model_name not in self.memory_data["learned_weights"]:
            self.memory_data["learned_weights"][model_name] = {}

        for pattern, weight in weight_adjustments.items():
            if pattern not in self.memory_data["learned_weights"][model_name]:
                self.memory_data["learned_weights"][model_name][pattern] = []
            self.memory_data["learned_weights"][model_name][pattern].append(
                {
                    "weight": weight,
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                }
            )
        self.save()

    def get_relevant_context(self, query: str, max_results: int = 5) -> List[Dict[str, Any]]:
        """Retrieve relevant context from memory for a query."""
        relevant_contexts = []

        # Search discovery history
        for discovery in reversed(self.memory_data["discovery_history"][-20:]):
            if any(term.lower() in query.lower() for term in discovery["patterns_found"]):
                relevant_contexts.append(
                    {
                        "type": "discovery",
                        "query": discovery["query"],
                        "patterns": discovery["patterns_found"],
                        "timestamp": discovery["timestamp"],
                    }
                )

        # Search knowledge graph entities
        query_lower = query.lower()
        for entity_id, entity_data in self.memory_data["knowledge_graph"]["entities"].items():
            if entity_data["name"].lower() in query_lower:
                relevant_contexts.append(
                    {
                        "type": "entity",
                        "name": entity_data["name"],
                        "entity_type": entity_data["type"],
                        "properties": entity_data["properties"],
                    }
                )

        return relevant_contexts[:max_results]

    def get_model_weights(self, model_name: str) -> Dict[str, List[Dict[str, Any]]]:
        """Get learned weights for a specific model."""
        return self.memory_data["learned_weights"].get(model_name, {})

    def get_statistics(self) -> Dict[str, Any]:
        """Get memory statistics."""
        return {
            "total_sessions": len(self.memory_data["sessions"]),
            "total_discoveries": len(self.memory_data["discovery_history"]),
            "total_entities": len(self.memory_data["knowledge_graph"]["entities"]),
            "total_relationships": len(self.memory_data["knowledge_graph"]["relationships"]),
            "total_patterns": len(self.memory_data["knowledge_graph"]["patterns"]),
            "models_with_weights": list(self.memory_data["learned_weights"].keys()),
            "memory_size_bytes": self.memory_path.stat().st_size if self.memory_path.exists() else 0,
        }

    def export_memory(self, export_path: Optional[Path] = None) -> Path:
        """Export memory to a file."""
        if export_path is None:
            export_path = self.config.repo_root / "memory_store" / f"memory_export_{datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S')}.json"
        export_path.parent.mkdir(parents=True, exist_ok=True)
        export_path.write_text(json.dumps(self.memory_data, indent=2, ensure_ascii=False), encoding="utf-8")
        return export_path

    def import_memory(self, import_path: Path) -> Dict[str, Any]:
        """Import memory from a file."""
        try:
            imported_data = json.loads(import_path.read_text(encoding="utf-8"))
            # Merge with existing memory
            self.memory_data["sessions"].extend(imported_data.get("sessions", []))
            self.memory_data["discovery_history"].extend(imported_data.get("discovery_history", []))
            self.memory_data["knowledge_graph"]["entities"].update(imported_data.get("knowledge_graph", {}).get("entities", {}))
            self.memory_data["knowledge_graph"]["relationships"].extend(imported_data.get("knowledge_graph", {}).get("relationships", []))
            self.memory_data["knowledge_graph"]["patterns"].extend(imported_data.get("knowledge_graph", {}).get("patterns", []))
            for model, weights in imported_data.get("learned_weights", {}).items():
                if model not in self.memory_data["learned_weights"]:
                    self.memory_data["learned_weights"][model] = {}
                for pattern, weight_list in weights.items():
                    if pattern not in self.memory_data["learned_weights"][model]:
                        self.memory_data["learned_weights"][model][pattern] = []
                    self.memory_data["learned_weights"][model][pattern].extend(weight_list)
            self.save()
            return {"success": True, "message": "Memory imported successfully"}
        except Exception as e:
            return {"success": False, "error": str(e)}

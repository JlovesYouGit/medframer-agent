from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, List, Optional

from .config import RuntimeConfig
from .persistent_memory import PersistentMemory
from .types import PatternReport


class WeightAdjuster:
    """Adjusts model weights based on medframework patterns and discovery results."""

    def __init__(self, config: Optional[RuntimeConfig] = None) -> None:
        self.config = config or RuntimeConfig()
        self.memory = PersistentMemory(config)
        self.weight_store_path = self.config.repo_root / "weight_store" / "adjustments.json"
        self.weight_store_path.parent.mkdir(parents=True, exist_ok=True)

    def _load_weight_adjustments(self) -> Dict[str, Any]:
        """Load existing weight adjustments."""
        if not self.weight_store_path.exists():
            return {"models": {}, "global_patterns": {}}
        try:
            return json.loads(self.weight_store_path.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            return {"models": {}, "global_patterns": {}}

    def _save_weight_adjustments(self, data: Dict[str, Any]) -> None:
        """Save weight adjustments to disk."""
        self.weight_store_path.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")

    def calculate_pattern_weights(self, patterns: PatternReport) -> Dict[str, float]:
        """Calculate weight adjustments based on pattern analysis."""
        weights = {}

        # Weight recursive signals higher
        for signal in patterns.recursive_signals:
            term = signal["term"]
            doc_count = signal["documents"]
            frequency = signal["frequency"]
            
            # Calculate weight based on cross-document presence and frequency
            weight = (doc_count * 0.7) + (frequency * 0.3)
            weights[term] = min(weight / 10.0, 1.0)  # Normalize to 0-1

        # Weight co-occurring pairs
        for pair in patterns.co_occurrence:
            a = pair["a"]
            b = pair["b"]
            weight = pair["weight"]
            
            # Boost weight for strong co-occurrences
            if a not in weights:
                weights[a] = 0.0
            if b not in weights:
                weights[b] = 0.0
            
            weights[a] += weight * 0.1
            weights[b] += weight * 0.1

        # Normalize final weights
        max_weight = max(weights.values()) if weights else 1.0
        if max_weight > 0:
            weights = {k: v / max_weight for k, v in weights.items()}

        return weights

    def apply_weight_adjustments(
        self, model_name: str, patterns: PatternReport, discovery_success: bool = True
    ) -> Dict[str, Any]:
        """Apply weight adjustments based on discovery results."""
        pattern_weights = self.calculate_pattern_weights(patterns)
        
        # Load existing adjustments
        adjustments = self._load_weight_adjustments()
        
        # Update model-specific weights
        if model_name not in adjustments["models"]:
            adjustments["models"][model_name] = {
                "pattern_weights": {},
                "adjustment_history": [],
                "success_rate": 0.0,
                "total_adjustments": 0,
            }
        
        model_data = adjustments["models"][model_name]
        
        # Apply pattern weights
        for pattern, weight in pattern_weights.items():
            if pattern not in model_data["pattern_weights"]:
                model_data["pattern_weights"][pattern] = []
            
            model_data["pattern_weights"][pattern].append({
                "weight": weight,
                "timestamp": json.dumps({"timestamp": "now"}),  # Simplified
                "discovery_success": discovery_success,
            })
        
        # Update success rate
        model_data["total_adjustments"] += 1
        if discovery_success:
            current_success = model_data["success_rate"]
            model_data["success_rate"] = (current_success * (model_data["total_adjustments"] - 1) + 1.0) / model_data["total_adjustments"]
        
        # Record adjustment in history
        model_data["adjustment_history"].append({
            "patterns_count": len(pattern_weights),
            "success": discovery_success,
            "timestamp": "now",
        })
        
        # Save adjustments
        self._save_weight_adjustments(adjustments)
        
        # Also update persistent memory
        self.memory.update_model_weights(model_name, pattern_weights)
        
        return {
            "model": model_name,
            "patterns_adjusted": len(pattern_weights),
            "current_success_rate": model_data["success_rate"],
            "total_adjustments": model_data["total_adjustments"],
        }

    def get_model_weights(self, model_name: str) -> Dict[str, Any]:
        """Get current weight adjustments for a model."""
        adjustments = self._load_weight_adjustments()
        if model_name not in adjustments["models"]:
            return {"error": f"No adjustments found for model {model_name}"}
        
        model_data = adjustments["models"][model_name]
        
        # Calculate current average weights
        current_weights = {}
        for pattern, weight_history in model_data["pattern_weights"].items():
            if weight_history:
                avg_weight = sum(w["weight"] for w in weight_history) / len(weight_history)
                current_weights[pattern] = avg_weight
        
        return {
            "model": model_name,
            "current_weights": current_weights,
            "success_rate": model_data["success_rate"],
            "total_adjustments": model_data["total_adjustments"],
            "adjustment_history": model_data["adjustment_history"][-10:],  # Last 10 adjustments
        }

    def get_weight_adjustment_summary(self) -> Dict[str, Any]:
        """Get summary of all weight adjustments."""
        adjustments = self._load_weight_adjustments()
        
        summary = {
            "total_models": len(adjustments["models"]),
            "models": {},
            "global_patterns": adjustments["global_patterns"],
        }
        
        for model_name, model_data in adjustments["models"].items():
            summary["models"][model_name] = {
                "success_rate": model_data["success_rate"],
                "total_adjustments": model_data["total_adjustments"],
                "pattern_count": len(model_data["pattern_weights"]),
            }
        
        return summary

    def reset_model_weights(self, model_name: str) -> Dict[str, Any]:
        """Reset weight adjustments for a specific model."""
        adjustments = self._load_weight_adjustments()
        
        if model_name in adjustments["models"]:
            del adjustments["models"][model_name]
            self._save_weight_adjustments(adjustments)
            return {"success": True, "message": f"Reset weights for model {model_name}"}
        
        return {"success": False, "error": f"No weights found for model {model_name}"}

    def export_weight_adjustments(self, export_path: Optional[Path] = None) -> Path:
        """Export weight adjustments to a file."""
        if export_path is None:
            from datetime import datetime, timezone
            export_path = self.config.repo_root / "weight_store" / f"weights_export_{datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S')}.json"
        
        export_path.parent.mkdir(parents=True, exist_ok=True)
        adjustments = self._load_weight_adjustments()
        export_path.write_text(json.dumps(adjustments, indent=2, ensure_ascii=False), encoding="utf-8")
        
        return export_path

    def import_weight_adjustments(self, import_path: Path) -> Dict[str, Any]:
        """Import weight adjustments from a file."""
        try:
            imported_data = json.loads(import_path.read_text(encoding="utf-8"))
            current_data = self._load_weight_adjustments()
            
            # Merge imported data
            for model_name, model_data in imported_data.get("models", {}).items():
                if model_name not in current_data["models"]:
                    current_data["models"][model_name] = model_data
                else:
                    # Merge pattern weights
                    for pattern, weight_list in model_data.get("pattern_weights", {}).items():
                        if pattern not in current_data["models"][model_name]["pattern_weights"]:
                            current_data["models"][model_name]["pattern_weights"][pattern] = []
                        current_data["models"][model_name]["pattern_weights"][pattern].extend(weight_list)
                    
                    # Merge adjustment history
                    current_data["models"][model_name]["adjustment_history"].extend(model_data.get("adjustment_history", []))
            
            # Merge global patterns
            current_data["global_patterns"].update(imported_data.get("global_patterns", {}))
            
            self._save_weight_adjustments(current_data)
            return {"success": True, "message": "Weight adjustments imported successfully"}
        
        except Exception as e:
            return {"success": False, "error": str(e)}

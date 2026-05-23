from __future__ import annotations

import asyncio
import json
import queue
import threading
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, Tuple

from .config import RuntimeConfig
from .persistent_memory import PersistentMemory
from .weight_adjuster import WeightAdjuster


class ContinuousDataFlow:
    """Always-open input channel for continuous data flow and processing."""

    def __init__(self, config: Optional[RuntimeConfig] = None) -> None:
        self.config = config or RuntimeConfig()
        self.memory = PersistentMemory(config)
        self.weight_adjuster = WeightAdjuster(config)
        
        # Data queues for continuous flow
        self.input_queue: queue.Queue = queue.Queue(maxsize=1000)
        self.processing_queue: queue.Queue = queue.Queue(maxsize=1000)
        self.output_queue: queue.Queue = queue.Queue(maxsize=1000)
        
        # Flow control
        self.is_running = False
        self.flow_thread: Optional[threading.Thread] = None
        self.processing_thread: Optional[threading.Thread] = None
        
        # Match rate tracking
        self.match_rates: Dict[str, List[float]] = {}
        self.match_rate_window = 100  # Number of samples to average
        
        # Synchronization state
        self.sync_lock = threading.Lock()
        self.last_sync_time = None
        self.sync_patterns: List[Dict[str, Any]] = []

    def start_flow(self) -> None:
        """Start the continuous data flow."""
        if self.is_running:
            return
        
        self.is_running = True
        self.flow_thread = threading.Thread(target=self._flow_loop, daemon=True)
        self.processing_thread = threading.Thread(target=self._processing_loop, daemon=True)
        
        self.flow_thread.start()
        self.processing_thread.start()
        
        print("Continuous data flow started")

    def stop_flow(self) -> None:
        """Stop the continuous data flow."""
        self.is_running = False
        if self.flow_thread:
            self.flow_thread.join(timeout=5)
        if self.processing_thread:
            self.processing_thread.join(timeout=5)
        print("Continuous data flow stopped")

    def _flow_loop(self) -> None:
        """Main data flow loop."""
        while self.is_running:
            try:
                # Process input queue
                if not self.input_queue.empty():
                    data = self.input_queue.get(timeout=0.1)
                    self.processing_queue.put(data)
                
                # Process output queue
                if not self.output_queue.empty():
                    result = self.output_queue.get(timeout=0.1)
                    self._handle_output(result)
                
                time.sleep(0.01)  # Prevent CPU spinning
                
            except queue.Empty:
                continue
            except Exception as e:
                print(f"Flow loop error: {e}")

    def _processing_loop(self) -> None:
        """Data processing loop."""
        while self.is_running:
            try:
                if not self.processing_queue.empty():
                    data = self.processing_queue.get(timeout=0.1)
                    processed = self._process_data(data)
                    self.output_queue.put(processed)
                else:
                    time.sleep(0.01)
            except queue.Empty:
                continue
            except Exception as e:
                print(f"Processing loop error: {e}")

    def _process_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Process incoming data through the pipeline."""
        # Extract QR patterns if present
        qr_patterns = self._extract_qr_patterns(data)
        
        # Calculate match rate
        match_rate = self._calculate_match_rate(data, qr_patterns)
        
        # Update match rate tracking
        self._update_match_rate(data.get("source", "unknown"), match_rate)
        
        # Apply weight adjustments based on patterns
        if qr_patterns:
            self._apply_pattern_weights(qr_patterns)
        
        # Synchronize if needed
        if self._should_sync(match_rate):
            self._synchronize_pipeline(qr_patterns)
        
        return {
            "original_data": data,
            "qr_patterns": qr_patterns,
            "match_rate": match_rate,
            "processed_at": datetime.now(timezone.utc).isoformat(),
            "sync_performed": self.last_sync_time is not None and 
                            (datetime.now(timezone.utc) - self.last_sync_time).total_seconds() < 1.0,
        }

    def _extract_qr_patterns(self, data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Extract QR patterns from data (both literal QR codes and pattern-based QR)."""
        patterns = []
        
        # Check for literal QR code data
        if "qr_code" in data or "barcode" in data:
            qr_data = data.get("qr_code") or data.get("barcode")
            if qr_data:
                patterns.append({
                    "type": "literal_qr",
                    "data": qr_data,
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                })
        
        # Extract pattern-based QR (Quick Response patterns from text)
        if "text" in data or "content" in data:
            text_content = data.get("text") or data.get("content", "")
            pattern_qrs = self._extract_pattern_qr(text_content)
            patterns.extend(pattern_qrs)
        
        # Extract from structured data
        if "patterns" in data:
            for pattern in data["patterns"]:
                patterns.append({
                    "type": "structured_pattern",
                    "pattern": pattern,
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                })
        
        return patterns

    def _extract_pattern_qr(self, text: str) -> List[Dict[str, Any]]:
        """Extract Quick Response patterns from text (high-frequency, high-relevance patterns)."""
        import re
        from collections import Counter
        
        # Tokenize and find frequent patterns
        words = re.findall(r'\b\w+\b', text.lower())
        word_freq = Counter(words)
        
        # Find QR patterns (high frequency words that appear in clusters)
        qr_patterns = []
        for word, freq in word_freq.most_common(20):
            if freq >= 3:  # Minimum frequency threshold
                # Find context around the word
                contexts = []
                for match in re.finditer(rf'\b{re.escape(word)}\b', text, re.IGNORECASE):
                    start = max(0, match.start() - 30)
                    end = min(len(text), match.end() + 30)
                    contexts.append(text[start:end])
                
                if contexts:
                    qr_patterns.append({
                        "type": "pattern_qr",
                        "pattern": word,
                        "frequency": freq,
                        "contexts": contexts[:3],  # Keep top 3 contexts
                        "timestamp": datetime.now(timezone.utc).isoformat(),
                    })
        
        return qr_patterns

    def _calculate_match_rate(self, data: Dict[str, Any], qr_patterns: List[Dict[str, Any]]) -> float:
        """Calculate match rate between input data and known patterns."""
        if not qr_patterns:
            return 0.0
        
        # Get known patterns from memory
        known_patterns = self.memory.memory_data["knowledge_graph"]["patterns"]
        
        if not known_patterns:
            return 0.5  # Default mid-range when no history
        
        # Calculate matches
        matches = 0
        total = len(qr_patterns)
        
        for qr_pattern in qr_patterns:
            pattern_key = qr_pattern.get("pattern", qr_pattern.get("data", ""))
            for known in known_patterns:
                if pattern_key.lower() in known.get("pattern", "").lower():
                    matches += 1
                    break
        
        return matches / total if total > 0 else 0.0

    def _update_match_rate(self, source: str, match_rate: float) -> None:
        """Update match rate tracking for a source."""
        if source not in self.match_rates:
            self.match_rates[source] = []
        
        self.match_rates[source].append(match_rate)
        
        # Keep only recent samples
        if len(self.match_rates[source]) > self.match_rate_window:
            self.match_rates[source] = self.match_rates[source][-self.match_rate_window:]

    def _apply_pattern_weights(self, qr_patterns: List[Dict[str, Any]]) -> None:
        """Apply weight adjustments based on QR patterns."""
        for pattern in qr_patterns:
            pattern_key = pattern.get("pattern", pattern.get("data", ""))
            if pattern_key:
                # Add to memory as learned pattern
                contexts = pattern.get("contexts", [])
                frequency = pattern.get("frequency", 1)
                self.memory.add_learned_pattern(pattern_key, frequency, contexts)

    def _should_sync(self, match_rate: float) -> bool:
        """Determine if synchronization should be performed."""
        # Sync if match rate is high (good pattern match)
        # or if it's been too long since last sync
        if match_rate > 0.8:
            return True
        
        if self.last_sync_time is None:
            return True
        
        time_since_sync = (datetime.now(timezone.utc) - self.last_sync_time).total_seconds()
        return time_since_sync > 60  # Sync at least every minute

    def _synchronize_pipeline(self, qr_patterns: List[Dict[str, Any]]) -> None:
        """Synchronize the pipeline using QR patterns."""
        with self.sync_lock:
            self.last_sync_time = datetime.now(timezone.utc)
            self.sync_patterns = qr_patterns
            
            # Update memory with sync event
            self.memory.add_entity(
                "sync_event",
                "pipeline_sync",
                {
                    "pattern_count": len(qr_patterns),
                    "sync_time": self.last_sync_time.isoformat(),
                }
            )
            
            print(f"Pipeline synchronized with {len(qr_patterns)} QR patterns")

    def input_data(self, data: Dict[str, Any]) -> bool:
        """Input data into the continuous flow."""
        if not self.is_running:
            print("Data flow is not running. Call start_flow() first.")
            return False
        
        try:
            self.input_queue.put(data, timeout=1.0)
            return True
        except queue.Full:
            print("Input queue is full")
            return False

    def get_output(self) -> Optional[Dict[str, Any]]:
        """Get processed output from the flow."""
        try:
            return self.output_queue.get(timeout=1.0)
        except queue.Empty:
            return None

    def get_flow_statistics(self) -> Dict[str, Any]:
        """Get statistics about the data flow."""
        avg_match_rates = {}
        for source, rates in self.match_rates.items():
            if rates:
                avg_match_rates[source] = sum(rates) / len(rates)
        
        return {
            "is_running": self.is_running,
            "input_queue_size": self.input_queue.qsize(),
            "processing_queue_size": self.processing_queue.qsize(),
            "output_queue_size": self.output_queue.qsize(),
            "average_match_rates": avg_match_rates,
            "last_sync_time": self.last_sync_time.isoformat() if self.last_sync_time else None,
            "sync_patterns_count": len(self.sync_patterns),
        }

    def get_match_rate_history(self, source: str) -> List[float]:
        """Get match rate history for a specific source."""
        return self.match_rates.get(source, [])

    def reset_flow(self) -> None:
        """Reset the data flow state."""
        with self.sync_lock:
            # Clear queues
            while not self.input_queue.empty():
                self.input_queue.get()
            while not self.processing_queue.empty():
                self.processing_queue.get()
            while not self.output_queue.empty():
                self.output_queue.get()
            
            # Reset tracking
            self.match_rates = {}
            self.last_sync_time = None
            self.sync_patterns = []
            
            print("Data flow reset")

"""
Real-Time Data Processing System for Live Molecular Analysis
Advanced algorithms for processing live data feeds during molecular manipulation
"""

import threading
import queue
import time
import json
from typing import Dict, List, Tuple, Callable, Any, Optional
from dataclasses import dataclass
from collections import deque
import statistics
# Removed numpy import as it's not essential for this implementation


@dataclass
class MolecularSignal:
    """Represents a molecular signal from sensors"""
    timestamp: float
    signal_type: str  # 'bond_vibration', 'electron_density', 'magnetic_response', etc.
    values: List[float]  # Signal values over time
    confidence: float  # Confidence level of measurement (0-1)
    metadata: Dict[str, Any]  # Additional metadata


@dataclass
class ProcessedData:
    """Processed molecular analysis result"""
    timestamp: float
    molecular_state: Dict[str, float]  # Current molecular state parameters
    bond_analysis: Dict[str, float]  # Bond strength, length, etc.
    confidence_score: float  # Overall confidence in analysis
    recommendations: List[str]  # Recommended actions based on analysis


class SignalBuffer:
    """Buffer for incoming molecular signals with real-time processing"""
    
    def __init__(self, buffer_size: int = 1000):
        self.buffer_size = buffer_size
        self.buffers: Dict[str, deque] = {
            'bond_vibration': deque(maxlen=buffer_size),
            'electron_density': deque(maxlen=buffer_size),
            'magnetic_response': deque(maxlen=buffer_size),
            'temperature': deque(maxlen=buffer_size),
            'pressure': deque(maxlen=buffer_size)
        }
        
    def add_signal(self, signal: MolecularSignal):
        """Add a signal to the appropriate buffer"""
        if signal.signal_type in self.buffers:
            self.buffers[signal.signal_type].append(signal)
    
    def get_recent_signals(self, signal_type: str, count: int = 10) -> List[MolecularSignal]:
        """Get recent signals of a specific type"""
        return list(self.buffers[signal_type])[-count:]
    
    def get_average_signal_value(self, signal_type: str, window: int = 10) -> Optional[float]:
        """Get average value for a signal type over a time window"""
        recent_signals = self.get_recent_signals(signal_type, window)
        if not recent_signals:
            return None
        
        all_values = []
        for signal in recent_signals:
            all_values.extend(signal.values)
        
        if all_values:
            return sum(all_values) / len(all_values)
        return None


class RealTimeAnalyzer:
    """Main analyzer for real-time molecular data processing"""
    
    def __init__(self):
        self.signal_buffer = SignalBuffer()
        self.analysis_queue = queue.Queue()
        self.result_callbacks: List[Callable[[ProcessedData], None]] = []
        self.is_running = False
        self.analysis_thread = None
        
        # Molecular state tracking
        self.current_molecular_state = {}
        self.bond_analysis = {}
        
        # Statistical analysis parameters
        self.signal_windows = {
            'short': 5,    # 5 samples for quick response
            'medium': 15,  # 15 samples for balanced analysis
            'long': 30     # 30 samples for stable readings
        }
    
    def start_analyzer(self):
        """Start the real-time analysis thread"""
        self.is_running = True
        self.analysis_thread = threading.Thread(target=self._analysis_loop)
        self.analysis_thread.daemon = True
        self.analysis_thread.start()
        print("Real-time analyzer started")
    
    def stop_analyzer(self):
        """Stop the real-time analysis thread"""
        self.is_running = False
        if self.analysis_thread:
            self.analysis_thread.join()
        print("Real-time analyzer stopped")
    
    def register_callback(self, callback: Callable[[ProcessedData], None]):
        """Register a callback for processed data results"""
        self.result_callbacks.append(callback)
    
    def add_signal(self, signal: MolecularSignal):
        """Add a signal for processing"""
        self.signal_buffer.add_signal(signal)
    
    def _analysis_loop(self):
        """Main analysis loop running in separate thread"""
        while self.is_running:
            try:
                # Perform analysis on buffered data
                processed_result = self._analyze_current_state()
                
                if processed_result:
                    # Call all registered callbacks
                    for callback in self.result_callbacks:
                        try:
                            callback(processed_result)
                        except Exception as e:
                            print(f"Error in callback: {e}")
                
                # Sleep briefly to prevent busy waiting
                time.sleep(0.01)  # 10ms interval
                
            except Exception as e:
                print(f"Error in analysis loop: {e}")
                time.sleep(0.1)  # Longer sleep on error
    
    def _analyze_current_state(self) -> Optional[ProcessedData]:
        """Analyze current molecular state from buffered signals"""
        try:
            # Get current signal averages
            bond_avg = self.signal_buffer.get_average_signal_value('bond_vibration', self.signal_windows['medium'])
            electron_avg = self.signal_buffer.get_average_signal_value('electron_density', self.signal_windows['medium'])
            mag_avg = self.signal_buffer.get_average_signal_value('magnetic_response', self.signal_windows['medium'])
            
            # Update molecular state
            molecular_state = {}
            if bond_avg is not None:
                molecular_state['bond_vibration_avg'] = bond_avg
            if electron_avg is not None:
                molecular_state['electron_density_avg'] = electron_avg
            if mag_avg is not None:
                molecular_state['magnetic_response_avg'] = mag_avg
            
            # Analyze bond characteristics
            bond_analysis = self._analyze_bond_characteristics()
            
            # Calculate overall confidence score
            confidence_score = self._calculate_confidence_score()
            
            # Generate recommendations
            recommendations = self._generate_recommendations(molecular_state, bond_analysis)
            
            # Create processed data result
            result = ProcessedData(
                timestamp=time.time(),
                molecular_state=molecular_state,
                bond_analysis=bond_analysis,
                confidence_score=confidence_score,
                recommendations=recommendations
            )
            
            return result
            
        except Exception as e:
            print(f"Error in state analysis: {e}")
            return None
    
    def _analyze_bond_characteristics(self) -> Dict[str, float]:
        """Analyze bond characteristics from vibration signals"""
        bond_signals = self.signal_buffer.get_recent_signals('bond_vibration', self.signal_windows['medium'])
        
        if not bond_signals:
            return {}
        
        # Extract vibration frequencies and amplitudes
        frequencies = []
        amplitudes = []
        
        for signal in bond_signals:
            if len(signal.values) >= 2:
                # Assuming signal.values contains frequency/amplitude data
                frequencies.extend(signal.values[::2])  # Even indices: frequencies
                amplitudes.extend(signal.values[1::2])  # Odd indices: amplitudes
        
        analysis = {}
        if frequencies:
            analysis['avg_frequency'] = statistics.mean(frequencies)
            analysis['freq_std_dev'] = statistics.stdev(frequencies) if len(frequencies) > 1 else 0
            analysis['freq_range'] = max(frequencies) - min(frequencies)
        
        if amplitudes:
            analysis['avg_amplitude'] = statistics.mean(amplitudes)
            analysis['amp_std_dev'] = statistics.stdev(amplitudes) if len(amplitudes) > 1 else 0
            analysis['amp_range'] = max(amplitudes) - min(amplitudes)
        
        return analysis
    
    def _calculate_confidence_score(self) -> float:
        """Calculate overall confidence in the current analysis"""
        # Factors affecting confidence:
        # 1. Number of recent signals
        # 2. Consistency of measurements
        # 3. Signal quality
        
        total_signals = sum(len(buffer) for buffer in self.signal_buffer.buffers.values())
        min_required_signals = 10  # Minimum signals for reliable analysis
        
        # Base confidence on signal quantity
        signal_confidence = min(1.0, total_signals / 50.0)
        
        # Factor in signal quality (average confidence from individual signals)
        avg_signal_quality = 0.0
        signal_count = 0
        for buffer in self.signal_buffer.buffers.values():
            for signal in buffer:
                avg_signal_quality += signal.confidence
                signal_count += 1
        
        if signal_count > 0:
            avg_signal_quality /= signal_count
        else:
            avg_signal_quality = 0.5  # Default medium quality
        
        # Combine confidences
        overall_confidence = (signal_confidence + avg_signal_quality) / 2.0
        return max(0.0, min(1.0, overall_confidence))
    
    def _generate_recommendations(self, molecular_state: Dict, bond_analysis: Dict) -> List[str]:
        """Generate recommendations based on current analysis"""
        recommendations = []
        
        # Analyze bond stability
        if 'avg_frequency' in bond_analysis and 'freq_std_dev' in bond_analysis:
            freq_std = bond_analysis['freq_std_dev']
            if freq_std > 0.5:  # High variation indicates instability
                recommendations.append("Bond instability detected - increase stabilization field")
            elif freq_std < 0.1:  # Very stable
                recommendations.append("Bond stable - maintain current parameters")
        
        # Analyze electron density
        if 'electron_density_avg' in molecular_state:
            elec_density = molecular_state['electron_density_avg']
            if elec_density > 1.5:  # High density
                recommendations.append("High electron density detected - adjust electromagnetic field")
            elif elec_density < 0.5:  # Low density
                recommendations.append("Low electron density - increase field intensity")
        
        # Temperature considerations
        temp_avg = self.signal_buffer.get_average_signal_value('temperature', self.signal_windows['short'])
        if temp_avg and temp_avg > 310:  # Too hot (>37°C)
            recommendations.append("Temperature elevated - activate cooling system")
        elif temp_avg and temp_avg < 290:  # Too cold (<17°C)
            recommendations.append("Temperature low - adjust thermal regulation")
        
        if not recommendations:
            recommendations.append("Molecular state stable - continue current operation")
        
        return recommendations


class LiveMolecularMonitor:
    """Monitors live molecular changes during manipulation process"""
    
    def __init__(self, analyzer: RealTimeAnalyzer):
        self.analyzer = analyzer
        self.data_history: List[ProcessedData] = []
        self.max_history = 1000
        self.monitoring_active = False
        
    def start_monitoring(self):
        """Start monitoring molecular changes"""
        self.monitoring_active = True
        self.analyzer.register_callback(self._process_analysis_result)
        self.analyzer.start_analyzer()
        print("Live molecular monitoring started")
    
    def stop_monitoring(self):
        """Stop monitoring molecular changes"""
        self.monitoring_active = False
        self.analyzer.stop_analyzer()
        print("Live molecular monitoring stopped")
    
    def _process_analysis_result(self, result: ProcessedData):
        """Process analysis results and store in history"""
        self.data_history.append(result)
        
        # Maintain history size
        if len(self.data_history) > self.max_history:
            self.data_history.pop(0)
        
        # Print current status for monitoring
        print(f"[{result.timestamp:.2f}] Molecular state updated. "
              f"Confidence: {result.confidence_score:.2f}. "
              f"Recommendations: {len(result.recommendations)}")
    
    def get_current_status(self) -> Dict[str, Any]:
        """Get current molecular status"""
        if not self.data_history:
            return {"status": "no_data", "timestamp": time.time()}
        
        latest = self.data_history[-1]
        return {
            "status": "active",
            "timestamp": latest.timestamp,
            "molecular_state": latest.molecular_state,
            "bond_analysis": latest.bond_analysis,
            "confidence": latest.confidence_score,
            "recommendations": latest.recommendations
        }
    
    def get_trend_analysis(self, minutes: int = 5) -> Dict[str, Any]:
        """Analyze trends over specified time period"""
        cutoff_time = time.time() - (minutes * 60)
        recent_data = [d for d in self.data_history if d.timestamp >= cutoff_time]
        
        if not recent_data:
            return {"trend": "insufficient_data"}
        
        # Analyze confidence trend
        confidences = [d.confidence_score for d in recent_data]
        avg_confidence = sum(confidences) / len(confidences)
        
        # Analyze molecular state trends
        state_keys = set()
        for data in recent_data:
            state_keys.update(data.molecular_state.keys())
        
        trends = {}
        for key in state_keys:
            values = [d.molecular_state.get(key, 0) for d in recent_data]
            if values:
                trends[key] = {
                    "current": values[-1],
                    "average": sum(values) / len(values),
                    "min": min(values),
                    "max": max(values),
                    "trend_direction": "increasing" if values[-1] > values[0] else "decreasing" if values[-1] < values[0] else "stable"
                }
        
        return {
            "period_minutes": minutes,
            "data_points": len(recent_data),
            "avg_confidence": avg_confidence,
            "molecular_trends": trends
        }


class AdaptiveControlSystem:
    """Adaptive control system that adjusts parameters based on real-time analysis"""
    
    def __init__(self, monitor: LiveMolecularMonitor):
        self.monitor = monitor
        self.control_parameters = {
            'voltage_multiplier': 1.0,
            'frequency_offset': 0.0,
            'magnetic_field_strength': 1.0,
            'pulse_duration': 0.001,
            'feedback_gain': 0.1
        }
        self.parameter_history: List[Dict] = []
        
    def update_parameters_based_on_feedback(self):
        """Update control parameters based on real-time feedback"""
        status = self.monitor.get_current_status()
        
        if status["status"] == "no_data":
            return
        
        recommendations = status.get("recommendations", [])
        
        # Process recommendations and adjust parameters
        for rec in recommendations:
            if "increase stabilization field" in rec:
                self.control_parameters['magnetic_field_strength'] *= 1.05  # Increase by 5%
                self.control_parameters['voltage_multiplier'] *= 1.02      # Small voltage increase
            elif "Bond stable" in rec:
                # Reduce power consumption when stable
                self.control_parameters['magnetic_field_strength'] *= 0.98
                self.control_parameters['voltage_multiplier'] *= 0.99
            elif "High electron density" in rec:
                self.control_parameters['frequency_offset'] += 0.01
            elif "Low electron density" in rec:
                self.control_parameters['frequency_offset'] -= 0.01
            elif "Temperature elevated" in rec:
                self.control_parameters['pulse_duration'] *= 0.95  # Reduce pulse duration
                self.control_parameters['voltage_multiplier'] *= 0.98
            elif "Temperature low" in rec:
                self.control_parameters['pulse_duration'] *= 1.02
                self.control_parameters['voltage_multiplier'] *= 1.01
        
        # Ensure parameters stay within safe bounds
        self._constrain_parameters()
        
        # Store in history
        self.parameter_history.append({
            "timestamp": time.time(),
            "parameters": self.control_parameters.copy()
        })
        
        # Maintain history size
        if len(self.parameter_history) > 100:
            self.parameter_history.pop(0)
    
    def _constrain_parameters(self):
        """Ensure control parameters stay within safe operational bounds"""
        constraints = {
            'voltage_multiplier': (0.1, 3.0),
            'frequency_offset': (-1.0, 1.0),
            'magnetic_field_strength': (0.1, 2.0),  # Limited by neodymium magnet
            'pulse_duration': (0.0001, 0.01),      # 0.1ms to 10ms
            'feedback_gain': (0.01, 1.0)
        }
        
        for param, (min_val, max_val) in constraints.items():
            current_val = self.control_parameters[param]
            self.control_parameters[param] = max(min_val, min(max_val, current_val))
    
    def get_optimal_parameters(self) -> Dict[str, float]:
        """Get current optimal parameters for molecular manipulation"""
        return self.control_parameters.copy()


def simulate_molecular_signals(analyzer: RealTimeAnalyzer, duration: float = 30.0):
    """Simulate molecular signals for testing the system"""
    import random
    
    start_time = time.time()
    signal_types = ['bond_vibration', 'electron_density', 'magnetic_response', 'temperature', 'pressure']
    
    while time.time() - start_time < duration:
        # Generate random molecular signals
        for signal_type in signal_types:
            # Create varying signal values based on type
            if signal_type == 'bond_vibration':
                values = [random.uniform(0.8, 1.2) for _ in range(5)]  # Vibration amplitudes
            elif signal_type == 'electron_density':
                values = [random.uniform(0.5, 1.5) for _ in range(3)]  # Density values
            elif signal_type == 'magnetic_response':
                values = [random.uniform(0.9, 1.1) for _ in range(4)]  # Response values
            elif signal_type == 'temperature':
                values = [random.uniform(295, 305)]  # Around 22-32°C in Kelvin
            else:  # pressure
                values = [random.uniform(0.95, 1.05)]  # Pressure ratios
            
            signal = MolecularSignal(
                timestamp=time.time(),
                signal_type=signal_type,
                values=values,
                confidence=random.uniform(0.7, 1.0),
                metadata={"sensor_id": f"sensor_{signal_type[:3]}_{random.randint(1, 10)}"}
            )
            
            analyzer.add_signal(signal)
        
        time.sleep(0.05)  # 50ms between signal batches


if __name__ == "__main__":
    # Example usage of the real-time data processing system
    analyzer = RealTimeAnalyzer()
    monitor = LiveMolecularMonitor(analyzer)
    controller = AdaptiveControlSystem(monitor)
    
    # Start monitoring
    monitor.start_monitoring()
    
    # Simulate molecular signals for 10 seconds
    print("Starting signal simulation...")
    sim_thread = threading.Thread(target=simulate_molecular_signals, args=(analyzer, 10.0))
    sim_thread.daemon = True
    sim_thread.start()
    
    # Run adaptive control for 10 seconds
    start_time = time.time()
    while time.time() - start_time < 10.0:
        controller.update_parameters_based_on_feedback()
        optimal_params = controller.get_optimal_parameters()
        print(f"Optimal parameters: {optimal_params}")
        time.sleep(1.0)
    
    # Stop monitoring
    monitor.stop_monitoring()
    print("Real-time data processing completed")
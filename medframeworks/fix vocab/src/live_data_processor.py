import json
import time
import logging
import threading
from typing import Dict, List, Optional, Callable
from dataclasses import dataclass
import numpy as np
from datetime import datetime

@dataclass
class DataPacket:
    packet_id: str
    timestamp: float
    data_type: str  # 'bbb', 'inflammation', 'stem_cells', 'exosomes', 'composite'
    values: Dict[str, float]
    quality_score: float
    source: str

class LiveDataProcessor:
    def __init__(self):
        self.data_streams = {}
        self.packet_queue = []
        self.processors = {}
        self.callbacks = []
        self.processing_active = False
        self.thread = None
        
        # Initialize data processors for different types
        self._initialize_processors()
        
    def _initialize_processors(self):
        """Initialize data processing functions for different data types"""
        self.processors = {
            'bbb': self._process_bbb_data,
            'inflammation': self._process_inflammation_data,
            'stem_cells': self._process_stem_cell_data,
            'exosomes': self._process_exosome_data,
            'composite': self._process_composite_data
        }
    
    def start_processing(self):
        """Start the data processing loop"""
        if self.processing_active:
            return
            
        self.processing_active = True
        self.thread = threading.Thread(target=self._processing_loop, daemon=True)
        self.thread.start()
        logging.info("Live data processing started")
    
    def stop_processing(self):
        """Stop data processing"""
        self.processing_active = False
        if self.thread and self.thread.is_alive():
            self.thread.join(timeout=1.0)
        logging.info("Live data processing stopped")
    
    def _processing_loop(self):
        """Main processing loop"""
        while self.processing_active:
            if self.packet_queue:
                packet = self.packet_queue.pop(0)
                self._process_packet(packet)
            time.sleep(0.1)  # 100ms processing interval
    
    def ingest_data_packet(self, raw_data: Dict, source: str = "biometric_sensor"):
        """Ingest a new data packet into the system"""
        try:
            packet = self._validate_and_package_data(raw_data, source)
            self.packet_queue.append(packet)
            logging.debug(f"Ingested packet {packet.packet_id} from {source}")
            return True
        except Exception as e:
            logging.error(f"Failed to ingest data packet: {e}")
            return False
    
    def _validate_and_package_data(self, raw_data: Dict, source: str) -> DataPacket:
        """Validate raw data and create structured packet"""
        # Validate required fields
        if 'data_type' not in raw_data or 'values' not in raw_data:
            raise ValueError("Missing required fields: data_type or values")
        
        # Create packet with unique ID and timestamp
        packet_id = f"pkt_{int(time.time() * 1000)}_{len(self.packet_queue)}"
        
        packet = DataPacket(
            packet_id=packet_id,
            timestamp=time.time(),
            data_type=raw_data['data_type'],
            values=raw_data['values'],
            quality_score=self._calculate_quality_score(raw_data),
            source=source
        )
        
        return packet
    
    def _calculate_quality_score(self, data: Dict) -> float:
        """Calculate data quality score (0-1)"""
        score = 1.0
        
        # Check for missing values
        if 'values' in data:
            for key, value in data['values'].items():
                if value is None or (isinstance(value, (int, float)) and not np.isfinite(value)):
                    score *= 0.8  # Penalize for invalid values
        
        # Check timestamp freshness (if provided)
        if 'timestamp' in data:
            age = time.time() - data['timestamp']
            if age > 300:  # 5 minutes old
                score *= max(0.5, 1.0 - (age - 300) / 3600)  # Gradual decay
        
        return max(0.0, min(1.0, score))
    
    def _process_packet(self, packet: DataPacket):
        """Process individual data packet"""
        processor = self.processors.get(packet.data_type)
        if processor:
            try:
                result = processor(packet)
                self._update_data_streams(packet.data_type, result)
                self._notify_callbacks(packet, result)
                logging.info(f"Processed {packet.data_type} packet: {result}")
            except Exception as e:
                logging.error(f"Failed to process packet {packet.packet_id}: {e}")
        else:
            logging.warning(f"No processor for data type: {packet.data_type}")
    
    def _process_bbb_data(self, packet: DataPacket) -> Dict:
        """Process blood-brain barrier integrity data"""
        values = packet.values
        return {
            'integrity_score': float(values.get('integrity', 0.0)),
            'permeability': float(values.get('permeability', 0.0)),
            'repair_rate': float(values.get('repair_rate', 0.0)),
            'confidence': packet.quality_score,
            'timestamp': packet.timestamp
        }
    
    def _process_inflammation_data(self, packet: DataPacket) -> Dict:
        """Process neuroinflammation data"""
        values = packet.values
        return {
            'inflammation_level': float(values.get('level', 0.0)),
            'cytokine_level': float(values.get('cytokines', 0.0)),
            'resolution_rate': float(values.get('resolution_rate', 0.0)),
            'confidence': packet.quality_score,
            'timestamp': packet.timestamp
        }
    
    def _process_stem_cell_data(self, packet: DataPacket) -> Dict:
        """Process stem cell activity data"""
        values = packet.values
        return {
            'activity_level': float(values.get('activity', 0.0)),
            'migration_rate': float(values.get('migration', 0.0)),
            'differentiation': float(values.get('differentiation', 0.0)),
            'viability': float(values.get('viability', 0.0)),
            'confidence': packet.quality_score,
            'timestamp': packet.timestamp
        }
    
    def _process_exosome_data(self, packet: DataPacket) -> Dict:
        """Process exosome delivery data"""
        values = packet.values
        return {
            'delivery_efficiency': float(values.get('efficiency', 0.0)),
            'targeting_accuracy': float(values.get('targeting', 0.0)),
            'cargo_quality': float(values.get('cargo', 0.0)),
            'uptake_rate': float(values.get('uptake', 0.0)),
            'confidence': packet.quality_score,
            'timestamp': packet.timestamp
        }
    
    def _process_composite_data(self, packet: DataPacket) -> Dict:
        """Process composite biological data"""
        values = packet.values
        return {
            'overall_health': float(values.get('health_score', 0.0)),
            'repair_progress': float(values.get('progress', 0.0)),
            'treatment_efficacy': float(values.get('efficacy', 0.0)),
            'predictive_outcome': float(values.get('outlook', 0.0)),
            'confidence': packet.quality_score,
            'timestamp': packet.timestamp
        }
    
    def _update_data_streams(self, data_type: str, processed_data: Dict):
        """Update data streams with processed results"""
        if data_type not in self.data_streams:
            self.data_streams[data_type] = []
        
        # Keep only the last 1000 entries per stream
        if len(self.data_streams[data_type]) >= 1000:
            self.data_streams[data_type].pop(0)
        
        self.data_streams[data_type].append(processed_data)
    
    def register_callback(self, callback: Callable[[DataPacket, Dict], None]):
        """Register callback for processed data"""
        self.callbacks.append(callback)
        logging.info(f"Registered new data callback")
    
    def _notify_callbacks(self, packet: DataPacket, result: Dict):
        """Notify all registered callbacks"""
        for callback in self.callbacks:
            try:
                callback(packet, result)
            except Exception as e:
                logging.error(f"Callback error: {e}")
    
    def get_latest_data(self, data_type: str = None) -> Dict:
        """Get latest data from all or specific streams"""
        if data_type:
            if data_type in self.data_streams and self.data_streams[data_type]:
                return self.data_streams[data_type][-1]
            return {}
        
        # Return latest from all streams
        latest = {}
        for stream_type, data_list in self.data_streams.items():
            if data_list:
                latest[stream_type] = data_list[-1]
        
        return latest
    
    def get_data_history(self, data_type: str, limit: int = 100) -> List[Dict]:
        """Get historical data for a specific type"""
        if data_type in self.data_streams:
            return self.data_streams[data_type][-limit:]
        return []
    
    def calculate_trends(self, data_type: str, window: int = 10) -> Dict:
        """Calculate trends for a data type"""
        history = self.get_data_history(data_type, window)
        if not history:
            return {}
        
        # Extract primary value (assuming first numeric value in dict)
        values = []
        for entry in history:
            for val in entry.values():
                if isinstance(val, (int, float)):
                    values.append(val)
                    break
        
        if not values:
            return {}
        
        # Calculate trend metrics
        values = np.array(values)
        trend = float(np.polyfit(range(len(values)), values, 1)[0])  # Slope
        volatility = float(np.std(values))
        mean = float(np.mean(values))
        
        return {
            'trend': trend,
            'volatility': volatility,
            'mean': mean,
            'trend_direction': 'increasing' if trend > 0 else 'decreasing' if trend < 0 else 'stable',
            'samples': len(values)
        }
    
    def generate_health_report(self) -> Dict:
        """Generate comprehensive health status report"""
        report = {
            'timestamp': datetime.now().isoformat(),
            'overall_score': 0.0,
            'components': {},
            'trends': {},
            'recommendations': []
        }
        
        # Collect data from all streams
        for data_type in self.data_streams:
            latest = self.get_latest_data(data_type)
            if latest:
                report['components'][data_type] = latest
                
                # Calculate trends
                trends = self.calculate_trends(data_type)
                if trends:
                    report['trends'][data_type] = trends
        
        # Calculate overall score (weighted average)
        weights = {'bbb': 0.3, 'inflammation': 0.25, 'stem_cells': 0.2, 'exosomes': 0.15, 'composite': 0.1}
        total_weight = 0.0
        weighted_sum = 0.0
        
        for comp_type, data in report['components'].items():
            weight = weights.get(comp_type, 0.1)
            # Use the first numeric value as score
            for value in data.values():
                if isinstance(value, (int, float)):
                    weighted_sum += value * weight
                    total_weight += weight
                    break
        
        if total_weight > 0:
            report['overall_score'] = weighted_sum / total_weight
        
        # Generate recommendations based on trends
        self._generate_recommendations(report)
        
        return report
    
    def _generate_recommendations(self, report: Dict):
        """Generate treatment recommendations based on data"""
        recommendations = []
        
        # BBB integrity recommendations
        if 'bbb' in report['components']:
            bbb_data = report['components']['bbb']
            if bbb_data.get('integrity_score', 0) < 70:
                recommendations.append({
                    'type': 'bbb_repair',
                    'priority': 'high',
                    'message': 'Increase stem cell therapy intensity for BBB repair',
                    'suggested_actions': ['boost_stem_cells', 'increase_exosome_delivery']
                })
        
        # Inflammation recommendations
        if 'inflammation' in report['components']:
            inflam_data = report['components']['inflammation']
            if inflam_data.get('inflammation_level', 100) > 50:
                recommendations.append({
                    'type': 'anti_inflammation',
                    'priority': 'medium',
                    'message': 'Consider anti-inflammatory protocols',
                    'suggested_actions': ['modulate_immune_response', 'apply_cooling_stimulation']
                })
        
        report['recommendations'] = recommendations

# Example usage
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    
    processor = LiveDataProcessor()
    processor.start_processing()
    
    try:
        # Example data packets
        test_data = [
            {'data_type': 'bbb', 'values': {'integrity': 65.5, 'permeability': 12.3}},
            {'data_type': 'inflammation', 'values': {'level': 45.2, 'cytokines': 23.1}},
            {'data_type': 'stem_cells', 'values': {'activity': 78.9, 'migration': 65.4}},
            {'data_type': 'exosomes', 'values': {'efficiency': 82.1, 'targeting': 75.6}},
            {'data_type': 'composite', 'values': {'health_score': 72.3, 'progress': 15.8}}
        ]
        
        for data in test_data:
            processor.ingest_data_packet(data, "test_sensor")
            time.sleep(0.5)
        
        # Wait for processing
        time.sleep(1)
        
        # Generate report
        report = processor.generate_health_report()
        print("\nHealth Report:")
        print(f"Overall Score: {report['overall_score']:.1f}%")
        for comp, data in report['components'].items():
            print(f"{comp}: {data}")
        
        print("\nRecommendations:")
        for rec in report['recommendations']:
            print(f"- {rec['message']} ({rec['priority']})")
        
    finally:
        processor.stop_processing()
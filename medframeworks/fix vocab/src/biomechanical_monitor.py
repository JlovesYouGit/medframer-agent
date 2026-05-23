import numpy as np
from typing import Dict, List, Optional
import time
import logging
from dataclasses import dataclass
import threading

@dataclass
class BioRepairStatus:
    bbb_integrity: float  # 0-100% blood-brain barrier integrity
    neuroinflammation: float  # 0-100% inflammation level (lower is better)
    stem_cell_activity: float  # 0-100% stem cell activity
    exosome_delivery: float  # 0-100% exosome delivery efficiency
    repair_progress: float  # 0-100% overall repair progress
    last_update: float

class BiomechanicalMonitor:
    def __init__(self):
        self.current_status = BioRepairStatus(
            bbb_integrity=0.0,
            neuroinflammation=100.0,
            stem_cell_activity=0.0,
            exosome_delivery=0.0,
            repair_progress=0.0,
            last_update=time.time()
        )
        self.monitoring_active = False
        self.thread = None
        self.data_packets = []
        
        # Simulated biological response parameters
        self.response_params = {
            'stimulation_effectiveness': 0.8,
            'repair_rate': 0.05,  # % per minute
            'max_repair': 100.0,
            'baseline_inflammation': 100.0
        }
    
    def start_monitoring(self):
        """Start continuous biomechanical monitoring"""
        if self.monitoring_active:
            return
            
        self.monitoring_active = True
        self.thread = threading.Thread(target=self._monitoring_loop, daemon=True)
        self.thread.start()
        logging.info("Biomechanical monitoring started")
    
    def stop_monitoring(self):
        """Stop monitoring"""
        self.monitoring_active = False
        if self.thread and self.thread.is_alive():
            self.thread.join(timeout=1.0)
        logging.info("Biomechanical monitoring stopped")
    
    def _monitoring_loop(self):
        """Continuous monitoring loop"""
        while self.monitoring_active:
            # Simulate gradual repair process
            self._update_repair_status()
            time.sleep(60)  # Update every minute
    
    def _update_repair_status(self):
        """Update repair status based on stimulation and time"""
        current_time = time.time()
        elapsed = (current_time - self.current_status.last_update) / 60  # minutes
        
        # Calculate repair progress
        repair_increment = self.response_params['repair_rate'] * elapsed
        
        # Update status with bounds checking
        new_bbb = min(self.current_status.bbb_integrity + repair_increment, 100.0)
        new_inflammation = max(self.current_status.neuroinflammation - repair_increment, 0.0)
        new_progress = (new_bbb + (100 - new_inflammation)) / 2
        
        self.current_status = BioRepairStatus(
            bbb_integrity=new_bbb,
            neuroinflammation=new_inflammation,
            stem_cell_activity=min(self.current_status.stem_cell_activity + repair_increment * 2, 100.0),
            exosome_delivery=min(self.current_status.exosome_delivery + repair_increment * 1.5, 100.0),
            repair_progress=new_progress,
            last_update=current_time
        )
    
    def process_data_packet(self, packet: Dict):
        """Process incoming biological data packets"""
        self.data_packets.append({
            'timestamp': time.time(),
            'data': packet,
            'processed': False
        })
        
        # Extract relevant metrics from packet
        if 'bbb_integrity' in packet:
            self.current_status.bbb_integrity = float(packet['bbb_integrity'])
        if 'inflammation' in packet:
            self.current_status.neuroinflammation = float(packet['inflammation'])
        if 'stem_cells' in packet:
            self.current_status.stem_cell_activity = float(packet['stem_cells'])
        if 'exosomes' in packet:
            self.current_status.exosome_delivery = float(packet['exosomes'])
        
        # Calculate overall progress
        self.current_status.repair_progress = self._calculate_overall_progress()
        self.current_status.last_update = time.time()
        
        logging.info(f"Processed data packet: BBB={self.current_status.bbb_integrity:.1f}%, "
                    f"Inflammation={self.current_status.neuroinflammation:.1f}%")
    
    def _calculate_overall_progress(self) -> float:
        """Calculate overall repair progress percentage"""
        weights = {
            'bbb': 0.4,
            'inflammation': 0.3,
            'stem_cells': 0.15,
            'exosomes': 0.15
        }
        
        progress = (
            weights['bbb'] * self.current_status.bbb_integrity +
            weights['inflammation'] * (100 - self.current_status.neuroinflammation) +
            weights['stem_cells'] * self.current_status.stem_cell_activity +
            weights['exosomes'] * self.current_status.exosome_delivery
        )
        
        return min(progress, 100.0)
    
    def apply_stimulation_boost(self, intensity: float, duration: float):
        """Apply stimulation boost to enhance biological repair"""
        boost_factor = intensity * duration / 60.0  # Normalized boost
        
        # Enhanced repair during stimulation
        repair_boost = boost_factor * 2.0  # 2x repair rate during stimulation
        
        self.current_status.bbb_integrity = min(
            self.current_status.bbb_integrity + repair_boost, 100.0
        )
        self.current_status.neuroinflammation = max(
            self.current_status.neuroinflammation - repair_boost, 0.0
        )
        self.current_status.repair_progress = self._calculate_overall_progress()
        
        logging.info(f"Applied stimulation boost: +{repair_boost:.2f}% repair progress")
    
    def generate_health_report(self) -> Dict:
        """Generate comprehensive health status report"""
        return {
            'timestamp': time.time(),
            'blood_brain_barrier': {
                'integrity_percent': float(self.current_status.bbb_integrity),
                'status': 'excellent' if self.current_status.bbb_integrity > 90 else
                         'good' if self.current_status.bbb_integrity > 70 else
                         'fair' if self.current_status.bbb_integrity > 50 else
                         'poor'
            },
            'neuroinflammation': {
                'level_percent': float(self.current_status.neuroinflammation),
                'status': 'low' if self.current_status.neuroinflammation < 20 else
                         'moderate' if self.current_status.neuroinflammation < 50 else
                         'high'
            },
            'stem_cell_therapy': {
                'activity_percent': float(self.current_status.stem_cell_activity),
                'efficiency': 'high' if self.current_status.stem_cell_activity > 80 else
                             'medium' if self.current_status.stem_cell_activity > 50 else
                             'low'
            },
            'exosome_delivery': {
                'efficiency_percent': float(self.current_status.exosome_delivery),
                'status': 'optimal' if self.current_status.exosome_delivery > 85 else
                         'good' if self.current_status.exosome_delivery > 60 else
                         'suboptimal'
            },
            'overall_repair': {
                'progress_percent': float(self.current_status.repair_progress),
                'projected_completion': self._calculate_projection(),
                'status': 'complete' if self.current_status.repair_progress >= 99.9 else
                         'final_stage' if self.current_status.repair_progress > 90 else
                         'advanced' if self.current_status.repair_progress > 70 else
                         'intermediate' if self.current_status.repair_progress > 40 else
                         'early_stage'
            }
        }
    
    def _calculate_projection(self) -> str:
        """Calculate projected completion time"""
        if self.current_status.repair_progress >= 99.9:
            return "complete"
        
        remaining = 100 - self.current_status.repair_progress
        hours_needed = remaining / self.response_params['repair_rate']
        
        if hours_needed < 1:
            return f"{int(hours_needed * 60)} minutes"
        elif hours_needed < 24:
            return f"{int(hours_needed)} hours"
        else:
            return f"{int(hours_needed / 24)} days"
    
    def reset_monitoring(self):
        """Reset monitoring to initial state"""
        self.current_status = BioRepairStatus(
            bbb_integrity=0.0,
            neuroinflammation=100.0,
            stem_cell_activity=0.0,
            exosome_delivery=0.0,
            repair_progress=0.0,
            last_update=time.time()
        )
        self.data_packets = []
        logging.info("Biomechanical monitoring reset")

# Example usage
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    
    monitor = BiomechanicalMonitor()
    monitor.start_monitoring()
    
    try:
        # Simulate data packets from biological sensors
        test_packets = [
            {'bbb_integrity': 25.0, 'inflammation': 75.0, 'stem_cells': 15.0, 'exosomes': 10.0},
            {'bbb_integrity': 45.0, 'inflammation': 55.0, 'stem_cells': 30.0, 'exosomes': 25.0},
            {'bbb_integrity': 70.0, 'inflammation': 30.0, 'stem_cells': 60.0, 'exosomes': 50.0}
        ]
        
        for packet in test_packets:
            monitor.process_data_packet(packet)
            report = monitor.generate_health_report()
            print(f"Progress: {report['overall_repair']['progress_percent']:.1f}%")
            time.sleep(2)
        
        # Apply stimulation boost
        monitor.apply_stimulation_boost(intensity=0.8, duration=30.0)
        
        final_report = monitor.generate_health_report()
        print("\nFinal Health Report:")
        for category, data in final_report.items():
            if isinstance(data, dict) and 'percent' in str(data).lower():
                print(f"  {category}: {data.get('progress_percent', data.get('level_percent', data.get('efficiency_percent', data.get('integrity_percent', 0)))):.1f}%")
        
    finally:
        monitor.stop_monitoring()
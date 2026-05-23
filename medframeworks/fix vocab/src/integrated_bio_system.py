import time
import logging
import json
from typing import Dict, List, Optional
from datetime import datetime

from .usb_neuro_stimulator import USBNeuroStimulator
from .biomechanical_monitor import BiomechanicalMonitor, BioRepairStatus
from .live_data_processor import LiveDataProcessor, DataPacket
from .vocal_rehabilitation_trainer import VocalRehabilitationTrainer
from .motor_coordinator import MotorCoordinator
from .vocal_muscle_controller import VocalMuscleController

class IntegratedBioSystem:
    def __init__(self):
        self.stimulator = USBNeuroStimulator()
        self.bio_monitor = BiomechanicalMonitor()
        self.data_processor = LiveDataProcessor()
        self.vocal_trainer = VocalRehabilitationTrainer()
        self.motor_coordinator = MotorCoordinator()
        self.muscle_controller = VocalMuscleController()
        
        self.system_status = {
            'online': False,
            'last_update': time.time(),
            'repair_progress': 0.0,
            'treatment_phase': 'initialization'
        }
        
        # Register data callbacks
        self.data_processor.register_callback(self._on_data_processed)
        
    def startup_sequence(self) -> bool:
        """Complete system startup sequence"""
        logging.info("Starting integrated bio-system...")
        
        try:
            # Connect to stimulation hardware
            hardware_connected = self.stimulator.connect()
            
            # Start monitoring and processing
            self.bio_monitor.start_monitoring()
            self.data_processor.start_processing()
            
            self.system_status.update({
                'online': True,
                'hardware_connected': hardware_connected,
                'startup_time': datetime.now().isoformat(),
                'treatment_phase': 'baseline_assessment'
            })
            
            logging.info("Integrated bio-system started successfully")
            return True
            
        except Exception as e:
            logging.error(f"System startup failed: {e}")
            return False
    
    def shutdown_sequence(self):
        """Graceful system shutdown"""
        logging.info("Shutting down integrated bio-system...")
        
        self.stimulator.stop_stimulation()
        self.stimulator.disconnect()
        self.bio_monitor.stop_monitoring()
        self.data_processor.stop_processing()
        self.vocal_trainer.end_session()
        
        self.system_status.update({
            'online': False,
            'shutdown_time': datetime.now().isoformat(),
            'final_progress': self.system_status['repair_progress']
        })
        
        logging.info("System shutdown complete")
    
    def _on_data_processed(self, packet: DataPacket, result: Dict):
        """Callback for processed data packets"""
        try:
            # Update repair status based on new data
            if packet.data_type == 'bbb':
                self.bio_monitor.current_status.bbb_integrity = result.get('integrity_score', 0)
            elif packet.data_type == 'inflammation':
                self.bio_monitor.current_status.neuroinflammation = result.get('inflammation_level', 100)
            elif packet.data_type == 'stem_cells':
                self.bio_monitor.current_status.stem_cell_activity = result.get('activity_level', 0)
            elif packet.data_type == 'exosomes':
                self.bio_monitor.current_status.exosome_delivery = result.get('delivery_efficiency', 0)
            
            # Update overall progress
            self.system_status['repair_progress'] = self.bio_monitor.current_status.repair_progress
            self.system_status['last_update'] = time.time()
            
            # Adaptive treatment adjustment (avoid recursion)
            # Only adjust if not already in a treatment cycle
            if not self.system_status.get('in_treatment_cycle', False):
                self._adjust_treatment_parameters()
            
        except Exception as e:
            logging.error(f"Error in data callback: {e}")
    
    def _adjust_treatment_parameters(self):
        """Adjust treatment parameters based on real-time data"""
        current_status = self.bio_monitor.current_status
        
        # Get motor coordination parameters
        motor_params = self.motor_coordinator.get_current_parameters()
        if not motor_params['safety_ok']:
            logging.warning("Motor parameters exceeded safety limits")
            self._reduce_stimulation_intensity()
            return
        
        # Determine stimulation intensity based on repair progress
        if current_status.repair_progress < 30:
            # Early phase - moderate stimulation
            stimulation_intensity = 0.4
            treatment_phase = 'early_repair'
        elif current_status.repair_progress < 70:
            # Middle phase - increased stimulation
            stimulation_intensity = 0.6
            treatment_phase = 'active_repair'
        else:
            # Final phase - maintenance stimulation
            stimulation_intensity = 0.3
            treatment_phase = 'maintenance'
        
        # Adjust for inflammation levels
        if current_status.neuroinflammation > 60:
            stimulation_intensity *= 0.7  # Reduce intensity during high inflammation
            treatment_phase = 'inflammatory_control'
        
        # Update stimulation if needed
        if self.system_status['treatment_phase'] != treatment_phase:
            self.system_status['treatment_phase'] = treatment_phase
            self._apply_optimized_stimulation(stimulation_intensity)
    
    def _apply_optimized_stimulation(self, intensity: float):
        """Apply optimized stimulation pattern based on current phase"""
        phase = self.system_status['treatment_phase']
        motor_params = self.motor_coordinator.get_current_parameters()
        
        # Adjust intensity based on motor coordination needs
        effective_intensity = intensity * motor_params['articulation_gain']
        effective_intensity = min(effective_intensity, 1.0)
        
        if phase == 'early_repair':
            # Focus on BBB repair and stem cell activation
            self.stimulator.stimulate_brain_region('broca', effective_intensity * 0.8)
            self.stimulator.stimulate_vocal_tract('thyroid', effective_intensity * 0.6)
            
            # Apply cortical lag compensation
            time.sleep(motor_params['effective_lag_ms'] / 1000)
            
        elif phase == 'active_repair':
            # Balanced stimulation for comprehensive repair
            self.stimulator.stimulate_brain_region('broca', effective_intensity)
            self.stimulator.stimulate_brain_region('dlmc', effective_intensity * 0.7)
            self.stimulator.stimulate_vocal_tract('thyroid', effective_intensity * 0.8)
            self.stimulator.stimulate_vocal_tract('vocal_fold', effective_intensity * 0.5)
            
            # Apply cortical lag compensation
            time.sleep(motor_params['effective_lag_ms'] / 1000)
            
        elif phase == 'maintenance':
            # Gentle maintenance stimulation
            self.stimulator.stimulate_brain_region('broca', effective_intensity * 0.5)
            self.stimulator.stimulate_vocal_tract('thyroid', effective_intensity * 0.4)
            
            # Apply minimal lag compensation
            time.sleep(max(0, motor_params['effective_lag_ms'] / 2000))
            
        elif phase == 'inflammatory_control':
            # Anti-inflammatory focused stimulation
            self.stimulator.stimulate_brain_region('dlmc', effective_intensity * 0.6)
            self.stimulator.stimulate_vocal_tract('vocal_fold', effective_intensity * 0.3)
            
            # Skip lag compensation in emergency mode
        
        logging.info(f"Applied {phase} stimulation at intensity {intensity:.2f}")
    
    def ingest_biological_data(self, data_type: str, values: Dict, source: str = "internal_sensor"):
        """Ingest biological data into the system"""
        packet_data = {
            'data_type': data_type,
            'values': values,
            'timestamp': time.time()
        }
        
        return self.data_processor.ingest_data_packet(packet_data, source)
    
    def run_treatment_cycle(self, audio_data_path: Optional[str] = None):
        """Run a complete treatment cycle"""
        if not self.system_status['online']:
            logging.warning("System not online - starting up")
            if not self.startup_sequence():
                return False
        
        try:
            # Reset muscle states at start of cycle
            self.muscle_controller.reset_to_neutral()
            
            # Phase 1: Biological assessment
            logging.info("Starting biological assessment...")
            health_report = self.bio_monitor.generate_health_report()
            
            # Phase 2: Vocal assessment (if audio provided)
            if audio_data_path:
                logging.info("Running vocal assessment...")
                vocal_features = self.vocal_trainer.analyze_audio(audio_data_path)
                health_report['vocal_analysis'] = vocal_features
                
                # Update muscle targets based on phonemes detected
                for phoneme in vocal_features.get('phonemes', []):
                    self.muscle_controller.set_speech_targets(phoneme)
            
            # Phase 3: Adaptive stimulation
            logging.info("Applying adaptive stimulation...")
            self._adjust_treatment_parameters()
            
            # Apply muscle contraction adjustments
            self.muscle_controller.update_muscle_states()
            health_report['muscle_states'] = self.muscle_controller.get_current_contractions()
            
            # Phase 4: Progress update
            self.system_status['repair_progress'] = self.bio_monitor.current_status.repair_progress
            health_report['system_status'] = self.system_status.copy()
            
            logging.info(f"Treatment cycle complete - Progress: {self.system_status['repair_progress']:.1f}%")
            return health_report
            
        except Exception as e:
            logging.error(f"Treatment cycle failed: {e}")
            return False
    
    def get_system_status(self) -> Dict:
        """Get current system status"""
        status = self.system_status.copy()
        status['bio_status'] = self.bio_monitor.generate_health_report()
        status['data_stats'] = {
            'processed_packets': len(self.data_processor.packet_queue),
            'active_streams': len(self.data_processor.data_streams)
        }
        return status
    
    def emergency_stop(self):
        """Emergency stop all activities"""
        logging.warning("EMERGENCY STOP ACTIVATED")
        
        self.stimulator.stop_stimulation()
        self.stimulator.disconnect()
        self.bio_monitor.stop_monitoring()
        self.data_processor.stop_processing()
        self.motor_coordinator.reset_session()
        self.muscle_controller.reset_to_neutral()
        
        self.system_status.update({
            'online': False,
            'emergency_stop': True,
            'stop_time': datetime.now().isoformat()
        })
    
    def simulate_treatment_progress(self, hours: int = 24):
        """Simulate treatment progress over time"""
        logging.info(f"Simulating {hours} hours of treatment...")
        
        # Simulate motor learning improvements
        motor_error_reduction = 0.8 / hours  # 80% error reduction over simulation
        
        self.startup_sequence()
        
        try:
            for hour in range(hours):
                # Simulate data improvements
                progress_increment = 100 / hours  # Linear progress
                
                # Update biological metrics
                current = self.bio_monitor.current_status
                new_status = BioRepairStatus(
                    bbb_integrity=min(current.bbb_integrity + progress_increment * 0.8, 100),
                    neuroinflammation=max(current.neuroinflammation - progress_increment * 0.9, 0),
                    stem_cell_activity=min(current.stem_cell_activity + progress_increment * 1.2, 100),
                    exosome_delivery=min(current.exosome_delivery + progress_increment * 1.0, 100),
                    repair_progress=min(current.repair_progress + progress_increment, 100),
                    last_update=time.time()
                )
                
                # Simulate motor coordination improvements
                self.motor_coordinator.update_error_correction(-motor_error_reduction)
                
                self.bio_monitor.current_status = new_status
                self.system_status['repair_progress'] = new_status.repair_progress
                
                logging.info(f"Hour {hour + 1}: Progress = {new_status.repair_progress:.1f}%")
                time.sleep(0.1)  # Quick simulation
                
            final_report = self.get_system_status()
            logging.info(f"Simulation complete - Final progress: {final_report['repair_progress']:.1f}%")
            return final_report
            
        finally:
            self.shutdown_sequence()

# Example usage
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    
    system = IntegratedBioSystem()
    
    try:
        # Start the system
        if system.startup_sequence():
            # Simulate some data intake
            test_data = [
                ('bbb', {'integrity': 35.0, 'permeability': 20.0}),
                ('inflammation', {'level': 75.0, 'cytokines': 40.0}),
                ('stem_cells', {'activity': 25.0, 'migration': 30.0}),
                ('exosomes', {'efficiency': 20.0, 'targeting': 25.0})
            ]
            
            for data_type, values in test_data:
                system.ingest_biological_data(data_type, values)
                time.sleep(0.5)
            
            # Run a treatment cycle
            report = system.run_treatment_cycle()
            print(f"\nInitial Progress: {report['system_status']['repair_progress']:.1f}%")
            
            # Show system status
            status = system.get_system_status()
            print(f"\nSystem Status: {status['treatment_phase']}")
            print(f"BBB Integrity: {status['bio_status']['blood_brain_barrier']['integrity_percent']:.1f}%")
            print(f"Inflammation: {status['bio_status']['neuroinflammation']['level_percent']:.1f}%")
            
    finally:
        system.shutdown_sequence()
#!/usr/bin/env python3
"""
Complete Integrated Biological Repair System Runner
This script starts all components of the vocal rehabilitation system
"""

import os
import sys
import time
import logging
import subprocess
import threading
from pathlib import Path

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('system_integration.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

class SystemIntegrator:
    def __init__(self):
        self.processes = []
        self.system_status = {
            'dashboard': False,
            'bio_system': False,
            'simulation': False
        }
    
    def check_venv(self):
        """Check if virtual environment is active"""
        return 'VIRTUAL_ENV' in os.environ
    
    def activate_venv(self):
        """Activate virtual environment"""
        if not self.check_venv():
            logger.warning("Virtual environment not active - attempting to activate")
            try:
                # Try to activate venv
                activate_script = Path('venv/Scripts/activate.bat')
                if activate_script.exists():
                    os.system('call venv\\Scripts\\activate.bat')
                    logger.info("Virtual environment activated")
                else:
                    logger.error("Virtual environment not found. Please run setup_venv.bat first")
                    return False
            except Exception as e:
                logger.error(f"Failed to activate venv: {e}")
                return False
        return True
    
    def install_dependencies(self):
        """Install all required dependencies"""
        logger.info("Installing dependencies...")
        try:
            # Install main requirements
            subprocess.run([sys.executable, '-m', 'pip', 'install', '-r', 'requirements.txt'], 
                         check=True, capture_output=True, text=True)
            
            # Install additional requirements
            subprocess.run([sys.executable, '-m', 'pip', 'install', '-r', 'requirements_additional.txt'], 
                         check=True, capture_output=True, text=True)
            
            logger.info("All dependencies installed successfully")
            return True
        except subprocess.CalledProcessError as e:
            logger.error(f"Dependency installation failed: {e}")
            return False
    
    def start_dashboard(self):
        """Start the web dashboard"""
        logger.info("Starting bio-dashboard...")
        try:
            dashboard_process = subprocess.Popen([
                sys.executable, '-m', 'src.bio_dashboard',
                '--host', '127.0.0.1',
                '--port', '5000'
            ], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            
            self.processes.append(('dashboard', dashboard_process))
            time.sleep(3)  # Give dashboard time to start
            
            # Check if dashboard is running
            if dashboard_process.poll() is None:
                self.system_status['dashboard'] = True
                logger.info("Dashboard started successfully")
                return True
            else:
                stderr = dashboard_process.stderr.read().decode() if dashboard_process.stderr else 'Unknown error'
                logger.error(f"Dashboard failed to start: {stderr}")
                return False
                
        except Exception as e:
            logger.error(f"Failed to start dashboard: {e}")
            return False
    
    def run_demo_treatment(self):
        """Run a demonstration treatment cycle"""
        logger.info("Starting demo treatment cycle...")
        try:
            # Import and run the integrated system
            from src.integrated_bio_system import IntegratedBioSystem
            
            system = IntegratedBioSystem()
            if system.startup_sequence():
                # Simulate some biological data
                demo_data = [
                    ('bbb', {'integrity': 45.0, 'permeability': 15.0}),
                    ('inflammation', {'level': 60.0, 'cytokines': 25.0}),
                    ('stem_cells', {'activity': 35.0, 'migration': 40.0}),
                    ('exosomes', {'efficiency': 30.0, 'targeting': 35.0})
                ]
                
                for data_type, values in demo_data:
                    system.ingest_biological_data(data_type, values)
                    time.sleep(0.5)
                
                # Run treatment cycle
                result = system.run_treatment_cycle()
                if result:
                    logger.info(f"Demo treatment completed. Progress: {result['system_status']['repair_progress']:.1f}%")
                    return True
            
            return False
            
        except Exception as e:
            logger.error(f"Demo treatment failed: {e}")
            return False
    
    def start_simulation_mode(self):
        """Start simulation mode in background"""
        logger.info("Starting simulation mode...")
        try:
            sim_process = subprocess.Popen([
                sys.executable, '-m', 'src.bio_dashboard',
                '--host', '127.0.0.1',
                '--port', '5001',
                '--simulate'
            ], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            
            self.processes.append(('simulation', sim_process))
            time.sleep(3)
            
            if sim_process.poll() is None:
                self.system_status['simulation'] = True
                logger.info("Simulation mode started on port 5001")
                return True
            return False
            
        except Exception as e:
            logger.error(f"Failed to start simulation: {e}")
            return False
    
    def monitor_system(self):
        """Monitor system processes"""
        try:
            while True:
                for name, process in self.processes:
                    if process.poll() is not None:
                        logger.warning(f"{name} process terminated unexpectedly")
                        # Attempt to restart
                        if name == 'dashboard':
                            self.start_dashboard()
                
                time.sleep(10)
        except KeyboardInterrupt:
            logger.info("Monitoring interrupted")
    
    def cleanup(self):
        """Clean up all processes"""
        logger.info("Cleaning up processes...")
        for name, process in self.processes:
            try:
                process.terminate()
                process.wait(timeout=5)
            except:
                process.kill()
        self.processes.clear()
        logger.info("Cleanup completed")
    
    def run_full_system(self):
        """Run the complete integrated system"""
        logger.info("=== Starting Full Integrated Biological Repair System ===")
        
        # Check and activate virtual environment
        if not self.activate_venv():
            logger.error("Virtual environment setup failed")
            return False
        
        # Install dependencies if needed
        if not self.install_dependencies():
            logger.warning("Dependency installation had issues - continuing anyway")
        
        # Start dashboard
        if not self.start_dashboard():
            logger.error("Dashboard startup failed")
            return False
        
        # Start simulation mode (optional)
        if len(sys.argv) > 1 and 'simulate' in sys.argv:
            self.start_simulation_mode()
        
        # Run demo treatment
        if not self.run_demo_treatment():
            logger.warning("Demo treatment had issues")
        
        logger.info("System startup completed successfully!")
        logger.info("Web dashboard available at: http://127.0.0.1:5000")
        if self.system_status['simulation']:
            logger.info("Simulation dashboard at: http://127.0.0.1:5001")
        
        try:
            # Start monitoring
            self.monitor_system()
        except KeyboardInterrupt:
            logger.info("Shutting down system...")
        finally:
            self.cleanup()
        
        return True

def main():
    """Main entry point"""
    integrator = SystemIntegrator()
    
    try:
        success = integrator.run_full_system()
        if success:
            print("\n" + "="*60)
            print("SYSTEM STARTUP COMPLETED SUCCESSFULLY!")
            print("Access dashboards at:")
            print("  - Main: http://127.0.0.1:5000")
            print("  - Sim:  http://127.0.0.1:5001 (if enabled)")
            print("="*60)
            sys.exit(0)
        else:
            print("\nSystem startup failed. Check system_integration.log for details.")
            sys.exit(1)
            
    except Exception as e:
        logger.error(f"Unhandled exception: {e}")
        print(f"System crashed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
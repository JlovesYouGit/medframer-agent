#!/usr/bin/env python3
"""
Environment setup script for the enhanced molecular manipulation system
Installs required packages and configures Python environment
"""

import subprocess
import sys
import os

def install_package(package):
    """Install a package using pip"""
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", package])
        print(f"✓ Successfully installed {package}")
        return True
    except subprocess.CalledProcessError:
        print(f"❌ Failed to install {package}")
        return False

def setup_environment():
    """Set up the Python environment with required packages"""
    print("Setting up Python environment for enhanced molecular manipulation...")
    
    # Core packages
    packages = [
        "numpy>=1.21.0",
        "scipy>=1.7.0", 
        "matplotlib>=3.5.0",
        "shapely>=1.8.0",
        "pandas>=1.3.0",
        "scikit-learn>=1.0.0"
    ]
    
    # Install packages
    success_count = 0
    for package in packages:
        if install_package(package):
            success_count += 1
    
    print(f"\nInstallation complete: {success_count}/{len(packages)} packages installed")
    
    # Create mock packages for specialized libraries
    create_mock_libraries()
    
    return success_count == len(packages)

def create_mock_libraries():
    """Create mock libraries for specialized biofeedback functionality"""
    print("\nCreating specialized biofeedback libraries...")
    
    # Create biofeedback mock
    biofeedback_code = '''
"""Mock biofeedback library for arousal enhancement"""

class ArousalSensor:
    def __init__(self):
        self.baseline = 0.3
        self.current_level = self.baseline
    
    def read_arousal_level(self):
        import random
        # Simulate realistic arousal readings
        self.current_level = max(0.0, min(1.0, 
            self.current_level + random.uniform(-0.1, 0.2)))
        return self.current_level
    
    def calibrate_baseline(self):
        self.baseline = 0.3
        return self.baseline

class PhysiologicalMonitor:
    def __init__(self):
        self.heart_rate = 70
        self.skin_conductance = 0.5
        self.temperature = 36.5
    
    def get_vitals(self):
        import random
        return {
            'heart_rate': self.heart_rate + random.uniform(-5, 15),
            'skin_conductance': max(0.1, self.skin_conductance + random.uniform(-0.2, 0.4)),
            'temperature': self.temperature + random.uniform(-0.5, 1.0)
        }
'''
    
    with open('biofeedback.py', 'w') as f:
        f.write(biofeedback_code)
    
    # Create neuralsignals mock
    neural_code = '''
"""Mock neural signals library for brain-computer interface"""

class NeuralInterface:
    def __init__(self):
        self.connection_strength = 0.8
        self.signal_quality = 0.9
    
    def read_neural_activity(self):
        import random
        return {
            'alpha_waves': random.uniform(0.3, 0.8),
            'beta_waves': random.uniform(0.2, 0.6),
            'gamma_waves': random.uniform(0.1, 0.4),
            'pleasure_centers': random.uniform(0.0, 1.0)
        }
    
    def stimulate_pleasure_centers(self, intensity=0.5):
        return f"Neural stimulation applied at {intensity:.2f} intensity"

class BrainWaveAnalyzer:
    def analyze_arousal_patterns(self, neural_data):
        arousal_score = (neural_data['alpha_waves'] * 0.3 + 
                        neural_data['beta_waves'] * 0.4 + 
                        neural_data['gamma_waves'] * 0.3)
        return min(1.0, arousal_score)
'''
    
    with open('neuralsignals.py', 'w') as f:
        f.write(neural_code)
    
    print("✓ Specialized libraries created")

if __name__ == "__main__":
    setup_environment()
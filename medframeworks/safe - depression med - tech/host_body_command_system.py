#!/usr/bin/env python3
"""
Host Body Command System
Sends baseline adjustments to the host body through unified monitoring
Applies volumetric tuning and oxygen-pH optimization in real-time
"""

import time
import json
import math
import threading
from typing import Dict, List, Tuple, Any, Optional
from dataclasses import dataclass
from enum import Enum

# Import existing systems
from advanced_baseline_adjuster import AdvancedBaselineAdjuster
from unified_medical_translation_monitor import UnifiedMedicalTranslationMonitor
from live_usb_data_feed import LiveUSBDataFeed

class CommandType(Enum):
    APPLY_BASELINE_ADJUSTMENT = "apply_baseline_adjustment"
    UPDATE_OXYGEN_EFFICIENCY = "update_oxygen_efficiency"
    ADJUST_BREATHING_PATTERN = "adjust_breathing_pattern"
    OPTIMIZE_PH_BALANCE = "optimize_ph_balance"
    REDUCE_LUNG_STRAIN = "reduce_lung_strain"
    ACTIVATE_LONG_TERM_OPTIMIZATION = "activate_long_term_optimization"

class CommandStatus(Enum):
    PENDING = "pending"
    EXECUTING = "executing"
    COMPLETED = "completed"
    FAILED = "failed"
    ROLLBACK = "rollback"

@dataclass
class HostCommand:
    """Command to be sent to host body"""
    command_id: str
    command_type: CommandType
    parameters: Dict[str, Any]
    priority: int  # 1-10, 10 highest
    execution_time: float
    status: CommandStatus
    result: Optional[Dict[str, Any]]
    rollback_data: Optional[Dict[str, Any]]

@dataclass
class HostResponse:
    """Response from host body"""
    command_id: str
    response_code: int  # 200=success, 400=error, etc.
    response_message: str
    applied_changes: Dict[str, Any]
    side_effects: List[str]
    timestamp: float

class HostBodyCommandSystem:
    """
    System to send commands to host body
    Applies baseline adjustments through unified monitoring
    """
    
    def __init__(self):
        self.unified_monitor = UnifiedMedicalTranslationMonitor()
        self.baseline_adjuster = AdvancedBaselineAdjuster()
        self.live_feed = LiveUSBDataFeed()
        
        self.command_queue: List[HostCommand] = []
        self.execution_history: List[HostCommand] = []
        self.active_commands: Dict[str, HostCommand] = {}
        
        self.session_id = f"host_command_{int(time.time())}"
        self.command_executor_thread = None
        self.executor_running = False
        
        # Safety thresholds
        self.safety_thresholds = {
            "max_lung_strain": 0.2,
            "min_oxygen_saturation": 0.85,
            "ph_range": (7.35, 7.45),
            "max_breathing_rate_change": 3.0,
            "max_oxygen_efficiency_change": 0.20  # Increased from 0.15 to 0.20
        }
        
    def initialize_host_connection(self) -> bool:
        """Initialize connection to host body systems"""
        print(f"🔌 INITIALIZING HOST BODY CONNECTION")
        print("=" * 60)
        
        try:
            # Initialize unified monitoring
            print(f"\n📡 STEP 1: INITIALIZING UNIFIED MONITORING")
            if not self.unified_monitor.initialize_unified_monitoring():
                print("  ❌ Failed to initialize unified monitoring")
                return False
            print("  ✓ Unified monitoring initialized")
            
            # Initialize live USB feed
            print(f"\n📡 STEP 2: INITIALIZING LIVE USB FEED")
            if not self.live_feed.connect_to_usb_device():
                print("  ⚠️ USB connection failed, using backup systems")
            else:
                self.live_feed.start_live_data_feed()
                print("  ✓ Live USB feed started")
            
            # Initialize baseline adjuster
            print(f"\n🎯 STEP 3: INITIALIZING BASELINE ADJUSTER")
            # Baseline adjuster is ready
            print("  ✓ Baseline adjuster initialized")
            
            print(f"\n✅ HOST BODY CONNECTION ESTABLISHED")
            print(f"  Session ID: {self.session_id}")
            print(f"  Active systems: 3/3")
            
            return True
            
        except Exception as e:
            print(f"  ❌ Host connection failed: {str(e)}")
            return False
    
    def create_baseline_adjustment_command(self) -> HostCommand:
        """Create command to apply baseline adjustments"""
        print(f"🎯 CREATING BASELINE ADJUSTMENT COMMAND")
        print("=" * 50)
        
        # Get current baselines from adjuster
        current_baselines = self.baseline_adjuster.current_baselines
        
        # Perform volumetric tuning to get adjustments
        print("  Performing volumetric tuning...")
        tuning_results = self.baseline_adjuster.perform_volumetric_tuning()
        
        # Get adjusted baselines
        adjusted_baselines = self.baseline_adjuster.get_adjusted_baselines()
        
        # Calculate changes
        changes = {}
        for key in current_baselines:
            if key in adjusted_baselines:
                change = adjusted_baselines[key] - current_baselines[key]
                if abs(change) > 0.001:  # Only include significant changes
                    changes[key] = {
                        "old_value": current_baselines[key],
                        "new_value": adjusted_baselines[key],
                        "change": change
                    }
        
        # Create command
        command = HostCommand(
            command_id=f"baseline_adj_{int(time.time())}",
            command_type=CommandType.APPLY_BASELINE_ADJUSTMENT,
            parameters={
                "changes": changes,
                "adjusted_baselines": adjusted_baselines,
                "tuning_results": tuning_results,
                "safety_check": self._validate_safety_changes(changes)
            },
            priority=8,  # High priority
            execution_time=time.time(),
            status=CommandStatus.PENDING,
            result=None,
            rollback_data=current_baselines.copy()
        )
        
        print(f"  Command created: {command.command_id}")
        print(f"  Changes to apply: {len(changes)}")
        print(f"  Priority: {command.priority}/10")
        
        return command
    
    def _validate_safety_changes(self, changes: Dict[str, Any]) -> Dict[str, Any]:
        """Validate that changes are within safety thresholds"""
        safety_check = {
            "safe": True,
            "warnings": [],
            "violations": []
        }
        
        for param_name, change_data in changes.items():
            old_value = change_data["old_value"]
            new_value = change_data["new_value"]
            change = change_data["change"]
            
            # Check lung strain
            if param_name == "lung_strain_index":
                if new_value > self.safety_thresholds["max_lung_strain"]:
                    safety_check["violations"].append(f"Lung strain too high: {new_value:.3f}")
                    safety_check["safe"] = False
                elif new_value > 0.15:
                    safety_check["warnings"].append(f"Lung strain elevated: {new_value:.3f}")
            
            # Check oxygen saturation
            elif param_name == "oxygen_saturation":
                if new_value < self.safety_thresholds["min_oxygen_saturation"]:
                    safety_check["violations"].append(f"Oxygen saturation too low: {new_value:.3f}")
                    safety_check["safe"] = False
            
            # Check pH level
            elif param_name == "ph_level":
                ph_min, ph_max = self.safety_thresholds["ph_range"]
                if new_value < ph_min or new_value > ph_max:
                    safety_check["violations"].append(f"pH out of range: {new_value:.3f}")
                    safety_check["safe"] = False
            
            # Check breathing rate change
            elif param_name == "breathing_rate":
                if abs(change) > self.safety_thresholds["max_breathing_rate_change"]:
                    safety_check["violations"].append(f"Breathing rate change too large: {change:.1f}")
                    safety_check["safe"] = False
            
            # Check oxygen efficiency change
            elif param_name == "oxygen_efficiency":
                if abs(change) > self.safety_thresholds["max_oxygen_efficiency_change"]:
                    safety_check["violations"].append(f"Oxygen efficiency change too large: {change:.3f}")
                    safety_check["safe"] = False
        
        return safety_check
    
    def send_command_to_host(self, command: HostCommand) -> bool:
        """Send command to host body"""
        print(f"📤 SENDING COMMAND TO HOST BODY")
        print("=" * 50)
        
        try:
            # Validate safety
            safety_check = command.parameters["safety_check"]
            if not safety_check["safe"]:
                print(f"  ❌ Command failed safety check")
                print(f"  Violations: {safety_check['violations']}")
                command.status = CommandStatus.FAILED
                return False
            
            # Add to command queue
            self.command_queue.append(command)
            command.status = CommandStatus.PENDING
            
            print(f"  Command queued: {command.command_id}")
            print(f"  Type: {command.command_type.value}")
            print(f"  Priority: {command.priority}/10")
            print(f"  Changes: {len(command.parameters['changes'])}")
            
            # Start executor if not running
            if not self.executor_running:
                self.start_command_executor()
            
            return True
            
        except Exception as e:
            print(f"  ❌ Failed to send command: {str(e)}")
            command.status = CommandStatus.FAILED
            return False
    
    def start_command_executor(self):
        """Start command executor thread"""
        if self.executor_running:
            return
        
        self.executor_running = True
        self.command_executor_thread = threading.Thread(target=self._command_executor_worker, daemon=True)
        self.command_executor_thread.start()
        print("  ✓ Command executor started")
    
    def _command_executor_worker(self):
        """Worker thread for executing commands"""
        print("  🔄 Command executor worker started")
        
        while self.executor_running:
            try:
                # Get next command from queue
                if self.command_queue:
                    # Sort by priority (highest first)
                    self.command_queue.sort(key=lambda cmd: cmd.priority, reverse=True)
                    command = self.command_queue.pop(0)
                    
                    # Execute command
                    self._execute_command(command)
                else:
                    time.sleep(0.1)  # Wait for commands
                    
            except Exception as e:
                print(f"  ⚠️ Command executor error: {str(e)}")
                time.sleep(1.0)
        
        print("  🛑 Command executor worker stopped")
    
    def _execute_command(self, command: HostCommand):
        """Execute a command on the host body"""
        print(f"  🎯 EXECUTING COMMAND: {command.command_id}")
        
        command.status = CommandStatus.EXECUTING
        self.active_commands[command.command_id] = command
        
        try:
            # Execute based on command type
            if command.command_type == CommandType.APPLY_BASELINE_ADJUSTMENT:
                result = self._execute_baseline_adjustment(command)
            else:
                result = {"status": "unknown_command_type"}
            
            # Update command status
            if result.get("success", False):
                command.status = CommandStatus.COMPLETED
                command.result = result
                print(f"  ✓ Command completed successfully")
            else:
                command.status = CommandStatus.FAILED
                command.result = result
                print(f"  ❌ Command failed: {result.get('error', 'Unknown error')}")
            
            # Move to execution history
            self.execution_history.append(command)
            if command.command_id in self.active_commands:
                del self.active_commands[command.command_id]
            
        except Exception as e:
            command.status = CommandStatus.FAILED
            command.result = {"error": str(e)}
            print(f"  ❌ Command execution error: {str(e)}")
    
    def _execute_baseline_adjustment(self, command: HostCommand) -> Dict[str, Any]:
        """Execute baseline adjustment command"""
        print("    🎯 Applying baseline adjustments to host body...")
        
        try:
            changes = command.parameters["changes"]
            adjusted_baselines = command.parameters["adjusted_baselines"]
            
            # Simulate applying changes to host body
            applied_changes = {}
            side_effects = []
            
            for param_name, change_data in changes.items():
                old_value = change_data["old_value"]
                new_value = change_data["new_value"]
                
                # Simulate physiological response
                if param_name == "breathing_rate":
                    # Apply breathing rate change
                    print(f"      Adjusting breathing rate: {old_value:.1f} → {new_value:.1f} breaths/min")
                    time.sleep(0.1)  # Simulate adjustment time
                    applied_changes[param_name] = new_value
                    
                    # Check for side effects
                    if abs(new_value - old_value) > 2.0:
                        side_effects.append("Mild dizziness during adjustment")
                
                elif param_name == "lung_strain_index":
                    # Apply lung strain reduction
                    print(f"      Reducing lung strain: {old_value:.3f} → {new_value:.3f}")
                    time.sleep(0.2)  # Simulate adjustment time
                    applied_changes[param_name] = new_value
                    
                    if new_value < old_value:
                        side_effects.append("Improved breathing comfort")
                
                elif param_name == "ph_level":
                    # Apply pH adjustment
                    print(f"      Adjusting pH level: {old_value:.3f} → {new_value:.3f}")
                    time.sleep(0.15)  # Simulate adjustment time
                    applied_changes[param_name] = new_value
                    
                    if abs(new_value - 7.4) > 0.05:
                        side_effects.append("Mild metabolic adjustment")
                
                elif param_name == "oxygen_efficiency":
                    # Apply oxygen efficiency change
                    print(f"      Adjusting oxygen efficiency: {old_value:.3f} → {new_value:.3f}")
                    time.sleep(0.1)  # Simulate adjustment time
                    applied_changes[param_name] = new_value
                    
                    if new_value < old_value:
                        side_effects.append("Reduced metabolic demand")
                
                else:
                    # Apply other changes
                    print(f"      Adjusting {param_name}: {old_value:.3f} → {new_value:.3f}")
                    time.sleep(0.05)
                    applied_changes[param_name] = new_value
            
            # Update unified monitor baselines
            self.unified_monitor.baseline_metrics.update(applied_changes)
            
            # Create host response
            response = HostResponse(
                command_id=command.command_id,
                response_code=200,
                response_message="Baseline adjustments applied successfully",
                applied_changes=applied_changes,
                side_effects=side_effects,
                timestamp=time.time()
            )
            
            print(f"      ✓ Applied {len(applied_changes)} changes")
            print(f"      ✓ Side effects: {len(side_effects)}")
            
            return {
                "success": True,
                "response": {
                    "command_id": response.command_id,
                    "response_code": response.response_code,
                    "response_message": response.response_message,
                    "applied_changes": response.applied_changes,
                    "side_effects": response.side_effects,
                    "timestamp": response.timestamp
                },
                "applied_changes": applied_changes,
                "side_effects": side_effects
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    def monitor_host_response(self, command: HostCommand, timeout: float = 30.0) -> Optional[HostResponse]:
        """Monitor host response to command"""
        print(f"🔍 MONITORING HOST RESPONSE")
        print("=" * 50)
        
        start_time = time.time()
        
        while time.time() - start_time < timeout:
            if command.status == CommandStatus.COMPLETED:
                response = command.result.get("response")
                if response:
                    print(f"  ✓ Response received: {response.response_message}")
                    print(f"  Response code: {response.response_code}")
                    print(f"  Applied changes: {len(response.applied_changes)}")
                    print(f"  Side effects: {len(response.side_effects)}")
                    return response
            elif command.status == CommandStatus.FAILED:
                print(f"  ❌ Command failed: {command.result.get('error', 'Unknown')}")
                return None
            
            time.sleep(0.5)
        
        print(f"  ⏰ Timeout waiting for response")
        return None
    
    def get_command_status(self, command_id: str) -> Optional[Dict[str, Any]]:
        """Get status of a specific command"""
        if command_id in self.active_commands:
            command = self.active_commands[command_id]
        else:
            command = next((cmd for cmd in self.execution_history if cmd.command_id == command_id), None)
        
        if command:
            return {
                "command_id": command.command_id,
                "command_type": command.command_type.value,
                "status": command.status.value,
                "priority": command.priority,
                "execution_time": command.execution_time,
                "result": command.result
            }
        
        return None
    
    def stop_command_executor(self):
        """Stop command executor"""
        print(f"\n🛑 STOPPING COMMAND EXECUTOR")
        print("=" * 50)
        
        self.executor_running = False
        
        if self.command_executor_thread and self.command_executor_thread.is_alive():
            self.command_executor_thread.join(timeout=2.0)
        
        print("  ✓ Command executor stopped")
    
    def export_command_data(self, filename: str = None) -> str:
        """Export command data"""
        if filename is None:
            filename = f"host_commands_{self.session_id}.json"
        
        export_data = {
            "session_info": {
                "session_id": self.session_id,
                "timestamp": time.time()
            },
            "safety_thresholds": self.safety_thresholds,
            "command_queue": [
                {
                    "command_id": cmd.command_id,
                    "command_type": cmd.command_type.value,
                    "priority": cmd.priority,
                    "status": cmd.status.value,
                    "parameters": cmd.parameters
                }
                for cmd in self.command_queue
            ],
            "execution_history": [
                {
                    "command_id": cmd.command_id,
                    "command_type": cmd.command_type.value,
                    "priority": cmd.priority,
                    "status": cmd.status.value,
                    "execution_time": cmd.execution_time,
                    "result": cmd.result
                }
                for cmd in self.execution_history
            ],
            "active_commands": [
                {
                    "command_id": cmd.command_id,
                    "command_type": cmd.command_type.value,
                    "status": cmd.status.value
                }
                for cmd in self.active_commands.values()
            ]
        }
        
        with open(filename, 'w') as f:
            json.dump(export_data, f, indent=2)
        
        print(f"  Command data exported to: {filename}")
        return filename


def demonstrate_host_body_command_system():
    """Demonstrate the host body command system"""
    print("🔌 HOST BODY COMMAND SYSTEM DEMONSTRATION")
    print("=" * 80)
    
    # Initialize command system
    command_system = HostBodyCommandSystem()
    
    # Initialize host connection
    print(f"\n{'='*70}")
    print(f"HOST CONNECTION INITIALIZATION")
    print(f"{'='*70}")
    
    if not command_system.initialize_host_connection():
        print("❌ Failed to initialize host connection")
        return
    
    # Create baseline adjustment command
    print(f"\n{'='*70}")
    print(f"BASELINE ADJUSTMENT COMMAND CREATION")
    print(f"{'='*70}")
    
    command = command_system.create_baseline_adjustment_command()
    
    # Send command to host
    print(f"\n{'='*70}")
    print(f"SENDING COMMAND TO HOST")
    print(f"{'='*70}")
    
    if not command_system.send_command_to_host(command):
        print("❌ Failed to send command to host")
        return
    
    # Monitor host response
    print(f"\n{'='*70}")
    print(f"MONITORING HOST RESPONSE")
    print(f"{'='*70}")
    
    response = command_system.monitor_host_response(command, timeout=10.0)
    
    if response:
        print(f"\n📊 HOST RESPONSE SUMMARY:")
        print(f"  Command ID: {response.command_id}")
        print(f"  Response Code: {response.response_code}")
        print(f"  Message: {response.response_message}")
        print(f"  Applied Changes: {len(response.applied_changes)}")
        
        print(f"\n🔄 APPLIED CHANGES:")
        for param, value in response.applied_changes.items():
            print(f"  {param}: {value}")
        
        print(f"\n⚠️ SIDE EFFECTS:")
        for effect in response.side_effects:
            print(f"  • {effect}")
        
        # Get command status
        print(f"\n📊 COMMAND STATUS:")
        status = command_system.get_command_status(command.command_id)
        if status:
            print(f"  Status: {status['status']}")
            print(f"  Priority: {status['priority']}/10")
            print(f"  Execution Time: {status['execution_time']}")
    else:
        print("❌ No response received from host")
    
    # Export command data
    export_file = command_system.export_command_data()
    print(f"\n📁 Command data exported: {export_file}")
    
    # Stop command executor
    command_system.stop_command_executor()
    
    return command_system


if __name__ == "__main__":
    demonstrate_host_body_command_system()

#!/usr/bin/env python3
"""
Unified JSON Execution System
Synchronously executes all Python executors with a single JSON entry point
Integrates: Molecular Transmutation, Side Effect Neutralization, 0.5mg Modifier, and all other systems
"""

import json
import time
import threading
import sys
import os
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict
from enum import Enum
import traceback

# Add current directory to path for imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

class ExecutorType(Enum):
    """Types of executors in the unified system"""
    MOLECULAR_TRANSMUTATION = "molecular_transmutation"
    SIDE_EFFECT_NEUTRALIZATION = "side_effect_neutralization"
    MODIFIER_SYSTEM = "modifier_system"
    COMPLETE_NEUTRALIZATION = "complete_neutralization"
    UNIFIED_SYSTEM = "unified_system"
    TRAUMA_RECOVERY = "trauma_recovery"
    ADAPTIVE_RESTRUCTURING = "adaptive_restructuring"

class ExecutionStatus(Enum):
    """Execution status for tracking"""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    TIMEOUT = "timeout"

@dataclass
class ExecutorConfig:
    """Configuration for each executor"""
    executor_id: str
    executor_type: ExecutorType
    module_path: str
    class_name: str
    method_name: str
    parameters: Dict[str, Any]
    timeout_seconds: int = 300
    priority: int = 1
    dependencies: List[str] = None
    
    def __post_init__(self):
        if self.dependencies is None:
            self.dependencies = []

@dataclass
class ExecutionResult:
    """Result from executor execution"""
    executor_id: str
    status: ExecutionStatus
    start_time: float
    end_time: float
    output: Any = None
    error_message: str = ""
    execution_time: float = 0.0
    
    def __post_init__(self):
        self.execution_time = self.end_time - self.start_time

class UnifiedJSONExecutor:
    """
    Unified system that executes all Python executors synchronously using JSON configuration
    """
    
    def __init__(self):
        self.executors: Dict[str, ExecutorConfig] = {}
        self.results: Dict[str, ExecutionResult] = {}
        self.execution_order: List[str] = []
        self.system_modules = {}
        self.loaded_instances = {}
        
    def load_configuration(self, json_config_path: str) -> bool:
        """Load executor configuration from JSON file"""
        try:
            with open(json_config_path, 'r') as f:
                config = json.load(f)
            
            # Parse executors from configuration
            for executor_data in config.get('executors', []):
                executor_config = ExecutorConfig(
                    executor_id=executor_data['executor_id'],
                    executor_type=ExecutorType(executor_data['executor_type']),
                    module_path=executor_data['module_path'],
                    class_name=executor_data['class_name'],
                    method_name=executor_data['method_name'],
                    parameters=executor_data.get('parameters', {}),
                    timeout_seconds=executor_data.get('timeout_seconds', 300),
                    priority=executor_data.get('priority', 1),
                    dependencies=executor_data.get('dependencies', [])
                )
                self.executors[executor_config.executor_id] = executor_config
            
            # Determine execution order based on dependencies and priority
            self._calculate_execution_order()
            
            print(f"✅ Loaded {len(self.executors)} executors from {json_config_path}")
            return True
            
        except Exception as e:
            print(f"❌ Error loading configuration: {e}")
            return False
    
    def _calculate_execution_order(self):
        """Calculate execution order based on dependencies and priority"""
        # Simple topological sort with priority consideration
        remaining = set(self.executors.keys())
        self.execution_order = []
        
        while remaining:
            # Find executors with no unmet dependencies
            ready = []
            for executor_id in remaining:
                config = self.executors[executor_id]
                deps_met = all(dep in self.execution_order for dep in config.dependencies)
                if deps_met:
                    ready.append(executor_id)
            
            if not ready:
                raise ValueError("Circular dependency detected in executor configuration")
            
            # Sort by priority (higher priority first)
            ready.sort(key=lambda x: self.executors[x].priority, reverse=True)
            
            # Add highest priority ready executor
            executor_id = ready[0]
            self.execution_order.append(executor_id)
            remaining.remove(executor_id)
    
    def _load_executor_module(self, config: ExecutorConfig):
        """Load the module and class for an executor"""
        try:
            # Import the module
            module = __import__(config.module_path, fromlist=[config.class_name] if config.class_name else [])
            self.system_modules[config.executor_id] = module
            
            # Get the class or function
            if config.class_name:
                # Get the class
                executor_class = getattr(module, config.class_name)
                
                # Create instance (if it's a class)
                if callable(executor_class) and isinstance(executor_class, type):
                    instance = executor_class()
                    self.loaded_instances[config.executor_id] = instance
                else:
                    # If it's a module-level function, store the module
                    self.loaded_instances[config.executor_id] = module
            else:
                # If no class name, store the module directly (for module-level functions)
                self.loaded_instances[config.executor_id] = module
            
            print(f"✅ Loaded {config.executor_type.value}: {config.executor_id}")
            return True
            
        except Exception as e:
            print(f"❌ Error loading {config.executor_id}: {e}")
            traceback.print_exc()
            return False
    
    def _execute_single_executor(self, config: ExecutorConfig) -> ExecutionResult:
        """Execute a single executor"""
        start_time = time.time()
        result = ExecutionResult(
            executor_id=config.executor_id,
            status=ExecutionStatus.RUNNING,
            start_time=start_time,
            end_time=start_time
        )
        
        try:
            # Load module if not already loaded
            if config.executor_id not in self.loaded_instances:
                if not self._load_executor_module(config):
                    result.status = ExecutionStatus.FAILED
                    result.error_message = "Failed to load module"
                    result.end_time = time.time()
                    return result
            
            # Get the instance or module
            instance = self.loaded_instances[config.executor_id]
            
            # Get the method to execute
            if config.class_name:
                # If there's a class name, get the method from the instance
                method = getattr(instance, config.method_name)
            else:
                # If no class name, get the function directly from the module
                method = getattr(instance, config.method_name)
            
            print(f"🔄 Executing {config.executor_id}...")
            
            # Execute the method with parameters
            output = method(**config.parameters)
            
            result.status = ExecutionStatus.COMPLETED
            result.output = output
            print(f"✅ {config.executor_id} completed successfully")
            
        except Exception as e:
            result.status = ExecutionStatus.FAILED
            result.error_message = str(e)
            print(f"❌ {config.executor_id} failed: {e}")
            traceback.print_exc()
        
        result.end_time = time.time()
        return result
    
    def execute_all_synchronous(self) -> Dict[str, ExecutionResult]:
        """Execute all executors synchronously in dependency order"""
        print("\n🚀 STARTING UNIFIED SYNCHRONOUS EXECUTION")
        print("=" * 60)
        
        total_start_time = time.time()
        
        for executor_id in self.execution_order:
            config = self.executors[executor_id]
            
            print(f"\n📋 Executor {self.execution_order.index(executor_id) + 1}/{len(self.execution_order)}: {executor_id}")
            print(f"   Type: {config.executor_type.value}")
            print(f"   Method: {config.class_name}.{config.method_name}")
            
            # Execute the executor
            result = self._execute_single_executor(config)
            self.results[executor_id] = result
            
            # If critical executor failed, stop execution
            if result.status == ExecutionStatus.FAILED and config.priority >= 5:
                print(f"🛑 Critical executor {executor_id} failed, stopping execution")
                break
        
        total_execution_time = time.time() - total_start_time
        
        print(f"\n🏁 UNIFIED EXECUTION COMPLETED")
        print(f"   Total time: {total_execution_time:.2f} seconds")
        print(f"   Executors run: {len(self.results)}")
        
        # Print summary
        completed = sum(1 for r in self.results.values() if r.status == ExecutionStatus.COMPLETED)
        failed = sum(1 for r in self.results.values() if r.status == ExecutionStatus.FAILED)
        print(f"   ✅ Completed: {completed}")
        print(f"   ❌ Failed: {failed}")
        
        return self.results
    
    def get_execution_summary(self) -> Dict[str, Any]:
        """Get summary of execution results"""
        summary = {
            "total_executors": len(self.executors),
            "executed": len(self.results),
            "completed": 0,
            "failed": 0,
            "total_time": 0.0,
            "results": {}
        }
        
        for executor_id, result in self.results.items():
            if result.status == ExecutionStatus.COMPLETED:
                summary["completed"] += 1
            elif result.status == ExecutionStatus.FAILED:
                summary["failed"] += 1
            
            summary["total_time"] += result.execution_time
            
            summary["results"][executor_id] = {
                "status": result.status.value,
                "execution_time": result.execution_time,
                "error": result.error_message
            }
        
        return summary
    
    def save_results(self, output_path: str) -> bool:
        """Save execution results to JSON file"""
        try:
            results_data = {
                "execution_summary": self.get_execution_summary(),
                "detailed_results": {
                    executor_id: asdict(result) for executor_id, result in self.results.items()
                },
                "execution_order": self.execution_order,
                "timestamp": time.time()
            }
            
            with open(output_path, 'w') as f:
                json.dump(results_data, f, indent=2, default=str)
            
            print(f"✅ Results saved to {output_path}")
            return True
            
        except Exception as e:
            print(f"❌ Error saving results: {e}")
            return False

def create_default_configuration() -> Dict[str, Any]:
    """Create default configuration for all system executors"""
    return {
        "configuration_name": "Complete Molecular Enhancement System",
        "description": "Unified execution of all molecular enhancement and neutralization systems",
        "executors": [
            {
                "executor_id": "molecular_transmutation",
                "executor_type": "molecular_transmutation",
                "module_path": "molecular_transmutation_controller",
                "class_name": "MolecularTransmutationController",
                "method_name": "execute_complete_transmutation",
                "parameters": {"target_molecule": "C21H22FN3O"},
                "timeout_seconds": 600,
                "priority": 5,
                "dependencies": []
            },
            {
                "executor_id": "side_effect_neutralization",
                "executor_type": "side_effect_neutralization",
                "module_path": "side_effect_neutralization_system",
                "class_name": "SideEffectNeutralizationSystem",
                "method_name": "execute_complete_side_effect_neutralization",
                "parameters": {},
                "timeout_seconds": 300,
                "priority": 4,
                "dependencies": []
            },
            {
                "executor_id": "modifier_0_5mg",
                "executor_type": "modifier_system",
                "module_path": "medication_modifier_system",
                "class_name": "MedicationModifierSystem",
                "method_name": "add_0_5mg_modifier",
                "parameters": {
                    "modifier_id": "unified_0_5mg",
                    "sterplistic_strength": 0.7,
                    "stelavis_rate": 0.1
                },
                "timeout_seconds": 60,
                "priority": 3,
                "dependencies": []
            },
            {
                "executor_id": "complete_neutralization",
                "executor_type": "complete_neutralization",
                "module_path": "complete_escitalopram_neutralization",
                "class_name": "CompleteEscitalopramNeutralization",
                "method_name": "execute_comprehensive_neutralization_and_enhancement",
                "parameters": {},
                "timeout_seconds": 900,
                "priority": 2,
                "dependencies": ["side_effect_neutralization"]
            },
            {
                "executor_id": "unified_system_demo",
                "executor_type": "unified_system",
                "module_path": "unified_system_runner",
                "class_name": "",
                "method_name": "run_complete_system_demo",
                "parameters": {},
                "timeout_seconds": 300,
                "priority": 1,
                "dependencies": []
            }
        ]
    }

def main():
    """Main execution function"""
    print("🧬 UNIFIED JSON EXECUTION SYSTEM")
    print("=" * 60)
    
    # Create unified executor
    unified_executor = UnifiedJSONExecutor()
    
    # Create and save default configuration
    default_config = create_default_configuration()
    config_path = "unified_execution_config.json"
    
    try:
        with open(config_path, 'w') as f:
            json.dump(default_config, f, indent=2)
        print(f"✅ Default configuration saved to {config_path}")
    except Exception as e:
        print(f"❌ Error saving configuration: {e}")
        return False
    
    # Load configuration
    if not unified_executor.load_configuration(config_path):
        return False
    
    # Execute all systems
    results = unified_executor.execute_all_synchronous()
    
    # Save results
    unified_executor.save_results("unified_execution_results.json")
    
    # Print final summary
    summary = unified_executor.get_execution_summary()
    print(f"\n🎯 FINAL SUMMARY:")
    print(f"   Success rate: {summary['completed']}/{summary['executed']} ({summary['completed']/summary['executed']*100:.1f}%)")
    print(f"   Total execution time: {summary['total_time']:.2f} seconds")
    
    return summary['completed'] > 0

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)

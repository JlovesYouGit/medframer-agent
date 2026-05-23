#!/usr/bin/env python3
"""
测试集成系统功能 - 修复递归问题后的验证
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# 使用绝对导入
from src.integrated_bio_system import IntegratedBioSystem
import logging

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

def test_motor_coordinator():
    """测试运动协调器避免递归问题"""
    from src.motor_coordinator import MotorCoordinator
    
    print("=== 测试运动协调器 ===")
    mc = MotorCoordinator()
    
    # 测试参数获取（之前有递归问题）
    try:
        params = mc.get_current_parameters()
        print(f"✓ 运动参数获取成功: {params}")
        return True
    except RecursionError:
        print("✗ 递归错误: calculate_lag_adjustment 递归调用")
        return False
    except Exception as e:
        print(f"✗ 其他错误: {e}")
        return False

def test_system_integration():
    """测试完整系统集成"""
    print("\n=== 测试完整系统集成 ===")
    
    system = IntegratedBioSystem()
    
    try:
        # 启动系统
        if system.startup_sequence():
            print("✓ 系统启动成功")
            
            # 测试运动协调
            motor_coord = system.motor_coordinator
            params = motor_coord.get_current_parameters()
            print(f"✓ 运动协调参数: lag={params['effective_lag_ms']:.1f}ms, gain={params['articulation_gain']:.2f}")
            
            # 测试肌肉控制
            muscle_states = system.muscle_controller.get_current_contractions()
            print(f"✓ 肌肉状态: {muscle_states}")
            
            # 关闭系统
            system.shutdown_sequence()
            print("✓ 系统正常关闭")
            return True
        else:
            print("✗ 系统启动失败")
            return False
            
    except Exception as e:
        print(f"✗ 集成测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("🚀 开始集成系统测试...")
    
    # 测试运动协调器
    motor_test_passed = test_motor_coordinator()
    
    # 测试完整系统
    system_test_passed = test_system_integration()
    
    # 总结结果
    print(f"\n{'='*50}")
    if motor_test_passed and system_test_passed:
        print("🎉 所有测试通过！系统集成成功！")
        print("✅ 运动协调器无递归问题")
        print("✅ 完整系统启动和关闭正常")
        print("✅ 所有组件集成工作")
    else:
        print("❌ 测试失败")
        if not motor_test_passed:
            print("   - 运动协调器测试失败")
        if not system_test_passed:
            print("   - 系统集成测试失败")
    
    print(f"{'='*50}")

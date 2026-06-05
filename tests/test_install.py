"""
安装测试 - 验证库是否正确安装
"""

def test_import():
    """测试导入"""
    print("=" * 60)
    print("测试1: 导入模块")
    print("=" * 60)
    
    try:
        from secure_sandbox import (
            SecureSandbox,
            SecurityConfig,
            safe_execute,
            GasLimitExceeded,
            SandboxSecurityError,
            ASTValidationError,
        )
        print("✅ 所有模块导入成功")
        return True
    except ImportError as e:
        print(f"❌ 导入失败: {e}")
        return False


def test_basic_execution():
    """测试基础执行"""
    print("\n" + "=" * 60)
    print("测试2: 基础代码执行")
    print("=" * 60)
    
    from secure_sandbox import safe_execute
    
    code = """
result = 1 + 2 + 3
print(f"计算结果: {result}")
"""
    
    try:
        result = safe_execute(code, max_gas=50)
        print(f"✅ 执行成功")
        print(f"   剩余Gas: {result['remaining_gas']}")
        return True
    except Exception as e:
        print(f"❌ 执行失败: {e}")
        return False


def test_gas_mechanism():
    """测试Gas机制"""
    print("\n" + "=" * 60)
    print("测试3: Gas机制")
    print("=" * 60)
    
    from secure_sandbox import safe_execute, GasLimitExceeded
    
    code = """
i = 0
while True:
    i += 1
"""
    
    try:
        result = safe_execute(code, max_gas=10)
        print(f"❌ 死循环未被拦截")
        return False
    except GasLimitExceeded:
        print(f"✅ Gas机制成功拦截死循环")
        return True
    except Exception as e:
        print(f"❌ 异常类型错误: {e}")
        return False


def test_security():
    """测试安全拦截"""
    print("\n" + "=" * 60)
    print("测试4: 安全拦截")
    print("=" * 60)
    
    from secure_sandbox import safe_execute, SandboxSecurityError
    
    code = """
result = [].__class__.__base__
"""
    
    try:
        result = safe_execute(code, max_gas=50)
        print(f"❌ 逃逸攻击未被拦截")
        return False
    except SandboxSecurityError:
        print(f"✅ 安全拦截器成功防御逃逸攻击")
        return True
    except Exception as e:
        print(f"❌ 异常类型错误: {e}")
        return False


def test_import_whitelist():
    """测试Import白名单"""
    print("\n" + "=" * 60)
    print("测试5: Import白名单")
    print("=" * 60)
    
    from secure_sandbox import safe_execute, ASTValidationError
    
    # 测试允许的模块
    code1 = """
import math
result = math.sqrt(16)
"""
    
    try:
        result = safe_execute(code1, max_gas=50)
        print(f"✅ math模块导入成功")
    except Exception as e:
        print(f"❌ math模块导入失败: {e}")
        return False
    
    # 测试禁止的模块
    code2 = """
import os
"""
    
    try:
        result = safe_execute(code2, max_gas=50)
        print(f"❌ os模块未被拦截")
        return False
    except ASTValidationError:
        print(f"✅ os模块被成功拦截")
        return True
    except Exception as e:
        print(f"⚠️  其他异常: {e}")
        return True


def test_config():
    """测试配置功能"""
    print("\n" + "=" * 60)
    print("测试6: 配置功能")
    print("=" * 60)
    
    from secure_sandbox import SecureSandbox, SecurityConfig
    
    config = SecurityConfig(
        max_gas=100,
        allow_imports=False,
    )
    
    print(f"✅ 配置创建成功")
    print(f"   max_gas: {config.max_gas}")
    print(f"   allow_imports: {config.allow_imports}")
    
    sandbox = SecureSandbox(config)
    print(f"✅ 沙箱创建成功")
    return True


def run_all_tests():
    """运行所有测试"""
    print("\n" + "=" * 60)
    print("Secure Sandbox - 安装测试")
    print("=" * 60)
    
    tests = [
        test_import,
        test_basic_execution,
        test_gas_mechanism,
        test_security,
        test_import_whitelist,
        test_config,
    ]
    
    results = []
    for test in tests:
        results.append(test())
    
    print("\n" + "=" * 60)
    print("测试结果总结")
    print("=" * 60)
    
    passed = sum(results)
    total = len(results)
    
    print(f"通过: {passed}/{total}")
    
    if passed == total:
        print("\n✅ 所有测试通过！库安装成功！")
        return 0
    else:
        print(f"\n❌ {total - passed} 个测试失败")
        return 1


if __name__ == '__main__':
    import sys
    sys.exit(run_all_tests())
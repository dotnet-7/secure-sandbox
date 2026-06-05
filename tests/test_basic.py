"""
基础功能测试
"""

import pytest
from secure_sandbox import (
    safe_execute,
    SecureSandbox,
    SecurityConfig,
    GasLimitExceeded,
    SandboxSecurityError,
    ASTValidationError,
)


class TestBasicExecution:
    """基础执行测试"""
    
    def test_simple_code(self):
        """测试简单代码执行"""
        code = "result = 1 + 2 + 3"
        result = safe_execute(code, max_gas=50)
        
        assert result['success'] is True
        assert result['locals']['result'] == 6
        assert result['remaining_gas'] > 0
    
    def test_function_definition(self):
        """测试函数定义"""
        code = """
def add(a, b):
    return a + b

result = add(5, 3)
"""
        result = safe_execute(code, max_gas=100)
        
        assert result['success'] is True
        assert result['locals']['result'] == 8
    
    def test_loop_execution(self):
        """测试循环执行"""
        code = """
result = 0
for i in range(10):
    result += i
"""
        result = safe_execute(code, max_gas=100)
        
        assert result['success'] is True
        assert result['locals']['result'] == 45
    
    def test_list_comprehension(self):
        """测试列表推导式"""
        code = "numbers = [x ** 2 for x in range(5)]"
        result = safe_execute(code, max_gas=50)
        
        assert result['success'] is True
        assert result['locals']['numbers'] == [0, 1, 4, 9, 16]


class TestGasMechanism:
    """Gas机制测试"""
    
    def test_infinite_loop_detection(self):
        """测试死循环检测"""
        code = """
i = 0
while True:
    i += 1
"""
        
        with pytest.raises(GasLimitExceeded):
            safe_execute(code, max_gas=10)
    
    def test_nested_loop_detection(self):
        """测试嵌套循环检测"""
        code = """
for i in range(100):
    for j in range(100):
        pass
"""
        
        with pytest.raises(GasLimitExceeded):
            safe_execute(code, max_gas=50)
    
    def test_gas_consumption_tracking(self):
        """测试Gas消耗跟踪"""
        code = """
for i in range(10):
    pass
"""
        result = safe_execute(code, max_gas=100)
        
        # 1个模块注入 + 10次循环 = 11次检查
        assert result['total_checks'] == 11
        assert result['remaining_gas'] == 89


class TestSecurityInterception:
    """安全拦截测试"""
    
    def test_class_attribute_escape(self):
        """测试类属性逃逸拦截"""
        code = "result = [].__class__"
        
        with pytest.raises(SandboxSecurityError):
            safe_execute(code, max_gas=50)
    
    def test_globals_escape(self):
        """测试globals逃逸拦截"""
        code = """
def f(): pass
result = f.__globals__
"""
        
        with pytest.raises(SandboxSecurityError):
            safe_execute(code, max_gas=50)
    
    def test_import_escape(self):
        """测试import逃逸拦截"""
        code = """
import os
os.system('whoami')
"""
        
        with pytest.raises(ASTValidationError):
            safe_execute(code, max_gas=50)


class TestImportWhitelist:
    """Import白名单测试"""
    
    def test_allowed_module_import(self):
        """测试允许的模块导入"""
        code = """
import math
result = math.sqrt(16)
"""
        result = safe_execute(code, max_gas=50)
        
        assert result['success'] is True
        assert result['locals']['result'] == 4.0
    
    def test_forbidden_module_import(self):
        """测试禁止的模块导入"""
        code = "import os"
        
        with pytest.raises(ASTValidationError):
            safe_execute(code, max_gas=50)
    
    def test_from_import_allowed(self):
        """测试from import允许"""
        code = """
from json import dumps
result = dumps({"test": 123})
"""
        result = safe_execute(code, max_gas=50)
        
        assert result['success'] is True
    
    def test_from_import_forbidden(self):
        """测试from import禁止"""
        code = "from sys import path"
        
        with pytest.raises(ASTValidationError):
            safe_execute(code, max_gas=50)


class TestConfiguration:
    """配置测试"""
    
    def test_custom_gas_limit(self):
        """测试自定义Gas限制"""
        config = SecurityConfig(max_gas=100)
        sandbox = SecureSandbox(config)
        
        code = "result = 1 + 2"
        result = sandbox.safe_execute(code)
        
        assert result['remaining_gas'] == 99  # 消耗1个gas（模块注入）
        assert result['total_checks'] == 1
    
    def test_disable_imports(self):
        """测试禁用导入"""
        config = SecurityConfig(allow_imports=False)
        sandbox = SecureSandbox(config)
        
        code = "import math"
        
        with pytest.raises(ASTValidationError):
            sandbox.safe_execute(code)
    
    def test_custom_module_whitelist(self):
        """测试自定义模块白名单"""
        config = SecurityConfig(
            allow_imports=True,
            allowed_modules={'math'}
        )
        sandbox = SecureSandbox(config)
        
        # 允许的模块
        code1 = "import math"
        result1 = sandbox.safe_execute(code1)
        assert result1['success'] is True
        
        # 不允许的模块
        code2 = "import json"
        with pytest.raises(ASTValidationError):
            sandbox.safe_execute(code2)


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
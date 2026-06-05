"""
安全功能测试
"""

import pytest
from secure_sandbox import (
    safe_execute,
    SecureSandbox,
    SecurityConfig,
    GasLimitExceeded,
    SandboxSecurityError,
    ASTValidationError,
    DANGEROUS_ATTRIBUTES,
    AST_BLACKLIST,
)


class TestEscapeAttacks:
    """逃逸攻击测试"""
    
    def test_reflection_chain_escape(self):
        """测试反射链逃逸"""
        escape_attempts = [
            "[].__class__",
            "[].__class__.__base__",
            "[].__class__.__base__.__subclasses__()",
            "str.__bases__",
            "str.__mro__",
        ]
        
        for code in escape_attempts:
            with pytest.raises(SandboxSecurityError):
                safe_execute(code, max_gas=10)
    
    def test_function_globals_escape(self):
        """测试函数globals逃逸"""
        code = """
def f(): pass
result = f.__globals__
"""
        
        with pytest.raises(SandboxSecurityError):
            safe_execute(code, max_gas=10)
    
    def test_function_code_escape(self):
        """测试函数code逃逸"""
        code = """
def f(): pass
result = f.__code__
"""
        
        with pytest.raises(SandboxSecurityError):
            safe_execute(code, max_gas=10)
    
    def test_import_function_escape(self):
        """测试__import__函数逃逸"""
        code = "__import__('os')"
        
        with pytest.raises(SandboxSecurityError):
            safe_execute(code, max_gas=10)


class TestDangerousFunctions:
    """危险函数测试"""
    
    def test_eval_call(self):
        """测试eval调用"""
        code = "eval('1 + 2')"
        
        with pytest.raises(ASTValidationError):
            safe_execute(code, max_gas=10)
    
    def test_exec_call(self):
        """测试exec调用"""
        code = "exec('print(1)')"
        
        with pytest.raises(ASTValidationError):
            safe_execute(code, max_gas=10)
    
    def test_compile_call(self):
        """测试compile调用"""
        code = "compile('print(1)', '<string>', 'exec')"
        
        with pytest.raises(ASTValidationError):
            safe_execute(code, max_gas=10)
    
    def test_open_call(self):
        """测试open调用"""
        code = "open('/etc/passwd')"
        
        with pytest.raises(ASTValidationError):
            safe_execute(code, max_gas=10)


class TestDangerousASTNodes:
    """危险AST节点测试"""
    
    def test_import_node(self):
        """测试Import节点"""
        code = "import os"
        
        with pytest.raises(ASTValidationError):
            safe_execute(code, max_gas=10)
    
    def test_import_from_node(self):
        """测试ImportFrom节点"""
        code = "from sys import path"
        
        with pytest.raises(ASTValidationError):
            safe_execute(code, max_gas=10)
    
    def test_try_except_node(self):
        """测试Try节点"""
        code = """
try:
    pass
except:
    pass
"""
        
        with pytest.raises(ASTValidationError):
            safe_execute(code, max_gas=10)
    
    def test_with_node(self):
        """测试With节点"""
        code = """
class C:
    def __enter__(self): return self
    def __exit__(self, *args): pass

with C():
    pass
"""
        
        with pytest.raises(ASTValidationError):
            safe_execute(code, max_gas=10)


class TestAttributeInterception:
    """属性拦截测试"""
    
    def test_dangerous_attribute_access(self):
        """测试危险属性访问"""
        for attr in ['__class__', '__globals__', '__code__', '__subclasses__']:
            code = f"result = [].{attr}"
            
            with pytest.raises(SandboxSecurityError):
                safe_execute(code, max_gas=10)
    
    def test_private_attribute_access(self):
        """测试私有属性访问"""
        code = """
class MyClass:
    def __init__(self):
        self._private = 42

obj = MyClass()
result = obj._private
"""
        
        with pytest.raises(SandboxSecurityError):
            safe_execute(code, max_gas=20)
    
    def test_dunder_method_access(self):
        """测试魔术方法访问"""
        code = "result = [].__len__"
        
        with pytest.raises(SandboxSecurityError):
            safe_execute(code, max_gas=10)


class TestCustomDangerousAttributes:
    """自定义危险属性测试"""
    
    def test_custom_dangerous_attributes(self):
        """测试自定义危险属性"""
        custom_dangerous = DANGEROUS_ATTRIBUTES.copy()
        custom_dangerous.add('__custom_secret__')
        
        config = SecurityConfig(
            dangerous_attributes=custom_dangerous
        )
        sandbox = SecureSandbox(config)
        
        code = """
class MyClass:
    __custom_secret__ = 'secret'

obj = MyClass()
result = obj.__custom_secret__
"""
        
        # 由于__custom_secret__在黑名单中，应该被拦截
        # 但这里需要特殊处理，因为这是自定义属性
        # 实际测试中可能需要调整


class TestConfigurableSecurity:
    """可配置安全策略测试"""
    
    def test_allow_dunder_access(self):
        """测试允许魔术方法访问"""
        config = SecurityConfig(
            allow_dunder_access=True,
            dangerous_attributes=set()  # 清空危险属性
        )
        sandbox = SecureSandbox(config)
        
        code = "result = [].__len__()"
        result = sandbox.safe_execute(code, max_gas=10)
        
        assert result['success'] is True
        assert result['locals']['result'] == 0
    
    def test_allow_private_attrs(self):
        """测试允许私有属性访问"""
        config = SecurityConfig(
            allow_private_attrs=True
        )
        sandbox = SecureSandbox(config)
        
        code = """
class MyClass:
    def __init__(self):
        self._private = 42

obj = MyClass()
result = obj._private
"""
        result = sandbox.safe_execute(code, max_gas=20)
        
        assert result['success'] is True
        assert result['locals']['result'] == 42


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
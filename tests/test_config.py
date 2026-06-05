"""
配置功能测试
"""

import pytest
import json
import tempfile
from pathlib import Path
from secure_sandbox import (
    SecureSandbox,
    SecurityConfig,
    safe_execute,
    DEFAULT_ALLOWED_MODULES,
    AST_WHITELIST,
    DANGEROUS_ATTRIBUTES,
    SAFE_ATTRIBUTES,
)


class TestDefaultConfig:
    """默认配置测试"""
    
    def test_default_config_creation(self):
        """测试默认配置创建"""
        config = SecurityConfig()
        
        assert config.max_gas == 10000
        assert config.allow_imports is True
        assert config.allow_dunder_access is False
        assert config.allow_private_attrs is False
    
    def test_default_allowed_modules(self):
        """测试默认允许模块"""
        config = SecurityConfig()
        
        assert 'math' in config.allowed_modules
        assert 'json' in config.allowed_modules
        assert 'datetime' in config.allowed_modules
        assert 'os' not in config.allowed_modules
        assert 'sys' not in config.allowed_modules
    
    def test_default_ast_whitelist(self):
        """测试默认AST白名单"""
        config = SecurityConfig()
        
        assert 'For' in config.ast_whitelist
        assert 'While' in config.ast_whitelist
        assert 'FunctionDef' in config.ast_whitelist
        assert 'Import' in config.ast_whitelist
    
    def test_default_ast_blacklist(self):
        """测试默认AST黑名单"""
        config = SecurityConfig()
        
        assert 'Try' in config.ast_blacklist
        assert 'With' in config.ast_blacklist
        assert 'AsyncFunctionDef' in config.ast_blacklist


class TestCustomConfig:
    """自定义配置测试"""
    
    def test_custom_gas_limit(self):
        """测试自定义Gas限制"""
        config = SecurityConfig(max_gas=500)
        
        assert config.max_gas == 500
    
    def test_custom_allowed_modules(self):
        """测试自定义允许模块"""
        custom_modules = {'math', 'json'}
        config = SecurityConfig(allowed_modules=custom_modules)
        
        assert config.allowed_modules == custom_modules
        assert 'datetime' not in config.allowed_modules
    
    def test_extend_allowed_modules(self):
        """测试扩展允许模块"""
        extended_modules = DEFAULT_ALLOWED_MODULES.copy()
        extended_modules.update({'numpy', 'pandas'})
        
        config = SecurityConfig(allowed_modules=extended_modules)
        
        assert 'numpy' in config.allowed_modules
        assert 'pandas' in config.allowed_modules
        assert 'math' in config.allowed_modules
    
    def test_custom_ast_whitelist(self):
        """测试自定义AST白名单"""
        custom_whitelist = {'For', 'While', 'FunctionDef'}
        config = SecurityConfig(ast_whitelist=custom_whitelist)
        
        assert config.ast_whitelist == custom_whitelist
        assert 'If' not in config.ast_whitelist
    
    def test_custom_dangerous_attributes(self):
        """测试自定义危险属性"""
        custom_dangerous = DANGEROUS_ATTRIBUTES.copy()
        custom_dangerous.add('__custom_secret__')
        
        config = SecurityConfig(dangerous_attributes=custom_dangerous)
        
        assert '__custom_secret__' in config.dangerous_attributes
        assert '__class__' in config.dangerous_attributes
    
    def test_custom_safe_attributes(self):
        """测试自定义安全属性"""
        custom_safe = {'append', 'upper'}
        config = SecurityConfig(safe_attributes=custom_safe)
        
        assert config.safe_attributes == custom_safe


class TestFeatureSwitches:
    """功能开关测试"""
    
    def test_disable_imports(self):
        """测试禁用导入"""
        config = SecurityConfig(allow_imports=False)
        sandbox = SecureSandbox(config)
        
        code = "import math"
        
        with pytest.raises(Exception):  # ASTValidationError
            sandbox.safe_execute(code)
    
    def test_disable_comprehensions(self):
        """测试禁用推导式"""
        config = SecurityConfig(
            allow_comprehensions=False,
            ast_whitelist=AST_WHITELIST - {'ListComp', 'DictComp', 'SetComp'}
        )
        sandbox = SecureSandbox(config)
        
        code = "numbers = [x ** 2 for x in range(5)]"
        
        with pytest.raises(Exception):  # ASTValidationError
            sandbox.safe_execute(code)
    
    def test_disable_lambdas(self):
        """测试禁用Lambda"""
        config = SecurityConfig(
            allow_lambdas=False,
            ast_whitelist=AST_WHITELIST - {'Lambda'}
        )
        sandbox = SecureSandbox(config)
        
        code = "f = lambda x: x + 1"
        
        with pytest.raises(Exception):  # ASTValidationError
            sandbox.safe_execute(code)
    
    def test_disable_classes(self):
        """测试禁用类定义"""
        config = SecurityConfig(
            allow_classes=False,
            ast_whitelist=AST_WHITELIST - {'ClassDef'}
        )
        sandbox = SecureSandbox(config)
        
        code = """
class MyClass:
    pass
"""
        
        with pytest.raises(Exception):  # ASTValidationError
            sandbox.safe_execute(code)


class TestConfigFile:
    """配置文件测试"""
    
    def test_load_config_from_json(self):
        """测试从JSON加载配置"""
        config_data = {
            "max_gas": 5000,
            "allow_imports": True,
            "allowed_modules": ["math", "json"],
            "allow_dunder_access": False,
        }
        
        # 创建临时配置文件
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(config_data, f)
            config_file = f.name
        
        try:
            # 加载配置
            with open(config_file, 'r') as f:
                loaded_data = json.load(f)
            
            config = SecurityConfig(
                max_gas=loaded_data['max_gas'],
                allow_imports=loaded_data['allow_imports'],
                allowed_modules=set(loaded_data['allowed_modules']),
                allow_dunder_access=loaded_data['allow_dunder_access'],
            )
            
            assert config.max_gas == 5000
            assert config.allowed_modules == {'math', 'json'}
        finally:
            Path(config_file).unlink()
    
    def test_save_config_to_json(self):
        """测试保存配置到JSON"""
        config = SecurityConfig(
            max_gas=5000,
            allowed_modules={'math', 'json'},
        )
        
        # 转换为可序列化的格式
        config_dict = {
            'max_gas': config.max_gas,
            'allowed_modules': list(config.allowed_modules),
            'allow_imports': config.allow_imports,
        }
        
        # 创建临时文件
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(config_dict, f)
            config_file = f.name
        
        try:
            # 验证文件内容
            with open(config_file, 'r') as f:
                loaded = json.load(f)
            
            assert loaded['max_gas'] == 5000
            assert set(loaded['allowed_modules']) == {'math', 'json'}
        finally:
            Path(config_file).unlink()


class TestSandboxWithConfig:
    """沙箱配置测试"""
    
    def test_sandbox_with_custom_config(self):
        """测试沙箱使用自定义配置"""
        config = SecurityConfig(
            max_gas=100,
            allowed_modules={'math'},
        )
        
        sandbox = SecureSandbox(config)
        
        # 允许的模块
        code1 = "import math; result = math.sqrt(16)"
        result1 = sandbox.safe_execute(code1)
        
        assert result1['success'] is True
    
    def test_sandbox_config_override(self):
        """测试沙箱配置覆盖"""
        config = SecurityConfig(max_gas=100)
        sandbox = SecureSandbox(config)
        
        # 使用不同的Gas额度
        code = "result = 1 + 2"
        result = sandbox.safe_execute(code, max_gas=50)
        
        # 应该使用传入的max_gas，消耗1个gas（模块注入）
        assert result['remaining_gas'] == 49
        assert result['total_checks'] == 1


class TestConfigValidation:
    """配置验证测试"""
    
    def test_invalid_max_gas(self):
        """测试无效的max_gas"""
        with pytest.raises(ValueError):
            SecurityConfig(max_gas=-1)
        
        with pytest.raises(ValueError):
            SecurityConfig(max_gas=0)
    
    def test_empty_allowed_modules(self):
        """测试空的允许模块"""
        config = SecurityConfig(allowed_modules=set())
        
        assert len(config.allowed_modules) == 0
        
        # 应该拒绝所有导入
        sandbox = SecureSandbox(config)
        code = "import math"
        
        with pytest.raises(Exception):
            sandbox.safe_execute(code)


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
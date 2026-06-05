"""
Secure Sandbox - 高安全性Python沙箱库

用于安全执行不可信的第三方代码（如AI生成的代码）

核心特性：
- Gas机制防止CPU DoS攻击
- AST白名单防止危险操作  
- 属性拦截防止沙箱逃逸
- Import白名单控制模块导入

作者: Python Security Architect
版本: 0.0.1
"""

from .core import (
    SecureSandbox,
    SecurityConfig,
    safe_execute,
    GasLimitExceeded,
    SandboxSecurityError,
    ASTValidationError,
    SandboxException,
)

from .whitelist import (
    AST_WHITELIST,
    AST_BLACKLIST,
    DANGEROUS_ATTRIBUTES,
    SAFE_ATTRIBUTES,
    SAFE_BUILTIN_TYPES,
    DEFAULT_ALLOWED_MODULES,
)

__version__ = "0.0.1"
__author__ = "Python Security Architect"
__email__ = "security@example.com"

__all__ = [
    # 核心类
    'SecureSandbox',
    'SecurityConfig',
    
    # 便捷函数
    'safe_execute',
    
    # 异常类
    'GasLimitExceeded',
    'SandboxSecurityError',
    'ASTValidationError',
    'SandboxException',
    
    # 白名单配置
    'AST_WHITELIST',
    'AST_BLACKLIST',
    'DANGEROUS_ATTRIBUTES',
    'SAFE_ATTRIBUTES',
    'SAFE_BUILTIN_TYPES',
    'DEFAULT_ALLOWED_MODULES',
    
    # 元数据
    '__version__',
    '__author__',
]
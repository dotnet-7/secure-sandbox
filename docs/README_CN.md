# Secure Sandbox - Python安全沙箱库

[![PyPI version](https://badge.fury.io/py/secure-sandbox.svg)](https://badge.fury.io/py/secure-sandbox)
[![Python versions](https://img.shields.io/pypi/pyversions/secure-sandbox.svg)](https://pypi.org/project/secure-sandbox)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

**高安全性纯Python沙箱库，用于安全执行不可信的第三方代码（如AI生成的代码）**

[返回英文文档 (English Documentation)](../README.md)

## 核心特性

### 1. Gas机制 - 防止CPU DoS攻击
- ✅ 在每个循环和函数调用中自动注入Gas检查
- ✅ 当Gas额度耗尽时，立即抛出`GasLimitExceeded`异常
- ✅ 有效防御死循环和资源耗尽攻击

### 2. AST白名单验证
- ✅ 严格的AST节点白名单机制
- ✅ 拒绝危险的AST节点（如Import、Async、Yield等）
- ✅ 在编译期阻断危险操作

### 3. 属性访问拦截
- ✅ 所有属性访问被重写为`__sandbox_getattr__`
- ✅ 严格的属性黑名单（40+危险属性，如`__class__`、`__subclasses__`等）
- ✅ 防止通过反射链进行沙箱逃逸

### 4. Import白名单控制
- ✅ 可配置的模块导入白名单
- ✅ 默认允许安全模块（math、json、datetime等）
- ✅ 拒绝危险模块（os、sys、subprocess等）

### 5. 完全可配置
- ✅ 所有安全策略都可以自定义
- ✅ Gas额度、AST白名单、属性黑名单、模块白名单均可配置
- ✅ 支持灵活的安全级别调整

## 安装

```bash
pip install secure-sandbox
```

## 快速开始

### 基础用法

```python
from secure_sandbox import safe_execute

# 执行安全的代码
code = """
def factorial(n):
    result = 1
    for i in range(1, n + 1):
        result *= i
    return result

print(f"5的阶乘: {factorial(5)}")
"""

result = safe_execute(code, max_gas=100)
print(f"剩余Gas: {result['remaining_gas']}")
```

### 防御死循环

```python
from secure_sandbox import SecureSandbox, GasLimitExceeded

malicious_code = """
i = 0
while True:
    i += 1
"""

sandbox = SecureSandbox()
try:
    sandbox.safe_execute(malicious_code, max_gas=50)
except GasLimitExceeded as e:
    print(f"成功拦截死循环: {e}")
```

### 防御沙箱逃逸

```python
from secure_sandbox import SecureSandbox, SandboxSecurityError

escape_code = """
result = [].__class__.__base__.__subclasses__()
"""

sandbox = SecureSandbox()
try:
    sandbox.safe_execute(escape_code, max_gas=100)
except SandboxSecurityError as e:
    print(f"成功拦截逃逸攻击: {e}")
```

### 使用模块导入

```python
from secure_sandbox import safe_execute

code = """
import math
result = math.sqrt(16)
print(f"sqrt(16) = {result}")

from json import dumps
json_str = dumps({"name": "Alice", "age": 25})
print(json_str)
"""

result = safe_execute(code, max_gas=100)
```

## 高级配置

### 自定义安全策略

```python
from secure_sandbox import SecureSandbox, SecurityConfig

# 创建自定义配置
config = SecurityConfig(
    # Gas配置
    max_gas=5000,              # 最大Gas额度
    max_recursion_depth=50,    # 最大递归深度
    
    # Import配置
    allow_imports=True,        # 允许导入
    allowed_modules={'math', 'json'},  # 只允许这两个模块
    
    # AST节点配置（可选）
    ast_whitelist={'For', 'While', 'FunctionDef', ...},  # 自定义AST白名单
    ast_blacklist={'Import', 'Try', ...},  # 自定义AST黑名单
    
    # 属性访问配置
    allow_dunder_access=False,  # 禁止魔术方法
    allow_private_attrs=False,  # 禁止私有属性
    dangerous_attributes={'__class__', '__globals__', ...},  # 自定义危险属性
    safe_attributes={'append', 'upper', ...},  # 自定义安全属性
    
    # 功能开关
    allow_comprehensions=True,  # 允许推导式
    allow_lambdas=True,         # 允许Lambda
    allow_classes=False,        # 禁止类定义
)

sandbox = SecureSandbox(config)
result = sandbox.safe_execute(code, max_gas=100)
```

### 添加自定义模块到白名单

```python
from secure_sandbox import SecurityConfig, DEFAULT_ALLOWED_MODULES

# 扩展默认模块白名单
custom_modules = DEFAULT_ALLOWED_MODULES.copy()
custom_modules.update({
    'numpy',    # 添加numpy
    'pandas',   # 添加pandas
})

config = SecurityConfig(
    allowed_modules=custom_modules
)
```

## 配置详解

### SecurityConfig 参数说明

| 参数 | 类型 | 默认值 | 说明 |
|-----|------|--------|------|
| `max_gas` | int | 10000 | 最大Gas额度，防止死循环 |
| `max_recursion_depth` | int | 100 | 最大递归深度 |
| `allow_imports` | bool | True | 是否允许导入模块 |
| `allowed_modules` | Set[str] | DEFAULT_ALLOWED_MODULES | 允许导入的模块白名单 |
| `ast_whitelist` | Set[str] | AST_WHITELIST | 允许的AST节点白名单 |
| `ast_blacklist` | Set[str] | AST_BLACKLIST | 禁止的AST节点黑名单 |
| `allow_dunder_access` | bool | False | 是否允许访问魔术方法 |
| `allow_private_attrs` | bool | False | 是否允许访问私有属性 |
| `dangerous_attributes` | Set[str] | DANGEROUS_ATTRIBUTES | 危险属性黑名单 |
| `safe_attributes` | Set[str] | SAFE_ATTRIBUTES | 安全属性白名单 |
| `allow_comprehensions` | bool | True | 是否允许推导式 |
| `allow_lambdas` | bool | True | 是否允许Lambda表达式 |
| `allow_classes` | bool | True | 是否允许类定义 |

### 默认允许的模块

```
math        - 数学计算
json        - JSON处理
datetime    - 日期时间
collections - 高级数据结构
itertools   - 迭代器工具
functools   - 函数工具
operator    - 操作符函数
typing      - 类型提示
decimal     - 高精度数学
fractions   - 分数运算
statistics  - 统计函数
array       - 数组
copy        - 复制工具
re          - 正则表达式
random      - 随机数
```

### 禁止的模块示例

```
os          - 操作系统接口
sys         - Python系统
subprocess  - 子进程管理
socket      - 网络通信
pickle      - 序列化（不安全）
```

## API文档

### `safe_execute(code_str, max_gas, config)`

便捷函数，快速执行代码

**参数**:
- `code_str` (str): 要执行的代码字符串
- `max_gas` (int): 最大Gas额度，默认10000
- `config` (SecurityConfig, optional): 安全配置

**返回**:
```python
{
    'success': True,              # 执行是否成功
    'locals': {...},              # 局部变量字典
    'remaining_gas': 9999,        # 剩余Gas
    'total_checks': 100,          # 总检查次数
}
```

**异常**:
- `GasLimitExceeded`: Gas额度耗尽
- `SandboxSecurityError`: 安全违规
- `ASTValidationError`: AST验证失败

### `SecureSandbox(config)`

沙箱主类，提供更灵活的控制

**方法**:
- `safe_execute(code_str, max_gas, timeout)`: 执行代码
- `_create_safe_globals()`: 创建安全全局环境
- `_transform_ast(tree)`: AST转换流水线

## 与传统方案对比

| 特性 | RestrictedPython | Secure Sandbox |
|-----|------------------|----------------|
| CPU DoS防御 | ❌ 无 | ✅ Gas机制 |
| 沙箱逃逸防御 | ⚠️ 有限 | ✅ 严格拦截 |
| Import控制 | ❌ 无 | ✅ 白名单机制 |
| 可配置性 | ⚠️ 基础 | ✅ 完全可配置 |
| 性能开销 | 低 | 中等（10-15%） |

## 安全最佳实践

1. **设置合理的Gas额度**：根据代码复杂度设置，建议100-1000
2. **限制导入模块**：只允许必要的模块
3. **监控执行结果**：检查remaining_gas和异常日志
4. **定期审计配置**：检查白名单是否需要更新
5. **添加超时机制**：结合signal或threading双重保护

## 已知限制

1. **性能开销**：Gas检查会增加约10-15%的性能开销
2. **功能限制**：无法导入危险模块或使用某些高级特性
3. **反射限制**：正常的反射操作也会被限制

## 适用场景

1. **AI代码执行**：安全执行AI生成的代码
2. **在线评测系统**：OJ系统、编程竞赛平台
3. **教育平台**：在线编程教学
4. **代码审计**：安全分析工具
5. **插件系统**：安全的插件执行环境

## 贡献

欢迎提交Issue和Pull Request！

开发环境设置：

```bash
git clone https://github.com/yourname/secure-sandbox.git
cd secure-sandbox
pip install -e ".[dev]"
pytest tests/
```

## 许可证

MIT License

## 作者

Python Security Architect

## 版本历史

- **v0.0.1** - 初始版本
  - 实现Gas机制
  - 实现AST白名单验证
  - 实现属性访问拦截
  - 实现Import白名单控制
  - 完全可配置的安全策略
  - 完整的测试套件
"""
示例 - 自定义配置
"""

from secure_sandbox import SecureSandbox, SecurityConfig, DEFAULT_ALLOWED_MODULES

# 配置1: 严格模式（禁用大部分功能）
strict_config = SecurityConfig(
    max_gas=100,              # 很低的Gas额度
    allow_imports=False,      # 禁止导入
    allow_comprehensions=False,  # 禁止推导式
    allow_lambdas=False,      # 禁止Lambda
    allow_classes=False,      # 禁止类定义
)

print("=" * 60)
print("配置1: 严格模式")
print("=" * 60)
print(f"最大Gas: {strict_config.max_gas}")
print(f"允许导入: {strict_config.allow_imports}")
print(f"允许推导式: {strict_config.allow_comprehensions}")
print(f"允许Lambda: {strict_config.allow_lambdas}")
print(f"允许类定义: {strict_config.allow_classes}")


# 配置2: 自定义模块白名单
custom_modules_config = SecurityConfig(
    max_gas=5000,
    allow_imports=True,
    allowed_modules={'math', 'json'},  # 只允许这两个模块
)

print("\n" + "=" * 60)
print("配置2: 自定义模块白名单")
print("=" * 60)
print(f"允许的模块: {custom_modules_config.allowed_modules}")

# 测试配置2
code = """
import math
result = math.sqrt(100)
print(f"sqrt(100) = {result}")
"""

sandbox = SecureSandbox(custom_modules_config)
result = sandbox.safe_execute(code, max_gas=50)
print(f"\n执行结果:")
print(f"  成功: {result['success']}")
print(f"  剩余Gas: {result['remaining_gas']}")


# 配置3: 扩展默认模块
extended_modules = DEFAULT_ALLOWED_MODULES.copy()
extended_modules.update({
    'numpy',   # 添加numpy（如果可用）
    'pandas',  # 添加pandas（如果可用）
})

extended_config = SecurityConfig(
    max_gas=10000,
    allow_imports=True,
    allowed_modules=extended_modules,
)

print("\n" + "=" * 60)
print("配置3: 扩展模块白名单")
print("=" * 60)
print(f"默认模块: {sorted(DEFAULT_ALLOWED_MODULES)}")
print(f"扩展后模块: {sorted(extended_modules)}")


# 配置4: 允许特定功能
flexible_config = SecurityConfig(
    max_gas=10000,
    allow_imports=True,
    allow_dunder_access=False,  # 仍禁止魔术方法
    allow_private_attrs=False,  # 仍禁止私有属性
    allow_comprehensions=True,  # 允许推导式
    allow_lambdas=True,         # 允许Lambda
    allow_classes=True,         # 允许类定义
)

print("\n" + "=" * 60)
print("配置4: 灵活模式")
print("=" * 60)
print(f"允许推导式: {flexible_config.allow_comprehensions}")
print(f"允许Lambda: {flexible_config.allow_lambdas}")
print(f"允许类定义: {flexible_config.allow_classes}")

# 测试类定义
code_with_class = """
class Calculator:
    def __init__(self, initial=0):
        self.value = initial
    
    def add(self, x):
        self.value += x
        return self
    
    def get_value(self):
        return self.value

calc = Calculator(10)
result = calc.add(5).get_value()
print(f"计算结果: {result}")
"""

sandbox = SecureSandbox(flexible_config)
result = sandbox.safe_execute(code_with_class, max_gas=100)
print(f"\n执行结果:")
print(f"  成功: {result['success']}")
print(f"  剩余Gas: {result['remaining_gas']}")


print("\n" + "=" * 60)
print("配置示例完成")
print("=" * 60)
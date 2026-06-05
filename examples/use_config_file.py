"""
示例 - 使用配置文件
"""

import json
import os
from pathlib import Path
from secure_sandbox import SecureSandbox, SecurityConfig

# 获取配置文件路径（与脚本同目录）
script_dir = Path(__file__).parent
config_file = script_dir / 'config.json'

# 从配置文件加载配置
with open(config_file, 'r') as f:
    config_data = json.load(f)

# 创建配置对象
config = SecurityConfig(
    max_gas=config_data.get('max_gas', 10000),
    max_recursion_depth=config_data.get('max_recursion_depth', 100),
    allow_imports=config_data.get('allow_imports', True),
    allowed_modules=set(config_data.get('allowed_modules', [])),
    allow_dunder_access=config_data.get('allow_dunder_access', False),
    allow_private_attrs=config_data.get('allow_private_attrs', False),
    allow_comprehensions=config_data.get('allow_comprehensions', True),
    allow_lambdas=config_data.get('allow_lambdas', True),
    allow_classes=config_data.get('allow_classes', False),
)

print("=" * 60)
print("从配置文件加载的配置:")
print("=" * 60)
print(json.dumps(config_data, indent=2))

# 使用配置执行代码
code = """
import math
import json

# 使用math模块
result = math.sqrt(25)
print(f"sqrt(25) = {result}")

# 使用json模块
data = {"test": "example"}
json_str = json.dumps(data)
print(f"JSON: {json_str}")
"""

print("\n" + "=" * 60)
print("执行代码:")
print("=" * 60)

sandbox = SecureSandbox(config)
result = sandbox.safe_execute(code, max_gas=config.max_gas)

print(f"\n执行结果:")
print(f"  成功: {result['success']}")
print(f"  剩余Gas: {result['remaining_gas']}")
print(f"  总检查次数: {result['total_checks']}")
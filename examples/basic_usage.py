"""
示例1 - 基础使用
"""

from secure_sandbox import safe_execute

# 执行安全的数学计算
code1 = """
def factorial(n):
    result = 1
    for i in range(1, n + 1):
        result *= i
    return result

result = factorial(10)
print(f"10的阶乘: {result}")
"""

print("=" * 60)
print("示例1: 数学计算")
print("=" * 60)

result = safe_execute(code1, max_gas=100)
print(f"\n执行结果:")
print(f"  成功: {result['success']}")
print(f"  剩余Gas: {result['remaining_gas']}")
print(f"  局部变量: {list(result['locals'].keys())}")


# 示例2 - 使用模块导入
code2 = """
import math
from json import dumps

# 使用math模块
result1 = math.sqrt(16)
result2 = math.log(10)

# 使用json模块
data = {"name": "Alice", "age": 25}
json_str = dumps(data)

print(f"sqrt(16) = {result1}")
print(f"log(10) = {result2}")
print(f"JSON: {json_str}")
"""

print("\n" + "=" * 60)
print("示例2: 模块导入")
print("=" * 60)

result = safe_execute(code2, max_gas=100)
print(f"\n执行结果:")
print(f"  成功: {result['success']}")
print(f"  剩余Gas: {result['remaining_gas']}")


# 示例3 - 数据结构操作
code3 = """
# 列表推导式
numbers = [x ** 2 for x in range(1, 11)]
print(f"平方列表: {numbers}")

# 字典推导式
squares = {x: x ** 2 for x in range(1, 6)}
print(f"平方字典: {squares}")

# 集合推导式
unique_squares = {x % 10 for x in range(20)}
print(f"唯一平方: {unique_squares}")
"""

print("\n" + "=" * 60)
print("示例3: 数据结构")
print("=" * 60)

result = safe_execute(code3, max_gas=100)
print(f"\n执行结果:")
print(f"  成功: {result['success']}")
print(f"  剩余Gas: {result['remaining_gas']}")


print("\n" + "=" * 60)
print("所有示例执行成功！")
print("=" * 60)
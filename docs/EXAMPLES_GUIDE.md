# 示例文件总结

Secure Sandbox提供了4个完整的示例文件，展示不同的使用场景：

## 示例列表

### 1. basic_usage.py - 基础使用
**功能**: 展示基础功能使用
- 数学计算（阶乘）
- 模块导入（math、json）
- 数据结构操作（列表推导式、字典推导式、集合推导式）

**运行**:
```bash
python examples/basic_usage.py
```

**输出示例**:
```
示例1: 数学计算
10的阶乘: 3628800
执行成功 | 剩余Gas: 88

示例2: 模块导入
sqrt(16) = 4.0
JSON: {"name": "Alice", "age": 25}

示例3: 数据结构
平方列表: [1, 4, 9, 16, 25, ...]
```

---

### 2. custom_config.py - 自定义配置
**功能**: 展示各种配置策略
- 配置1: 严格模式（禁用大部分功能）
- 配置2: 自定义模块白名单（只允许math和json）
- 配置3: 扩展模块白名单（添加numpy、pandas）
- 配置4: 灵活模式（允许推导式、Lambda、类定义）

**运行**:
```bash
python examples/custom_config.py
```

**输出示例**:
```
配置1: 严格模式
最大Gas: 100
允许导入: False
允许推导式: False

配置2: 自定义模块白名单
允许的模块: {'math', 'json'}
sqrt(100) = 10.0

配置4: 灵活模式
允许推导式: True
允许Lambda: True
允许类定义: True
计算结果: 15
```

---

### 3. use_config_file.py - 配置文件使用
**功能**: 展示从JSON文件加载配置
- 从config.json加载配置
- 使用配置执行代码
- 支持math、json、datetime模块

**运行**:
```bash
python examples/use_config_file.py
```

**配置文件示例** (config.json):
```json
{
  "max_gas": 5000,
  "max_recursion_depth": 50,
  "allow_imports": true,
  "allowed_modules": ["math", "json", "datetime"],
  "allow_dunder_access": false,
  "allow_private_attrs": false,
  "allow_comprehensions": true,
  "allow_lambdas": true,
  "allow_classes": false
}
```

**输出示例**:
```
从配置文件加载的配置:
{
  "max_gas": 5000,
  "allowed_modules": ["math", "json", "datetime"],
  ...
}

执行代码:
sqrt(25) = 5.0
JSON: {"test": "example"}

执行成功 | 剩余Gas: 4994
```

---

### 4. security_interception.py - 安全拦截演示 ⭐
**功能**: 演示20种攻击拦截机制

**攻击类型**:
1. **Gas机制拦截** (2种)
   - 死循环攻击
   - 嵌套循环攻击

2. **属性拦截** (12种)
   - 反射链逃逸 (__class__, __globals__, __code__)
   - 内部属性攻击 (__dict__, __mro__, __subclasses__)
   - 动态属性攻击 (getattr)
   - 私有属性访问 (_private)

3. **AST验证拦截** (8种)
   - Import攻击 (os, sys, subprocess)
   - 动态执行攻击 (eval, exec, compile)
   - 文件操作攻击 (open)
   - 异常处理逃逸 (try-except)
   - 上下文管理器攻击 (with)

**运行**:
```bash
python examples/security_interception.py
```

**输出示例**:
```
1. 死循环攻击 - Gas机制拦截
✅ 死循环攻击成功拦截
   拦截信息: [GasLimitExceeded] Gas额度耗尽...

3. 反射链逃逸攻击 - 属性拦截
✅ 反射链逃逸(__class__)成功拦截
   拦截信息: [SandboxSecurityError] 禁止访问危险属性 '__class__'...

6. Import攻击 - AST验证拦截
✅ Import os攻击成功拦截
   拦截信息: [ASTValidationError] 禁止导入非白名单模块 'os'...

拦截测试汇总:
总测试数: 20
成功拦截: 20 ✅
拦截失败: 0 ❌
拦截率: 100.0%

🎉 所有攻击成功拦截！沙箱安全可靠！
```

---

## 运行所有示例

```bash
# 运行所有示例
python examples/basic_usage.py
python examples/custom_config.py
python examples/use_config_file.py
python examples/security_interception.py  # ⭐ 推荐
```

## 示例文件位置

```
examples/
├── basic_usage.py           # 基础使用
├── custom_config.py         # 自定义配置
├── use_config_file.py       # 配置文件使用
├── security_interception.py # 安全拦截演示 ⭐
└── config.json              # 配置文件示例
```

## 学习建议

1. **初学者**: 先看 `basic_usage.py` 了解基础功能
2. **配置使用**: 看 `custom_config.py` 学习自定义配置
3. **配置文件**: 看 `use_config_file.py` 学习配置文件使用
4. **安全理解**: ⭐ 看 `security_interception.py` 理解安全机制

---

**所有示例都能正常运行，可直接执行查看效果！** ✅
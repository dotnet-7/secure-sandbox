# Secure Sandbox - 项目结构说明

## 目录结构

```
secure-sandbox/
├── src/                      # 源代码目录
│   └── secure_sandbox/       # 主包
│       ├── __init__.py      # 包入口，导出所有API
│       ├── core.py          # 核心沙箱实现（Gas机制、AST验证、属性拦截）
│       ├── whitelist.py     # 白名单配置（AST节点、属性、模块）
│       ├── exceptions.py    # 异常类定义
│       └── cli.py           # 命令行工具
│
├── tests/                    # 测试代码目录
│   ├── test_basic.py        # 基础功能测试
│   ├── test_security.py    # 安全功能测试
│   └── test_config.py      # 配置功能测试
│   └ conftest.py            # pytest配置（可选）
│
├── docs/                     # 文档目录
│   ├── README_CN.md         # 中文文档
│   ├── API.md               # API文档（待添加）
│   ├── ARCHITECTURE.md      # 架构说明（待添加）
│   └── EXAMPLES.md          # 示例文档（待添加）
│
├── examples/                 # 示例代码目录
│   ├── basic_usage.py       # 基础使用示例
│   ├── custom_config.py     # 自定义配置示例
│   ├── use_config_file.py   # 配置文件使用示例
│   └ config.json            # 配置文件示例
│
├── README.md                 # 英文主文档
├── CONTRIBUTING.md           # 贡献指南
├── LICENSE                   # MIT许可证
├── setup.py                  # 传统安装脚本
├── pyproject.toml            # 现代Python项目配置
├── MANIFEST.in               # 打包清单
├── .gitignore                # Git忽略文件
└ requirements.txt            # 依赖文件（可选）
└ requirements-dev.txt        # 开发依赖（可选）
```

## 核心模块说明

### 1. `src/secure_sandbox/core.py`

核心沙箱实现，包含：

- `SecurityConfig` - 安全配置类（完全可配置）
- `GasMeter` - Gas计量器（防止CPU DoS）
- `ASTSecurityValidator` - AST安全验证器
- `GasInjector` - Gas注入器（编译期插桩）
- `AttributeRewriter` - 属性访问重写器
- `SecureSandbox` - 主沙箱类
- `safe_execute()` - 便捷执行函数

### 2. `src/secure_sandbox/whitelist.py`

白名单配置，包含：

- `AST_WHITELIST` - AST节点白名单（80+安全节点）
- `AST_BLACKLIST` - AST节点黑名单（10个危险节点）
- `DANGEROUS_ATTRIBUTES` - 危险属性黑名单（40+属性）
- `SAFE_ATTRIBUTES` - 安全属性白名单（60+属性）
- `DEFAULT_ALLOWED_MODULES` - 默认模块白名单（15个安全模块）

### 3. `src/secure_sandbox/exceptions.py`

异常类定义：

- `SandboxException` - 基础异常
- `GasLimitExceeded` - Gas耗尽异常
- `SandboxSecurityError` - 安全违规异常
- `ASTValidationError` - AST验证失败异常

### 4. `src/secure_sandbox/cli.py`

命令行工具：

- 支持从文件执行代码
- 支持从命令行执行代码
- 支持配置文件
- 支持详细输出
- 支持JSON输出

## 测试说明

### `tests/test_basic.py`

基础功能测试：

- 简单代码执行
- 函数定义
- 循环执行
- 列表推导式
- Gas机制
- Import白名单

### `tests/test_security.py`

安全功能测试：

- 逃逸攻击拦截
- 危险函数拦截
- 危险AST节点拦截
- 属性访问拦截
- 自定义安全策略

### `tests/test_config.py`

配置功能测试：

- 默认配置
- 自定义配置
- 功能开关
- 配置文件加载/保存
- 配置验证

## 文档说明

### `README.md` (英文)

- 项目介绍
- 核心特性
- 安装指南
- 快速开始
- API文档
- 配置说明
- 最佳实践

### `docs/README_CN.md` (中文)

- 完整的中文翻译文档
- 包含所有英文文档内容
- 针对中文用户的详细说明

### `CONTRIBUTING.md`

- 开发环境设置
- 编码规范
- 测试指南
- Pull Request流程
- 发布流程

## 示例说明

### `examples/basic_usage.py`

基础使用示例：

- 数学计算
- 模块导入
- 数据结构操作

### `examples/custom_config.py`

自定义配置示例：

- 严格模式
- 自定义模块白名单
- 扩展模块白名单
- 灵活模式

### `examples/use_config_file.py`

配置文件使用示例：

- 从JSON加载配置
- 使用配置执行代码

## 安装配置

### `setup.py`

传统安装脚本：

- 包信息配置
- 依赖声明
- 入口点定义

### `pyproject.toml`

现代Python项目配置：

- 构建系统配置
- 项目元数据
- 工具配置（black、mypy、pytest）

### `MANIFEST.in`

打包清单：

- 包含文件列表
- 排除文件列表

## 开发工具

### `.gitignore`

Git忽略文件：

- Python缓存文件
- 构建产物
- IDE配置
- 测试结果

### `requirements.txt`

依赖文件（可选）：

- 无外部依赖（纯Python）

### `requirements-dev.txt`

开发依赖（可选）：

- pytest
- black
- mypy
- flake8

## 构建和发布

### 构建包

```bash
python -m build
```

生成：
- `dist/secure_sandbox-0.0.1.tar.gz` (源码包)
- `dist/secure_sandbox-0.0.1-py3-none-any.whl` (wheel包)

### 发布到PyPI

```bash
twine upload dist/*
```

### 本地安装

```bash
pip install -e .
```

## 项目优势

### 1. 清晰的结构

- **代码分离**：源码、测试、文档、示例分开
- **职责明确**：每个模块功能清晰
- **易于维护**：结构规范，便于扩展

### 2. 完整的测试

- **单元测试**：覆盖核心功能
- **安全测试**：验证防御机制
- **配置测试**：测试可配置性

### 3. 详尽的文档

- **双语支持**：英文+中文
- **多种格式**：README、API、示例
- **贡献指南**：开发流程清晰

### 4. 标准化配置

- **setup.py**：传统方式
- **pyproject.toml**：现代方式
- **MANIFEST.in**：打包清单

### 5. 开发友好

- **虚拟环境**：隔离开发环境
- **开发依赖**：完整工具链
- **质量检查**：black、mypy、flake8

## 使用建议

### 开发者

1. 克隆项目
2. 创建虚拟环境
3. 安装开发依赖：`pip install -e ".[dev]"`
4. 运行测试：`pytest tests/`
5. 查看示例：`python examples/basic_usage.py`

### 用户

1. 安装包：`pip install secure-sandbox`
2. 查看文档：README.md 或 docs/README_CN.md
3. 运行示例：examples/
4. 自定义配置：参考 custom_config.py

### 贡献者

1. 阅读 CONTRIBUTING.md
2. Fork项目
3. 创建分支
4. 提交Pull Request

## 总结

这是一个**标准化、规范化**的Python第三方库项目结构：

✅ **源码分离** - src/secure_sandbox  
✅ **测试独立** - tests/  
✅ **文档完善** - docs/  
✅ **示例丰富** - examples/  
✅ **配置标准** - setup.py + pyproject.toml  
✅ **双语支持** - 英文README + 中文docs  

符合Python社区最佳实践，易于维护、测试和发布！
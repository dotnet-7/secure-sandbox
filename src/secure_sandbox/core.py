"""
核心沙箱实现 - 安全执行引擎
"""

import ast
import sys
import builtins
import types
from typing import Any, Dict, Set, Optional, List, Callable
from dataclasses import dataclass, field

from .exceptions import (
    SandboxException,
    GasLimitExceeded,
    SandboxSecurityError,
    ASTValidationError,
)
from .whitelist import (
    AST_WHITELIST,
    AST_BLACKLIST,
    DANGEROUS_ATTRIBUTES,
    SAFE_ATTRIBUTES,
    SAFE_BUILTIN_TYPES,
    DEFAULT_ALLOWED_MODULES,
)


@dataclass
class SecurityConfig:
    """
    安全配置 - 完全可配置的安全策略
    
    所有安全相关的配置都可以自定义：
    - Gas额度限制
    - AST节点白名单/黑名单
    - 属性访问控制
    - 模块导入控制
    """
    
    # Gas配置
    max_gas: int = 10000
    max_recursion_depth: int = 100
    
    # Import配置
    allow_imports: bool = True
    allowed_modules: Optional[Set[str]] = None
    
    # AST节点配置
    ast_whitelist: Optional[Set[str]] = None
    ast_blacklist: Optional[Set[str]] = None
    
    # 属性访问配置
    allow_dunder_access: bool = False
    allow_private_attrs: bool = False
    dangerous_attributes: Optional[Set[str]] = None
    safe_attributes: Optional[Set[str]] = None
    
    # 功能开关
    allow_comprehensions: bool = True
    allow_lambdas: bool = True
    allow_classes: bool = True
    
    def __post_init__(self):
        """初始化默认配置并验证参数"""
        if self.max_gas <= 0:
            raise ValueError(f"max_gas必须为正整数, 当前: {self.max_gas}")
        
        if self.allowed_modules is None:
            self.allowed_modules = DEFAULT_ALLOWED_MODULES.copy()
        
        if self.ast_whitelist is None:
            self.ast_whitelist = AST_WHITELIST.copy()
        
        if self.ast_blacklist is None:
            self.ast_blacklist = AST_BLACKLIST.copy()
        
        if self.dangerous_attributes is None:
            self.dangerous_attributes = DANGEROUS_ATTRIBUTES.copy()
        
        if self.safe_attributes is None:
            self.safe_attributes = SAFE_ATTRIBUTES.copy()


class GasMeter:
    """Gas计量器 - 核心防护机制"""
    
    __slots__ = ['_max_gas', '_current_gas', '_check_count']
    
    def __init__(self, max_gas: int):
        if max_gas <= 0:
            raise ValueError(f"max_gas必须为正整数, 当前: {max_gas}")
        self._max_gas = max_gas
        self._current_gas = max_gas
        self._check_count = 0
    
    def check_gas(self) -> None:
        """检查并消耗Gas - 高频调用函数"""
        if self._current_gas <= 0:
            raise GasLimitExceeded(
                f"Gas额度耗尽! 已执行 {self._check_count} 次操作, "
                f"最大额度: {self._max_gas}"
            )
        self._current_gas -= 1
        self._check_count += 1
    
    def reset(self, max_gas: Optional[int] = None) -> None:
        """重置Gas额度"""
        if max_gas is not None:
            if max_gas <= 0:
                raise ValueError(f"max_gas必须为正整数, 当前: {max_gas}")
            self._max_gas = max_gas
        self._current_gas = self._max_gas
        self._check_count = 0
    
    @property
    def remaining_gas(self) -> int:
        return self._current_gas
    
    @property
    def max_gas(self) -> int:
        return self._max_gas


class ASTSecurityValidator(ast.NodeVisitor):
    """AST安全验证器 - 白名单检查"""
    
    def __init__(self, config: SecurityConfig):
        self.config = config
        self.violations: List[str] = []
    
    def visit(self, node: ast.AST) -> None:
        node_name = node.__class__.__name__
        
        # 检查黑名单
        blacklist = self.config.ast_blacklist if self.config.ast_blacklist else set()
        if node_name in blacklist:
            self.violations.append(
                f"检测到黑名单AST节点 '{node_name}' - "
                f"位置: 行{getattr(node, 'lineno', '?')} "
                f"列{getattr(node, 'col_offset', '?')}"
            )
        # 检查白名单
        else:
            whitelist = self.config.ast_whitelist if self.config.ast_whitelist else set()
            if node_name not in whitelist:
                self.violations.append(
                    f"检测到非白名单AST节点 '{node_name}' - "
                    f"位置: 行{getattr(node, 'lineno', '?')} "
                    f"列{getattr(node, 'col_offset', '?')}"
                )
        
        super().visit(node)
    
    def visit_Import(self, node: ast.Import) -> None:
        """检查import语句的白名单"""
        if not self.config.allow_imports:
            self.violations.append(
                f"禁止导入模块 - 位置: 行{node.lineno}"
            )
        else:
            allowed = self.config.allowed_modules if self.config.allowed_modules else set()
            for alias in node.names:
                module_name = alias.name
                if module_name not in allowed:
                    self.violations.append(
                        f"禁止导入非白名单模块 '{module_name}' - "
                        f"位置: 行{node.lineno} "
                        f"白名单模块: {', '.join(sorted(allowed))}"
                    )
        self.generic_visit(node)
    
    def visit_ImportFrom(self, node: ast.ImportFrom) -> None:
        """检查from...import语句的白名单"""
        if not self.config.allow_imports:
            self.violations.append(
                f"禁止从模块导入 - 位置: 行{node.lineno}"
            )
        else:
            allowed = self.config.allowed_modules if self.config.allowed_modules else set()
            module_name = node.module if node.module else ''
            if module_name not in allowed:
                self.violations.append(
                    f"禁止从非白名单模块 '{module_name}' 导入 - "
                    f"位置: 行{node.lineno} "
                    f"白名单模块: {', '.join(sorted(allowed))}"
                )
        self.generic_visit(node)
    
    def visit_Call(self, node: ast.Call) -> None:
        """检查危险函数调用"""
        if isinstance(node.func, ast.Name):
            dangerous_functions = ['eval', 'exec', 'compile', 'open', 'input']
            if node.func.id in dangerous_functions:
                self.violations.append(
                    f"禁止调用危险函数 '{node.func.id}' - "
                    f"位置: 行{node.lineno}"
                )
        self.generic_visit(node)
    
    def validate(self, tree: ast.AST) -> bool:
        """验证AST树"""
        self.violations.clear()
        self.visit(tree)
        return len(self.violations) == 0


class GasInjector(ast.NodeTransformer):
    """Gas注入器 - 在关键节点注入检查"""
    
    def __init__(self, config: SecurityConfig):
        self.config = config
        self._injected_count = 0
    
    def _create_gas_check_call(self) -> ast.Expr:
        """创建Gas检查调用节点"""
        gas_check = ast.Expr(
            value=ast.Call(
                func=ast.Name(id='__sandbox_check_gas__', ctx=ast.Load()),
                args=[],
                keywords=[]
            )
        )
        ast.fix_missing_locations(gas_check)
        self._injected_count += 1
        return gas_check
    
    def visit_Module(self, node: ast.Module) -> ast.Module:
        """在模块开头注入Gas检查"""
        self.generic_visit(node)
        if node.body:
            node.body.insert(0, self._create_gas_check_call())
        return node
    
    def visit_For(self, node: ast.For) -> ast.For:
        """在for循环体开头注入Gas检查"""
        self.generic_visit(node)
        node.body.insert(0, self._create_gas_check_call())
        return node
    
    def visit_While(self, node: ast.While) -> ast.While:
        """在while循环体开头注入Gas检查"""
        self.generic_visit(node)
        node.body.insert(0, self._create_gas_check_call())
        return node
    
    def visit_FunctionDef(self, node: ast.FunctionDef) -> ast.FunctionDef:
        """在函数定义开头注入Gas检查"""
        self.generic_visit(node)
        if node.body and not (len(node.body) == 1 and isinstance(node.body[0], ast.Pass)):
            node.body.insert(0, self._create_gas_check_call())
        return node


class AttributeRewriter(ast.NodeTransformer):
    """属性访问重写器 - 核心安全拦截"""
    
    def __init__(self, config: SecurityConfig):
        self.config = config
        self._rewritten_count = 0
    
    def visit_Attribute(self, node: ast.Attribute) -> ast.AST:
        """重写所有属性访问为安全调用"""
        if isinstance(node.ctx, ast.Store):
            self.generic_visit(node)
            return node
        
        self.generic_visit(node)
        
        rewritten = ast.Call(
            func=ast.Name(id='__sandbox_getattr__', ctx=ast.Load()),
            args=[
                node.value,
                ast.Constant(value=node.attr)
            ],
            keywords=[]
        )
        ast.fix_missing_locations(rewritten)
        self._rewritten_count += 1
        
        return rewritten


class SecureSandbox:
    """安全沙箱 - 主执行引擎"""
    
    __slots__ = ['config', '_gas_meter', '_safe_globals', '_safe_builtins']
    
    def __init__(self, config: Optional[SecurityConfig] = None):
        self.config = config or SecurityConfig()
        self._gas_meter = GasMeter(self.config.max_gas)
        self._safe_globals: Optional[Dict[str, Any]] = None
        self._safe_builtins: Optional[Dict[str, Any]] = None
    
    def _create_safe_getattr(self) -> Callable[[Any, str], Any]:
        """创建安全的属性访问函数"""
        gas_meter = self._gas_meter
        config = self.config
        
        def __sandbox_getattr__(obj: Any, attr: str) -> Any:
            gas_meter.check_gas()
            
            dangerous_attrs = config.dangerous_attributes if config.dangerous_attributes else set()
            safe_attrs = config.safe_attributes if config.safe_attributes else set()
            allowed_modules = config.allowed_modules if config.allowed_modules else set()
            
            # 检查危险属性
            if attr in dangerous_attrs:
                raise SandboxSecurityError(
                    f"禁止访问危险属性 '{attr}' - "
                    f"类型: {type(obj).__name__}"
                )
            
            # 检查魔术方法
            if attr.startswith('__') and attr.endswith('__'):
                if not config.allow_dunder_access:
                    if attr not in safe_attrs:
                        raise SandboxSecurityError(
                            f"禁止访问魔术属性 '{attr}' - "
                            f"类型: {type(obj).__name__}"
                        )
            
            # 检查私有属性
            elif attr.startswith('_'):
                if not config.allow_private_attrs:
                    raise SandboxSecurityError(
                        f"禁止访问私有属性 '{attr}' - "
                        f"类型: {type(obj).__name__}"
                    )
            
            try:
                value = object.__getattribute__(obj, attr)
                
                # 检查可调用对象
                if callable(value):
                    obj_type = type(obj)
                    
                    # 模块对象检查
                    if isinstance(obj, types.ModuleType):
                        try:
                            module_name = obj.__name__
                            if module_name in allowed_modules:
                                return value
                            else:
                                raise SandboxSecurityError(
                                    f"禁止访问非白名单模块 '{module_name}' 的方法 '{attr}'"
                                )
                        except:
                            raise SandboxSecurityError(
                                f"禁止访问模块的方法 '{attr}'"
                            )
                    
                    # 类对象检查
                    if obj_type is type:
                        try:
                            module_name = getattr(obj, '__module__', '')
                            if module_name in allowed_modules:
                                return value
                        except:
                            pass
                    
                    # 用户自定义对象检查（在沙箱内创建的对象）
                    try:
                        obj_module = getattr(obj, '__module__', '')
                        # 如果对象在沙箱内创建，允许访问所有方法
                        if obj_module == '__sandbox__' or obj_module.startswith('__sandbox__'):
                            return value
                    except:
                        pass
                    
                    # 非安全类型检查
                    if obj_type not in SAFE_BUILTIN_TYPES:
                        if attr not in safe_attrs:
                            raise SandboxSecurityError(
                                f"禁止调用非白名单方法 '{attr}' - "
                                f"类型: {obj_type.__name__}"
                            )
                
                return value
                
            except AttributeError:
                raise SandboxSecurityError(
                    f"属性 '{attr}' 不存在于对象 {type(obj).__name__} 中"
                )
            except Exception as e:
                raise SandboxSecurityError(
                    f"访问属性 '{attr}' 时发生错误: {e}"
                ) from e
        
        return __sandbox_getattr__
    
    def _create_safe_import(self) -> Callable[[str, Any], Any]:
        """创建安全的__import__函数"""
        gas_meter = self._gas_meter
        config = self.config
        
        def __sandbox_import__(name: str, globals=None, locals=None, fromlist=(), level=0) -> Any:
            """安全的导入函数，只允许白名单模块"""
            gas_meter.check_gas()
            
            if not config.allow_imports:
                raise SandboxSecurityError(
                    f"禁止导入模块 '{name}' - 导入功能已禁用"
                )
            
            allowed = config.allowed_modules or set()
            if name not in allowed:
                raise SandboxSecurityError(
                    f"禁止导入非白名单模块 '{name}' - "
                    f"白名单模块: {', '.join(sorted(allowed))}"
                )
            
            try:
                module = builtins.__import__(name, globals, locals, fromlist, level)
                return module
            except ImportError as e:
                raise SandboxSecurityError(
                    f"导入模块 '{name}' 失败: {e}"
                ) from e
            except Exception as e:
                raise SandboxSecurityError(
                    f"导入模块 '{name}' 时发生错误: {e}"
                ) from e
        
        return __sandbox_import__
    
    def _create_safe_print(self) -> Callable[..., None]:
        """创建安全的print函数"""
        gas_meter = self._gas_meter
        
        def __sandbox_print__(*args, **kwargs) -> None:
            gas_meter.check_gas()
            
            safe_args = []
            for arg in args:
                if isinstance(arg, (str, int, float, bool, type(None))):
                    safe_args.append(arg)
                else:
                    safe_args.append(f"<{type(arg).__name__}>")
            
            builtins.print(*safe_args, **kwargs)
        
        return __sandbox_print__
    
    def _create_safe_builtins(self) -> Dict[str, Any]:
        """创建安全的内置函数字典"""
        if self._safe_builtins is not None:
            return self._safe_builtins
        
        safe_builtins = {
            'True': True,
            'False': False,
            'None': None,
            
            # 安全的内置函数
            'abs': abs,
            'all': all,
            'any': any,
            'bin': bin,
            'bool': bool,
            'chr': chr,
            'divmod': divmod,
            'enumerate': enumerate,
            'filter': filter,
            'float': float,
            'format': format,
            'hex': hex,
            'int': int,
            'isinstance': isinstance,
            'iter': iter,
            'len': len,
            'list': list,
            'map': map,
            'max': max,
            'min': min,
            'next': next,
            'oct': oct,
            'ord': ord,
            'pow': pow,
            'print': self._create_safe_print(),
            'range': range,
            'repr': repr,
            'reversed': reversed,
            'round': round,
            'set': set,
            'sorted': sorted,
            'str': str,
            'sum': sum,
            'tuple': tuple,
            'type': lambda obj: type(obj).__name__,
            'zip': zip,
            
            # 数据类型
            'dict': dict,
            'frozenset': frozenset,
            'bytes': bytes,
            'bytearray': bytearray,
            'complex': complex,
            
            # 受限的属性访问函数
            'hasattr': lambda obj, name: False,
            'getattr': self._create_safe_getattr(),
            'setattr': lambda obj, name, value: (_ for _ in ()).throw(
                SandboxSecurityError(f"禁止使用setattr")
            ),
            'delattr': lambda obj, name: (_ for _ in ()).throw(
                SandboxSecurityError(f"禁止使用delattr")
            ),
            
            # 受限的导入函数
            '__import__': self._create_safe_import(),
            
            # 类构建函数（如果允许类定义）
            '__build_class__': __build_class__ if self.config.allow_classes else None,
        }
        
        # 如果不允许类定义，移除__build_class__
        if not self.config.allow_classes:
            safe_builtins['__build_class__'] = lambda *args, **kwargs: (_ for _ in ()).throw(
                SandboxSecurityError("禁止定义类")
            )
        
        self._safe_builtins = safe_builtins
        return safe_builtins
    
    def _create_safe_globals(self) -> Dict[str, Any]:
        """创建安全的全局命名空间"""
        if self._safe_globals is not None:
            return self._safe_globals
        
        safe_globals = {
            '__builtins__': self._create_safe_builtins(),
            '__sandbox_check_gas__': self._gas_meter.check_gas,
            '__sandbox_getattr__': self._create_safe_getattr(),
            '__name__': '__sandbox__',
            '__doc__': None,
        }
        
        self._safe_globals = safe_globals
        return safe_globals
    
    def _transform_ast(self, tree: ast.Module) -> ast.Module:
        """AST转换流水线"""
        # 验证AST
        validator = ASTSecurityValidator(self.config)
        if not validator.validate(tree):
            raise ASTValidationError(
                f"AST验证失败:\n" + "\n".join(validator.violations)
            )
        
        # 重写属性访问
        rewriter = AttributeRewriter(self.config)
        tree = rewriter.visit(tree)
        ast.fix_missing_locations(tree)
        
        # 注入Gas检查
        injector = GasInjector(self.config)
        tree = injector.visit(tree)
        ast.fix_missing_locations(tree)
        
        return tree
    
    def safe_execute(
        self, 
        code_str: str, 
        max_gas: Optional[int] = None,
        timeout: Optional[float] = None
    ) -> Dict[str, Any]:
        """
        安全执行不可信代码
        
        Args:
            code_str: 要执行的代码字符串
            max_gas: 最大Gas额度（可选，默认使用配置值）
            timeout: 执行超时时间（秒，可选）
        
        Returns:
            包含执行结果的字典
        
        Raises:
            GasLimitExceeded: Gas额度耗尽
            SandboxSecurityError: 安全违规
            ASTValidationError: AST验证失败
        """
        if max_gas is not None:
            self._gas_meter.reset(max_gas)
        else:
            self._gas_meter.reset(self.config.max_gas)
        
        # 解析AST
        try:
            tree = ast.parse(code_str, mode='exec', filename='<sandbox>')
        except SyntaxError as e:
            raise ASTValidationError(f"代码语法错误: {e}") from e
        
        # 转换AST
        tree = self._transform_ast(tree)
        
        # 编译代码
        try:
            code_obj = compile(tree, '<sandbox>', 'exec', dont_inherit=True)
        except Exception as e:
            raise ASTValidationError(f"代码编译失败: {e}") from e
        
        # 创建安全环境
        safe_globals = self._create_safe_globals()
        safe_locals: Dict[str, Any] = {}
        
        # 执行代码
        try:
            exec(code_obj, safe_globals, safe_locals)
            
            result = {
                'success': True,
                'locals': safe_locals,
                'remaining_gas': self._gas_meter.remaining_gas,
                'total_checks': self._gas_meter._check_count,
            }
            
            return result
            
        except GasLimitExceeded as e:
            raise e
        except SandboxSecurityError as e:
            raise e
        except RecursionError as e:
            raise SandboxSecurityError(f"递归深度超限: {e}") from e
        except MemoryError as e:
            raise SandboxSecurityError(f"内存不足: {e}") from e
        except Exception as e:
            raise SandboxSecurityError(
                f"执行期间发生未预期错误: {type(e).__name__}: {e}"
            ) from e


def safe_execute(
    code_str: str, 
    max_gas: int = 10000,
    config: Optional[SecurityConfig] = None
) -> Dict[str, Any]:
    """
    安全执行不可信代码的便捷函数
    
    Args:
        code_str: 要执行的代码字符串
        max_gas: 最大Gas额度
        config: 安全配置（可选）
    
    Returns:
        包含执行结果的字典
    """
    if config is None:
        config = SecurityConfig(max_gas=max_gas)
    else:
        config.max_gas = max_gas
    
    sandbox = SecureSandbox(config)
    return sandbox.safe_execute(code_str, max_gas)
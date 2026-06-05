"""
白名单配置 - 定义安全的AST节点、属性和模块
"""

from typing import Set
import types

# AST节点白名单 - 允许的安全节点类型
AST_WHITELIST: Set[str] = {
    # 模块和表达式
    'Module', 'Expr', 'Constant', 'Num', 'Str', 'Bytes', 'NameConstant',
    
    # 变量操作
    'Name', 'Load', 'Store', 'Del',
    
    # 运算符
    'BinOp', 'UnaryOp', 'BoolOp', 'Compare', 'IfExp',
    
    # 函数调用
    'Call', 'Starred', 'keyword',
    
    # 属性和索引
    'Attribute', 'Subscript', 'Slice', 'Index', 'ExtSlice',
    
    # 数据结构
    'List', 'Tuple', 'Dict', 'Set',
    
    # 推导式
    'ListComp', 'DictComp', 'SetComp', 'GeneratorExp',
    
    # Lambda和函数定义
    'Lambda', 'arguments', 'arg', 'comprehension',
    
    # 赋值语句
    'Assign', 'AnnAssign', 'AugAssign',
    
    # 控制流
    'If', 'For', 'While', 'Break', 'Continue', 'Pass',
    
    # 函数和类定义
    'Return', 'FunctionDef', 'ClassDef',
    
    # 其他语句
    'Assert', 'Delete', 'Global', 'Nonlocal',
    
    # 算术运算符
    'Add', 'Sub', 'Mult', 'Div', 'FloorDiv', 'Mod', 'Pow',
    'LShift', 'RShift', 'BitOr', 'BitXor', 'BitAnd',
    
    # 单目运算符
    'Invert', 'Not', 'UAdd', 'USub',
    
    # 比较运算符
    'Eq', 'NotEq', 'Lt', 'LtE', 'Gt', 'GtE', 'Is', 'IsNot', 'In', 'NotIn',
    
    # 逻辑运算符
    'And', 'Or',
    
    # 字符串格式化
    'FormattedValue', 'JoinedStr',
    
    # Import支持（通过白名单验证）
    'alias', 'Import', 'ImportFrom',
}

# AST节点黑名单 - 禁止的危险节点类型
AST_BLACKLIST: Set[str] = {
    # 异步操作
    'AsyncFunctionDef', 'AsyncFor', 'AsyncWith', 'Await',
    
    # 生成器
    'Yield', 'YieldFrom',
    
    # 异常处理（安全考虑）
    'With', 'Try', 'ExceptHandler', 'Raise',
    
    # 已废弃的节点
    'Exec', 'Print',
}

# 危险属性黑名单 - 禁止访问的反射链属性
DANGEROUS_ATTRIBUTES: Set[str] = {
    # 类和继承相关
    '__class__', '__bases__', '__base__', '__mro__', '__subclasses__',
    
    # 函数和代码对象
    '__globals__', '__code__', '__builtins__', '__import__',
    
    # 属性访问控制
    '__getattribute__', '__setattr__', '__delattr__',
    
    # 对象内部属性
    '__dict__', '__doc__', '__module__', '__init__', '__init_subclass__',
    '__new__', '__reduce__', '__reduce_ex__', '__getstate__', '__setstate__',
    '__slots__', '__weakref__',
    
    # 生成器和协程属性
    'gi_frame', 'gi_code', 'gi_yieldfrom', 'gi_running',
    
    # 代码对象属性
    'co_code', 'co_consts', 'co_names', 'co_varnames',
    
    # 函数属性
    'func_globals', 'func_code', 'func_closure', 'func_defaults',
    
    # 堆栈帧属性
    'f_globals', 'f_locals', 'f_code', 'f_builtins',
    
    # 协程属性
    'cr_code', 'cr_frame',
    
    # 方法属性
    '__self__', '__func__', '__closure__',
    
    # 名称属性
    '__name__', '__qualname__',
    
    # 异常属性
    'tb_frame', 'tb_next',
    '__traceback__', '__context__', '__cause__', '__suppress_context__',
    
    # 描述符协议
    '__call__', '__get__', '__set__', '__delete__',
    
    # 容器协议
    '__iter__', '__next__',
    '__enter__', '__exit__',
    '__len__', '__getitem__', '__setitem__', '__delitem__',
    '__contains__', '__bool__',
}

# 安全属性白名单 - 允许访问的普通属性和方法
SAFE_ATTRIBUTES: Set[str] = {
    # 列表方法
    'append', 'extend', 'insert', 'remove', 'pop', 'clear', 'copy',
    'index', 'count', 'sort', 'reverse',
    
    # 字典方法
    'keys', 'values', 'items', 'get', 'update', 'setdefault', 'popitem',
    
    # 字串方法
    'upper', 'lower', 'strip', 'lstrip', 'rstrip', 'split', 'rsplit',
    'join', 'replace', 'find', 'rfind', 'index', 'rindex',
    'format', 'encode', 'decode', 'startswith', 'endswith',
    'isdigit', 'isalpha', 'isalnum', 'isspace', 'islower', 'isupper',
    'capitalize', 'title', 'swapcase', 'center', 'ljust', 'rjust', 'zfill',
    
    # 数字属性
    'real', 'imag', 'numerator', 'denominator', 'conjugate',
    'bit_length', 'to_bytes', 'from_bytes',
    'hex', 'oct', 'bin',
    
    # Range属性
    'start', 'stop', 'step',
    
    # 运算符方法
    'add', 'sub', 'mul', 'truediv', 'floordiv', 'mod', 'pow',
    
    # 集合方法
    'union', 'intersection', 'difference', 'symmetric_difference',
    'isdisjoint', 'issubset', 'issuperset',
    
    # 文件方法（受限）
    'read', 'readline', 'readlines', 'write', 'writelines',
    'seek', 'tell', 'flush', 'close', 'fileno',
    'mode', 'name', 'closed',
    
    # 其他
    'is_integer',
}

# 安全的内置类型
SAFE_BUILTIN_TYPES: Set[type] = {
    int, float, str, bool, list, tuple, dict, set, frozenset,
    bytes, bytearray, complex,
    range, enumerate, zip, map, filter, reversed, slice,
    type(None),
}

# 默认允许导入的模块白名单
DEFAULT_ALLOWED_MODULES: Set[str] = {
    # 数学计算
    'math',
    
    # JSON处理
    'json',
    
    # 随机数（受限）
    'random',
    
    # 日期时间
    'datetime',
    
    # 正则表达式（受限）
    're',
    
    # 高级数据结构
    'collections',
    
    # 迭代器工具
    'itertools',
    
    # 函数工具
    'functools',
    
    # 操作符函数
    'operator',
    
    # 类型提示
    'typing',
    
    # 高精度数学
    'decimal',
    
    # 分数运算
    'fractions',
    
    # 统计函数
    'statistics',
    
    # 数组
    'array',
    
    # 复制工具
    'copy',
}


def get_default_ast_whitelist() -> Set[str]:
    """获取默认AST白名单"""
    return AST_WHITELIST.copy()


def get_default_ast_blacklist() -> Set[str]:
    """获取默认AST黑名单"""
    return AST_BLACKLIST.copy()


def get_default_dangerous_attributes() -> Set[str]:
    """获取默认危险属性黑名单"""
    return DANGEROUS_ATTRIBUTES.copy()


def get_default_safe_attributes() -> Set[str]:
    """获取默认安全属性白名单"""
    return SAFE_ATTRIBUTES.copy()


def get_default_allowed_modules() -> Set[str]:
    """获取默认允许导入的模块"""
    return DEFAULT_ALLOWED_MODULES.copy()
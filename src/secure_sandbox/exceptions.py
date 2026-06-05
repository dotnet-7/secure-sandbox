"""
异常类定义 - 沙箱专用异常
"""


class SandboxException(Exception):
    """沙箱异常基类"""
    pass


class GasLimitExceeded(SandboxException):
    """Gas额度耗尽异常 - 防止CPU DoS攻击"""
    
    def __init__(self, message: str):
        super().__init__(message)
        self.message = message
    
    def __str__(self) -> str:
        return f"[GasLimitExceeded] {self.message}"


class SandboxSecurityError(SandboxException):
    """沙箱安全违规异常"""
    
    def __init__(self, message: str):
        super().__init__(message)
        self.message = message
    
    def __str__(self) -> str:
        return f"[SandboxSecurityError] {self.message}"


class ASTValidationError(SandboxException):
    """AST验证失败异常"""
    
    def __init__(self, message: str):
        super().__init__(message)
        self.message = message
    
    def __str__(self) -> str:
        return f"[ASTValidationError] {self.message}"


class ExecutionTimeout(SandboxException):
    """执行超时异常"""
    
    def __init__(self, timeout: float):
        super().__init__(f"执行超时: {timeout}秒")
        self.timeout = timeout
    
    def __str__(self) -> str:
        return f"[ExecutionTimeout] 执行超时 {self.timeout}秒"
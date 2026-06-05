"""
安全拦截示例 - 演示核心攻击拦截机制
"""

from secure_sandbox import (
    safe_execute,
    GasLimitExceeded,
    SandboxSecurityError,
    ASTValidationError,
)

ATTACKS = [
    ("死循环攻击", GasLimitExceeded, "i = 0\nwhile True:\n    i += 1"),
    ("嵌套循环攻击", GasLimitExceeded, "for i in range(100):\n    for j in range(100):\n        pass"),
    ("反射链攻击", SandboxSecurityError, "result = [].__class__.__bases__"),
    ("函数globals攻击", SandboxSecurityError, "def f(): pass\nresult = f.__globals__"),
    ("Import os攻击", ASTValidationError, "import os\nos.system('whoami')"),
    ("eval攻击", ASTValidationError, "eval('__import__(\"os\")')"),
    ("exec攻击", ASTValidationError, "exec('import os')"),
    ("open攻击", ASTValidationError, "open('/etc/passwd')"),
    ("私有属性攻击", SandboxSecurityError, "class C:\n  _x=1\nC()._x"),
    ("__dict__攻击", SandboxSecurityError, "class C: pass\nC().__dict__"),
]

def main():
    print("Secure Sandbox - 安全拦截演示")
    print("=" * 60)
    
    passed = 0
    for name, expected_exc, code in ATTACKS:
        try:
            safe_execute(code, max_gas=100)
            print(f"❌ {name} 未拦截")
        except expected_exc:
            print(f"✅ {name} 成功拦截")
            passed += 1
        except Exception as e:
            print(f"⚠️  {name} 异常类型不符: {type(e).__name__}")
    
    print("\n" + "=" * 60)
    print(f"拦截率: {passed}/{len(ATTACKS)} ({passed/len(ATTACKS)*100:.1f}%)")
    
    if passed == len(ATTACKS):
        print("🎉 所有攻击成功拦截！")
    
    print("\n防御机制:")
    print("1. Gas机制 - 拦截死循环/递归攻击")
    print("2. AST验证 - 拦截import/eval/exec/open")
    print("3. 属性拦截 - 拦截__class__/__globals__/__dict__")

if __name__ == '__main__':
    main()
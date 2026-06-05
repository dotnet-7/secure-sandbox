"""
CLI工具 - 命令行接口
"""

import argparse
import sys
import json
from typing import Optional

from .core import SecureSandbox, SecurityConfig, safe_execute
from .exceptions import (
    GasLimitExceeded,
    SandboxSecurityError,
    ASTValidationError,
)


def main():
    """命令行主函数"""
    parser = argparse.ArgumentParser(
        description="Secure Sandbox - 安全执行Python代码",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  # 从文件执行代码
  secure-sandbox script.py --max-gas 1000
  
  # 从命令行执行代码
  secure-sandbox -c "print('Hello, World!')" --max-gas 50
  
  # 使用自定义配置
  secure-sandbox script.py --config config.json
  
  # 显示执行结果
  secure-sandbox script.py --verbose
        """
    )
    
    parser.add_argument(
        'file',
        nargs='?',
        help='要执行的Python脚本文件'
    )
    
    parser.add_argument(
        '-c', '--code',
        help='直接执行代码字符串'
    )
    
    parser.add_argument(
        '--max-gas',
        type=int,
        default=10000,
        help='最大Gas额度 (默认: 10000)'
    )
    
    parser.add_argument(
        '--allow-imports',
        action='store_true',
        default=True,
        help='允许导入模块 (默认: True)'
    )
    
    parser.add_argument(
        '--no-imports',
        action='store_true',
        help='禁止导入模块'
    )
    
    parser.add_argument(
        '--modules',
        nargs='+',
        help='允许导入的模块列表（覆盖默认白名单）'
    )
    
    parser.add_argument(
        '--config',
        help='配置文件路径 (JSON格式)'
    )
    
    parser.add_argument(
        '--verbose',
        action='store_true',
        help='显示详细执行信息'
    )
    
    parser.add_argument(
        '--output-json',
        action='store_true',
        help='以JSON格式输出结果'
    )
    
    parser.add_argument(
        '--version',
        action='version',
        version='Secure Sandbox v0.0.1'
    )
    
    args = parser.parse_args()
    
    # 获取代码
    code: Optional[str] = None
    if args.code:
        code = args.code
    elif args.file:
        try:
            with open(args.file, 'r', encoding='utf-8') as f:
                code = f.read()
        except FileNotFoundError:
            print(f"错误: 文件 '{args.file}' 不存在", file=sys.stderr)
            sys.exit(1)
        except Exception as e:
            print(f"错误: 无法读取文件 '{args.file}': {e}", file=sys.stderr)
            sys.exit(1)
    else:
        print("错误: 请提供要执行的代码（通过文件或-c参数）", file=sys.stderr)
        parser.print_help()
        sys.exit(1)
    
    # 创建配置
    config = SecurityConfig(max_gas=args.max_gas)
    
    # 加载配置文件
    if args.config:
        try:
            with open(args.config, 'r', encoding='utf-8') as f:
                config_data = json.load(f)
            
            # 更新配置
            for key, value in config_data.items():
                if hasattr(config, key):
                    setattr(config, key, value)
        except FileNotFoundError:
            print(f"错误: 配置文件 '{args.config}' 不存在", file=sys.stderr)
            sys.exit(1)
        except json.JSONDecodeError as e:
            print(f"错误: 配置文件格式错误: {e}", file=sys.stderr)
            sys.exit(1)
    
    # 处理import参数
    if args.no_imports:
        config.allow_imports = False
    
    if args.modules:
        config.allowed_modules = set(args.modules)
    
    # 执行代码
    sandbox = SecureSandbox(config)
    
    if not code:
        print("错误: 无法获取代码内容", file=sys.stderr)
        sys.exit(1)
    
    try:
        result = sandbox.safe_execute(code, max_gas=args.max_gas)
        
        if args.output_json:
            # JSON格式输出
            output = {
                'success': result['success'],
                'remaining_gas': result['remaining_gas'],
                'total_checks': result['total_checks'],
                'locals': {k: str(v) for k, v in result['locals'].items()},
            }
            print(json.dumps(output, indent=2))
        elif args.verbose:
            # 详细输出
            print("\n" + "="*60)
            print("执行成功")
            print("="*60)
            print(f"剩余Gas: {result['remaining_gas']}")
            print(f"总检查次数: {result['total_checks']}")
            print(f"局部变量: {list(result['locals'].keys())}")
            print("="*60)
        else:
            # 简洁输出
            print(f"✅ 执行成功 | 剩余Gas: {result['remaining_gas']}")
        
        sys.exit(0)
        
    except GasLimitExceeded as e:
        if args.output_json:
            output = {
                'success': False,
                'error': 'GasLimitExceeded',
                'message': str(e),
            }
            print(json.dumps(output, indent=2))
        else:
            print(f"❌ Gas额度耗尽: {e}", file=sys.stderr)
        sys.exit(2)
        
    except SandboxSecurityError as e:
        if args.output_json:
            output = {
                'success': False,
                'error': 'SandboxSecurityError',
                'message': str(e),
            }
            print(json.dumps(output, indent=2))
        else:
            print(f"❌ 安全违规: {e}", file=sys.stderr)
        sys.exit(3)
        
    except ASTValidationError as e:
        if args.output_json:
            output = {
                'success': False,
                'error': 'ASTValidationError',
                'message': str(e),
            }
            print(json.dumps(output, indent=2))
        else:
            print(f"❌ AST验证失败: {e}", file=sys.stderr)
        sys.exit(4)
        
    except Exception as e:
        if args.output_json:
            output = {
                'success': False,
                'error': type(e).__name__,
                'message': str(e),
            }
            print(json.dumps(output, indent=2))
        else:
            print(f"❌ 未预期错误: {type(e).__name__}: {e}", file=sys.stderr)
        sys.exit(5)


if __name__ == '__main__':
    main()
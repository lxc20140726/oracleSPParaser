#!/usr/bin/env python3
"""
Oracle SP Parser 一键部署安装脚本

支持多种部署模式：
- 开发环境部署
- 生产环境部署  
- 测试环境部署
- API服务部署

自动处理虚拟环境创建和依赖安装
"""

import os
import sys
import subprocess
import argparse
from pathlib import Path


def run_command(cmd, description="", capture_output=False):
    """运行命令并显示结果"""
    print(f"🚀 {description}")
    print(f"执行命令: {' '.join(cmd) if isinstance(cmd, list) else cmd}")
    print("-" * 50)
    
    try:
        if isinstance(cmd, str):
            result = subprocess.run(cmd, shell=True, check=True, capture_output=capture_output, text=True)
        else:
            result = subprocess.run(cmd, check=True, capture_output=capture_output, text=True)
        
        print(f"✅ {description} 成功完成")
        
        if capture_output and result.stdout:
            print("输出:")
            print(result.stdout)
            
        return True, result
        
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} 失败: {e}")
        if capture_output and e.stdout:
            print("输出:")
            print(e.stdout)
        if capture_output and e.stderr:
            print("错误:")
            print(e.stderr)
        return False, e
    except Exception as e:
        print(f"⚠️ {description} 出现错误: {e}")
        return False, e
    
    finally:
        print("=" * 50)


def check_python_version():
    """检查Python版本"""
    major, minor = sys.version_info[:2]
    
    if major < 3 or (major == 3 and minor < 8):
        print("❌ Python版本过低！")
        print(f"当前版本: Python {major}.{minor}")
        print("最低要求: Python 3.8+")
        print("\n请升级Python版本后重试。")
        return False
    
    print(f"✅ Python版本检查通过: Python {major}.{minor}")
    return True


def check_pip():
    """检查pip是否可用"""
    try:
        subprocess.run([sys.executable, "-m", "pip", "--version"], 
                      check=True, capture_output=True)
        print("✅ pip检查通过")
        return True
    except subprocess.CalledProcessError:
        print("❌ pip不可用，请安装pip")
        return False


def create_virtual_environment(venv_path="venv"):
    """创建虚拟环境"""
    venv_dir = Path(venv_path)
    
    if venv_dir.exists():
        print(f"✅ 虚拟环境已存在: {venv_path}")
        return True, venv_path
    
    success, _ = run_command(
        [sys.executable, "-m", "venv", venv_path],
        f"创建虚拟环境: {venv_path}"
    )
    
    return success, venv_path


def get_venv_python(venv_path):
    """获取虚拟环境中的Python路径"""
    if os.name == "nt":  # Windows
        return str(Path(venv_path) / "Scripts" / "python.exe")
    else:  # Unix/Linux/macOS
        return str(Path(venv_path) / "bin" / "python")


def get_venv_pip(venv_path):
    """获取虚拟环境中的pip路径"""
    python_path = get_venv_python(venv_path)
    return [python_path, "-m", "pip"]


def upgrade_pip_in_venv(venv_path):
    """在虚拟环境中升级pip"""
    pip_cmd = get_venv_pip(venv_path)
    success, _ = run_command(
        pip_cmd + ["install", "--upgrade", "pip", "setuptools", "wheel"],
        "升级虚拟环境中的pip和构建工具"
    )
    return success


def install_package_in_venv(venv_path, mode="dev"):
    """在虚拟环境中安装包和依赖"""
    pip_cmd = get_venv_pip(venv_path)
    
    if mode == "dev":
        # 开发模式：可编辑安装 + 所有依赖
        install_cmd = pip_cmd + [
            "install", "-e", ".[dev,test,docs,api]",
            "--no-cache-dir"
        ]
        description = "安装开发环境 (包含所有依赖)"
        
    elif mode == "prod":
        # 生产模式：核心功能 + API
        install_cmd = pip_cmd + [
            "install", ".[prod]",
            "--no-cache-dir"
        ]
        description = "安装生产环境 (核心功能 + API)"
        
    elif mode == "test":
        # 测试模式：测试依赖
        install_cmd = pip_cmd + [
            "install", "-e", ".[test]",
            "--no-cache-dir" 
        ]
        description = "安装测试环境"
        
    elif mode == "api":
        # API模式：仅API服务
        install_cmd = pip_cmd + [
            "install", ".[api]",
            "--no-cache-dir"
        ]
        description = "安装API服务环境"
        
    elif mode == "minimal":
        # 最小安装：仅核心功能
        install_cmd = pip_cmd + [
            "install", ".",
            "--no-cache-dir"
        ]
        description = "最小安装 (仅核心功能)"
        
    else:
        print(f"❌ 未知的安装模式: {mode}")
        return False
    
    success, _ = run_command(install_cmd, description)
    return success


def verify_installation_in_venv(venv_path):
    """在虚拟环境中验证安装结果"""
    print("🔍 验证安装结果...")
    
    python_cmd = get_venv_python(venv_path)
    
    # 检查包是否正确安装
    try:
        success, result = run_command(
            [python_cmd, "-c", "import oracle_sp_parser; print(f'Version: {oracle_sp_parser.__version__}')"],
            "检查oracle_sp_parser包",
            capture_output=True
        )
        
        if success:
            print("✅ oracle_sp_parser 包安装成功")
        else:
            print("❌ oracle_sp_parser 包导入失败")
            return False
            
    except Exception as e:
        print(f"❌ 包验证失败: {e}")
        return False
    
    return True


def create_activation_script(venv_path):
    """创建虚拟环境激活脚本"""
    print("🔗 创建虚拟环境激活脚本...")
    
    # 获取激活脚本路径
    if os.name == "nt":  # Windows
        activate_script = Path(venv_path) / "Scripts" / "activate.bat"
        activate_cmd = f"call {activate_script}"
    else:  # Unix/Linux/macOS
        activate_script = Path(venv_path) / "bin" / "activate"
        activate_cmd = f"source {activate_script}"
    
    # 创建快捷脚本
    scripts = {
        "activate_env.sh": f'''#!/bin/bash
# 激活Oracle SP Parser虚拟环境
{activate_cmd}
echo "✅ Oracle SP Parser 虚拟环境已激活"
echo "📖 使用方法:"
echo "  - oracle-sp-parser --help"
echo "  - oracle-sp-backend"
echo "  - oracle-sp-test --smoke"
exec "$SHELL"
''',
        "start_backend_venv.py": f'''#!/usr/bin/env python3
"""在虚拟环境中启动Oracle SP Parser后端服务"""
import subprocess
import sys
from pathlib import Path

venv_python = "{get_venv_python(venv_path)}"

if __name__ == "__main__":
    try:
        subprocess.run([venv_python, "-m", "uvicorn", "backend.main:app", 
                       "--host", "0.0.0.0", "--port", "8000", "--reload"])
    except KeyboardInterrupt:
        print("\\n服务已停止")
    except ImportError:
        print("请先激活虚拟环境并安装API依赖")
''',
        "run_tests_venv.py": f'''#!/usr/bin/env python3
"""在虚拟环境中运行测试"""
import subprocess
import sys

venv_python = "{get_venv_python(venv_path)}"

if __name__ == "__main__":
    subprocess.run([venv_python, "run_tests.py"] + sys.argv[1:])
'''
    }
    
    for script_name, content in scripts.items():
        script_path = Path(script_name)
        with open(script_path, "w", encoding="utf-8") as f:
            f.write(content)
        
        # 设置可执行权限 (Unix系统)
        if os.name != "nt":
            os.chmod(script_path, 0o755)
        
        print(f"  ✅ 创建脚本: {script_name}")


def show_usage_info(venv_path, mode):
    """显示使用说明"""
    print("\n" + "=" * 60)
    print("🎉 Oracle SP Parser 安装完成！")
    print("=" * 60)
    
    # 获取激活命令
    if os.name == "nt":  # Windows
        activate_cmd = f"call {venv_path}\\Scripts\\activate"
    else:  # Unix/Linux/macOS
        activate_cmd = f"source {venv_path}/bin/activate"
    
    print(f"\n🌟 虚拟环境路径: {venv_path}")
    print(f"📁 当前安装模式: {mode}")
    
    print(f"\n🔧 激活虚拟环境:")
    print(f"  {activate_cmd}")
    print("  # 或者运行：bash activate_env.sh")
    
    print("\n📖 使用方法 (需要先激活虚拟环境):")
    print("  1. 命令行分析:")
    print("     oracle-sp-parser input.sql")
    
    print("\n  2. 启动Web服务:")
    print("     oracle-sp-backend")
    print("     # 或者运行：python3 start_backend_venv.py")
    
    print("\n  3. 运行测试:")
    print("     oracle-sp-test --smoke")
    print("     # 或者运行：python3 run_tests_venv.py --smoke")
    
    print("\n  4. Python模块使用:")
    print("     python3 -c \"import oracle_sp_parser; oracle_sp_parser.info()\"")
    
    print("\n🌐 Web界面:")
    print("  启动后端服务后访问: http://localhost:8000")
    
    print("\n📚 文档和报告:")
    print("  - 测试报告: docs/test_reports/report.html")
    print("  - 覆盖率报告: docs/coverage/index.html")
    
    print("\n🔧 开发工具 (开发模式):")
    if mode == "dev":
        print("  - 代码格式化: black src/ backend/ tests/")
        print("  - 代码检查: flake8 src/ backend/ tests/")
        print("  - 运行测试: python3 run_tests.py")
    
    print(f"\n💡 提示:")
    print(f"  - 每次使用前需要激活虚拟环境: {activate_cmd}")
    print(f"  - 或者使用提供的快捷脚本 (已设置正确的环境)")
    
    print("\n" + "=" * 60)


def main():
    """主函数"""
    parser = argparse.ArgumentParser(
        description="Oracle SP Parser 一键部署安装脚本"
    )
    
    parser.add_argument(
        "--mode", 
        choices=["dev", "prod", "test", "api", "minimal"],
        default="dev",
        help="安装模式 (默认: dev)"
    )
    
    parser.add_argument(
        "--venv",
        default="venv",
        help="虚拟环境目录名 (默认: venv)"
    )
    
    parser.add_argument(
        "--skip-venv",
        action="store_true",
        help="跳过虚拟环境创建，使用当前Python环境"
    )
    
    parser.add_argument(
        "--skip-pip-upgrade",
        action="store_true",
        help="跳过pip升级"
    )
    
    parser.add_argument(
        "--skip-verification",
        action="store_true", 
        help="跳过安装验证"
    )
    
    parser.add_argument(
        "--create-scripts",
        action="store_true",
        help="创建激活脚本和快捷启动脚本"
    )
    
    args = parser.parse_args()
    
    print("🚀 Oracle SP Parser 一键部署安装")
    print("=" * 50)
    
    # 系统检查
    if not check_python_version():
        sys.exit(1)
    
    if not check_pip():
        sys.exit(1)
    
    # 虚拟环境处理
    venv_path = None
    if not args.skip_venv:
        print(f"\n📦 设置虚拟环境 (目录: {args.venv})")
        success, venv_path = create_virtual_environment(args.venv)
        if not success:
            print("❌ 虚拟环境创建失败！")
            sys.exit(1)
            
        # 升级虚拟环境中的pip
        if not args.skip_pip_upgrade:
            if not upgrade_pip_in_venv(venv_path):
                print("⚠️ pip升级失败，继续安装...")
        
        # 在虚拟环境中安装包
        print(f"\n📦 在虚拟环境中安装 (模式: {args.mode})")
        if not install_package_in_venv(venv_path, args.mode):
            print("❌ 安装失败！")
            sys.exit(1)
        
        # 在虚拟环境中验证安装
        if not args.skip_verification:
            if not verify_installation_in_venv(venv_path):
                print("⚠️ 安装验证未完全通过，但基本功能可能可用")
        
    else:
        # 不使用虚拟环境，直接安装到当前环境
        print(f"\n📦 在当前环境中安装 (模式: {args.mode})")
        print("⚠️ 注意：在macOS上可能需要使用 --break-system-packages 或虚拟环境")
        
        # 这里可以添加直接安装的逻辑
        # 但建议使用虚拟环境
    
    # 创建激活脚本
    if args.create_scripts and venv_path:
        create_activation_script(venv_path)
    
    # 显示使用说明
    show_usage_info(venv_path or "当前环境", args.mode)
    
    print("✨ 安装完成！享受使用 Oracle SP Parser 吧！")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n⚠️ 安装被用户中断")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ 安装过程中出现错误: {e}")
        sys.exit(1) 
#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys
import subprocess
import threading
import time
import webbrowser
import venv
from pathlib import Path

def check_python_version():
    """检查Python版本"""
    if sys.version_info < (3, 8):
        print("❌ 错误: 需要Python 3.8或更高版本")
        sys.exit(1)
    print(f"✅ Python版本: {sys.version}")

def create_virtual_environment():
    """创建虚拟环境"""
    venv_path = Path("venv")
    
    if venv_path.exists():
        print("✅ 虚拟环境已存在")
        return venv_path
    
    print("📦 创建虚拟环境...")
    try:
        venv.create(venv_path, with_pip=True)
        print("✅ 虚拟环境创建成功")
        return venv_path
    except Exception as e:
        print(f"❌ 虚拟环境创建失败: {e}")
        return None

def get_venv_python(venv_path):
    """获取虚拟环境中的Python解释器路径"""
    if sys.platform == "win32":
        return venv_path / "Scripts" / "python.exe"
    else:
        return venv_path / "bin" / "python"

def get_venv_pip(venv_path):
    """获取虚拟环境中的pip路径"""
    if sys.platform == "win32":
        return venv_path / "Scripts" / "pip"
    else:
        return venv_path / "bin" / "pip"

def install_backend_dependencies():
    """安装后端依赖"""
    print("📦 安装后端依赖...")
    
    # 创建虚拟环境
    venv_path = create_virtual_environment()
    if not venv_path:
        return False
    
    # 获取虚拟环境中的pip
    pip_path = get_venv_pip(venv_path)
    
    try:
        # 升级pip
        subprocess.run([str(pip_path), "install", "--upgrade", "pip"], check=True)
        
        # 安装依赖
        subprocess.run([str(pip_path), "install", "-r", "requirements.txt"], check=True)
        print("✅ 后端依赖安装完成")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ 后端依赖安装失败: {e}")
        
        # 尝试使用 --break-system-packages 作为备选方案
        print("⚠️  尝试使用备选安装方法...")
        try:
            subprocess.run([
                sys.executable, "-m", "pip", "install", 
                "--break-system-packages", "--user", 
                "-r", "requirements.txt"
            ], check=True)
            print("✅ 后端依赖安装完成 (使用备选方法)")
            return True
        except subprocess.CalledProcessError as e2:
            print(f"❌ 备选安装方法也失败: {e2}")
            return False

def install_frontend_dependencies():
    """安装前端依赖"""
    print("📦 安装前端依赖...")
    frontend_dir = Path("frontend")
    
    if not frontend_dir.exists():
        print("❌ 前端目录不存在")
        return False
    
    try:
        # 检查npm是否可用
        subprocess.run(["npm", "--version"], check=True, capture_output=True)
        
        # 安装依赖
        subprocess.run(["npm", "install"], cwd=frontend_dir, check=True)
        print("✅ 前端依赖安装完成")
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("⚠️  npm不可用，尝试使用yarn...")
        try:
            subprocess.run(["yarn", "--version"], check=True, capture_output=True)
            subprocess.run(["yarn", "install"], cwd=frontend_dir, check=True)
            print("✅ 前端依赖安装完成 (使用yarn)")
            return True
        except (subprocess.CalledProcessError, FileNotFoundError):
            print("❌ npm和yarn都不可用，请先安装Node.js")
            return False

def build_frontend():
    """构建前端"""
    print("🔨 构建前端...")
    frontend_dir = Path("frontend")
    
    try:
        # 尝试使用npm
        try:
            subprocess.run(["npm", "run", "build"], cwd=frontend_dir, check=True)
        except FileNotFoundError:
            # 如果npm不可用，尝试yarn
            subprocess.run(["yarn", "build"], cwd=frontend_dir, check=True)
        
        print("✅ 前端构建完成")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ 前端构建失败: {e}")
        return False

def start_backend():
    """启动后端服务"""
    print("🚀 启动后端服务...")
    backend_dir = Path("backend")
    
    try:
        # 确保后端目录存在
        if not backend_dir.exists():
            print("❌ 后端目录不存在")
            return None
        
        # 检查虚拟环境
        venv_path = Path("venv")
        if venv_path.exists():
            # 使用虚拟环境中的Python - 使用绝对路径
            python_path = venv_path.absolute() / "bin" / "python"
            if not python_path.exists():
                # Windows路径
                python_path = venv_path.absolute() / "Scripts" / "python.exe"
            if not python_path.exists():
                print("⚠️  虚拟环境Python不存在，使用系统Python")
                python_path = sys.executable
        else:
            # 使用系统Python
            python_path = sys.executable
            
        # 启动FastAPI服务
        process = subprocess.Popen([
            str(python_path), "-m", "uvicorn", 
            "main:app", 
            "--host", "0.0.0.0", 
            "--port", "8000", 
            "--reload"
        ], cwd=backend_dir)
        
        print("✅ 后端服务已启动 (端口: 8000)")
        return process
    except Exception as e:
        print(f"❌ 后端服务启动失败: {e}")
        return None

def wait_for_server(url="http://localhost:8000", timeout=30):
    """等待服务器启动"""
    print(f"⏳ 等待服务器启动...")
    start_time = time.time()
    
    while time.time() - start_time < timeout:
        try:
            # 尝试导入requests，如果不存在则跳过健康检查
            try:
                import requests
                response = requests.get(f"{url}/api/health", timeout=2)
                if response.status_code == 200:
                    print("✅ 服务器已就绪")
                    return True
            except ImportError:
                # 如果requests不可用，简单等待几秒钟
                if time.time() - start_time > 5:
                    print("✅ 服务器应该已就绪 (无法验证)")
                    return True
        except:
            pass
        time.sleep(1)
    
    print("❌ 服务器启动超时")
    return False

def open_browser():
    """打开浏览器"""
    url = "http://localhost:8000"
    print(f"🌐 打开浏览器: {url}")
    try:
        webbrowser.open(url)
    except Exception as e:
        print(f"❌ 无法自动打开浏览器: {e}")
        print(f"请手动访问: {url}")

def setup_environment():
    """环境设置说明"""
    print("🔧 环境设置建议:")
    print("   如果遇到权限问题，您可以:")
    print("   1. 使用虚拟环境 (推荐，自动处理)")
    print("   2. 手动创建虚拟环境:")
    print("      python3 -m venv venv")
    print("      source venv/bin/activate  # Linux/Mac")
    print("      venv\\Scripts\\activate     # Windows")
    print("      pip install -r requirements.txt")

def main():
    """主函数"""
    print("🔍 Oracle存储过程分析工具 - Web版本启动器")
    print("=" * 50)
    
    # 检查Python版本
    check_python_version()
    
    # 显示环境设置建议
    setup_environment()
    print()
    
    # 安装依赖
    if not install_backend_dependencies():
        print("\n❌ 后端依赖安装失败")
        print("💡 解决方案:")
        print("   1. 手动创建虚拟环境:")
        print("      python3 -m venv venv")
        print("      source venv/bin/activate")
        print("      pip install -r requirements.txt")
        print("   2. 或者使用以下命令强制安装:")
        print("      pip install --break-system-packages --user -r requirements.txt")
        sys.exit(1)
    
    # 安装前端依赖 - 允许失败
    frontend_deps_ok = install_frontend_dependencies()
    if not frontend_deps_ok:
        print("⚠️  跳过前端依赖安装")
    
    # 构建前端 - 允许失败
    frontend_build_ok = False
    if frontend_deps_ok:
        frontend_build_ok = build_frontend()
        if not frontend_build_ok:
            print("⚠️  前端构建失败，将使用开发模式运行")
    
    # 启动后端
    backend_process = start_backend()
    if not backend_process:
        sys.exit(1)
    
    try:
        # 等待服务器启动
        if wait_for_server():
            # 打开浏览器
            open_browser()
            
            print("\n" + "=" * 50)
            print("🎉 应用已成功启动!")
            print("📍 访问地址: http://localhost:8000")
            print("📚 API文档: http://localhost:8000/api/docs")
            if not frontend_build_ok:
                print("⚠️  前端使用开发模式运行")
            print("💡 按 Ctrl+C 停止服务")
            print("=" * 50)
            
            # 保持运行
            backend_process.wait()
        else:
            print("❌ 服务器启动失败")
            backend_process.terminate()
            sys.exit(1)
            
    except KeyboardInterrupt:
        print("\n⏹️  正在停止服务...")
        backend_process.terminate()
        backend_process.wait()
        print("✅ 服务已停止")

if __name__ == "__main__":
    main() 
#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys
import subprocess
import venv
from pathlib import Path

def create_virtual_environment():
    """创建和设置虚拟环境"""
    venv_path = Path("venv")
    
    print("🔍 Oracle存储过程分析工具 - 环境设置")
    print("=" * 50)
    
    if venv_path.exists():
        print("✅ 虚拟环境已存在")
    else:
        print("📦 创建虚拟环境...")
        try:
            venv.create(venv_path, with_pip=True)
            print("✅ 虚拟环境创建成功")
        except Exception as e:
            print(f"❌ 虚拟环境创建失败: {e}")
            return False
    
    # 获取虚拟环境中的pip路径
    if sys.platform == "win32":
        pip_path = venv_path / "Scripts" / "pip"
        activate_script = venv_path / "Scripts" / "activate.bat"
    else:
        pip_path = venv_path / "bin" / "pip"
        activate_script = venv_path / "bin" / "activate"
    
    print("📦 安装Python依赖...")
    try:
        # 升级pip
        subprocess.run([str(pip_path), "install", "--upgrade", "pip"], check=True)
        
        # 安装依赖
        subprocess.run([str(pip_path), "install", "-r", "requirements.txt"], check=True)
        print("✅ Python依赖安装完成")
    except subprocess.CalledProcessError as e:
        print(f"❌ 依赖安装失败: {e}")
        return False
    
    print("\n" + "=" * 50)
    print("🎉 环境设置完成!")
    print("\n📋 后续操作:")
    
    if sys.platform == "win32":
        print("1. 激活虚拟环境:")
        print("   venv\\Scripts\\activate")
        print("\n2. 启动后端服务:")
        print("   cd backend")
        print("   python main.py")
    else:
        print("1. 激活虚拟环境:")
        print("   source venv/bin/activate")
        print("\n2. 启动后端服务:")
        print("   cd backend")
        print("   python main.py")
    
    print("\n3. 访问应用:")
    print("   http://localhost:8000")
    
    print("\n💡 或者直接运行:")
    print("   python start_web.py")
    
    return True

if __name__ == "__main__":
    create_virtual_environment() 
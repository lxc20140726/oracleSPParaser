#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
简化的后端启动脚本
"""

import sys
import os
import subprocess
from pathlib import Path

def get_venv_python():
    """获取虚拟环境中的Python路径"""
    project_root = Path(__file__).parent
    venv_path = project_root / "venv"
    
    if venv_path.exists():
        # macOS/Linux
        python_path = venv_path / "bin" / "python"
        if python_path.exists():
            return python_path
        
        # Windows
        python_path = venv_path / "Scripts" / "python.exe"
        if python_path.exists():
            return python_path
    
    # 如果没有虚拟环境，返回系统Python
    return sys.executable

def main():
    print("🚀 启动Oracle SP Parser后端服务...")
    
    # 设置路径
    project_root = Path(__file__).parent
    src_path = project_root / "src"
    backend_path = project_root / "backend"
    
    print(f"📁 项目根目录: {project_root}")
    print(f"📁 源码目录: {src_path}")
    print(f"📁 后端目录: {backend_path}")
    
    # 获取正确的Python解释器
    python_path = get_venv_python()
    print(f"🐍 使用Python: {python_path}")
    
    # 检查虚拟环境
    if "venv" in str(python_path):
        print("✅ 使用虚拟环境")
    else:
        print("⚠️  使用系统Python，建议激活虚拟环境")
        print("💡 激活虚拟环境: source venv/bin/activate (Linux/Mac) 或 venv\\Scripts\\activate (Windows)")
    
    try:
        # 首先测试是否能导入必要的模块
        print("🔍 检查依赖...")
        result = subprocess.run([
            str(python_path), "-c", 
            "import uvicorn, fastapi; print('依赖检查通过')"
        ], capture_output=True, text=True, cwd=project_root)
        
        if result.returncode != 0:
            print(f"❌ 依赖检查失败: {result.stderr}")
            print("请运行: pip install -r requirements.txt")
            return False
        
        print("✅ 依赖检查通过")
        
        # 启动服务器
        print("🌐 启动服务器在 http://localhost:8000")
        print("📚 API文档: http://localhost:8000/api/docs")
        print("💡 按 Ctrl+C 停止服务")
        print("-" * 50)
        
        # 使用subprocess启动，这样可以保持环境一致性
        subprocess.run([
            str(python_path), "-m", "uvicorn",
            "main:app",
            "--host", "0.0.0.0",
            "--port", "8000",
            "--reload"
        ], cwd=backend_path)
        
    except KeyboardInterrupt:
        print("\n🛑 服务已停止")
    except Exception as e:
        print(f"❌ 启动错误: {e}")
        return False

if __name__ == "__main__":
    main() 
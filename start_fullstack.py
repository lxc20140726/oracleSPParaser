#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
全栈启动脚本 - 同时启动前端和后端服务
"""

import sys
import os
import subprocess
import time
import signal
import threading
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

def start_backend():
    """启动后端服务"""
    print("🚀 启动后端服务...")
    
    project_root = Path(__file__).parent
    backend_path = project_root / "backend"
    python_path = get_venv_python()
    
    # 启动后端
    process = subprocess.Popen([
        str(python_path), "-m", "uvicorn",
        "main:app",
        "--host", "0.0.0.0",
        "--port", "8000",
        "--reload"
    ], cwd=backend_path)
    
    return process

def start_frontend():
    """启动前端服务"""
    print("🌐 启动前端服务...")
    
    project_root = Path(__file__).parent
    frontend_path = project_root / "frontend"
    
    # 启动前端
    process = subprocess.Popen([
        "npm", "start"
    ], cwd=frontend_path)
    
    return process

def wait_for_service(url, service_name, timeout=30):
    """等待服务启动"""
    print(f"⏳ 等待{service_name}启动...")
    
    for i in range(timeout):
        try:
            import requests
            response = requests.get(url, timeout=2)
            if response.status_code == 200:
                print(f"✅ {service_name}已就绪")
                return True
        except:
            pass
        time.sleep(1)
    
    print(f"❌ {service_name}启动超时")
    return False

def main():
    print("🎯 Oracle SP Parser 全栈启动")
    print("=" * 50)
    
    # 存储进程引用
    backend_process = None
    frontend_process = None
    
    def signal_handler(signum, frame):
        print("\n🛑 正在停止服务...")
        if backend_process:
            backend_process.terminate()
        if frontend_process:
            frontend_process.terminate()
        print("✅ 服务已停止")
        sys.exit(0)
    
    # 注册信号处理器
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    try:
        # 启动后端
        backend_process = start_backend()
        time.sleep(3)  # 给后端一些启动时间
        
        # 检查后端是否启动成功
        if wait_for_service("http://localhost:8000/api/health", "后端服务"):
            print("✅ 后端服务启动成功")
        else:
            print("❌ 后端服务启动失败")
            return False
        
        # 启动前端
        frontend_process = start_frontend()
        time.sleep(5)  # 给前端一些启动时间
        
        # 检查前端是否启动成功
        if wait_for_service("http://localhost:3000", "前端服务"):
            print("✅ 前端服务启动成功")
        else:
            print("❌ 前端服务启动失败")
            return False
        
        print("\n🎉 全栈服务启动成功!")
        print("=" * 50)
        print("📍 访问地址:")
        print("   🌐 前端界面: http://localhost:3000")
        print("   📡 后端API: http://localhost:8000")
        print("   📚 API文档: http://localhost:8000/api/docs")
        print("   ❤️  健康检查: http://localhost:8000/api/health")
        print("=" * 50)
        print("💡 按 Ctrl+C 停止所有服务")
        
        # 保持运行
        while True:
            time.sleep(1)
            
            # 检查进程是否还在运行
            if backend_process.poll() is not None:
                print("❌ 后端进程意外退出")
                break
            if frontend_process.poll() is not None:
                print("❌ 前端进程意外退出")
                break
    
    except KeyboardInterrupt:
        print("\n🛑 收到停止信号...")
    except Exception as e:
        print(f"❌ 启动过程中发生错误: {e}")
    finally:
        # 清理进程
        if backend_process:
            backend_process.terminate()
        if frontend_process:
            frontend_process.terminate()
        print("✅ 所有服务已停止")

if __name__ == "__main__":
    main() 
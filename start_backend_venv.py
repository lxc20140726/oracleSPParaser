#!/usr/bin/env python3
"""在虚拟环境中启动Oracle SP Parser后端服务"""
import subprocess
import sys
from pathlib import Path

venv_python = "venv/bin/python"

if __name__ == "__main__":
    try:
        subprocess.run([venv_python, "-m", "uvicorn", "backend.main:app", 
                       "--host", "0.0.0.0", "--port", "8000", "--reload"])
    except KeyboardInterrupt:
        print("\n服务已停止")
    except ImportError:
        print("请先激活虚拟环境并安装API依赖")

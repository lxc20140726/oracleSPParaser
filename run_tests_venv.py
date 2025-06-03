#!/usr/bin/env python3
"""在虚拟环境中运行测试"""
import subprocess
import sys

venv_python = "venv/bin/python"

if __name__ == "__main__":
    subprocess.run([venv_python, "run_tests.py"] + sys.argv[1:])

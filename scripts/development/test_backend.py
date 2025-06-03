#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试后端导入是否正常工作
"""

import sys
from pathlib import Path

def test_imports():
    print("🧪 测试Oracle SP Parser后端导入...")
    
    # 设置路径
    project_root = Path(__file__).parent
    src_path = project_root / "src"
    backend_path = project_root / "backend"
    
    print(f"📁 项目根目录: {project_root}")
    print(f"📁 源码目录: {src_path}")
    print(f"📁 后端目录: {backend_path}")
    
    # 添加路径
    sys.path.insert(0, str(src_path))
    sys.path.insert(0, str(backend_path))
    
    try:
        print("1️⃣ 测试基础依赖导入...")
        import fastapi
        import uvicorn
        print("   ✅ FastAPI和Uvicorn导入成功")
        
        print("2️⃣ 测试src模块导入...")
        # 使用动态导入避免命名冲突
        import importlib.util
        spec = importlib.util.spec_from_file_location("src_main", src_path / "main.py")
        src_main = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(src_main)
        OracleSPAnalyzer = src_main.OracleSPAnalyzer
        print("   ✅ OracleSPAnalyzer导入成功")
        
        print("3️⃣ 测试分析器实例化...")
        analyzer = OracleSPAnalyzer()
        print("   ✅ OracleSPAnalyzer实例化成功")
        
        print("4️⃣ 测试backend主模块...")
        # 切换到backend目录
        import os
        old_cwd = os.getcwd()
        os.chdir(backend_path)
        
        # 导入backend main模块
        spec = importlib.util.spec_from_file_location("backend_main", backend_path / "main.py")
        backend_main = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(backend_main)
        app = backend_main.app
        print("   ✅ Backend FastAPI应用导入成功")
        
        # 恢复工作目录
        os.chdir(old_cwd)
        
        print("🎉 所有导入测试通过!")
        return True
        
    except Exception as e:
        print(f"❌ 导入测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_imports()
    sys.exit(0 if success else 1) 
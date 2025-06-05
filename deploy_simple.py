#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Oracle SP Parser - 简化部署工具
创建最小化的部署包，适用于有Python环境的Windows主机
"""

import os
import sys
import shutil
import subprocess
import json
from pathlib import Path
from datetime import datetime

def create_simple_package():
    """创建简化的部署包"""
    project_root = Path(__file__).parent
    package_name = f"oracle-sp-parser-simple-{datetime.now().strftime('%Y%m%d-%H%M%S')}"
    package_dir = project_root / "dist" / package_name
    
    print(f"🚀 创建简化部署包: {package_name}")
    print("=" * 50)
    
    # 清理并创建目录
    print("🧹 准备目录...")
    if package_dir.exists():
        shutil.rmtree(package_dir)
    package_dir.mkdir(parents=True, exist_ok=True)
    
    # 复制核心文件
    print("📁 复制项目文件...")
    
    # 复制Python代码
    for src_dir in ["src", "backend"]:
        src_path = project_root / src_dir
        dst_path = package_dir / src_dir
        if src_path.exists():
            # 如果目标目录已存在，先删除再复制
            if dst_path.exists():
                print(f"  ⚠️ 目录 {src_dir} 已存在，先清理...")
                shutil.rmtree(dst_path)
            
            shutil.copytree(src_path, dst_path, 
                          ignore=shutil.ignore_patterns('__pycache__', '*.pyc', '.DS_Store'))
            print(f"  ✅ 已复制 {src_dir}/")
    
    # 复制前端构建文件（如果存在）
    print("🌐 处理前端文件...")
    frontend_build = project_root / "frontend" / "build"
    if frontend_build.exists():
        # 确保backend目录已经存在
        backend_dir = package_dir / "backend"
        if not backend_dir.exists():
            print("  ⚠️ backend目录不存在，先创建...")
            backend_dir.mkdir(parents=True, exist_ok=True)
        
        # 复制到backend目录下的static文件夹
        backend_static = backend_dir / "static"
        if backend_static.exists():
            print("  🧹 清理已存在的backend/static目录...")
            shutil.rmtree(backend_static)
        
        shutil.copytree(frontend_build, backend_static)
        print("  ✅ 已复制前端文件到backend/static")
        
        # 同时复制到根目录的static文件夹（备用）
        root_static = package_dir / "static"
        if root_static.exists():
            print("  🧹 清理已存在的根目录static...")
            shutil.rmtree(root_static)
        shutil.copytree(frontend_build, root_static)
        print("  ✅ 已复制前端文件到根目录static")
        
        # 验证关键文件是否存在
        key_files = ["index.html", "static/js", "static/css"]
        missing_files = []
        for key_file in key_files:
            if not (backend_static / key_file).exists():
                missing_files.append(key_file)
        
        if missing_files:
            print(f"  ⚠️ 缺少关键前端文件: {missing_files}")
        else:
            print("  ✅ 前端文件完整性检查通过")
            
    else:
        print("  ⚠️ 前端构建文件不存在，请先构建前端:")
        print("     cd frontend && npm install && npm run build")
        print("  📝 创建占位符静态目录...")
        
        # 创建占位符静态目录和基本HTML
        backend_static = package_dir / "backend" / "static"
        backend_static.mkdir(parents=True, exist_ok=True)
        
        # 创建简单的index.html作为后备
        fallback_html = '''<!DOCTYPE html>
<html>
<head>
    <title>Oracle SP Parser</title>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <style>
        body { font-family: Arial, sans-serif; margin: 40px; }
        .container { max-width: 800px; margin: 0 auto; }
        .warning { background: #fff3cd; border: 1px solid #ffeaa7; padding: 20px; border-radius: 5px; }
    </style>
</head>
<body>
    <div class="container">
        <h1>Oracle存储过程分析工具</h1>
        <div class="warning">
            <h3>前端界面未构建</h3>
            <p>请先构建前端界面，然后重新部署：</p>
            <pre>cd frontend<br>npm install<br>npm run build</pre>
        </div>
        <h3>可用的API接口：</h3>
        <ul>
            <li><a href="/api/docs">API文档</a></li>
            <li><a href="/api/health">健康检查</a></li>
        </ul>
    </div>
</body>
</html>'''
        
        with open(backend_static / "index.html", "w", encoding="utf-8") as f:
            f.write(fallback_html)
    
    # 复制配置和文档
    for file_name in ["requirements.txt", "README.md", "START_GUIDE.md", "diagnose_deployment.py"]:
        src_file = project_root / file_name
        if src_file.exists():
            shutil.copy2(src_file, package_dir)
            print(f"  ✅ 已复制 {file_name}")
    
    # 复制示例数据（如果存在且不太大）
    for data_dir in ["data", "examples"]:
        data_path = project_root / data_dir
        if data_path.exists():
            try:
                shutil.copytree(data_path, package_dir / data_dir,
                              ignore=shutil.ignore_patterns('*.log', '__pycache__', '*.tmp'))
                print(f"  ✅ 已复制 {data_dir}/")
            except Exception as e:
                print(f"  ⚠️ 跳过 {data_dir}/: {e}")
    
    # 创建一键启动脚本
    print("📝 创建启动脚本...")
    
    # Windows一键启动脚本
    start_bat = '''@echo off
cls
echo ============================================
echo     Oracle SP Parser - Simple Deploy
echo ============================================
echo.

:: 保存当前目录
set "SCRIPT_DIR=%~dp0"
cd /d "%SCRIPT_DIR%"

:: Check Python
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: Python not found, please install Python 3.8+
    echo Download: https://www.python.org/downloads/
    echo.
    pause
    exit /b 1
)

echo OK: Python environment detected
echo Current directory: %CD%
echo.

:: Check pip
pip --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: pip not found
    pause
    exit /b 1
)

:: Install dependencies
echo Installing Python dependencies...
echo This may take a few minutes, please wait...
pip install -r requirements.txt --quiet --disable-pip-version-check

if %errorlevel% neq 0 (
    echo ERROR: Dependencies installation failed
    echo Try manual install: pip install -r requirements.txt
    pause
    exit /b 1
)

echo OK: Dependencies installed
echo.

:: Set environment variables
set "PYTHONPATH=%CD%\\src;%CD%"
set "PYTHONIOENCODING=utf-8"

:: Debug: Print paths
echo Debug info:
echo PYTHONPATH=%PYTHONPATH%
echo Backend directory: %CD%\\backend
echo Static directory: %CD%\\backend\\static
if exist "%CD%\\backend\\static" (
    echo ✅ Backend static directory exists
) else (
    echo ❌ Backend static directory missing
)
echo.

:: Start application
echo Starting Oracle SP Parser...
echo.
echo Web App: http://localhost:8000
echo API Docs: http://localhost:8000/api/docs
echo Press Ctrl+C to stop service
echo.
echo ----------------------------------------
echo.

cd backend
python -m uvicorn main:app --host 0.0.0.0 --port 8000

echo.
echo Service stopped
pause
'''
    
    with open(package_dir / "start.bat", "w", encoding="cp1252", errors="replace") as f:
        f.write(start_bat)
    
    # 创建安装依赖的独立脚本
    install_deps_bat = '''@echo off
cls
echo ============================================
echo      Install Python Dependencies
echo ============================================
echo.

python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: Python not found
    pause
    exit /b 1
)

echo Installing dependencies...
pip install -r requirements.txt

if %errorlevel% neq 0 (
    echo.
    echo ERROR: Installation failed, try these solutions:
    echo 1. Check network connection
    echo 2. Run as administrator
    echo 3. Manual install: pip install sqlparse networkx pydantic fastapi uvicorn python-multipart requests
    echo.
) else (
    echo.
    echo OK: Dependencies installed successfully!
    echo You can now run "start.bat"
    echo.
)

pause
'''
    
    with open(package_dir / "install_deps.bat", "w", encoding="cp1252", errors="replace") as f:
        f.write(install_deps_bat)
    
    # 创建问题排查脚本
    check_env_bat = '''@echo off
cls
echo ============================================
echo       Environment Check and Diagnosis
echo ============================================
echo.

echo Checking Python environment...
python --version 2>nul
if %errorlevel% neq 0 (
    echo ERROR: Python not installed or not in PATH
    echo Please download from https://www.python.org/downloads/
    echo Make sure to check "Add Python to PATH" during installation
) else (
    echo OK: Python is installed
)
echo.

echo Checking pip...
pip --version 2>nul
if %errorlevel% neq 0 (
    echo ERROR: pip not installed
) else (
    echo OK: pip is installed
)
echo.

echo Checking Python packages...
python -c "import sys; print('Python version:', sys.version)" 2>nul
echo.

for %%p in (sqlparse networkx pydantic fastapi uvicorn) do (
    echo Checking %%p...
    python -c "import %%p; print('OK: %%p installed')" 2>nul || echo "ERROR: %%p not installed"
)

echo.
echo Checking port usage...
netstat -an | findstr :8000 >nul
if %errorlevel% equ 0 (
    echo WARNING: Port 8000 is in use
    echo Please close programs using port 8000, or modify port in start script
) else (
    echo OK: Port 8000 is available
)

echo.
echo Checking firewall...
echo If you cannot access the app, check Windows Firewall settings
echo Allow Python or port 8000 inbound connections

echo.
echo =======================================
echo Common Solutions:
echo.
echo 1. Python not installed:
echo    Download and install Python 3.8+ (check Add to PATH)
echo.  
echo 2. Dependencies missing:
echo    Run "install_deps.bat"
echo.
echo 3. Port occupied:
echo    Close programs using port 8000
echo.
echo 4. Firewall blocking:
echo    Allow Python in Windows Firewall
echo.
echo 5. Permission issues:
echo    Run scripts as administrator
echo =======================================
echo.

pause
'''
    
    with open(package_dir / "check_env.bat", "w", encoding="cp1252", errors="replace") as f:
        f.write(check_env_bat)
    
    # 创建部署说明文档
    readme_content = '''# Oracle SP Parser - 简化部署包

## 🎯 使用说明

### 快速启动 (推荐)
1. 双击运行 `启动应用.bat`
2. 等待依赖安装完成
3. 浏览器访问 http://localhost:8000

### 分步操作
1. 双击运行 `install_deps.bat` (仅需运行一次)
2. 双击运行 `start.bat`

### 问题排查
如果遇到问题，双击运行 `check_env.bat` 进行诊断

## 📋 系统要求

- Windows 7/8/10/11
- Python 3.8 或更高版本
- 网络连接 (首次安装依赖时需要)
- 4GB+ 可用内存

## 🔧 Python安装

如果没有Python环境：
1. 访问 https://www.python.org/downloads/
2. 下载Python 3.8+
3. 安装时务必勾选 "Add Python to PATH"
4. 安装完成后重启计算机

## 🌐 访问地址

- 应用主页: http://localhost:8000
- API文档: http://localhost:8000/api/docs
- 健康检查: http://localhost:8000/api/health

## 📁 文件说明

- `start.bat` - 一键启动脚本
- `install_deps.bat` - 单独安装依赖
- `check_env.bat` - 问题诊断工具
- `requirements.txt` - Python依赖列表
- `src/` - 核心分析代码
- `backend/` - Web API服务
- `static/` - 前端界面文件

## 🔧 故障排除

### 常见错误

1. **"python不是内部或外部命令"**
   - Python未安装或未添加到PATH
   - 重新安装Python并勾选"Add to PATH"

2. **依赖安装失败**
   - 检查网络连接
   - 以管理员身份运行
   - 手动执行: `pip install -r requirements.txt`

3. **端口8000被占用**
   - 关闭其他占用该端口的程序
   - 或修改启动脚本中的端口号

4. **无法访问网页**
   - 检查Windows防火墙设置
   - 确保8000端口未被阻止

5. **中文显示乱码**
   - 确保使用UTF-8编码
   - 更新Windows系统

## 🆘 获取帮助

运行 `check_env.bat` 可以自动诊断大部分问题。

## 📞 手动安装依赖

如果自动安装失败，可以手动执行：

```cmd
pip install sqlparse>=0.4.0
pip install networkx>=3.0  
pip install pydantic>=2.0.0
pip install fastapi>=0.100.0
pip install uvicorn[standard]>=0.20.0
pip install python-multipart>=0.0.5
pip install requests>=2.28.0
```

## 🔄 更新说明

要更新应用，只需要替换整个文件夹即可。
'''
    
    with open(package_dir / "使用说明.md", "w", encoding="utf-8") as f:
        f.write(readme_content)
    
    # 创建包信息
    package_info = {
        "package_name": package_name,
        "package_type": "simple",
        "created_date": datetime.now().isoformat(),
        "python_version_required": "3.8+",
        "includes_venv": False,
        "auto_install_deps": True,
        "target_platform": "Windows",
        "package_size_mb": round(sum(f.stat().st_size for f in package_dir.rglob('*') if f.is_file()) / 1024 / 1024, 2)
    }
    
    with open(package_dir / "package_info.json", "w", encoding="utf-8") as f:
        json.dump(package_info, f, indent=2, ensure_ascii=False)
    
    # 创建压缩包
    print("📦 创建压缩包...")
    try:
        import zipfile
        zip_path = package_dir.parent / f"{package_name}.zip"
        
        with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED, compresslevel=6) as zipf:
            for file_path in package_dir.rglob('*'):
                if file_path.is_file():
                    arcname = file_path.relative_to(package_dir.parent)
                    zipf.write(file_path, arcname)
        
        zip_size_mb = round(zip_path.stat().st_size / 1024 / 1024, 2)
        print(f"✅ 压缩包已创建: {zip_path} ({zip_size_mb}MB)")
        
    except Exception as e:
        print(f"⚠️ 创建压缩包失败: {e}")
        zip_path = None
    
    print("=" * 50)
    print("🎉 简化部署包创建完成！")
    print(f"📁 部署包目录: {package_dir}")
    if zip_path:
        print(f"📦 压缩包文件: {zip_path}")
    print()
    print("📋 部署步骤:")
    print("1. 将压缩包传输到目标Windows主机")
    print("2. 解压到任意目录")
    print("3. 双击运行 'start.bat'")
    print("4. 等待依赖自动安装完成")
    print("5. 浏览器访问 http://localhost:8000")
    print()
    print("💡 如果目标主机没有Python，请先安装Python 3.8+")
    print("   下载地址: https://www.python.org/downloads/")

if __name__ == "__main__":
    create_simple_package() 
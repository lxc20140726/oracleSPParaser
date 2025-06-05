#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Oracle SP Parser - 便携式打包工具
将项目打包成自包含的便携式部署包
"""

import os
import sys
import shutil
import subprocess
import json
from pathlib import Path
from datetime import datetime

class PortablePackager:
    def __init__(self):
        self.project_root = Path(__file__).parent
        self.package_name = f"oracle-sp-parser-portable-{datetime.now().strftime('%Y%m%d-%H%M%S')}"
        self.package_dir = self.project_root / "dist" / self.package_name
        
    def clean_build_dir(self):
        """清理构建目录"""
        print("🧹 清理构建目录...")
        if self.package_dir.exists():
            shutil.rmtree(self.package_dir)
        self.package_dir.mkdir(parents=True, exist_ok=True)
        
    def build_frontend(self):
        """构建前端"""
        print("🏗️ 构建前端...")
        frontend_dir = self.project_root / "frontend"
        
        if not frontend_dir.exists():
            print("⚠️ 前端目录不存在，跳过前端构建")
            return
            
        try:
            # 检查npm是否可用
            subprocess.run(["npm", "--version"], check=True, capture_output=True)
            
            # 安装依赖并构建
            print("📦 安装前端依赖...")
            subprocess.run(["npm", "install"], cwd=frontend_dir, check=True)
            
            print("🔨 构建前端...")
            subprocess.run(["npm", "run", "build"], cwd=frontend_dir, check=True)
            
            # 复制构建结果
            build_dir = frontend_dir / "build"
            if build_dir.exists():
                self._copy_frontend_files(build_dir)
                print("✅ 前端构建完成")
            else:
                print("⚠️ 前端构建目录不存在")
                
        except (subprocess.CalledProcessError, FileNotFoundError):
            print("⚠️ 无法构建前端 (npm不可用或构建失败)，将使用现有构建文件")
            # 尝试复制现有的构建文件
            existing_build = frontend_dir / "build"
            if existing_build.exists():
                self._copy_frontend_files(existing_build)
                print("✅ 使用现有前端构建文件")
            else:
                print("❌ 没有可用的前端构建文件")
                self._create_fallback_frontend()
                
    def _copy_frontend_files(self, build_dir):
        """复制前端文件到部署包"""
        print("🌐 复制前端文件...")
        
        # 确保backend目录已经存在
        backend_dir = self.package_dir / "backend"
        if not backend_dir.exists():
            print("  ⚠️ backend目录不存在，先创建...")
            backend_dir.mkdir(parents=True, exist_ok=True)
        
        # 复制到backend目录下的static文件夹
        backend_static = backend_dir / "static"
        if backend_static.exists():
            print("  🧹 清理已存在的backend/static目录...")
            shutil.rmtree(backend_static)
        
        shutil.copytree(build_dir, backend_static)
        print("  ✅ 已复制前端文件到backend/static")
        
        # 同时复制到根目录的static文件夹（备用）
        root_static = self.package_dir / "static"
        if root_static.exists():
            print("  🧹 清理已存在的根目录static...")
            shutil.rmtree(root_static)
        shutil.copytree(build_dir, root_static)
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
    
    def _create_fallback_frontend(self):
        """创建备用前端页面"""
        print("📝 创建备用前端页面...")
        
        # 确保backend目录存在
        backend_dir = self.package_dir / "backend"
        backend_dir.mkdir(parents=True, exist_ok=True)
        
        # 创建static目录
        backend_static = backend_dir / "static"
        backend_static.mkdir(parents=True, exist_ok=True)
        
        # 创建简单的index.html作为后备
        fallback_html = '''<!DOCTYPE html>
<html>
<head>
    <title>Oracle SP Parser</title>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <style>
        body { font-family: Arial, sans-serif; margin: 40px; background: #f5f5f5; }
        .container { max-width: 800px; margin: 0 auto; background: white; padding: 40px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
        .warning { background: #fff3cd; border: 1px solid #ffeaa7; padding: 20px; border-radius: 5px; }
        .success { background: #d4edda; border: 1px solid #c3e6cb; padding: 20px; border-radius: 5px; }
        h1 { color: #333; }
        pre { background: #f8f9fa; padding: 10px; border-radius: 3px; overflow-x: auto; }
        a { color: #007bff; text-decoration: none; }
        a:hover { text-decoration: underline; }
    </style>
</head>
<body>
    <div class="container">
        <h1>🔍 Oracle存储过程分析工具</h1>
        <div class="warning">
            <h3>⚠️ 前端界面未构建</h3>
            <p>当前使用的是备用页面。要使用完整的Web界面，请构建前端：</p>
            <pre>cd frontend
npm install
npm run build</pre>
            <p>然后重新运行部署脚本。</p>
        </div>
        
        <div class="success">
            <h3>✅ API服务正常运行</h3>
            <p>您可以使用以下API接口：</p>
            <ul>
                <li><a href="/api/docs" target="_blank">📚 API文档 (Swagger UI)</a></li>
                <li><a href="/api/redoc" target="_blank">📖 API文档 (ReDoc)</a></li>
                <li><a href="/api/health" target="_blank">💚 健康检查</a></li>
            </ul>
        </div>
        
        <h3>🚀 快速测试</h3>
        <p>您可以使用curl或其他HTTP客户端测试API：</p>
        <pre>curl -X POST http://localhost:8000/api/analyze \\
  -H "Content-Type: application/json" \\
  -d '{"stored_procedure": "CREATE OR REPLACE PROCEDURE test AS BEGIN NULL; END;"}'</pre>
    </div>
</body>
</html>'''
        
        with open(backend_static / "index.html", "w", encoding="utf-8") as f:
            f.write(fallback_html)
        
        print("  ✅ 备用前端页面创建完成")
    
    def copy_project_files(self):
        """复制项目文件"""
        print("📁 复制项目文件...")
        
        # 复制核心代码
        src_dirs = ["src", "backend"]
        for src_dir in src_dirs:
            src_path = self.project_root / src_dir
            dst_path = self.package_dir / src_dir
            
            if src_path.exists():
                if src_dir == "backend":
                    # 对于backend目录，需要特殊处理以保留已有的static文件
                    if dst_path.exists():
                        # 备份static目录（如果存在）
                        static_backup = None
                        static_dir = dst_path / "static"
                        if static_dir.exists():
                            print(f"  🔄 备份现有的static目录...")
                            static_backup = self.package_dir / "static_backup_temp"
                            shutil.move(str(static_dir), str(static_backup))
                        
                        print(f"  ⚠️ 目录 {src_dir} 已存在，先清理...")
                        shutil.rmtree(dst_path)
                        
                        # 复制backend目录
                        shutil.copytree(src_path, dst_path, 
                                      ignore=shutil.ignore_patterns('__pycache__', '*.pyc', '.DS_Store'))
                        
                        # 恢复static目录
                        if static_backup and static_backup.exists():
                            print(f"  🔄 恢复static目录...")
                            final_static_dir = dst_path / "static"
                            if final_static_dir.exists():
                                shutil.rmtree(final_static_dir)
                            shutil.move(str(static_backup), str(final_static_dir))
                    else:
                        shutil.copytree(src_path, dst_path, 
                                      ignore=shutil.ignore_patterns('__pycache__', '*.pyc', '.DS_Store'))
                else:
                    # 对于其他目录，正常处理
                    if dst_path.exists():
                        print(f"  ⚠️ 目录 {src_dir} 已存在，先清理...")
                        shutil.rmtree(dst_path)
                    
                    shutil.copytree(src_path, dst_path, 
                                  ignore=shutil.ignore_patterns('__pycache__', '*.pyc', '.DS_Store'))
                
                print(f"  ✅ 已复制 {src_dir}/")
        
        # 复制配置文件
        config_files = ["requirements.txt", "README.md", "START_GUIDE.md", "diagnose_deployment.py"]
        for config_file in config_files:
            src_file = self.project_root / config_file
            if src_file.exists():
                shutil.copy2(src_file, self.package_dir)
                print(f"  ✅ 已复制 {config_file}")
        
        # 复制示例数据
        for data_dir in ["data", "examples"]:
            data_path = self.project_root / data_dir
            dst_path = self.package_dir / data_dir
            
            if data_path.exists():
                # 如果目标目录已存在，先删除再复制
                if dst_path.exists():
                    shutil.rmtree(dst_path)
                
                shutil.copytree(data_path, dst_path,
                              ignore=shutil.ignore_patterns('*.log', '__pycache__'))
                print(f"  ✅ 已复制 {data_dir}/")
    
    def create_virtual_env(self):
        """创建虚拟环境并安装依赖"""
        print("🐍 创建虚拟环境...")
        venv_dir = self.package_dir / "venv"
        
        try:
            # 创建虚拟环境
            subprocess.run([sys.executable, "-m", "venv", str(venv_dir)], check=True)
            
            # 获取虚拟环境中的pip路径
            if os.name == 'nt':  # Windows
                pip_path = venv_dir / "Scripts" / "pip.exe"
                python_path = venv_dir / "Scripts" / "python.exe"
            else:  # Unix-like
                pip_path = venv_dir / "bin" / "pip"
                python_path = venv_dir / "bin" / "python"
            
            print("📦 安装Python依赖...")
            # 安装依赖
            subprocess.run([str(pip_path), "install", "--upgrade", "pip"], check=True)
            subprocess.run([str(pip_path), "install", "-r", "requirements.txt"], 
                         cwd=self.package_dir, check=True)
            
            print("✅ 虚拟环境创建完成")
            return True
            
        except subprocess.CalledProcessError as e:
            print(f"❌ 虚拟环境创建失败: {e}")
            return False
    
    def create_startup_scripts(self):
        """创建启动脚本"""
        print("📝 创建启动脚本...")
        
        # Windows批处理脚本
        bat_content = '''@echo off
cls
title Oracle SP Parser
echo ===================================================
echo         Oracle SP Parser - Portable Version
echo ===================================================
echo.

:: 保存当前目录
set "SCRIPT_DIR=%~dp0"
cd /d "%SCRIPT_DIR%"

:: Check Python environment
if exist "venv\\Scripts\\python.exe" (
    echo OK: Using bundled Python environment
    set "PYTHON_CMD=%CD%\\venv\\Scripts\\python.exe"
    set "PIP_CMD=%CD%\\venv\\Scripts\\pip.exe"
) else (
    echo WARNING: Bundled Python not found, using system Python
    set PYTHON_CMD=python
    set PIP_CMD=pip
)

:: Check dependencies
echo Checking dependencies...
"%PYTHON_CMD%" -c "import uvicorn, fastapi" >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: Missing dependencies, trying to install...
    if exist "requirements.txt" (
        "%PIP_CMD%" install -r requirements.txt
    ) else (
        echo ERROR: requirements.txt not found
        pause
        exit /b 1
    )
)

:: Set environment variables
set "PYTHONPATH=%CD%\\src;%CD%"
set "PYTHONIOENCODING=utf-8"

:: Debug: Print paths
echo Debug info:
echo Current directory: %CD%
echo PYTHONPATH=%PYTHONPATH%
echo Python command: %PYTHON_CMD%
echo Backend directory: %CD%\\backend
echo Static directory: %CD%\\backend\\static
if exist "%CD%\\backend\\static" (
    echo ✅ Backend static directory exists
    if exist "%CD%\\backend\\static\\static" (
        echo ✅ Frontend assets directory exists
    ) else (
        echo ⚠️ Frontend assets directory missing
    )
) else (
    echo ❌ Backend static directory missing
)
echo.

:: Start service
echo Starting Oracle SP Parser...
echo Service URL: http://localhost:8000
echo API Docs: http://localhost:8000/api/docs
echo Press Ctrl+C to stop service
echo.

cd backend
"%PYTHON_CMD%" -m uvicorn main:app --host 0.0.0.0 --port 8000 --reload

echo.
echo Press any key to exit...
pause >nul
'''
        
        with open(self.package_dir / "start.bat", "w", encoding="cp1252", errors="replace") as f:
            f.write(bat_content)
        
        # PowerShell脚本
        ps1_content = '''# Oracle SP Parser - 便携式启动脚本
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8

Write-Host "===================================================" -ForegroundColor Blue
Write-Host "        Oracle SP Parser - 便携式版本" -ForegroundColor Blue
Write-Host "===================================================" -ForegroundColor Blue
Write-Host ""

# 检查Python环境
if (Test-Path "venv/Scripts/python.exe") {
    Write-Host "✅ 使用内置Python环境" -ForegroundColor Green
    $pythonCmd = "venv/Scripts/python.exe"
    $pipCmd = "venv/Scripts/pip.exe"
} else {
    Write-Host "⚠️ 内置Python环境不存在，使用系统Python" -ForegroundColor Yellow
    $pythonCmd = "python"
    $pipCmd = "pip"
}

# 检查依赖
Write-Host "🔍 检查依赖..." -ForegroundColor Blue
try {
    & $pythonCmd -c "import uvicorn, fastapi" 2>$null
    if ($LASTEXITCODE -ne 0) {
        throw "Dependencies missing"
    }
} catch {
    Write-Host "❌ 缺少必要依赖，尝试安装..." -ForegroundColor Red
    if (Test-Path "requirements.txt") {
        & $pipCmd install -r requirements.txt
    } else {
        Write-Host "❌ 找不到requirements.txt文件" -ForegroundColor Red
        Read-Host "按任意键退出"
        exit 1
    }
}

# 设置环境变量
$env:PYTHONPATH = "$PWD/src;$PWD"
$env:PYTHONIOENCODING = "utf-8"

# 启动服务
Write-Host "🚀 启动Oracle SP Parser..." -ForegroundColor Green
Write-Host "🌐 服务地址: http://localhost:8000" -ForegroundColor Cyan
Write-Host "📚 API文档: http://localhost:8000/api/docs" -ForegroundColor Cyan
Write-Host "💡 按Ctrl+C停止服务" -ForegroundColor Yellow
Write-Host ""

Set-Location backend
& $pythonCmd -m uvicorn main:app --host 0.0.0.0 --port 8000 --reload

Write-Host ""
Read-Host "按任意键退出"
'''
        
        with open(self.package_dir / "start.ps1", "w", encoding="utf-8") as f:
            f.write(ps1_content)
        
        # Linux/Mac脚本
        sh_content = '''#!/bin/bash
# Oracle SP Parser - 便携式启动脚本

echo "==================================================="
echo "        Oracle SP Parser - 便携式版本"
echo "==================================================="
echo ""

# 检查Python环境
if [ -f "venv/bin/python" ]; then
    echo "✅ 使用内置Python环境"
    PYTHON_CMD="venv/bin/python"
    PIP_CMD="venv/bin/pip"
else
    echo "⚠️ 内置Python环境不存在，使用系统Python"
    PYTHON_CMD="python3"
    PIP_CMD="pip3"
fi

# 检查依赖
echo "🔍 检查依赖..."
$PYTHON_CMD -c "import uvicorn, fastapi" 2>/dev/null
if [ $? -ne 0 ]; then
    echo "❌ 缺少必要依赖，尝试安装..."
    if [ -f "requirements.txt" ]; then
        $PIP_CMD install -r requirements.txt
    else
        echo "❌ 找不到requirements.txt文件"
        exit 1
    fi
fi

# 设置环境变量
export PYTHONPATH="$(pwd)/src:$(pwd)"
export PYTHONIOENCODING=utf-8

# 启动服务
echo "🚀 启动Oracle SP Parser..."
echo "🌐 服务地址: http://localhost:8000"
echo "📚 API文档: http://localhost:8000/api/docs"
echo "💡 按Ctrl+C停止服务"
echo ""

cd backend
$PYTHON_CMD -m uvicorn main:app --host 0.0.0.0 --port 8000 --reload
'''
        
        with open(self.package_dir / "start.sh", "w", encoding="utf-8") as f:
            f.write(sh_content)
        
        # 设置执行权限
        os.chmod(self.package_dir / "start.sh", 0o755)
        
    def create_readme(self):
        """创建部署说明文档"""
        print("📄 创建部署说明...")
        
        readme_content = '''# Oracle SP Parser - 便携式部署包

## 🎯 快速启动

### Windows用户
双击运行以下任一脚本：
- `start.bat` (推荐)
- `start.ps1` (PowerShell版本)

### Linux/Mac用户
```bash
./start.sh
```

## 📋 系统要求

- Python 3.8+ (如果没有内置Python环境)
- 8GB+ 可用内存
- 1GB+ 可用磁盘空间

## 🌐 访问地址

启动成功后访问：
- 应用主页: http://localhost:8000
- API文档: http://localhost:8000/api/docs

## 📁 目录结构

```
oracle-sp-parser-portable/
├── src/                    # 核心代码
├── backend/               # 后端API
├── static/               # 前端静态文件
├── venv/                 # Python虚拟环境 (如果存在)
├── data/                 # 示例数据
├── examples/             # 示例文件
├── requirements.txt      # Python依赖
├── start.bat            # Windows启动脚本
├── start.ps1            # PowerShell启动脚本
├── start.sh             # Linux/Mac启动脚本
└── README.md            # 本文件
```

## 🔧 故障排除

### 常见问题

1. **Python未安装**
   - Windows: 下载安装Python 3.8+ from python.org
   - Linux: sudo apt install python3 python3-pip
   - Mac: brew install python3

2. **端口占用**
   - 修改启动脚本中的端口号 (默认8000)
   - 或停止占用8000端口的其他程序

3. **权限问题 (Linux/Mac)**
   ```bash
   chmod +x start.sh
   ```

4. **依赖安装失败**
   ```bash
   # 手动安装依赖
   pip install -r requirements.txt
   ```

### 日志查看

- 启动日志会在控制台显示
- 如需保存日志，重定向输出：
  ```bash
  ./start.sh > app.log 2>&1
  ```

## 🆘 获取帮助

如遇问题，请检查：
1. Python版本是否符合要求
2. 网络连接是否正常
3. 防火墙是否阻止了8000端口
4. 控制台错误信息

## 📞 技术支持

- 查看详细文档: START_GUIDE.md
- 示例文件: examples/ 目录
- 测试数据: data/ 目录
'''
        
        with open(self.package_dir / "DEPLOY_README.md", "w", encoding="utf-8") as f:
            f.write(readme_content)
    
    def create_package_info(self):
        """创建打包信息文件"""
        info = {
            "package_name": self.package_name,
            "package_date": datetime.now().isoformat(),
            "python_version": f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}",
            "platform": sys.platform,
            "includes_venv": (self.package_dir / "venv").exists(),
            "includes_frontend": (self.package_dir / "static").exists(),
        }
        
        with open(self.package_dir / "package_info.json", "w", encoding="utf-8") as f:
            json.dump(info, f, indent=2, ensure_ascii=False)
    
    def create_archive(self):
        """创建压缩包"""
        print("📦 创建压缩包...")
        
        try:
            import zipfile
            
            zip_path = self.package_dir.parent / f"{self.package_name}.zip"
            
            with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
                for root, dirs, files in os.walk(self.package_dir):
                    for file in files:
                        file_path = Path(root) / file
                        arcname = file_path.relative_to(self.package_dir.parent)
                        zipf.write(file_path, arcname)
            
            print(f"✅ 压缩包已创建: {zip_path}")
            return zip_path
            
        except Exception as e:
            print(f"❌ 创建压缩包失败: {e}")
            return None
    
    def run(self):
        """执行打包流程"""
        print(f"🚀 开始创建便携式部署包: {self.package_name}")
        print("=" * 60)
        
        try:
            self.clean_build_dir()
            self.build_frontend()
            self.copy_project_files()
            
            # 询问是否创建虚拟环境
            create_venv = input("是否创建内置Python虚拟环境？(推荐) [Y/n]: ").strip().lower()
            if create_venv not in ['n', 'no']:
                self.create_virtual_env()
            
            self.create_startup_scripts()
            self.create_readme()
            self.create_package_info()
            
            # 询问是否创建压缩包
            create_zip = input("是否创建ZIP压缩包？[Y/n]: ").strip().lower()
            if create_zip not in ['n', 'no']:
                zip_path = self.create_archive()
            
            print("=" * 60)
            print("🎉 打包完成！")
            print(f"📁 部署包位置: {self.package_dir}")
            if 'zip_path' in locals() and zip_path:
                print(f"📦 压缩包位置: {zip_path}")
            print()
            print("📋 部署说明:")
            print("1. 将整个文件夹复制到目标Windows主机")
            print("2. 双击运行 start.bat 启动应用")
            print("3. 浏览器访问 http://localhost:8000")
            
        except Exception as e:
            print(f"❌ 打包失败: {e}")
            return False
        
        return True

if __name__ == "__main__":
    packager = PortablePackager()
    packager.run() 
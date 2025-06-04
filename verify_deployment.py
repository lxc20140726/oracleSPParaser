#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Oracle SP Parser - 部署包验证工具
验证部署包的完整性，确保前端文件正确部署
"""

import os
import sys
from pathlib import Path
import json

def check_file_exists(file_path, description):
    """检查文件是否存在"""
    if file_path.exists():
        size = file_path.stat().st_size
        print(f"  ✅ {description}: {file_path} ({size} bytes)")
        return True
    else:
        print(f"  ❌ {description}: {file_path} (不存在)")
        return False

def check_directory_exists(dir_path, description):
    """检查目录是否存在"""
    if dir_path.exists() and dir_path.is_dir():
        count = len(list(dir_path.rglob('*')))
        print(f"  ✅ {description}: {dir_path} ({count} 个文件)")
        return True
    else:
        print(f"  ❌ {description}: {dir_path} (不存在)")
        return False

def verify_deployment_package(package_path):
    """验证部署包完整性"""
    print(f"🔍 验证部署包: {package_path}")
    print("=" * 60)
    
    package_dir = Path(package_path)
    if not package_dir.exists():
        print(f"❌ 部署包目录不存在: {package_path}")
        return False
    
    issues = []
    
    # 1. 检查核心目录
    print("\n📁 检查核心目录结构...")
    core_dirs = [
        ("src", "核心分析代码"),
        ("backend", "Web API服务"),
    ]
    
    for dir_name, description in core_dirs:
        if not check_directory_exists(package_dir / dir_name, description):
            issues.append(f"缺少{description}目录")
    
    # 2. 检查前端文件
    print("\n🌐 检查前端文件...")
    
    # 检查backend/static目录
    backend_static = package_dir / "backend" / "static"
    if check_directory_exists(backend_static, "前端静态文件目录 (backend/static)"):
        # 检查关键前端文件
        frontend_files = [
            ("index.html", "主页面"),
            ("manifest.json", "应用清单"),
            ("static/js", "JavaScript文件目录"),
            ("static/css", "CSS样式文件目录"),
        ]
        
        for file_path, description in frontend_files:
            full_path = backend_static / file_path
            if file_path.endswith("目录"):
                if not check_directory_exists(full_path, description):
                    issues.append(f"前端{description}缺失")
            else:
                if not check_file_exists(full_path, description):
                    issues.append(f"前端{description}缺失")
        
        # 检查JS文件
        js_dir = backend_static / "static" / "js"
        if js_dir.exists():
            js_files = list(js_dir.glob("*.js"))
            if js_files:
                print(f"  ✅ JavaScript文件: {len(js_files)} 个")
            else:
                print(f"  ⚠️ JavaScript文件: 无")
                issues.append("缺少JavaScript文件")
        
        # 检查CSS文件
        css_dir = backend_static / "static" / "css"
        if css_dir.exists():
            css_files = list(css_dir.glob("*.css"))
            if css_files:
                print(f"  ✅ CSS文件: {len(css_files)} 个")
            else:
                print(f"  ⚠️ CSS文件: 无")
                issues.append("缺少CSS文件")
    else:
        issues.append("缺少前端静态文件目录")
    
    # 3. 检查配置文件
    print("\n📋 检查配置文件...")
    config_files = [
        ("requirements.txt", "Python依赖列表"),
        ("README.md", "项目说明"),
    ]
    
    for file_name, description in config_files:
        if not check_file_exists(package_dir / file_name, description):
            issues.append(f"缺少{description}")
    
    # 4. 检查启动脚本
    print("\n🚀 检查启动脚本...")
    startup_files = [
        ("start.bat", "Windows启动脚本"),
    ]
    
    for file_name, description in startup_files:
        if not check_file_exists(package_dir / file_name, description):
            issues.append(f"缺少{description}")
    
    # 5. 检查虚拟环境（便携式包）
    print("\n🐍 检查Python环境...")
    venv_dir = package_dir / "venv"
    if venv_dir.exists():
        print("  ✅ 便携式Python虚拟环境已包含")
        # 检查虚拟环境结构
        if os.name == 'nt':  # Windows
            python_exe = venv_dir / "Scripts" / "python.exe"
            pip_exe = venv_dir / "Scripts" / "pip.exe"
        else:  # Unix-like
            python_exe = venv_dir / "bin" / "python"
            pip_exe = venv_dir / "bin" / "pip"
        
        check_file_exists(python_exe, "Python解释器")
        check_file_exists(pip_exe, "pip包管理器")
    else:
        print("  ℹ️ 未包含虚拟环境（简化部署包）")
    
    # 6. 生成验证报告
    print("\n" + "=" * 60)
    if not issues:
        print("🎉 验证通过！部署包完整，可以正常使用。")
        print("\n📋 部署说明:")
        print("1. 将部署包复制到目标主机")
        print("2. 运行 start.bat 启动服务")
        print("3. 浏览器访问 http://localhost:8000")
        return True
    else:
        print(f"⚠️ 发现 {len(issues)} 个问题:")
        for i, issue in enumerate(issues, 1):
            print(f"  {i}. {issue}")
        
        print("\n🔧 建议解决方案:")
        if "前端" in str(issues):
            print("- 前端文件问题: 请先构建前端")
            print("  cd frontend && npm install && npm run build")
            print("  然后重新运行部署脚本")
        
        if "缺少" in str(issues) and "目录" in str(issues):
            print("- 文件缺失: 请重新运行部署脚本")
            print("  python deploy_simple.py 或 python package_portable.py")
        
        return False

def main():
    """主函数"""
    if len(sys.argv) != 2:
        print("使用方法: python verify_deployment.py <部署包路径>")
        print("\n示例:")
        print("  python verify_deployment.py dist/oracle-sp-parser-simple-20231201-120000")
        print("  python verify_deployment.py dist/oracle-sp-parser-portable-20231201-120000")
        sys.exit(1)
    
    package_path = sys.argv[1]
    success = verify_deployment_package(package_path)
    
    if not success:
        sys.exit(1)

if __name__ == "__main__":
    main() 
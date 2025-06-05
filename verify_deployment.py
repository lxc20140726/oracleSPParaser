#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Oracle SP Parser - 部署包验证工具
验证部署包的完整性和正确性
"""

import sys
import json
from pathlib import Path
from datetime import datetime

def verify_deployment_package(package_path):
    """验证部署包"""
    package_dir = Path(package_path)
    
    if not package_dir.exists():
        print(f"❌ 部署包不存在: {package_path}")
        return False
    
    print(f"🔍 验证部署包: {package_dir.name}")
    print("="*60)
    
    results = {}
    
    # 检查必需文件
    required_files = [
        ("start.bat", "Windows启动脚本"),
        ("backend/main.py", "后端服务主程序"),
        ("src/main.py", "核心分析模块"),
        ("requirements.txt", "Python依赖配置"),
        ("diagnose_deployment.py", "诊断工具"),
        ("使用说明.md", "使用说明文档"),
    ]
    
    print("📁 检查必需文件:")
    for file_path, description in required_files:
        file_exists = (package_dir / file_path).exists()
        status = "✅" if file_exists else "❌"
        print(f"  {status} {description}: {file_path}")
        results[f"file_{file_path}"] = file_exists
    
    # 检查前端文件
    print("\n🌐 检查前端文件:")
    frontend_files = [
        ("backend/static/index.html", "前端主页"),
        ("backend/static/manifest.json", "应用清单"),
        ("backend/static/static/js", "JavaScript目录"),
        ("backend/static/static/css", "CSS目录"),
    ]
    
    for file_path, description in frontend_files:
        file_exists = (package_dir / file_path).exists()
        status = "✅" if file_exists else "❌"
        print(f"  {status} {description}: {file_path}")
        results[f"frontend_{file_path}"] = file_exists
    
    # 检查脚本文件
    print("\n📝 检查启动脚本:")
    script_files = [
        ("start.bat", "Windows批处理"),
        ("install_deps.bat", "依赖安装脚本"),
        ("check_env.bat", "环境检查脚本"),
    ]
    
    for file_path, description in script_files:
        file_exists = (package_dir / file_path).exists()
        status = "✅" if file_exists else "❌"
        print(f"  {status} {description}: {file_path}")
        results[f"script_{file_path}"] = file_exists
    
    # 检查包信息
    print("\n📋 检查包信息:")
    package_info_file = package_dir / "package_info.json"
    if package_info_file.exists():
        try:
            with open(package_info_file, 'r', encoding='utf-8') as f:
                package_info = json.load(f)
            
            print(f"  ✅ 包名: {package_info.get('package_name', 'unknown')}")
            print(f"  ✅ 创建日期: {package_info.get('created_date', 'unknown')}")
            print(f"  ✅ 包类型: {package_info.get('package_type', 'unknown')}")
            print(f"  ✅ 包大小: {package_info.get('package_size_mb', 'unknown')} MB")
            results["package_info"] = True
        except Exception as e:
            print(f"  ❌ 包信息读取失败: {e}")
            results["package_info"] = False
    else:
        print("  ❌ 包信息文件不存在")
        results["package_info"] = False
    
    # 统计结果
    total_checks = len(results)
    passed_checks = sum(1 for result in results.values() if result)
    
    print("\n📊 验证结果:")
    print(f"  总检查项: {total_checks}")
    print(f"  通过: {passed_checks}")
    print(f"  失败: {total_checks - passed_checks}")
    print(f"  成功率: {(passed_checks/total_checks*100):.1f}%")
    
    if passed_checks == total_checks:
        print("\n🎉 验证通过！部署包完整且正确。")
        return True
    else:
        print("\n⚠️ 验证未完全通过，请检查缺失的文件。")
        return False

def main():
    """主函数"""
    if len(sys.argv) != 2:
        print("用法: python verify_deployment.py <部署包路径>")
        sys.exit(1)
    
    package_path = sys.argv[1]
    success = verify_deployment_package(package_path)
    
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main() 
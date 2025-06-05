#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Oracle SP Parser - Windows部署诊断工具
专门用于排查Windows环境中的部署问题
"""

import sys
import subprocess
import json
from pathlib import Path
import requests
import time

def print_section(title):
    """打印章节标题"""
    print(f"\n{'='*60}")
    print(f"  {title}")
    print('='*60)

def check_file_exists(file_path, description):
    """检查文件是否存在并显示详细信息"""
    if file_path.exists():
        size = file_path.stat().st_size
        print(f"  ✅ {description}: {file_path} ({size} bytes)")
        return True
    else:
        print(f"  ❌ {description}: {file_path} (不存在)")
        return False

def check_service_health():
    """检查服务健康状态"""
    print_section("🏥 服务健康检查")
    
    try:
        print("  🔄 检查API服务...")
        response = requests.get("http://localhost:8000/api/health", timeout=5)
        if response.status_code == 200:
            print("  ✅ API服务正常运行")
            data = response.json()
            print(f"     状态: {data.get('status', 'unknown')}")
            print(f"     消息: {data.get('message', 'no message')}")
            return True
        else:
            print(f"  ❌ API服务返回错误状态码: {response.status_code}")
            return False
    except requests.ConnectionError:
        print("  ❌ 无法连接到服务 (服务可能未启动)")
        return False
    except requests.Timeout:
        print("  ❌ 连接超时")
        return False
    except Exception as e:
        print(f"  ❌ 检查服务时出错: {e}")
        return False

def check_static_resources():
    """检查静态资源访问"""
    print_section("📁 静态资源访问检查")
    
    resources_to_check = [
        ("/", "主页面"),
        ("/favicon.ico", "网站图标"),
        ("/manifest.json", "应用清单"),
        ("/static/css/main.cd6ddea4.css", "CSS样式文件"),
        ("/static/js/main.d2256801.js", "JavaScript文件"),
    ]
    
    all_ok = True
    for resource_path, description in resources_to_check:
        try:
            url = f"http://localhost:8000{resource_path}"
            print(f"  🔄 检查 {description}: {resource_path}")
            
            response = requests.get(url, timeout=5)
            if response.status_code == 200:
                content_length = len(response.content)
                content_type = response.headers.get('content-type', 'unknown')
                print(f"      ✅ 成功 ({content_length} bytes, {content_type})")
            else:
                print(f"      ❌ 失败 (状态码: {response.status_code})")
                all_ok = False
                
        except requests.ConnectionError:
            print(f"      ❌ 连接失败")
            all_ok = False
        except Exception as e:
            print(f"      ❌ 错误: {e}")
            all_ok = False
    
    return all_ok

def check_local_files():
    """检查本地文件结构"""
    print_section("📂 本地文件结构检查")
    
    current_dir = Path.cwd()
    print(f"  当前工作目录: {current_dir}")
    
    # 检查关键目录和文件
    files_to_check = [
        ("backend/main.py", "后端主程序"),
        ("backend/static/index.html", "前端主页面"),
        ("backend/static/manifest.json", "应用清单"),
        ("backend/static/favicon.ico", "网站图标"),
        ("backend/static/static/js", "JavaScript目录"),
        ("backend/static/static/css", "CSS目录"),
        ("src", "核心分析代码目录"),
        ("requirements.txt", "Python依赖文件"),
    ]
    
    all_ok = True
    for file_path, description in files_to_check:
        path = current_dir / file_path
        if not check_file_exists(path, description):
            all_ok = False
    
    # 检查具体的JS和CSS文件
    print("\n  🔍 检查具体的前端资源文件:")
    js_dir = current_dir / "backend/static/static/js"
    css_dir = current_dir / "backend/static/static/css"
    
    if js_dir.exists():
        js_files = list(js_dir.glob("*.js"))
        print(f"      JavaScript文件: {len(js_files)} 个")
        for js_file in js_files[:3]:  # 只显示前3个
            print(f"        - {js_file.name}")
    
    if css_dir.exists():
        css_files = list(css_dir.glob("*.css"))
        print(f"      CSS文件: {len(css_files)} 个")
        for css_file in css_files[:3]:  # 只显示前3个
            print(f"        - {css_file.name}")
    
    return all_ok

def check_browser_console():
    """提供浏览器控制台检查指导"""
    print_section("🌐 浏览器控制台检查指导")
    
    print("""
  如果页面仍然无法加载，请按以下步骤检查浏览器控制台：
  
  1. 在浏览器中打开 http://localhost:8000
  2. 按 F12 打开开发者工具
  3. 切换到 "Console" (控制台) 选项卡
  4. 查看是否有红色错误信息
  
  常见错误和解决方案：
  
  ❌ "Failed to load resource: net::ERR_CONNECTION_REFUSED"
     → 服务未启动或端口被占用
  
  ❌ "404 (Not Found)" 错误，针对 /static/js/xxx.js 或 /static/css/xxx.css
     → 静态文件路径映射问题
  
  ❌ "MIME type mismatch" 错误
     → 静态文件服务配置问题
  
  ❌ 页面显示但样式丢失
     → CSS文件无法加载
  
  ❌ 页面空白但无错误
     → JavaScript文件无法加载或执行错误
  """)

def check_port_usage():
    """检查端口使用情况"""
    print_section("🔌 端口使用情况检查")
    
    try:
        # 在Windows上使用netstat检查端口
        result = subprocess.run(
            ["netstat", "-an"], 
            capture_output=True, 
            text=True, 
            shell=True
        )
        
        if result.returncode == 0:
            lines = result.stdout.split('\n')
            port_8000_lines = [line for line in lines if ':8000' in line]
            
            if port_8000_lines:
                print("  🔍 端口8000的使用情况:")
                for line in port_8000_lines:
                    print(f"    {line.strip()}")
            else:
                print("  ⚠️ 端口8000未被使用 (服务可能未启动)")
        else:
            print("  ❌ 无法检查端口使用情况")
            
    except Exception as e:
        print(f"  ❌ 检查端口时出错: {e}")

def main():
    """主诊断函数"""
    print("🔍 Oracle SP Parser - Windows部署诊断工具")
    print("此工具将帮助您诊断部署中的常见问题")
    
    # 基本检查
    check_local_files()
    check_port_usage()
    
    # 等待用户确认服务已启动
    print_section("⏳ 等待服务启动")
    print("  请确保已经运行了 start.bat 并且看到 'Started server process' 消息")
    input("  按Enter键继续检查服务状态...")
    
    # 服务检查
    service_ok = check_service_health()
    
    if service_ok:
        static_ok = check_static_resources()
        
        if static_ok:
            print_section("🎉 诊断结果")
            print("  ✅ 所有检查通过！服务应该正常运行。")
            print("  📱 请在浏览器中访问: http://localhost:8000")
        else:
            print_section("⚠️ 诊断结果")
            print("  🔧 静态资源存在问题，这可能导致页面无法正确显示。")
            check_browser_console()
    else:
        print_section("❌ 诊断结果") 
        print("  🚨 服务未正常运行，请检查:")
        print("    1. start.bat 是否成功启动")
        print("    2. 是否有错误信息在控制台")
        print("    3. Python依赖是否正确安装")
        print("    4. 防火墙是否阻止了端口8000")
    
    check_browser_console()

if __name__ == "__main__":
    main() 
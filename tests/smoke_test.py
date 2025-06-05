#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Oracle SP Parser - 完整冒烟测试
验证项目的所有关键功能是否正常工作
"""

import sys
import os
import subprocess
import requests
import json
import time
import threading
from pathlib import Path
from datetime import datetime

class SmokeTest:
    def __init__(self):
        self.project_root = Path(__file__).parent
        self.results = {}
        self.server_process = None
        self.base_url = "http://localhost:8000"
        
    def print_header(self, title):
        """打印测试章节标题"""
        print(f"\n{'='*80}")
        print(f"🧪 {title}")
        print('='*80)
        
    def print_test(self, test_name, status, details=""):
        """打印测试结果"""
        status_icon = "✅" if status else "❌"
        print(f"  {status_icon} {test_name}")
        if details:
            print(f"     {details}")
        self.results[test_name] = status
        
    def test_environment_setup(self):
        """测试环境设置"""
        self.print_header("环境设置检查")
        
        # 检查Python版本
        try:
            python_version = sys.version_info
            if python_version >= (3, 8):
                self.print_test("Python版本检查", True, f"Python {python_version.major}.{python_version.minor}.{python_version.micro}")
            else:
                self.print_test("Python版本检查", False, f"需要Python 3.8+，当前: {python_version.major}.{python_version.minor}")
        except Exception as e:
            self.print_test("Python版本检查", False, str(e))
            
        # 检查关键文件
        critical_files = [
            ("src/main.py", "核心分析模块"),
            ("backend/main.py", "后端服务"),
            ("frontend/package.json", "前端配置"),
            ("requirements.txt", "依赖配置"),
        ]
        
        for file_path, description in critical_files:
            file_exists = (self.project_root / file_path).exists()
            self.print_test(f"文件检查: {description}", file_exists, file_path)
            
    def test_dependencies(self):
        """测试依赖安装"""
        self.print_header("依赖检查")
        
        # 检查Python依赖
        python_deps = ["sqlparse", "networkx", "pydantic", "fastapi", "uvicorn"]
        for dep in python_deps:
            try:
                __import__(dep)
                self.print_test(f"Python依赖: {dep}", True)
            except ImportError:
                self.print_test(f"Python依赖: {dep}", False, "未安装")
                
        # 检查前端依赖
        try:
            result = subprocess.run(
                ["npm", "--version"], 
                capture_output=True, 
                text=True, 
                cwd=self.project_root / "frontend"
            )
            if result.returncode == 0:
                self.print_test("npm可用性", True, f"版本: {result.stdout.strip()}")
            else:
                self.print_test("npm可用性", False)
        except FileNotFoundError:
            self.print_test("npm可用性", False, "npm未安装")
            
    def test_frontend_build(self):
        """测试前端构建"""
        self.print_header("前端构建测试")
        
        frontend_dir = self.project_root / "frontend"
        if not frontend_dir.exists():
            self.print_test("前端目录", False, "前端目录不存在")
            return
            
        try:
            # 检查是否已有构建文件
            build_dir = frontend_dir / "build"
            if build_dir.exists():
                self.print_test("前端构建目录", True, "build目录已存在")
            else:
                self.print_test("前端构建目录", False, "需要构建前端")
                
            # 检查关键构建文件
            build_files = [
                ("build/index.html", "主页面"),
                ("build/static/js", "JavaScript文件"),
                ("build/static/css", "CSS文件"),
                ("build/manifest.json", "应用清单"),
            ]
            
            for file_path, description in build_files:
                file_exists = (frontend_dir / file_path).exists()
                self.print_test(f"构建文件: {description}", file_exists, file_path)
                
        except Exception as e:
            self.print_test("前端构建检查", False, str(e))
            
    def test_core_analysis(self):
        """测试核心分析功能"""
        self.print_header("核心分析功能测试")
        
        try:
            # 导入核心模块
            sys.path.insert(0, str(self.project_root / "src"))
            from main import OracleSPAnalyzer
            
            self.print_test("核心模块导入", True)
            
            # 创建分析器实例
            analyzer = OracleSPAnalyzer()
            self.print_test("分析器实例化", True)
            
            # 测试简单的存储过程分析
            test_sp = """
            CREATE OR REPLACE PROCEDURE test_proc AS
            BEGIN
                SELECT * FROM employees;
                INSERT INTO logs VALUES ('test');
            END;
            """
            
            result = analyzer.analyze(test_sp)
            self.print_test("存储过程分析", True, f"找到 {len(result.sp_structure.sql_statements)} 个SQL语句")
            
        except Exception as e:
            self.print_test("核心分析功能", False, str(e))
            
    def start_backend_server(self):
        """启动后端服务器"""
        try:
            backend_dir = self.project_root / "backend"
            # 正确设置环境变量
            env = os.environ.copy()
            env["PYTHONPATH"] = f"{self.project_root / 'src'}:{self.project_root}"
            
            self.server_process = subprocess.Popen(
                [sys.executable, "-m", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"],
                cwd=backend_dir,
                env=env,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )
            
            # 等待服务器启动
            time.sleep(3)
            return True
        except Exception as e:
            print(f"启动服务器失败: {e}")
            return False
            
    def stop_backend_server(self):
        """停止后端服务器"""
        if self.server_process:
            self.server_process.terminate()
            self.server_process.wait()
            
    def test_backend_api(self):
        """测试后端API"""
        self.print_header("后端API测试")
        
        # 启动服务器
        print("🚀 启动后端服务器...")
        server_started = self.start_backend_server()
        
        if not server_started:
            self.print_test("服务器启动", False)
            return
            
        try:
            # 等待服务器完全启动
            max_retries = 10
            for i in range(max_retries):
                try:
                    response = requests.get(f"{self.base_url}/api/health", timeout=2)
                    if response.status_code == 200:
                        break
                except:
                    if i < max_retries - 1:
                        time.sleep(1)
                    else:
                        raise
                        
            # 测试健康检查
            response = requests.get(f"{self.base_url}/api/health", timeout=5)
            self.print_test("健康检查API", response.status_code == 200, f"状态码: {response.status_code}")
            
            # 测试主页
            response = requests.get(f"{self.base_url}/", timeout=5)
            self.print_test("主页访问", response.status_code == 200, f"状态码: {response.status_code}")
            
            # 测试静态资源
            response = requests.get(f"{self.base_url}/manifest.json", timeout=5)
            self.print_test("manifest.json", response.status_code == 200, f"状态码: {response.status_code}")
            
            response = requests.get(f"{self.base_url}/favicon.ico", timeout=5)
            self.print_test("favicon.ico", response.status_code == 200, f"状态码: {response.status_code}")
            
            # 测试分析API
            test_data = {
                "stored_procedure": "CREATE PROCEDURE test AS BEGIN SELECT * FROM users; END;"
            }
            response = requests.post(f"{self.base_url}/api/analyze", json=test_data, timeout=10)
            self.print_test("分析API", response.status_code == 200, f"状态码: {response.status_code}")
            
            if response.status_code == 200:
                result = response.json()
                success = result.get("success", False)
                self.print_test("分析结果", success, f"消息: {result.get('message', '')}")
                
        except Exception as e:
            self.print_test("API测试", False, str(e))
        finally:
            self.stop_backend_server()
            
    def test_deployment_packages(self):
        """测试部署包"""
        self.print_header("部署包测试")
        
        # 测试简化部署包生成
        try:
            result = subprocess.run(
                [sys.executable, "deploy_simple.py"],
                capture_output=True,
                text=True,
                timeout=120
            )
            
            success = result.returncode == 0 and "🎉 简化部署包创建完成" in result.stdout
            self.print_test("简化部署包生成", success)
            
            if success:
                # 检查生成的包
                dist_dir = self.project_root / "dist"
                if dist_dir.exists():
                    packages = list(dist_dir.glob("oracle-sp-parser-simple-*"))
                    # 过滤出目录（不是zip文件）
                    package_dirs = [p for p in packages if p.is_dir()]
                    if package_dirs:
                        latest_package = max(package_dirs, key=lambda p: p.stat().st_mtime)
                        self.print_test("部署包验证", True, f"生成包: {latest_package.name}")
                        
                        # 验证包内容
                        required_files = [
                            "start.bat",
                            "backend/main.py",
                            "backend/static/index.html",
                            "src/main.py",
                            "requirements.txt",
                            "diagnose_deployment.py"
                        ]
                        
                        missing_files = []
                        for file_path in required_files:
                            if not (latest_package / file_path).exists():
                                missing_files.append(file_path)
                        
                        if not missing_files:
                            self.print_test("部署包完整性", True, "所有必需文件存在")
                        else:
                            self.print_test("部署包完整性", False, f"缺少文件: {missing_files}")
                    else:
                        self.print_test("部署包验证", False, "未找到生成的包目录")
                else:
                    self.print_test("部署包验证", False, "dist目录不存在")
            
        except subprocess.TimeoutExpired:
            self.print_test("简化部署包生成", False, "超时")
        except Exception as e:
            self.print_test("简化部署包生成", False, str(e))
            
    def test_verification_tools(self):
        """测试验证工具"""
        self.print_header("验证工具测试")
        
        # 测试验证脚本是否能正常运行
        try:
            # 找到最新的部署包
            dist_dir = self.project_root / "dist"
            if dist_dir.exists():
                packages = list(dist_dir.glob("oracle-sp-parser-*"))
                # 过滤出目录（不是zip文件）
                package_dirs = [p for p in packages if p.is_dir()]
                if package_dirs:
                    latest_package = max(package_dirs, key=lambda p: p.stat().st_mtime)
                    
                    # 测试验证脚本
                    result = subprocess.run(
                        [sys.executable, "verify_deployment.py", str(latest_package)],
                        capture_output=True,
                        text=True,
                        timeout=30
                    )
                    
                    success = result.returncode == 0 and "🎉 验证通过" in result.stdout
                    self.print_test("部署包验证脚本", success)
                    
                    if not success and result.stderr:
                        print(f"     错误: {result.stderr.strip()}")
                    if not success and result.stdout:
                        print(f"     输出: {result.stdout.strip()[-200:]}")  # 只显示最后200字符
                else:
                    self.print_test("部署包验证脚本", False, "没有找到部署包目录")
            else:
                self.print_test("部署包验证脚本", False, "dist目录不存在")
                
        except Exception as e:
            self.print_test("验证工具", False, str(e))
            
    def generate_report(self):
        """生成测试报告"""
        self.print_header("测试报告")
        
        total_tests = len(self.results)
        passed_tests = sum(1 for result in self.results.values() if result)
        failed_tests = total_tests - passed_tests
        
        print(f"📊 测试统计:")
        print(f"   总测试数: {total_tests}")
        print(f"   通过: {passed_tests} ✅")
        print(f"   失败: {failed_tests} ❌")
        print(f"   成功率: {(passed_tests/total_tests*100):.1f}%")
        
        if failed_tests > 0:
            print(f"\n❌ 失败的测试:")
            for test_name, result in self.results.items():
                if not result:
                    print(f"   - {test_name}")
                    
        # 生成JSON报告
        report = {
            "timestamp": datetime.now().isoformat(),
            "total_tests": total_tests,
            "passed_tests": passed_tests,
            "failed_tests": failed_tests,
            "success_rate": passed_tests/total_tests*100,
            "results": self.results
        }
        
        report_file = self.project_root / "smoke_test_report.json"
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        
        print(f"\n📄 详细报告已保存到: {report_file}")
        
        return failed_tests == 0
        
    def run_all_tests(self):
        """运行所有测试"""
        print("🧪 Oracle SP Parser - 完整冒烟测试")
        print(f"开始时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        try:
            self.test_environment_setup()
            self.test_dependencies()
            self.test_frontend_build()
            self.test_core_analysis()
            self.test_backend_api()
            self.test_deployment_packages()
            self.test_verification_tools()
            
        except KeyboardInterrupt:
            print("\n\n⚠️ 测试被用户中断")
            return False
        except Exception as e:
            print(f"\n\n❌ 测试过程中发生未预期错误: {e}")
            return False
        finally:
            self.stop_backend_server()
            
        return self.generate_report()

def main():
    """主函数"""
    import os
    
    smoke_test = SmokeTest()
    success = smoke_test.run_all_tests()
    
    if success:
        print("\n🎉 所有冒烟测试通过！项目状态正常。")
        sys.exit(0)
    else:
        print("\n⚠️ 部分测试失败，请检查上述错误并修复。")
        sys.exit(1)

if __name__ == "__main__":
    main() 
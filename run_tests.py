#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试运行脚本
提供各种测试运行选项和便捷命令
"""

import sys
import os
import subprocess
import argparse
from pathlib import Path
import time
from typing import List, Optional

def run_command(cmd: List[str], description: str = None) -> int:
    """运行命令并返回退出码"""
    if description:
        print(f"\n🔄 {description}")
    
    print(f"执行命令: {' '.join(cmd)}")
    
    try:
        result = subprocess.run(cmd, check=False, capture_output=False)
        return result.returncode
    except KeyboardInterrupt:
        print("\n❌ 测试被用户中断")
        return 1
    except Exception as e:
        print(f"❌ 执行命令时出错: {e}")
        return 1

def install_test_dependencies():
    """安装测试依赖"""
    print("📦 安装测试依赖...")
    
    # 安装测试依赖
    cmd = [sys.executable, "-m", "pip", "install", "-r", "requirements-test.txt"]
    return run_command(cmd, "安装测试依赖包")

def run_unit_tests():
    """运行单元测试"""
    cmd = [
        "python", "-m", "pytest", 
        "tests/unit/", 
        "-v", 
        "--tb=short",
        "-m", "unit"
    ]
    return run_command(cmd, "运行单元测试")

def run_integration_tests():
    """运行集成测试"""
    cmd = [
        "python", "-m", "pytest", 
        "tests/integration/", 
        "-v", 
        "--tb=short",
        "-m", "integration"
    ]
    return run_command(cmd, "运行集成测试")

def run_api_tests():
    """运行API测试"""
    cmd = [
        "python", "-m", "pytest", 
        "tests/api/", 
        "-v", 
        "--tb=short",
        "-m", "api"
    ]
    return run_command(cmd, "运行API测试")

def run_performance_tests():
    """运行性能测试"""
    cmd = [
        "python", "-m", "pytest", 
        "tests/performance/", 
        "-v", 
        "--tb=short",
        "-m", "performance",
        "-s"  # 显示print输出
    ]
    return run_command(cmd, "运行性能测试")

def run_smoke_tests():
    """运行冒烟测试"""
    cmd = [
        "python", "-m", "pytest", 
        "-v", 
        "--tb=short",
        "-m", "smoke",
        "--maxfail=1"  # 第一个失败就停止
    ]
    return run_command(cmd, "运行冒烟测试")

def run_all_tests():
    """运行所有测试"""
    cmd = [
        "python", "-m", "pytest", 
        "tests/", 
        "-v", 
        "--tb=short"
    ]
    return run_command(cmd, "运行所有测试")

def run_coverage_tests():
    """运行测试并生成覆盖率报告"""
    cmd = [
        "python", "-m", "pytest", 
        "tests/", 
        "--cov=src", 
        "--cov=backend",
        "--cov-report=html:test_results/coverage_html",
        "--cov-report=xml:test_results/coverage.xml",
        "--cov-report=term-missing",
        "--html=test_results/report.html",
        "--self-contained-html"
    ]
    return run_command(cmd, "运行测试并生成覆盖率报告")

def run_parallel_tests():
    """并行运行测试"""
    cmd = [
        "python", "-m", "pytest", 
        "tests/", 
        "-n", "auto",  # 自动确定进程数
        "-v"
    ]
    return run_command(cmd, "并行运行测试")

def run_specific_test(test_path: str):
    """运行特定测试"""
    cmd = [
        "python", "-m", "pytest", 
        test_path, 
        "-v", 
        "--tb=short"
    ]
    return run_command(cmd, f"运行特定测试: {test_path}")

def run_tests_by_keyword(keyword: str):
    """根据关键字运行测试"""
    cmd = [
        "python", "-m", "pytest", 
        "-k", keyword,
        "-v", 
        "--tb=short"
    ]
    return run_command(cmd, f"运行包含关键字 '{keyword}' 的测试")

def run_failed_tests():
    """重新运行失败的测试"""
    cmd = [
        "python", "-m", "pytest", 
        "--lf",  # last failed
        "-v", 
        "--tb=short"
    ]
    return run_command(cmd, "重新运行失败的测试")

def run_tests_with_timeout():
    """运行测试并设置超时"""
    cmd = [
        "python", "-m", "pytest", 
        "tests/", 
        "--timeout=300",  # 5分钟超时
        "-v"
    ]
    return run_command(cmd, "运行测试（设置超时）")

def clean_test_artifacts():
    """清理测试产生的文件"""
    print("🧹 清理测试产生的文件...")
    
    artifacts = [
        "test_results/",
        ".pytest_cache/",
        "__pycache__/",
        "*.pyc",
        ".coverage",
        "coverage.xml",
        "htmlcov/"
    ]
    
    for artifact in artifacts:
        if Path(artifact).exists():
            if Path(artifact).is_dir():
                import shutil
                shutil.rmtree(artifact)
                print(f"删除目录: {artifact}")
            else:
                os.remove(artifact)
                print(f"删除文件: {artifact}")

def setup_test_environment():
    """设置测试环境"""
    print("🔧 设置测试环境...")
    
    # 创建测试结果目录
    test_results_dir = Path("test_results")
    test_results_dir.mkdir(exist_ok=True)
    
    # 安装依赖
    if install_test_dependencies() != 0:
        print("❌ 依赖安装失败")
        return 1
    
    print("✅ 测试环境设置完成")
    return 0

def show_test_results():
    """显示测试结果"""
    results_dir = Path("test_results")
    
    if not results_dir.exists():
        print("❌ 未找到测试结果目录")
        return
    
    print("\n📊 测试结果文件:")
    for file in results_dir.glob("*"):
        if file.is_file():
            print(f"  📄 {file.name}")
    
    # 显示覆盖率报告路径
    coverage_html = results_dir / "coverage_html" / "index.html"
    if coverage_html.exists():
        print(f"\n🌐 覆盖率报告: file://{coverage_html.absolute()}")
    
    # 显示测试报告路径
    test_report = results_dir / "report.html"
    if test_report.exists():
        print(f"📋 测试报告: file://{test_report.absolute()}")

def main():
    """主函数"""
    parser = argparse.ArgumentParser(
        description="Oracle存储过程分析工具测试运行器",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例用法:
  python run_tests.py --all                    # 运行所有测试
  python run_tests.py --unit                   # 运行单元测试
  python run_tests.py --integration            # 运行集成测试
  python run_tests.py --api                    # 运行API测试
  python run_tests.py --performance            # 运行性能测试
  python run_tests.py --smoke                  # 运行冒烟测试
  python run_tests.py --coverage               # 运行测试并生成覆盖率
  python run_tests.py --parallel               # 并行运行测试
  python run_tests.py --specific tests/unit/test_parser.py  # 运行特定测试
  python run_tests.py --keyword "parser"       # 运行包含关键字的测试
  python run_tests.py --failed                 # 重新运行失败的测试
  python run_tests.py --setup                  # 设置测试环境
  python run_tests.py --clean                  # 清理测试文件
  python run_tests.py --results                # 显示测试结果
        """
    )
    
    # 测试类型选项
    parser.add_argument("--all", action="store_true", help="运行所有测试")
    parser.add_argument("--unit", action="store_true", help="运行单元测试")
    parser.add_argument("--integration", action="store_true", help="运行集成测试")
    parser.add_argument("--api", action="store_true", help="运行API测试")
    parser.add_argument("--performance", action="store_true", help="运行性能测试")
    parser.add_argument("--smoke", action="store_true", help="运行冒烟测试")
    
    # 特殊选项
    parser.add_argument("--coverage", action="store_true", help="运行测试并生成覆盖率报告")
    parser.add_argument("--parallel", action="store_true", help="并行运行测试")
    parser.add_argument("--timeout", action="store_true", help="运行测试并设置超时")
    parser.add_argument("--failed", action="store_true", help="重新运行失败的测试")
    
    # 特定测试选项
    parser.add_argument("--specific", metavar="PATH", help="运行特定测试文件或目录")
    parser.add_argument("--keyword", metavar="KEYWORD", help="根据关键字运行测试")
    
    # 环境和清理选项
    parser.add_argument("--setup", action="store_true", help="设置测试环境")
    parser.add_argument("--clean", action="store_true", help="清理测试产生的文件")
    parser.add_argument("--results", action="store_true", help="显示测试结果")
    
    # 详细输出选项
    parser.add_argument("--verbose", "-v", action="store_true", help="详细输出")
    parser.add_argument("--quiet", "-q", action="store_true", help="安静模式")
    
    args = parser.parse_args()
    
    # 如果没有提供任何参数，显示帮助
    if len(sys.argv) == 1:
        parser.print_help()
        return 0
    
    start_time = time.time()
    exit_code = 0
    
    try:
        # 环境设置
        if args.setup:
            exit_code = setup_test_environment()
            if exit_code != 0:
                return exit_code
        
        # 清理操作
        if args.clean:
            clean_test_artifacts()
            return 0
        
        # 显示结果
        if args.results:
            show_test_results()
            return 0
        
        # 运行测试
        if args.all:
            exit_code = run_all_tests()
        elif args.unit:
            exit_code = run_unit_tests()
        elif args.integration:
            exit_code = run_integration_tests()
        elif args.api:
            exit_code = run_api_tests()
        elif args.performance:
            exit_code = run_performance_tests()
        elif args.smoke:
            exit_code = run_smoke_tests()
        elif args.coverage:
            exit_code = run_coverage_tests()
        elif args.parallel:
            exit_code = run_parallel_tests()
        elif args.timeout:
            exit_code = run_tests_with_timeout()
        elif args.failed:
            exit_code = run_failed_tests()
        elif args.specific:
            exit_code = run_specific_test(args.specific)
        elif args.keyword:
            exit_code = run_tests_by_keyword(args.keyword)
        else:
            print("❌ 请指定要运行的测试类型")
            parser.print_help()
            return 1
        
        # 总结
        end_time = time.time()
        duration = end_time - start_time
        
        print(f"\n⏱️  总执行时间: {duration:.2f}秒")
        
        if exit_code == 0:
            print("✅ 所有测试通过!")
            if args.coverage or args.all:
                show_test_results()
        else:
            print("❌ 测试失败!")
        
        return exit_code
        
    except KeyboardInterrupt:
        print("\n❌ 测试被用户中断")
        return 1
    except Exception as e:
        print(f"❌ 运行测试时出现错误: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main()) 
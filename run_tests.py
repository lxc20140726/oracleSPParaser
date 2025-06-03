#!/usr/bin/env python3
"""
Oracle SP Parser 测试运行脚本

提供多种测试运行选项：
- 单元测试
- 集成测试
- API测试
- 完整测试套件
- 性能测试
"""

import sys
import os
import argparse
import subprocess
from pathlib import Path


def run_command(cmd, description=""):
    """运行命令并显示结果"""
    print(f"🚀 {description}")
    print(f"执行命令: {' '.join(cmd)}")
    print("-" * 50)
    
    result = subprocess.run(cmd, capture_output=False)
    
    if result.returncode == 0:
        print(f"✅ {description} 成功完成")
    else:
        print(f"❌ {description} 失败 (退出码: {result.returncode})")
    
    print("=" * 50)
    return result.returncode


def setup_environment():
    """设置测试环境"""
    # 确保当前目录在Python路径中
    current_dir = Path(__file__).parent
    src_dir = current_dir / "src"
    backend_dir = current_dir / "backend"
    
    paths_to_add = [str(current_dir), str(src_dir), str(backend_dir)]
    
    for path in paths_to_add:
        if path not in sys.path:
            sys.path.insert(0, path)
    
    # 设置环境变量
    os.environ["PYTHONPATH"] = ":".join(paths_to_add)
    os.environ["TESTING"] = "true"
    
    # 创建docs目录结构
    docs_dir = current_dir / "docs"
    test_reports_dir = docs_dir / "test_reports"
    coverage_dir = docs_dir / "coverage"
    
    for dir_path in [docs_dir, test_reports_dir, coverage_dir]:
        dir_path.mkdir(exist_ok=True)


def run_unit_tests(verbose=False):
    """运行单元测试"""
    cmd = ["pytest", "tests/unit/", "-m", "unit"]
    if verbose:
        cmd.extend(["-v", "-s"])
    cmd.extend(["--tb=short"])
    
    return run_command(cmd, "运行单元测试")


def run_integration_tests(verbose=False):
    """运行集成测试"""
    cmd = ["pytest", "tests/integration/", "-m", "integration"]
    if verbose:
        cmd.extend(["-v", "-s"])
    cmd.extend(["--tb=short"])
    
    return run_command(cmd, "运行集成测试")


def run_api_tests(verbose=False):
    """运行API测试"""
    cmd = ["pytest", "tests/api/", "-m", "api"]
    if verbose:
        cmd.extend(["-v", "-s"])
    cmd.extend(["--tb=short"])
    
    return run_command(cmd, "运行API测试")


def run_performance_tests(verbose=False):
    """运行性能测试"""
    cmd = ["pytest", "tests/", "-m", "performance"]
    if verbose:
        cmd.extend(["-v", "-s"])
    cmd.extend(["--tb=short", "--benchmark-only"])
    
    return run_command(cmd, "运行性能测试")


def run_smoke_tests(verbose=False):
    """运行冒烟测试"""
    cmd = ["pytest", "tests/", "-m", "smoke"]
    if verbose:
        cmd.extend(["-v", "-s"])
    cmd.extend(["--tb=short"])
    
    return run_command(cmd, "运行冒烟测试")


def run_all_tests(verbose=False, coverage=True):
    """运行完整测试套件"""
    cmd = ["pytest", "tests/"]
    
    if verbose:
        cmd.extend(["-v", "-s"])
    
    if coverage:
        cmd.extend([
            "--cov=src",
            "--cov=backend", 
            "--cov-report=term-missing",
            "--cov-report=html:docs/coverage",
            "--cov-report=xml:docs/test_reports/coverage.xml"
        ])
    
    cmd.extend(["--tb=short"])
    
    return run_command(cmd, "运行完整测试套件")


def run_specific_test(test_path, verbose=False):
    """运行特定测试"""
    cmd = ["pytest", test_path]
    if verbose:
        cmd.extend(["-v", "-s"])
    cmd.extend(["--tb=short"])
    
    return run_command(cmd, f"运行特定测试: {test_path}")


def install_test_dependencies():
    """安装测试依赖"""
    cmd = ["pip", "install", "-r", "test_requirements.txt"]
    return run_command(cmd, "安装测试依赖")


def generate_test_report():
    """生成测试报告"""
    cmd = [
        "pytest", "tests/",
        "--html=docs/test_reports/report.html",
        "--self-contained-html",
        "--json-report",
        "--json-report-file=docs/test_reports/report.json",
        "--cov=src",
        "--cov=backend",
        "--cov-report=html:docs/coverage",
        "--cov-report=xml:docs/test_reports/coverage.xml"
    ]
    
    return run_command(cmd, "生成测试报告")


def lint_code():
    """代码质量检查"""
    print("🔍 代码质量检查")
    
    # Black 格式化检查
    black_cmd = ["black", "--check", "src/", "backend/", "tests/"]
    black_result = run_command(black_cmd, "Black 格式化检查")
    
    # Flake8 语法检查
    flake8_cmd = ["flake8", "src/", "backend/", "tests/"]
    flake8_result = run_command(flake8_cmd, "Flake8 语法检查")
    
    # isort 导入排序检查
    isort_cmd = ["isort", "--check-only", "src/", "backend/", "tests/"]
    isort_result = run_command(isort_cmd, "isort 导入排序检查")
    
    return max(black_result, flake8_result, isort_result)


def main():
    """主函数"""
    parser = argparse.ArgumentParser(description="Oracle SP Parser 测试运行器")
    
    parser.add_argument("--unit", action="store_true", help="运行单元测试")
    parser.add_argument("--integration", action="store_true", help="运行集成测试")
    parser.add_argument("--api", action="store_true", help="运行API测试")
    parser.add_argument("--performance", action="store_true", help="运行性能测试")
    parser.add_argument("--smoke", action="store_true", help="运行冒烟测试")
    parser.add_argument("--all", action="store_true", help="运行完整测试套件")
    parser.add_argument("--test", type=str, help="运行特定测试文件或目录")
    parser.add_argument("--install-deps", action="store_true", help="安装测试依赖")
    parser.add_argument("--report", action="store_true", help="生成测试报告")
    parser.add_argument("--lint", action="store_true", help="运行代码质量检查")
    parser.add_argument("--verbose", "-v", action="store_true", help="详细输出")
    parser.add_argument("--no-coverage", action="store_true", help="跳过覆盖率报告")
    
    args = parser.parse_args()
    
    # 设置环境
    setup_environment()
    
    exit_code = 0
    
    try:
        if args.install_deps:
            exit_code = max(exit_code, install_test_dependencies())
        
        if args.lint:
            exit_code = max(exit_code, lint_code())
        
        if args.unit:
            exit_code = max(exit_code, run_unit_tests(args.verbose))
        
        if args.integration:
            exit_code = max(exit_code, run_integration_tests(args.verbose))
        
        if args.api:
            exit_code = max(exit_code, run_api_tests(args.verbose))
        
        if args.performance:
            exit_code = max(exit_code, run_performance_tests(args.verbose))
        
        if args.smoke:
            exit_code = max(exit_code, run_smoke_tests(args.verbose))
        
        if args.test:
            exit_code = max(exit_code, run_specific_test(args.test, args.verbose))
        
        if args.report:
            exit_code = max(exit_code, generate_test_report())
        
        if args.all or not any([args.unit, args.integration, args.api, args.performance, 
                              args.smoke, args.test, args.install_deps, args.report, args.lint]):
            # 如果没有指定特定选项，运行完整测试套件
            exit_code = max(exit_code, run_all_tests(args.verbose, not args.no_coverage))
    
    except KeyboardInterrupt:
        print("\n⚠️ 测试被用户中断")
        exit_code = 1
    except Exception as e:
        print(f"\n❌ 测试运行过程中出现错误: {e}")
        exit_code = 1
    
    # 输出结果摘要
    print("\n" + "=" * 60)
    if exit_code == 0:
        print("🎉 所有测试成功完成！")
        print(f"📊 测试报告: docs/test_reports/report.html")
        print(f"📈 覆盖率报告: docs/coverage/index.html")
    else:
        print(f"⚠️ 测试完成，但有 {exit_code} 个失败")
    print("=" * 60)
    
    sys.exit(exit_code)


if __name__ == "__main__":
    main() 
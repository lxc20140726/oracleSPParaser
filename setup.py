#!/usr/bin/env python3
"""
Oracle SP Parser - 项目安装配置
支持一键部署和环境搭建
"""

import os
import sys
from pathlib import Path
from setuptools import setup, find_packages
from setuptools.command.develop import develop
from setuptools.command.install import install


def read_file(filename):
    """读取文件内容"""
    file_path = Path(__file__).parent / filename
    if file_path.exists():
        with open(file_path, "r", encoding="utf-8") as f:
            return f.read()
    return ""


def parse_requirements(filename):
    """解析requirements文件"""
    content = read_file(filename)
    requirements = []
    for line in content.splitlines():
        line = line.strip()
        if line and not line.startswith("#") and not line.startswith("-"):
            requirements.append(line)
    return requirements


def get_version():
    """获取版本号"""
    version_file = Path(__file__).parent / "src" / "__init__.py"
    if version_file.exists():
        content = read_file("src/__init__.py")
        for line in content.splitlines():
            if line.startswith("__version__"):
                return line.split("=")[1].strip().strip("\"'")
    return "1.0.0"


class PostDevelopCommand(develop):
    """开发模式安装后的后处理"""
    def run(self):
        develop.run(self)
        self.execute_post_install()

    def execute_post_install(self):
        """执行安装后的配置"""
        print("🔧 配置开发环境...")
        
        # 创建必要的目录
        dirs_to_create = [
            "data/input",
            "data/output", 
            "logs",
            "docs/test_reports",
            "docs/coverage"
        ]
        
        for dir_path in dirs_to_create:
            Path(dir_path).mkdir(parents=True, exist_ok=True)
            print(f"  ✅ 创建目录: {dir_path}")
        
        # 创建.gitkeep文件
        gitkeep_files = [
            "data/input/.gitkeep",
            "data/output/.gitkeep",
            "logs/.gitkeep"
        ]
        
        for gitkeep_file in gitkeep_files:
            gitkeep_path = Path(gitkeep_file)
            gitkeep_path.touch(exist_ok=True)
        
        print("✅ 开发环境配置完成！")


class PostInstallCommand(install):
    """生产模式安装后的后处理"""
    def run(self):
        install.run(self)
        self.execute_post_install()

    def execute_post_install(self):
        """执行安装后的配置"""
        print("🚀 配置生产环境...")
        
        # 创建运行时必要的目录
        dirs_to_create = [
            "data/input",
            "data/output",
            "logs"
        ]
        
        for dir_path in dirs_to_create:
            Path(dir_path).mkdir(parents=True, exist_ok=True)
            print(f"  ✅ 创建目录: {dir_path}")
        
        print("✅ 生产环境配置完成！")
        print("\n🎉 Oracle SP Parser 安装完成！")
        print("📖 使用方法:")
        print("  - 命令行: oracle-sp-parser --help")
        print("  - Web服务: oracle-sp-backend")
        print("  - Python模块: import oracle_sp_parser")


# 读取长描述
long_description = read_file("README.md")

# 解析依赖文件
install_requires = parse_requirements("requirements.txt")
test_requires = parse_requirements("test_requirements.txt")

# 开发依赖 (从test_requirements.txt中提取)
dev_requires = [
    "pytest>=7.0.0",
    "pytest-cov>=4.0.0", 
    "pytest-mock>=3.10.0",
    "black>=23.0.0",
    "flake8>=6.0.0",
    "isort>=5.12.0",
    "mypy>=1.0.0",
]

# 测试依赖 (完整的测试套件)
test_extra_requires = test_requires

# 文档依赖
docs_requires = [
    "sphinx>=4.0.0",
    "sphinx-rtd-theme>=1.0.0",
    "myst-parser>=0.18.0",
]

# API服务依赖 (用于独立部署API服务)
api_requires = [
    "fastapi[all]>=0.100.0",
    "uvicorn[standard]>=0.20.0",
    "python-multipart>=0.0.5",
]

# 获取所有Python包
packages = find_packages(where="src")

# 总是包含oracle_sp_parser.py作为py_modules
py_modules = ["oracle_sp_parser"]

setup(
    # 基本信息
    name="oracle-sp-parser",
    version=get_version(),
    author="Oracle SP Parser Team",
    author_email="oracle-sp-parser@example.com",
    description="Oracle存储过程解析和分析工具 - 企业级SQL代码分析平台",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/oracleSPParaser",
    project_urls={
        "Bug Reports": "https://github.com/yourusername/oracleSPParaser/issues",
        "Source": "https://github.com/yourusername/oracleSPParaser",
        "Documentation": "https://github.com/yourusername/oracleSPParaser/blob/main/README.md",
    },
    
    # 包配置
    packages=packages,
    py_modules=py_modules,
    package_dir={"": "src"},
    
    # 包含数据文件
    include_package_data=True,
    package_data={
        "": [
            "*.md",
            "*.txt", 
            "*.yaml",
            "*.yml",
            "*.json",
            "config/*.yaml",
            "config/*.json",
            "templates/*.html",
            "static/*",
        ],
    },
    
    # 分类信息
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Intended Audience :: System Administrators", 
        "Intended Audience :: Information Technology",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Database :: Database Engines/Servers",
        "Topic :: Software Development :: Code Generators",
        "Topic :: Software Development :: Testing",
        "Topic :: Text Processing :: Linguistic",
    ],
    
    # Python版本要求
    python_requires=">=3.8",
    
    # 核心依赖
    install_requires=install_requires,
    
    # 可选依赖
    extras_require={
        # 开发环境 (代码质量工具)
        "dev": dev_requires,
        
        # 测试环境 (完整测试套件)
        "test": test_extra_requires,
        
        # 文档生成
        "docs": docs_requires,
        
        # API服务部署
        "api": api_requires,
        
        # 完整安装 (包含所有功能)
        "all": list(set(dev_requires + test_extra_requires + docs_requires + api_requires)),
        
        # 生产环境 (仅核心功能 + API)
        "prod": api_requires,
    },
    
    # 命令行入口点
    entry_points={
        "console_scripts": [
            # 主程序入口
            "oracle-sp-parser=main:main",
            
            # Web服务入口  
            "oracle-sp-backend=backend.main:start_server",
            
            # 测试运行器
            "oracle-sp-test=run_tests:main",
            
            # 工具脚本
            "oracle-sp-analyze=main:analyze_file",
        ],
    },
    
    # 自定义命令
    cmdclass={
        "develop": PostDevelopCommand,
        "install": PostInstallCommand,
    },
    
    # 配置选项
    zip_safe=False,
    
    # 关键词
    keywords=[
        "oracle", "sql", "parser", "analyzer", "stored-procedure", 
        "database", "code-analysis", "ast", "fastapi", "web-service"
    ],
    
    # 许可证
    license="MIT",
    
    # 平台兼容性
    platforms=["any"],
) 
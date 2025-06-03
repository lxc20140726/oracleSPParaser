#!/bin/bash

# Oracle SP Parser 自动部署脚本
# 用于在新主机上快速部署项目

set -e  # 遇到错误立即退出

echo "🚀 Oracle SP Parser 自动部署脚本"
echo "=================================="

# 检查Python版本
check_python() {
    if ! command -v python3 &> /dev/null; then
        echo "❌ 错误: 未找到 python3，请先安装 Python 3.8+"
        exit 1
    fi
    
    python_version=$(python3 -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')")
    echo "✅ 检测到 Python $python_version"
    
    if [[ $(echo "$python_version >= 3.8" | bc -l) != 1 ]]; then
        echo "❌ 错误: 需要 Python 3.8 或更高版本，当前版本: $python_version"
        exit 1
    fi
}

# 创建虚拟环境
setup_venv() {
    echo "🔧 创建虚拟环境..."
    if [ -d "venv" ]; then
        echo "⚠️  虚拟环境已存在，删除旧环境..."
        rm -rf venv
    fi
    
    python3 -m venv venv
    source venv/bin/activate
    echo "✅ 虚拟环境创建完成"
}

# 安装依赖
install_dependencies() {
    echo "📦 安装项目依赖..."
    
    # 升级pip
    pip install --upgrade pip
    
    # 安装项目依赖
    if [ -f "requirements.txt" ]; then
        pip install -r requirements.txt
        echo "✅ 依赖安装完成"
    else
        echo "❌ 错误: 未找到 requirements.txt 文件"
        exit 1
    fi
}

# 检查项目结构
check_project_structure() {
    echo "🔍 检查项目结构..."
    
    required_dirs=("src" "backend" "config")
    required_files=("requirements.txt" "run_backend.py")
    
    for dir in "${required_dirs[@]}"; do
        if [ ! -d "$dir" ]; then
            echo "❌ 错误: 缺少必需的目录: $dir"
            exit 1
        fi
    done
    
    for file in "${required_files[@]}"; do
        if [ ! -f "$file" ]; then
            echo "❌ 错误: 缺少必需的文件: $file"
            exit 1
        fi
    done
    
    echo "✅ 项目结构检查通过"
}

# 创建必要的目录
create_directories() {
    echo "📁 创建必要的目录..."
    
    dirs=("logs" "data/input" "data/output" "data/cache")
    
    for dir in "${dirs[@]}"; do
        mkdir -p "$dir"
        echo "✅ 创建目录: $dir"
    done
}

# 设置权限
set_permissions() {
    echo "🔐 设置文件权限..."
    
    if [ -f "run_backend.py" ]; then
        chmod +x run_backend.py
    fi
    
    if [ -d "scripts" ]; then
        chmod +x scripts/*.py 2>/dev/null || true
    fi
    
    echo "✅ 权限设置完成"
}

# 测试部署
test_deployment() {
    echo "🧪 测试部署..."
    
    # 简单的导入测试
    python3 -c "
import sys
import os
sys.path.insert(0, os.path.join(os.getcwd(), 'src'))
try:
    from analyzer.oracle_sp_analyzer import OracleSPAnalyzer
    print('✅ 核心模块导入成功')
except ImportError as e:
    print(f'❌ 模块导入失败: {e}')
    sys.exit(1)
"
}

# 显示启动信息
show_startup_info() {
    echo ""
    echo "🎉 部署完成!"
    echo "============="
    echo ""
    echo "启动服务:"
    echo "  python3 run_backend.py"
    echo ""
    echo "服务访问:"
    echo "  Web界面: http://localhost:8000"
    echo "  API文档: http://localhost:8000/api/docs"
    echo "  健康检查: http://localhost:8000/api/health"
    echo ""
    echo "开发模式:"
    echo "  source venv/bin/activate"
    echo "  cd backend"
    echo "  uvicorn main:app --host 0.0.0.0 --port 8000 --reload"
    echo ""
}

# 主程序
main() {
    echo "开始部署 Oracle SP Parser..."
    
    check_python
    check_project_structure
    setup_venv
    install_dependencies
    create_directories
    set_permissions
    test_deployment
    show_startup_info
    
    echo "✅ 部署完成，可以启动服务了！"
}

# 如果直接执行此脚本
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    main "$@"
fi 
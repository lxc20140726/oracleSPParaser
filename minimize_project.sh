#!/bin/bash

# Oracle SP Parser 项目精简脚本
# 只保留运行项目所需的核心文件和目录

set -e

echo "🧹 Oracle SP Parser 项目精简化"
echo "=============================="
echo ""
echo "⚠️  这将删除以下非核心内容："
echo "   - 开发和构建工具"
echo "   - 示例和测试文件"
echo "   - 文档和说明（除README）"
echo "   - 容器化配置"
echo "   - 临时和缓存文件"
echo "   - 前端源码（保留构建文件）"
echo ""
echo "✅ 保留的核心内容："
echo "   - 核心源代码 (src/)"
echo "   - 后端API服务 (backend/)"
echo "   - 基础配置 (config/)"
echo "   - 依赖文件 (requirements.txt)"
echo "   - 启动脚本 (run_backend.py)"
echo "   - 项目说明 (README.md)"
echo ""

# 确认操作
read -p "是否继续精简化项目？(y/N): " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "❌ 已取消操作"
    exit 1
fi

echo "开始精简化..."

# 删除开发工具和脚本
cleanup_development_files() {
    echo "🗑️  删除开发工具和脚本..."
    
    rm -rf scripts/ 2>/dev/null || true
    rm -rf tests/ 2>/dev/null || true
    rm -f start_fullstack.py 2>/dev/null || true
    
    echo "✅ 开发工具清理完成"
}

# 删除文档和示例
cleanup_docs_and_examples() {
    echo "📚 删除文档和示例..."
    
    rm -rf docs/ 2>/dev/null || true
    rm -rf examples/ 2>/dev/null || true
    
    echo "✅ 文档和示例清理完成"
}

# 删除容器化和部署配置
cleanup_deployment_configs() {
    echo "🐳 删除容器化和部署配置..."
    
    rm -rf docker/ 2>/dev/null || true
    
    echo "✅ 部署配置清理完成"
}

# 清理前端（保留构建文件但删除源码）
cleanup_frontend() {
    echo "🎨 处理前端文件..."
    
    if [ -d "frontend" ]; then
        # 保留构建文件，删除源码和依赖
        rm -rf frontend/src/ 2>/dev/null || true
        rm -rf frontend/public/ 2>/dev/null || true  
        rm -rf frontend/node_modules/ 2>/dev/null || true
        rm -f frontend/package*.json 2>/dev/null || true
        rm -f frontend/tsconfig.json 2>/dev/null || true
        rm -f frontend/tailwind.config.js 2>/dev/null || true
        
        # 如果没有构建文件，删除整个frontend目录
        if [ ! -d "frontend/build" ]; then
            rm -rf frontend/ 2>/dev/null || true
            echo "   删除了整个frontend目录（无构建文件）"
        else
            echo "   保留了frontend/build/构建文件"
        fi
    fi
    
    echo "✅ 前端处理完成"
}

# 清理临时和缓存文件
cleanup_temp_files() {
    echo "🧽 清理临时和缓存文件..."
    
    rm -rf temp/ 2>/dev/null || true
    rm -rf releases/ 2>/dev/null || true
    rm -rf logs/ 2>/dev/null || true
    rm -rf __pycache__/ 2>/dev/null || true
    
    # 清理Python缓存
    find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
    find . -name "*.pyc" -delete 2>/dev/null || true
    find . -name "*.pyo" -delete 2>/dev/null || true
    
    # 清理系统文件
    find . -name ".DS_Store" -delete 2>/dev/null || true
    find . -name "Thumbs.db" -delete 2>/dev/null || true
    
    echo "✅ 临时文件清理完成"
}

# 简化数据目录
simplify_data_directory() {
    echo "📁 简化数据目录..."
    
    if [ -d "data" ]; then
        # 保留目录结构但清空内容
        find data/ -type f -delete 2>/dev/null || true
        
        # 确保基本目录存在
        mkdir -p data/input 2>/dev/null || true
        mkdir -p data/output 2>/dev/null || true
        
        # 创建说明文件
        cat > data/README.md << 'EOF'
# 数据目录

- `input/` - 存放输入的存储过程文件
- `output/` - 存放分析结果和报告

此目录在运行时会自动创建所需文件。
EOF
    fi
    
    echo "✅ 数据目录简化完成"
}

# 删除虚拟环境（应该由用户重新创建）
cleanup_venv() {
    echo "🐍 删除虚拟环境..."
    
    rm -rf venv/ 2>/dev/null || true
    echo "   虚拟环境已删除，部署时需要重新创建"
    
    echo "✅ 虚拟环境清理完成"
}

# 简化配置目录
simplify_config() {
    echo "⚙️  简化配置目录..."
    
    if [ -d "config" ]; then
        # 只保留基础配置文件
        find config/ -name "*.yml" -o -name "*.yaml" -o -name "*.json" | head -2 | while read file; do
            echo "   保留配置文件: $file"
        done
        
        # 删除过多的配置文件（保留前2个）
        find config/ -name "*.yml" -o -name "*.yaml" -o -name "*.json" | tail -n +3 | xargs rm -f 2>/dev/null || true
    fi
    
    echo "✅ 配置简化完成"
}

# 创建精简版README
create_minimal_readme() {
    echo "📝 创建精简版README..."
    
    cat > README.md << 'EOF'
# Oracle SP Parser

Oracle存储过程分析工具 - 精简版

## 🚀 快速开始

### 1. 环境准备
```bash
# 创建虚拟环境
python3 -m venv venv
source venv/bin/activate

# 安装依赖
pip install -r requirements.txt
```

### 2. 启动服务
```bash
python3 run_backend.py
```

### 3. 访问服务
- **Web界面**: http://localhost:8000
- **API文档**: http://localhost:8000/api/docs

## 📋 功能特性

- ✅ Oracle存储过程解析
- ✅ 数据流向分析  
- ✅ 表关系识别
- ✅ 参数依赖分析
- ✅ RESTful API接口
- ✅ Web可视化界面

## 🛠️ 使用方法

### API调用
```bash
curl -X POST http://localhost:8000/api/analyze \
  -H "Content-Type: application/json" \
  -d '{
    "stored_procedure": "CREATE OR REPLACE PROCEDURE test_proc AS BEGIN SELECT * FROM users; END;"
  }'
```

### Web界面
访问 http://localhost:8000 使用图形界面进行分析。

## 📁 项目结构

```
oracleSPParaser/
├── src/                    # 核心分析引擎
├── backend/               # FastAPI后端服务
├── config/                # 配置文件
├── data/                  # 数据目录
├── requirements.txt       # 依赖清单
├── setup.py              # 安装配置
├── run_backend.py        # 启动脚本
└── README.md             # 项目说明
```

## 🔧 开发说明

这是精简版本，包含核心功能。如需完整开发环境，请：
1. 添加测试用例
2. 配置开发工具
3. 设置前端构建环境

---
*Oracle SP Parser - 精简版*
EOF
    
    echo "✅ 精简版README创建完成"
}

# 更新gitignore
update_gitignore() {
    echo "📄 更新.gitignore..."
    
    cat > .gitignore << 'EOF'
# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
venv/
env/
ENV/

# IDEs
.vscode/
.idea/
*.swp
*.swo

# OS
.DS_Store
Thumbs.db

# Logs
*.log
logs/

# Data
data/input/*
data/output/*
!data/input/.gitkeep
!data/output/.gitkeep

# Temporary
temp/
*.tmp
*.bak

# Build
build/
dist/
*.egg-info/
EOF
    
    # 创建gitkeep文件
    mkdir -p data/input data/output
    touch data/input/.gitkeep data/output/.gitkeep
    
    echo "✅ .gitignore更新完成"
}

# 显示精简结果
show_results() {
    echo ""
    echo "🎉 项目精简化完成!"
    echo "=================="
    echo ""
    echo "📊 精简统计:"
    
    # 计算目录和文件数量
    dir_count=$(find . -type d -not -path "./.git*" -not -path "./venv*" | wc -l)
    file_count=$(find . -type f -not -path "./.git*" -not -path "./venv*" | wc -l)
    
    echo "- 📁 目录数: $dir_count"
    echo "- 📄 文件数: $file_count"
    echo ""
    
    echo "📂 保留的核心目录:"
    ls -la | grep "^d" | grep -v -E "(\.git|venv)" | awk '{print "   📁 " $9}'
    echo ""
    
    echo "📄 保留的核心文件:"
    ls -la | grep "^-" | awk '{print "   📄 " $9}'
    echo ""
    
    echo "🚀 下一步操作:"
    echo "1. 创建虚拟环境: python3 -m venv venv"
    echo "2. 激活环境: source venv/bin/activate"  
    echo "3. 安装依赖: pip install -r requirements.txt"
    echo "4. 启动服务: python3 run_backend.py"
    echo ""
    
    echo "✅ 项目已精简为核心功能版本！"
}

# 主程序
main() {
    cleanup_development_files
    cleanup_docs_and_examples
    cleanup_deployment_configs
    cleanup_frontend
    cleanup_temp_files
    simplify_data_directory
    cleanup_venv
    simplify_config
    cleanup_temp_files  # 再次清理，确保彻底
    create_minimal_readme
    update_gitignore
    show_results
}

# 执行主程序
main "$@" 
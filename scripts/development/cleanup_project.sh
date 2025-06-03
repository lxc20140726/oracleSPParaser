#!/bin/bash

# Oracle SP Parser 项目目录整理脚本
# 清理临时文件，优化项目结构

set -e

echo "🧹 Oracle SP Parser 项目目录整理"
echo "================================"

# 创建整理目录
create_organization_dirs() {
    echo "📁 创建组织目录..."
    
    # 创建releases目录用于存放打包文件
    mkdir -p releases
    
    # 创建temp目录用于临时文件
    mkdir -p temp
    
    # 确保logs目录存在
    mkdir -p logs
    
    echo "✅ 目录创建完成"
}

# 清理构建文件
cleanup_build_files() {
    echo "🗑️  清理构建文件..."
    
    # 清理Python构建文件
    if [ -d "build" ]; then
        echo "删除build目录..."
        rm -rf build
    fi
    
    if [ -d "src/oracle_sp_parser.egg-info" ]; then
        echo "删除egg-info目录..."
        rm -rf src/oracle_sp_parser.egg-info
    fi
    
    # 清理临时虚拟环境
    if [ -d "build_venv" ]; then
        echo "删除构建用临时虚拟环境..."
        rm -rf build_venv
    fi
    
    echo "✅ 构建文件清理完成"
}

# 清理缓存文件
cleanup_cache_files() {
    echo "🧽 清理缓存文件..."
    
    # 清理Python缓存
    find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
    find . -name "*.pyc" -delete 2>/dev/null || true
    find . -name "*.pyo" -delete 2>/dev/null || true
    
    # 清理系统文件
    find . -name ".DS_Store" -delete 2>/dev/null || true
    find . -name "Thumbs.db" -delete 2>/dev/null || true
    
    # 清理临时文件
    find . -name "*.tmp" -delete 2>/dev/null || true
    find . -name "*.bak" -delete 2>/dev/null || true
    
    # 清理日志文件（保留目录）
    if [ -d "logs" ]; then
        find logs -name "*.log" -type f -delete 2>/dev/null || true
    fi
    
    echo "✅ 缓存文件清理完成"
}

# 移动打包文件到releases目录
move_package_files() {
    echo "📦 整理打包文件..."
    
    # 移动tar.gz文件
    if ls oracle-sp-parser-*.tar.gz 1> /dev/null 2>&1; then
        echo "移动压缩包文件到releases目录..."
        mv oracle-sp-parser-*.tar.gz releases/ 2>/dev/null || true
    fi
    
    # 移动dist目录内容到releases
    if [ -d "dist" ]; then
        echo "移动Python包到releases目录..."
        mkdir -p releases/python-packages
        mv dist/* releases/python-packages/ 2>/dev/null || true
        rmdir dist 2>/dev/null || true
    fi
    
    echo "✅ 打包文件整理完成"
}

# 整理文档文件
organize_docs() {
    echo "📚 整理文档文件..."
    
    # 创建docs子目录
    mkdir -p docs/deployment
    mkdir -p docs/development
    mkdir -p docs/api
    
    # 移动部署相关文档
    if [ -f "DEPLOYMENT_GUIDE.md" ]; then
        mv DEPLOYMENT_GUIDE.md docs/deployment/
    fi
    
    if [ -f "QUICK_DEPLOYMENT.md" ]; then
        mv QUICK_DEPLOYMENT.md docs/deployment/
    fi
    
    if [ -f "START_GUIDE.md" ]; then
        mv START_GUIDE.md docs/deployment/
    fi
    
    # 移动开发相关文档
    if [ -f "PROJECT_STRUCTURE.md" ]; then
        mv PROJECT_STRUCTURE.md docs/development/
    fi
    
    if [ -f "DIRECTORY_STRUCTURE_REPORT.md" ]; then
        mv DIRECTORY_STRUCTURE_REPORT.md docs/development/
    fi
    
    echo "✅ 文档整理完成"
}

# 创建工具脚本目录
organize_scripts() {
    echo "🔧 整理脚本文件..."
    
    # 创建scripts子目录
    mkdir -p scripts/deployment
    mkdir -p scripts/development
    mkdir -p scripts/packaging
    
    # 移动部署脚本
    if [ -f "deploy.sh" ]; then
        mv deploy.sh scripts/deployment/
    fi
    
    # 移动打包脚本
    if [ -f "package.sh" ]; then
        mv package.sh scripts/packaging/
    fi
    
    # 移动当前脚本到开发工具
    # （注意：这个脚本运行完后会移动自己）
    
    # 移动测试脚本
    if [ -f "test_backend.py" ]; then
        mv test_backend.py scripts/development/
    fi
    
    echo "✅ 脚本整理完成"
}

# 清理空目录
cleanup_empty_dirs() {
    echo "🗂️  清理空目录..."
    
    # 删除空目录（但保留重要的结构目录）
    find . -type d -empty -not -path "./venv*" -not -path "./.git*" \
           -not -path "./logs" -not -path "./data*" \
           -not -path "./temp" -not -path "./releases*" \
           -not -path "./docs*" -not -path "./scripts*" \
           -delete 2>/dev/null || true
    
    echo "✅ 空目录清理完成"
}

# 生成新的目录结构报告
generate_structure_report() {
    echo "📊 生成整理后的目录结构报告..."
    
    cat > "docs/development/PROJECT_STRUCTURE_CLEAN.md" << 'EOF'
# Oracle SP Parser 整理后的项目结构

## 📁 目录组织

```
oracleSPParaser/
├── 📂 src/                     # 核心源代码
│   ├── analyzer/               # 分析引擎
│   ├── models/                 # 数据模型
│   ├── parser/                 # 解析器
│   ├── utils/                  # 工具类
│   └── visualizer/            # 可视化
├── 📂 backend/                 # FastAPI后端服务
├── 📂 frontend/               # React前端（可选）
├── 📂 config/                 # 配置文件
├── 📂 tests/                  # 测试用例
├── 📂 examples/               # 示例文件
├── 📂 docker/                 # 容器化配置
├── 📂 docs/                   # 文档目录
│   ├── deployment/            # 部署文档
│   ├── development/           # 开发文档
│   └── api/                   # API文档
├── 📂 scripts/                # 脚本工具
│   ├── deployment/            # 部署脚本
│   ├── development/           # 开发脚本
│   └── packaging/             # 打包脚本
├── 📂 releases/               # 发布文件
│   └── python-packages/       # Python包
├── 📂 logs/                   # 日志文件
├── 📂 data/                   # 数据目录
│   ├── input/                 # 输入数据
│   ├── output/                # 输出数据
│   └── cache/                 # 缓存数据
├── 📂 temp/                   # 临时文件
├── 📂 venv/                   # 虚拟环境
├── 📄 README.md               # 项目说明
├── 📄 requirements.txt        # 依赖清单
├── 📄 setup.py               # 安装配置
├── 📄 .gitignore             # Git忽略
└── 📄 run_backend.py         # 快速启动脚本
```

## 🎯 目录说明

### 核心代码目录
- `src/` - 核心分析引擎代码
- `backend/` - Web API服务
- `frontend/` - Web界面（可选）

### 配置和数据
- `config/` - 应用配置文件
- `data/` - 数据存储目录
- `logs/` - 运行日志

### 工具和脚本
- `scripts/deployment/` - 部署相关脚本
- `scripts/packaging/` - 打包相关脚本  
- `scripts/development/` - 开发工具脚本

### 文档
- `docs/deployment/` - 部署指南
- `docs/development/` - 开发文档
- `docs/api/` - API文档

### 发布和构建
- `releases/` - 打包好的发布文件
- `temp/` - 临时文件目录

## 🚀 使用方式

### 快速启动
```bash
python3 run_backend.py
```

### 部署到新环境
```bash
# 使用部署脚本
./scripts/deployment/deploy.sh
```

### 打包项目
```bash
# 使用打包脚本
./scripts/packaging/package.sh
```

### 开发模式
```bash
# 激活虚拟环境
source venv/bin/activate

# 运行测试
python scripts/development/test_backend.py
```

---
*整理完成时间: $(date)*
EOF
    
    echo "✅ 结构报告生成完成"
}

# 更新README文件
update_readme() {
    echo "📝 更新README文件..."
    
    # 在README中添加整理说明（如果还没有的话）
    if ! grep -q "项目结构整理" README.md; then
        cat >> README.md << 'EOF'

## 📁 项目结构整理

项目已经过整理，采用标准化目录结构：

- **核心代码**: `src/`, `backend/`, `frontend/`
- **脚本工具**: `scripts/`（按功能分类）
- **文档**: `docs/`（按类型分类）
- **发布文件**: `releases/`
- **配置数据**: `config/`, `data/`, `logs/`

详细结构说明请查看: `docs/development/PROJECT_STRUCTURE_CLEAN.md`

### 常用命令

```bash
# 快速启动
python3 run_backend.py

# 部署
./scripts/deployment/deploy.sh

# 打包
./scripts/packaging/package.sh
```
EOF
    fi
    
    echo "✅ README更新完成"
}

# 设置脚本权限
set_permissions() {
    echo "🔐 设置脚本权限..."
    
    # 为scripts目录下的所有.sh文件设置执行权限
    find scripts -name "*.sh" -type f -exec chmod +x {} \; 2>/dev/null || true
    find scripts -name "*.py" -type f -exec chmod +x {} \; 2>/dev/null || true
    
    # 为根目录的启动脚本设置权限
    chmod +x run_backend.py 2>/dev/null || true
    chmod +x start_fullstack.py 2>/dev/null || true
    
    echo "✅ 权限设置完成"
}

# 显示整理结果
show_results() {
    echo ""
    echo "🎉 项目目录整理完成!"
    echo "===================="
    echo ""
    echo "📊 整理统计:"
    echo "- 🗑️  清理了构建文件和缓存"
    echo "- 📁 创建了标准化目录结构"
    echo "- 📦 整理了打包和发布文件"
    echo "- 📚 重新组织了文档结构"
    echo "- 🔧 分类整理了脚本工具"
    echo ""
    echo "📂 主要目录:"
    ls -la | grep "^d" | grep -E "(docs|scripts|releases|src|backend|config)"
    echo ""
    echo "🚀 下一步:"
    echo "1. 查看新结构: docs/development/PROJECT_STRUCTURE_CLEAN.md"
    echo "2. 快速启动: python3 run_backend.py"
    echo "3. 部署脚本: ./scripts/deployment/deploy.sh"
    echo "4. 打包脚本: ./scripts/packaging/package.sh"
    echo ""
}

# 主程序
main() {
    echo "开始整理项目目录..."
    
    create_organization_dirs
    cleanup_build_files
    cleanup_cache_files
    move_package_files
    organize_docs
    organize_scripts
    cleanup_empty_dirs
    generate_structure_report
    update_readme
    set_permissions
    
    show_results
    
    echo "✅ 整理完成！"
    
    # 最后移动自己到开发脚本目录
    echo "📝 移动整理脚本到scripts/development/目录..."
    mv "$0" scripts/development/ 2>/dev/null || echo "注意：无法移动脚本文件"
}

# 确认执行
echo "⚠️  此操作将重新组织项目目录结构"
echo "是否继续？(y/N)"
read -r response
if [[ "$response" =~ ^[Yy]$ ]]; then
    main "$@"
else
    echo "❌ 已取消操作"
    exit 0
fi 
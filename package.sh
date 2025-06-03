#!/bin/bash

# Oracle SP Parser 项目打包脚本
# 用于创建可分发的项目压缩包

set -e

echo "📦 Oracle SP Parser 项目打包"
echo "============================"

# 获取项目版本
get_version() {
    if [ -f "setup.py" ]; then
        version=$(python3 -c "
import re
with open('setup.py', 'r') as f:
    content = f.read()
    match = re.search(r'version=[\"\'](.*?)[\"\']', content)
    print(match.group(1) if match else '1.0.0')
")
    else
        version="1.0.0"
    fi
    echo "$version"
}

# 清理项目
cleanup_project() {
    echo "🧹 清理项目..."
    
    # 删除Python缓存文件
    find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
    find . -name "*.pyc" -delete 2>/dev/null || true
    find . -name "*.pyo" -delete 2>/dev/null || true
    
    # 删除系统文件
    find . -name ".DS_Store" -delete 2>/dev/null || true
    find . -name "Thumbs.db" -delete 2>/dev/null || true
    
    # 删除临时文件
    find . -name "*.tmp" -delete 2>/dev/null || true
    find . -name "*.log" -delete 2>/dev/null || true
    
    echo "✅ 项目清理完成"
}

# 创建分发包
create_package() {
    local version=$1
    local package_name="oracle-sp-parser-v${version}"
    local timestamp=$(date +"%Y%m%d_%H%M%S")
    
    echo "📦 创建项目包: ${package_name}"
    
    # 要排除的文件和目录
    exclude_patterns=(
        "venv"
        ".git"
        "__pycache__"
        "*.pyc"
        "*.pyo"
        ".DS_Store"
        "Thumbs.db"
        "*.tmp"
        "*.log"
        "node_modules"
        ".pytest_cache"
        ".coverage"
        "htmlcov"
        "dist"
        "build"
        "*.egg-info"
        ".env"
        ".env.local"
        "frontend/build"
        "frontend/node_modules"
    )
    
    # 构建tar排除选项
    exclude_opts=""
    for pattern in "${exclude_patterns[@]}"; do
        exclude_opts="${exclude_opts} --exclude='${pattern}'"
    done
    
    # 创建完整包（包含frontend源码）
    echo "创建完整包（包含前端源码）..."
    eval "tar ${exclude_opts} -czf ${package_name}-full.tar.gz ."
    
    # 创建后端专用包（仅后端，适合纯API使用）
    echo "创建后端专用包（仅API服务）..."
    backend_exclude_opts="${exclude_opts} --exclude='frontend'"
    eval "tar ${backend_exclude_opts} -czf ${package_name}-backend-only.tar.gz ."
    
    # 创建带时间戳的备份包
    echo "创建备份包..."
    eval "tar ${exclude_opts} -czf ${package_name}_${timestamp}.tar.gz ."
    
    echo "✅ 包创建完成:"
    echo "   📄 ${package_name}-full.tar.gz        (完整版: 包含前端源码)"
    echo "   📄 ${package_name}-backend-only.tar.gz (轻量版: 仅后端API)"
    echo "   📄 ${package_name}_${timestamp}.tar.gz  (备份版)"
}

# 创建Docker构建包
create_docker_package() {
    local version=$1
    
    echo "🐳 创建Docker构建包..."
    
    if [ ! -d "docker" ]; then
        echo "⚠️  未找到docker目录，跳过Docker包创建"
        return
    fi
    
    # 检查Docker是否可用
    if ! command -v docker &> /dev/null; then
        echo "⚠️  Docker未安装，跳过Docker镜像构建"
        return
    fi
    
    # 构建Docker镜像
    echo "构建Docker镜像..."
    docker build -f docker/Dockerfile -t oracle-sp-parser:${version} .
    docker build -f docker/Dockerfile -t oracle-sp-parser:latest .
    
    # 保存Docker镜像
    echo "保存Docker镜像..."
    docker save -o oracle-sp-parser-v${version}.tar oracle-sp-parser:${version}
    
    # 压缩镜像文件
    gzip oracle-sp-parser-v${version}.tar
    
    echo "✅ Docker包创建完成:"
    echo "   🐳 oracle-sp-parser-v${version}.tar.gz"
}

# 创建安装包
create_wheel_package() {
    echo "🎡 创建Python安装包..."
    
    if [ ! -f "setup.py" ]; then
        echo "⚠️  未找到setup.py，跳过wheel包创建"
        return
    fi
    
    # 创建虚拟环境用于构建
    if [ ! -d "build_venv" ]; then
        python3 -m venv build_venv
    fi
    
    source build_venv/bin/activate
    
    # 安装构建工具
    pip install --upgrade pip setuptools wheel build
    
    # 构建包
    python setup.py sdist bdist_wheel
    
    # 清理构建环境
    deactivate
    rm -rf build_venv
    
    echo "✅ Python包创建完成:"
    if [ -d "dist" ]; then
        ls -la dist/
    fi
}

# 生成部署文档
create_deployment_docs() {
    local version=$1
    
    echo "📚 生成部署文档..."
    
    cat > "DEPLOYMENT_GUIDE.md" << EOF
# Oracle SP Parser v${version} 部署指南

## 📦 部署包内容

- \`oracle-sp-parser-v${version}.tar.gz\` - 完整项目源码
- \`deploy.sh\` - 自动部署脚本
- \`DEPLOYMENT_GUIDE.md\` - 本部署指南

## 🚀 快速部署

### 方法一：使用自动部署脚本（推荐）

\`\`\`bash
# 1. 解压项目
tar -xzf oracle-sp-parser-v${version}.tar.gz
cd oracleSPParaser

# 2. 运行自动部署脚本
chmod +x deploy.sh
./deploy.sh

# 3. 启动服务
python3 run_backend.py
\`\`\`

### 方法二：手动部署

\`\`\`bash
# 1. 解压项目
tar -xzf oracle-sp-parser-v${version}.tar.gz
cd oracleSPParaser

# 2. 创建虚拟环境
python3 -m venv venv
source venv/bin/activate

# 3. 安装依赖
pip install -r requirements.txt

# 4. 启动服务
python3 run_backend.py
\`\`\`

### 方法三：Docker部署（如果有Docker镜像）

\`\`\`bash
# 加载Docker镜像
docker load -i oracle-sp-parser-v${version}.tar.gz

# 运行容器
docker run -d -p 8000:8000 --name oracle-sp-parser oracle-sp-parser:${version}
\`\`\`

## 📋 系统要求

- Python 3.8 或更高版本
- 2GB+ 可用内存
- 1GB+ 可用磁盘空间

## 🔧 配置说明

- 服务端口：8000
- Web界面：http://localhost:8000
- API文档：http://localhost:8000/api/docs

## 🆘 故障排除

### 端口占用
\`\`\`bash
lsof -ti:8000 | xargs kill -9
\`\`\`

### 权限问题
\`\`\`bash
chmod +x run_backend.py
chmod +x deploy.sh
\`\`\`

### 依赖问题
\`\`\`bash
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
\`\`\`

## 📞 技术支持

如遇问题，请检查：
1. Python版本是否符合要求
2. 网络连接是否正常
3. 防火墙是否允许8000端口
4. 虚拟环境是否正确激活

---
*Oracle SP Parser v${version} - $(date +"%Y-%m-%d")*
EOF
    
    echo "✅ 部署文档创建完成: DEPLOYMENT_GUIDE.md"
}

# 显示包信息
show_package_info() {
    local version=$1
    
    echo ""
    echo "🎉 打包完成!"
    echo "============="
    echo ""
    echo "📦 创建的文件:"
    ls -lh oracle-sp-parser-v${version}* 2>/dev/null || true
    ls -lh DEPLOYMENT_GUIDE.md 2>/dev/null || true
    
    if [ -d "dist" ]; then
        echo ""
        echo "🎡 Python包:"
        ls -lh dist/ 2>/dev/null || true
    fi
    
    echo ""
    echo "📋 推荐使用场景:"
    echo "🔹 oracle-sp-parser-v${version}-backend-only.tar.gz - API服务部署（推荐）"
    echo "   - 体积小，启动快"
    echo "   - 仅包含后端API服务"
    echo "   - 适合纯API使用场景"
    echo ""
    echo "🔹 oracle-sp-parser-v${version}-full.tar.gz - 完整项目部署"
    echo "   - 包含前端源码"
    echo "   - 支持前端开发和构建"
    echo "   - 适合需要Web界面的场景"
    echo ""
    echo "📋 部署步骤（后端专用版）:"
    echo "1. 将 oracle-sp-parser-v${version}-backend-only.tar.gz 复制到目标服务器"
    echo "2. 解压: tar -xzf oracle-sp-parser-v${version}-backend-only.tar.gz"
    echo "3. 进入目录: cd oracleSPParaser"
    echo "4. 运行部署脚本: ./deploy.sh"
    echo "5. 启动服务: python3 run_backend.py"
    echo "6. 访问API: http://localhost:8000/api/docs"
    echo ""
}

# 主程序
main() {
    echo "开始打包 Oracle SP Parser..."
    
    # 获取版本信息
    version=$(get_version)
    echo "📋 项目版本: $version"
    
    # 清理项目
    cleanup_project
    
    # 创建各种包
    create_package "$version"
    create_wheel_package
    # create_docker_package "$version"  # 可选，需要Docker
    
    # 生成部署文档
    create_deployment_docs "$version"
    
    # 显示包信息
    show_package_info "$version"
    
    echo "✅ 打包完成！"
}

# 如果直接执行此脚本
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    main "$@"
fi 
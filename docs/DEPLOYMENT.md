# Oracle SP Parser 一键部署指南

本文档提供了Oracle SP Parser的多种部署方式，支持不同的使用场景。

## 🚀 快速开始

### 方式1：使用一键安装脚本（推荐）

```bash
# 克隆项目
git clone <repository-url>
cd oracleSPParaser

# 运行一键安装脚本
python3 install.py
```

### 方式2：使用pip安装

```bash
# 开发环境安装（包含所有依赖）
pip install -e .[dev,test,docs,api]

# 生产环境安装（核心功能+API）
pip install .[prod]

# 最小安装（仅核心功能）
pip install .
```

## 📦 安装模式详解

### 🛠️ 开发模式 (dev)

适用于开发人员，包含完整功能：

```bash
# 使用安装脚本
python3 install.py --mode dev --create-shortcuts

# 手动安装
pip install -e .[dev,test,docs,api]
```

**包含组件：**
- ✅ 核心解析功能
- ✅ Web API服务
- ✅ 测试框架（90+测试用例）
- ✅ 代码质量工具（Black、Flake8、isort）
- ✅ 文档生成工具
- ✅ 开发时热重载

### 🏭 生产模式 (prod)

适用于生产环境部署：

```bash
# 使用安装脚本
python3 install.py --mode prod

# 手动安装
pip install .[prod]
```

**包含组件：**
- ✅ 核心解析功能
- ✅ Web API服务
- ✅ 高性能运行时
- ❌ 开发工具
- ❌ 测试框架

### 🧪 测试模式 (test)

适用于CI/CD和测试环境：

```bash
# 使用安装脚本
python3 install.py --mode test

# 手动安装
pip install -e .[test]
```

**包含组件：**
- ✅ 核心解析功能
- ✅ 完整测试套件
- ✅ 测试报告生成
- ✅ 覆盖率分析

### 🌐 API模式 (api)

仅部署Web API服务：

```bash
# 使用安装脚本
python3 install.py --mode api

# 手动安装
pip install .[api]
```

**包含组件：**
- ✅ 核心解析功能
- ✅ FastAPI Web服务
- ✅ Web界面
- ❌ 开发工具
- ❌ 测试框架

### 💎 最小模式 (minimal)

仅核心功能，适用于嵌入式使用：

```bash
# 使用安装脚本
python3 install.py --mode minimal

# 手动安装
pip install .
```

**包含组件：**
- ✅ 核心解析功能
- ❌ Web API服务
- ❌ 开发工具
- ❌ 测试框架

## 🔧 环境要求

### 系统要求
- **Python**: 3.8+ (推荐 3.9+)
- **操作系统**: Windows, macOS, Linux
- **内存**: 最少 2GB RAM
- **磁盘**: 最少 1GB 可用空间

### 依赖检查

安装脚本会自动检查：

```bash
# Python版本检查
python3 --version  # 应该 >= 3.8

# pip可用性检查
python3 -m pip --version

# 网络连接检查（下载依赖时需要）
```

## 🌐 Web服务部署

### 开发服务器

```bash
# 方式1：使用命令行工具
oracle-sp-backend

# 方式2：使用快捷脚本
python3 start_backend.py

# 方式3：使用uvicorn直接启动
python3 -m uvicorn backend.main:app --host 0.0.0.0 --port 8000 --reload
```

### 生产服务器

```bash
# 使用Gunicorn（推荐）
pip install gunicorn
gunicorn backend.main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000

# 使用uvicorn生产模式
python3 -m uvicorn backend.main:app --host 0.0.0.0 --port 8000 --workers 4
```

### Docker部署

```dockerfile
# Dockerfile
FROM python:3.9-slim

WORKDIR /app
COPY . .

RUN python3 install.py --mode prod --skip-verification

EXPOSE 8000
CMD ["oracle-sp-backend"]
```

```bash
# 构建和运行
docker build -t oracle-sp-parser .
docker run -p 8000:8000 oracle-sp-parser
```

## 📋 验证安装

### 自动验证

```bash
# 使用安装脚本自动验证
python3 install.py --mode dev

# 手动验证
python3 -c "import oracle_sp_parser; print(oracle_sp_parser.__version__)"
```

### 功能测试

```bash
# 运行快速测试
oracle-sp-test --smoke

# 运行完整测试套件
python3 run_tests.py --all

# 测试Web服务
curl http://localhost:8000/health
```

### 命令行测试

```bash
# 测试命令行工具
oracle-sp-parser --help

# 分析示例文件
oracle-sp-parser tests/data/sample_procedures.sql
```

## 🔄 更新和升级

### 升级到最新版本

```bash
# Git方式更新
git pull origin main
python3 install.py --mode dev

# pip方式更新（如果发布到PyPI）
pip install --upgrade oracle-sp-parser
```

### 重新安装

```bash
# 清理旧安装
pip uninstall oracle-sp-parser -y

# 重新安装
python3 install.py --mode dev
```

## 🛠️ 故障排除

### 常见问题

**1. Python版本过低**
```bash
# 检查版本
python3 --version

# 升级Python（macOS）
brew install python@3.9

# 升级Python（Ubuntu）
sudo apt update && sudo apt install python3.9
```

**2. pip权限问题**
```bash
# 使用用户安装
python3 install.py --mode dev

# 或使用虚拟环境
python3 -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
python3 install.py --mode dev
```

**3. 网络连接问题**
```bash
# 使用国内镜像
pip install -i https://pypi.tuna.tsinghua.edu.cn/simple .[dev]

# 离线安装（需要预先下载wheel文件）
pip install oracle-sp-parser --no-index --find-links ./wheels/
```

**4. 依赖冲突**
```bash
# 使用虚拟环境隔离
python3 -m venv clean_env
source clean_env/bin/activate
python3 install.py --mode dev
```

### 日志和调试

```bash
# 启用详细日志
export PYTHONPATH=src:backend:$PYTHONPATH
export TESTING=true
export DEBUG=true

# 查看安装日志
python3 install.py --mode dev 2>&1 | tee install.log

# 查看服务日志
oracle-sp-backend --log-level debug
```

## 📞 获取帮助

### 文档资源
- **项目README**: `README.md`
- **API文档**: 启动服务后访问 `http://localhost:8000/docs`
- **测试文档**: `tests/README.md`

### 社区支持
- **问题报告**: 在GitHub Issues中创建
- **功能请求**: 在GitHub Discussions中讨论
- **贡献代码**: 参考 `CONTRIBUTING.md`

### 快速联系
```bash
# 查看版本和帮助信息
oracle-sp-parser --version
oracle-sp-parser --help

# 运行健康检查
python3 -c "import oracle_sp_parser; oracle_sp_parser.info()"
```

---

## 🎉 部署完成！

恭喜！您已成功部署Oracle SP Parser。现在可以：

1. **使用命令行工具**：`oracle-sp-parser input.sql`
2. **启动Web服务**：`oracle-sp-backend`
3. **运行测试**：`oracle-sp-test --smoke`
4. **访问Web界面**：`http://localhost:8000`

享受使用Oracle SP Parser进行SQL代码分析吧！🚀 
# Oracle SP Parser 快速部署指南

## 🚀 一键部署（推荐）

```bash
# 1. 克隆项目
git clone <repository-url>
cd oracleSPParaser

# 2. 运行一键安装脚本
python3 install.py --mode dev --create-scripts

# 3. 激活虚拟环境
source venv/bin/activate

# 4. 验证安装
python -c "import oracle_sp_parser; oracle_sp_parser.info()"

# 5. 启动Web服务
oracle-sp-backend
```

## 📦 安装模式选择

| 模式 | 命令 | 适用场景 | 包含组件 |
|------|------|----------|----------|
| **开发模式** | `--mode dev` | 开发和调试 | 完整功能 + 开发工具 |
| **生产模式** | `--mode prod` | 生产部署 | 核心功能 + API服务 |
| **测试模式** | `--mode test` | CI/CD测试 | 核心功能 + 测试套件 |
| **API模式** | `--mode api` | 仅Web服务 | 核心功能 + FastAPI |
| **最小模式** | `--mode minimal` | 嵌入使用 | 仅核心解析功能 |

## 🔧 手动安装

```bash
# 创建虚拟环境
python3 -m venv venv
source venv/bin/activate

# 升级pip和构建工具
pip install --upgrade pip setuptools wheel

# 安装包（选择合适的模式）
pip install -e .[dev,test,docs,api]  # 开发模式
pip install .[prod]                  # 生产模式
pip install .[api]                   # API模式
pip install .                        # 最小模式
```

## 🌐 Web服务启动

```bash
# 方式1：使用命令行工具
oracle-sp-backend

# 方式2：使用uvicorn直接启动
python -m uvicorn backend.main:app --host 0.0.0.0 --port 8000 --reload

# 方式3：使用快捷脚本（如果创建了）
python start_backend_venv.py
```

## 🧪 验证安装

```bash
# 检查包版本
python -c "import oracle_sp_parser; print(oracle_sp_parser.__version__)"

# 显示包信息
python -c "import oracle_sp_parser; oracle_sp_parser.info()"

# 测试命令行工具
oracle-sp-parser --help

# 运行快速测试
oracle-sp-test --smoke
```

## 📋 命令行工具

安装后可用的命令：

- `oracle-sp-parser` - 主程序，SQL分析工具
- `oracle-sp-backend` - Web服务启动器
- `oracle-sp-test` - 测试运行器
- `oracle-sp-analyze` - 文件分析工具

## 🐳 Docker部署

```dockerfile
FROM python:3.9-slim
WORKDIR /app
COPY . .
RUN python3 install.py --mode prod --skip-verification
EXPOSE 8000
CMD ["oracle-sp-backend"]
```

```bash
docker build -t oracle-sp-parser .
docker run -p 8000:8000 oracle-sp-parser
```

## 🔍 故障排除

### 常见问题

**1. externally-managed-environment (macOS)**
```bash
# 解决方案：使用虚拟环境
python3 install.py --mode dev  # 自动创建虚拟环境
```

**2. ModuleNotFoundError**
```bash
# 检查虚拟环境是否激活
source venv/bin/activate
pip list | grep oracle
```

**3. 权限问题**
```bash
# 使用虚拟环境避免权限问题
python3 install.py --mode dev
```

## 📞 获取帮助

- **安装脚本帮助**: `python3 install.py --help`
- **详细文档**: `README_SETUP.md`
- **部署文档**: `DEPLOYMENT.md`
- **测试文档**: `tests/README.md`

## 🎉 快速开始示例

```bash
# 完整的开发环境设置
git clone <repository-url>
cd oracleSPParaser
python3 install.py --mode dev --create-scripts
source venv/bin/activate

# 验证安装
oracle-sp-parser --version
oracle-sp-backend &  # 后台启动Web服务
oracle-sp-test --smoke  # 运行快速测试

# 访问Web界面
open http://localhost:8000
```

---

**总结**: Oracle SP Parser提供了完整的一键部署解决方案，支持多种安装模式和部署场景。推荐使用 `python3 install.py` 进行自动化安装和配置。 
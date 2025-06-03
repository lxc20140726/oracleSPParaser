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

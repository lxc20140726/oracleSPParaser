# Oracle SP Parser v1.0.0 部署指南

## 📦 部署包内容

- `oracle-sp-parser-v1.0.0.tar.gz` - 完整项目源码
- `deploy.sh` - 自动部署脚本
- `DEPLOYMENT_GUIDE.md` - 本部署指南

## 🚀 快速部署

### 方法一：使用自动部署脚本（推荐）

```bash
# 1. 解压项目
tar -xzf oracle-sp-parser-v1.0.0.tar.gz
cd oracleSPParaser

# 2. 运行自动部署脚本
chmod +x deploy.sh
./deploy.sh

# 3. 启动服务
python3 run_backend.py
```

### 方法二：手动部署

```bash
# 1. 解压项目
tar -xzf oracle-sp-parser-v1.0.0.tar.gz
cd oracleSPParaser

# 2. 创建虚拟环境
python3 -m venv venv
source venv/bin/activate

# 3. 安装依赖
pip install -r requirements.txt

# 4. 启动服务
python3 run_backend.py
```

### 方法三：Docker部署（如果有Docker镜像）

```bash
# 加载Docker镜像
docker load -i oracle-sp-parser-v1.0.0.tar.gz

# 运行容器
docker run -d -p 8000:8000 --name oracle-sp-parser oracle-sp-parser:1.0.0
```

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
```bash
lsof -ti:8000 | xargs kill -9
```

### 权限问题
```bash
chmod +x run_backend.py
chmod +x deploy.sh
```

### 依赖问题
```bash
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
```

## 📞 技术支持

如遇问题，请检查：
1. Python版本是否符合要求
2. 网络连接是否正常
3. 防火墙是否允许8000端口
4. 虚拟环境是否正确激活

---
*Oracle SP Parser v1.0.0 - 2025-06-03*

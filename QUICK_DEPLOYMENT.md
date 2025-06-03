# Oracle SP Parser 快速部署指南

## 📋 项目概述

Oracle SP Parser是一个Oracle存储过程分析工具，包含以下组件：
- **后端服务**: FastAPI + Python (端口8000)
- **前端界面**: React (可选)
- **分析引擎**: Oracle存储过程解析和数据流分析
- **虚拟环境**: Python依赖隔离

## 🎯 部署场景

将现有项目（包含虚拟环境）打包并部署到新主机上。

## 🚀 快速部署（3种方法）

### 方法一：一键打包 + 自动部署 ⭐️ 推荐

#### 在原主机（当前机器）：
```bash
# 1. 运行打包脚本
./package.sh

# 2. 传输到目标主机
scp oracle-sp-parser-v1.0.0.tar.gz user@target-host:/tmp/
```

#### 在目标主机：
```bash
# 1. 解压项目
cd /path/to/deploy
tar -xzf /tmp/oracle-sp-parser-v1.0.0.tar.gz
cd oracleSPParaser

# 2. 自动部署
chmod +x deploy.sh
./deploy.sh

# 3. 启动服务
python3 run_backend.py
```

### 方法二：Docker容器化部署 🐳

#### 在原主机构建：
```bash
# 构建Docker镜像
docker build -f docker/Dockerfile -t oracle-sp-parser:latest .

# 保存镜像
docker save -o oracle-sp-parser.tar oracle-sp-parser:latest
gzip oracle-sp-parser.tar
```

#### 在目标主机部署：
```bash
# 加载镜像
docker load -i oracle-sp-parser.tar.gz

# 运行服务
docker run -d -p 8000:8000 --name oracle-sp-parser oracle-sp-parser:latest

# 或使用docker-compose
docker-compose -f docker/docker-compose.yml up -d
```

### 方法三：手动打包 + 部署

#### 在原主机：
```bash
# 手动打包（排除虚拟环境）
tar --exclude='venv' --exclude='.git' --exclude='__pycache__' \
    --exclude='*.pyc' --exclude='.DS_Store' --exclude='node_modules' \
    -czf oracle-sp-parser-manual.tar.gz .
```

#### 在目标主机：
```bash
# 解压并部署
tar -xzf oracle-sp-parser-manual.tar.gz
cd oracleSPParaser

# 手动创建环境
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# 启动服务
python3 run_backend.py
```

## 📋 系统要求

### 目标主机最低要求：
- **操作系统**: Linux/macOS/Windows
- **Python**: 3.8+ 版本
- **内存**: 2GB+
- **磁盘**: 1GB+ 可用空间
- **网络**: 8000端口可访问

### 可选要求：
- **Docker**: 如使用容器化部署
- **Git**: 如需要版本控制

## 🔧 配置说明

### 默认配置：
- **服务端口**: 8000
- **Web界面**: http://localhost:8000
- **API文档**: http://localhost:8000/api/docs
- **健康检查**: http://localhost:8000/api/health

### 自定义配置：
可修改 `config/` 目录下的配置文件。

## 🧪 验证部署

### 1. 健康检查
```bash
curl http://localhost:8000/api/health
```

### 2. API测试
```bash
curl -X POST http://localhost:8000/api/analyze \
  -H "Content-Type: application/json" \
  -d '{
    "stored_procedure": "CREATE OR REPLACE PROCEDURE test_proc AS BEGIN SELECT * FROM users; END;"
  }'
```

### 3. Web界面
访问: http://localhost:8000

## 🆘 常见问题

### Q1: 端口被占用
```bash
# 查找并杀死占用进程
lsof -ti:8000 | xargs kill -9
```

### Q2: Python版本不兼容
```bash
# 检查Python版本
python3 --version

# 使用pyenv管理多版本（如果需要）
curl https://pyenv.run | bash
pyenv install 3.9.0
pyenv global 3.9.0
```

### Q3: 依赖安装失败
```bash
# 更新pip
python3 -m pip install --upgrade pip

# 清理缓存重装
pip cache purge
pip install -r requirements.txt --no-cache-dir
```

### Q4: 权限问题
```bash
# 设置脚本权限
chmod +x run_backend.py deploy.sh

# 检查文件所有权
chown -R $USER:$USER /path/to/project
```

### Q5: 虚拟环境问题
```bash
# 删除并重建虚拟环境
rm -rf venv
python3 -m venv venv
source venv/bin/activate
```

## 📊 部署验证清单

- [ ] Python 3.8+ 已安装
- [ ] 项目文件已完整传输
- [ ] 虚拟环境已创建并激活
- [ ] 依赖包已安装成功
- [ ] 8000端口可正常访问
- [ ] 健康检查API返回正常
- [ ] 存储过程分析功能正常

## 🔄 回滚方案

如果部署失败，可以：
1. 停止服务：`pkill -f "python.*run_backend"`
2. 删除部署目录
3. 使用备份重新部署

## 📈 扩展部署

### 生产环境部署：
- 使用Nginx反向代理
- 配置SSL证书
- 设置系统服务(systemd)
- 配置日志轮转
- 设置监控告警

### 高可用部署：
- 负载均衡器
- 多实例部署
- 数据库集群
- 容器编排(K8s)

---

## 📞 技术支持

如遇到部署问题：
1. 查看日志文件：`logs/` 目录
2. 检查系统资源：内存、磁盘、网络
3. 验证配置文件：`config/` 目录
4. 运行诊断脚本（如果有）

**部署成功标志**: 访问 http://localhost:8000 能看到服务界面 ✅ 
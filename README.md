# Oracle存储过程分析工具 2.0

一个现代化的Web应用，用于分析Oracle存储过程的数据流向、表关系和字段血缘关系。

## ✨ 新特性

- 🌐 **Web界面**: 优雅的前后端分离架构
- 📊 **可视化图形**: 交互式网络图展示数据流向
- 🎯 **实时分析**: 无需数据库连接的静态分析
- 📱 **响应式设计**: 支持各种设备和屏幕尺寸
- 🔄 **文件上传**: 支持SQL文件直接上传分析
- 📋 **详细报告**: 多维度分析结果展示

## 🏗️ 技术栈

### 后端
- **FastAPI**: 现代、高性能的Python Web框架
- **SQLParse**: SQL语句解析
- **NetworkX**: 图形分析算法
- **Pydantic**: 数据验证和序列化

### 前端
- **React 18**: 现代React框架
- **TypeScript**: 类型安全的JavaScript
- **Cytoscape.js**: 强大的网络图可视化
- **Tailwind CSS**: 实用优先的CSS框架
- **React Hot Toast**: 优雅的通知系统

## 🚀 快速开始

### 方式1: 一键启动 (推荐)

```bash
python start_web.py
```

这个脚本会自动：
1. 检查环境依赖
2. 安装所需包
3. 构建前端
4. 启动后端服务
5. 打开浏览器

### 方式2: 手动启动

#### 安装依赖

```bash
# 安装Python依赖
pip install -r requirements.txt

# 安装前端依赖 (需要Node.js)
cd frontend
npm install
npm run build
cd ..
```

#### 启动服务

```bash
# 启动后端API服务
cd backend
python main.py

# 或使用uvicorn
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

## 🎯 使用指南

### 1. Web界面使用

1. 访问 `http://localhost:8000`
2. 在左侧输入面板输入存储过程代码
3. 点击"开始分析"按钮
4. 在右侧查看可视化结果
5. 点击节点查看详细信息

### 2. 文件上传

- 支持 `.sql`, `.txt`, `.pls` 格式
- 文件大小限制: 10MB
- 必须使用UTF-8编码

### 3. API接口

#### 分析存储过程
```bash
curl -X POST "http://localhost:8000/api/analyze" \
     -H "Content-Type: application/json" \
     -d '{
       "stored_procedure": "CREATE OR REPLACE PROCEDURE..."
     }'
```

#### 文件上传分析
```bash
curl -X POST "http://localhost:8000/api/analyze/file" \
     -F "file=@procedure.sql"
```

#### 健康检查
```bash
curl "http://localhost:8000/api/health"
```

## 📊 功能特性

### 可视化图形
- **参数节点**: 蓝色圆角矩形，显示输入/输出参数
- **物理表**: 绿色矩形，表示数据库中的实际表
- **临时表**: 黄色虚线矩形，表示临时创建的表
- **数据流**: 蓝色箭头，表示数据从源表到目标表的流向
- **JOIN连接**: 红色箭头，表示表之间的关联关系
- **参数使用**: 紫色虚线，表示参数在SQL语句中的使用

### 交互功能
- **节点选择**: 点击节点查看详细信息
- **视图控制**: 缩放、平移、重置视图
- **布局算法**: 自动优化节点排列
- **响应式**: 适配不同屏幕尺寸

### 分析结果
- **概览统计**: 参数、表、SQL语句数量
- **参数详情**: 类型、方向、使用情况
- **表结构**: 字段信息、类型区分
- **SQL语句**: 详细的SQL代码和执行流程
- **JOIN条件**: 表关联的具体条件

## 🔧 配置选项

### 环境变量
```bash
# API基础URL (前端)
REACT_APP_API_URL=http://localhost:8000/api

# 服务端口 (后端)
PORT=8000

# 开发模式
DEBUG=true
```

### API配置
- **CORS**: 配置跨域访问
- **文件上传**: 限制文件大小和类型
- **日志级别**: 控制输出详细程度

## 📁 项目结构

```
oracleSPParaser/
├── src/                    # 核心分析引擎
│   ├── parser/            # SQL解析模块
│   ├── analyzer/          # 数据分析模块
│   ├── visualizer/        # 可视化模块
│   └── models/            # 数据模型
├── backend/               # FastAPI后端
│   └── main.py           # API服务入口
├── frontend/             # React前端
│   ├── src/
│   │   ├── components/   # React组件
│   │   ├── services/     # API服务
│   │   └── types.ts      # TypeScript类型
│   └── package.json
├── tests/                # 测试用例
├── start_web.py          # 一键启动脚本
└── requirements.txt      # Python依赖
```

## 🧪 测试用例

### 运行测试
```bash
# 运行所有测试
python -m pytest tests/

# 运行特定测试
python test_complex_procedure.py
```

### 示例存储过程
项目包含多个测试用例：
- 简单存储过程: 基础CRUD操作
- 复杂存储过程: 包含游标、变量、临时表
- JOIN分析: 多表关联查询
- 参数使用: 不同类型参数的处理

## 🔍 API文档

启动服务后访问：
- **Swagger UI**: `http://localhost:8000/api/docs`
- **ReDoc**: `http://localhost:8000/api/redoc`

## 🤝 贡献指南

1. Fork项目
2. 创建特性分支: `git checkout -b feature/AmazingFeature`
3. 提交更改: `git commit -m 'Add some AmazingFeature'`
4. 推送分支: `git push origin feature/AmazingFeature`
5. 创建Pull Request

## 📄 许可证

本项目采用MIT许可证 - 查看 [LICENSE](LICENSE) 文件了解详情。

## 🔄 版本历史

### 2.0.0 (2024-12-07)
- 🌐 全新Web界面
- 📊 交互式可视化
- 🔧 前后端分离架构
- 📱 响应式设计
- 🎯 改进的分析算法

## 功能改进
1.对大型sp的支持依然不足，无法读取其中的数据
~~2.无法正确识别视图.表名的格式的表~~
~~3.无法区分临时表（临时表的表名通常有#）~~
4.未能通过一个完整的sql语句来自动识别并扩充存储物理表和临时表的固有字段并在图中呈现
5.添加标明识别部分与未识别部分功能
6.多表联查的识别与呈现，能够识别参与的物理表与临时表和他们参与的字段并可视化呈现
7.默认按照sp的逻辑和层级关系来呈现

### 1.0.0 (2024-12-06)
- 🎉 初始版本
- 📋 命令行界面
- 🔍 基础分析功能
- 📊 ASCII可视化

## 📞 技术支持

如有问题或建议，请：
1. 查看API文档: `http://localhost:8000/api/docs`
2. 创建Issue: [GitHub Issues](https://github.com/your-repo/issues)
3. 查看测试用例: `tests/` 目录

---

**Oracle存储过程分析工具 2.0** - 让数据流向分析变得简单而优雅 ✨ 
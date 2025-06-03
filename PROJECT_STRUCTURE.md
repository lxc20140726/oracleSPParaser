# Oracle SP Parser - 项目结构规范

## 标准目录结构

```
oracleSPParaser/
├── README.md                    # 项目说明文档
├── requirements.txt             # Python依赖
├── setup.py                     # 项目安装配置
├── .gitignore                   # Git忽略文件
├── .env.example                 # 环境变量示例
│
├── src/                         # 核心源码目录
│   ├── __init__.py
│   ├── main.py                  # 主入口文件
│   ├── parser/                  # 解析器模块
│   │   ├── __init__.py
│   │   ├── sp_parser.py         # 存储过程解析器
│   │   └── sql_parser.py        # SQL解析器
│   ├── analyzer/                # 分析器模块
│   │   ├── __init__.py
│   │   ├── table_analyzer.py    # 表分析器
│   │   ├── table_field_analyzer.py  # 表字段分析器
│   │   ├── condition_analyzer.py    # 条件分析器
│   │   ├── parameter_analyzer.py    # 参数分析器
│   │   └── metadata_expander.py     # 元数据展开器
│   ├── models/                  # 数据模型
│   │   ├── __init__.py
│   │   └── data_models.py       # 数据模型定义
│   ├── visualizer/              # 可视化模块
│   │   ├── __init__.py
│   │   ├── graph_generator.py   # 图表生成器
│   │   └── interactive_visualizer.py  # 交互式可视化
│   └── utils/                   # 工具模块
│       ├── __init__.py
│       ├── config.py            # 配置管理
│       ├── logger.py            # 日志工具
│       └── helpers.py           # 辅助函数
│
├── backend/                     # 后端服务
│   ├── __init__.py
│   ├── main.py                  # FastAPI主应用
│   ├── api/                     # API路由
│   │   ├── __init__.py
│   │   ├── routes.py            # API路由定义
│   │   └── dependencies.py      # 依赖注入
│   ├── services/                # 业务服务层
│   │   ├── __init__.py
│   │   ├── parser_service.py    # 解析服务
│   │   └── analyzer_service.py  # 分析服务
│   └── config/                  # 后端配置
│       ├── __init__.py
│       └── settings.py          # 配置设置
│
├── frontend/                    # 前端应用
│   ├── package.json
│   ├── package-lock.json
│   ├── public/                  # 静态资源
│   ├── src/                     # 前端源码
│   │   ├── components/          # React组件
│   │   ├── pages/               # 页面组件
│   │   ├── services/            # API服务
│   │   ├── utils/               # 工具函数
│   │   └── styles/              # 样式文件
│   └── build/                   # 构建输出
│
├── tests/                       # 测试文件
│   ├── __init__.py
│   ├── unit/                    # 单元测试
│   │   ├── test_parser.py       # 解析器测试
│   │   ├── test_analyzer.py     # 分析器测试
│   │   └── test_models.py       # 模型测试
│   ├── integration/             # 集成测试
│   │   ├── test_api.py          # API集成测试
│   │   └── test_workflow.py     # 工作流测试
│   ├── fixtures/                # 测试数据
│   │   ├── sample_sp.sql        # 示例存储过程
│   │   └── test_data.json       # 测试数据
│   └── conftest.py              # pytest配置
│
├── docs/                        # 文档目录
│   ├── README.md                # 文档索引
│   ├── api/                     # API文档
│   │   └── endpoints.md         # 接口文档
│   ├── development/             # 开发文档
│   │   ├── setup.md             # 环境搭建
│   │   ├── contributing.md      # 贡献指南
│   │   └── architecture.md      # 架构设计
│   └── user-guide/              # 用户指南
│       ├── installation.md      # 安装指南
│       └── usage.md             # 使用说明
│
├── scripts/                     # 脚本工具
│   ├── setup_env.py             # 环境设置脚本
│   ├── run_tests.py             # 测试运行脚本
│   ├── build.py                 # 构建脚本
│   └── deploy.py                # 部署脚本
│
├── examples/                    # 示例文件
│   ├── sample_procedures/       # 示例存储过程
│   ├── analysis_results/        # 分析结果示例
│   └── visualization_samples/   # 可视化示例
│
├── data/                        # 数据文件
│   ├── input/                   # 输入数据
│   ├── output/                  # 输出结果
│   └── cache/                   # 缓存文件
│
├── config/                      # 配置文件
│   ├── development.yml          # 开发环境配置
│   ├── production.yml           # 生产环境配置
│   └── database.yml             # 数据库配置
│
└── docker/                      # Docker相关
    ├── Dockerfile               # Docker镜像定义
    ├── docker-compose.yml       # Docker编排
    └── docker-compose.dev.yml   # 开发环境编排
```

## 目录说明

### 核心目录
- **src/**: 核心源代码，包含所有业务逻辑模块
- **backend/**: 后端API服务，基于FastAPI
- **frontend/**: 前端应用，基于React
- **tests/**: 完整的测试套件，包含单元测试和集成测试

### 支撑目录
- **docs/**: 项目文档，包含API文档、开发指南等
- **scripts/**: 自动化脚本和工具
- **examples/**: 示例文件和演示代码
- **data/**: 数据文件存储目录
- **config/**: 环境配置文件
- **docker/**: 容器化部署文件

## 文件命名规范

### Python文件
- 模块文件：小写+下划线，如 `sp_parser.py`
- 类名：帕斯卡命名法，如 `SPParser`
- 函数名：小写+下划线，如 `parse_stored_procedure`
- 常量：大写+下划线，如 `MAX_PARSE_DEPTH`

### JavaScript文件
- 组件文件：帕斯卡命名法，如 `ParserComponent.jsx`
- 工具文件：小驼峰命名法，如 `apiService.js`
- 样式文件：小写+连字符，如 `parser-component.css`

### 文档文件
- Markdown文件：小写+连字符，如 `user-guide.md`
- 配置文件：小写+下划线或连字符，如 `docker-compose.yml`

## 迁移计划

1. **阶段一**：创建标准目录结构
2. **阶段二**：移动现有文件到对应目录
3. **阶段三**：更新导入路径和配置
4. **阶段四**：清理根目录临时文件
5. **阶段五**：更新文档和配置文件 
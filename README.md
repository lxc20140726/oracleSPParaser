# Oracle SP Parser

<div align="center">

![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)
![FastAPI](https://img.shields.io/badge/FastAPI-0.100+-green.svg)
![License](https://img.shields.io/badge/License-MIT-yellow.svg)
![Status](https://img.shields.io/badge/Status-Active-success.svg)

**Oracle存储过程智能分析工具**

*解析、分析、可视化Oracle存储过程的数据流向与表关系*

[🚀 快速开始](#-快速开始) • [📋 功能特性](#-功能特性) • [📖 使用指南](#-使用指南) • [🔧 API文档](#-api文档) • [💻 开发指南](#-开发指南)

</div>

---

## 📋 项目简介

Oracle SP Parser 是一个专业的Oracle存储过程分析工具，能够智能解析存储过程代码，分析数据流向，识别表关系，并提供直观的可视化展示。

### 🎯 主要功能

- **🔍 智能解析**: 深度解析Oracle存储过程语法和结构
- **📊 数据流分析**: 追踪数据在存储过程中的流向路径
- **🔗 关系识别**: 自动识别表间关系和JOIN条件
- **📈 可视化展示**: 生成清晰的数据流向图和关系图
- **🌐 Web界面**: 提供友好的Web操作界面
- **🔌 API接口**: 完整的RESTful API支持

### ✨ 核心特性

| 特性 | 描述 |
|------|------|
| **多格式支持** | 支持多种Oracle存储过程格式 |
| **参数分析** | 分析输入/输出参数的使用情况 |
| **表关系映射** | 自动构建表之间的关系图谱 |
| **字段血缘** | 追踪字段在不同表间的血缘关系 |
| **条件逻辑** | 解析WHERE子句和JOIN条件 |
| **实时分析** | 支持实时上传和分析 |

---

## 🚀 快速开始

### 📋 系统要求

- **Python**: 3.8 或更高版本
- **操作系统**: Windows / macOS / Linux
- **内存**: 建议 2GB 以上
- **磁盘空间**: 100MB 以上

### ⚡ 快速安装

```bash
# 1. 克隆项目
git clone <repository-url>
cd oracleSPParaser

# 2. 创建虚拟环境
python3 -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 3. 安装依赖
pip install -r requirements.txt

# 4. 启动服务
python3 run_backend.py
```

### 🌐 访问服务

启动成功后，您可以通过以下方式访问：

- **Web界面**: http://localhost:8000
- **API文档**: http://localhost:8000/api/docs
- **健康检查**: http://localhost:8000/api/health

---

## 📖 使用指南

### 💻 Web界面使用

1. **打开浏览器**，访问 http://localhost:8000
2. **上传存储过程**文件或直接粘贴代码
3. **点击分析按钮**开始解析
4. **查看结果**：数据流向图、表关系、参数分析等

### 🔌 API调用示例

#### 分析存储过程

```bash
curl -X POST "http://localhost:8000/api/analyze" \
  -H "Content-Type: application/json" \
  -d '{
    "stored_procedure": "CREATE OR REPLACE PROCEDURE process_employee_data(p_dept_id IN NUMBER, p_start_date IN DATE) AS BEGIN INSERT INTO employee_reports SELECT dept_id, COUNT(*) as emp_count, AVG(salary) as avg_salary FROM employees WHERE department_id = p_dept_id AND hire_date >= p_start_date GROUP BY dept_id; END;"
  }'
```

#### 返回结果示例

```json
{
  "success": true,
  "message": "成功分析存储过程 'process_employee_data'",
  "data": {
    "procedure_name": "process_employee_data",
    "parameters": [
      {
        "name": "p_dept_id",
        "direction": "IN",
        "data_type": "NUMBER"
      },
      {
        "name": "p_start_date", 
        "direction": "IN",
        "data_type": "DATE"
      }
    ],
    "tables": {
      "physical": {
        "employees": {
          "fields": ["department_id", "hire_date", "salary"]
        },
        "employee_reports": {
          "fields": ["dept_id", "emp_count", "avg_salary"]
        }
      }
    },
    "statistics": {
      "parameter_count": 2,
      "sql_statement_count": 1,
      "physical_table_count": 2
    }
  }
}
```

### 📁 文件上传

```bash
curl -X POST "http://localhost:8000/api/analyze/file" \
  -F "file=@procedure.sql"
```

---

## 🔧 API文档

### 核心接口

| 接口 | 方法 | 描述 |
|------|------|------|
| `/api/health` | GET | 健康检查 |
| `/api/analyze` | POST | 分析存储过程代码 |
| `/api/analyze/file` | POST | 上传文件分析 |

### 请求参数

#### `/api/analyze`

```json
{
  "stored_procedure": "string",  // 存储过程代码
  "options": {                   // 可选配置
    "include_visualization": true,
    "detail_level": "full"
  }
}
```

#### `/api/analyze/file`

- **file**: 存储过程文件 (.sql, .txt, .pls)

### 响应格式

```json
{
  "success": boolean,
  "message": "string",
  "data": {
    "procedure_name": "string",
    "parameters": [...],
    "sql_statements": [...],
    "tables": {...},
    "join_conditions": [...],
    "statistics": {...}
  },
  "visualization": {...}
}
```

详细API文档请访问: http://localhost:8000/api/docs

---

## 📁 项目结构

```
oracleSPParaser/
├── 📂 src/                     # 🔧 核心分析引擎
│   ├── analyzer/               #    ├── 分析器模块
│   │   ├── oracle_sp_analyzer.py     #    │   ├── 主分析器
│   │   ├── parameter_analyzer.py     #    │   ├── 参数分析
│   │   ├── table_analyzer.py         #    │   ├── 表分析
│   │   ├── condition_analyzer.py     #    │   └── 条件分析
│   │   └── table_field_analyzer.py   #    │
│   ├── models/                 #    ├── 数据模型
│   │   └── data_models.py      #    │   └── 核心数据结构
│   ├── parser/                 #    ├── 解析器
│   │   ├── sp_parser.py        #    │   ├── 存储过程解析
│   │   └── sql_parser.py       #    │   └── SQL语句解析
│   ├── utils/                  #    ├── 工具类
│   │   ├── config.py           #    │   ├── 配置管理
│   │   ├── logger.py           #    │   ├── 日志管理
│   │   └── helpers.py          #    │   └── 辅助函数
│   ├── visualizer/             #    ├── 可视化
│   │   ├── graph_generator.py  #    │   ├── 图形生成
│   │   └── interactive_visualizer.py #  │   └── 交互式可视化
│   └── main.py                 #    └── 主入口文件
├── 📂 backend/                 # 🌐 FastAPI后端服务
│   ├── api/                    #    ├── API路由
│   ├── config/                 #    ├── 后端配置
│   ├── services/               #    ├── 业务服务
│   └── main.py                 #    └── 后端主文件
├── 📂 frontend/                # 🎨 Web前端界面
│   └── build/                  #    └── 构建文件
├── 📂 config/                  # ⚙️ 配置文件
│   ├── development.yml         #    ├── 开发环境配置
│   └── production.yml          #    └── 生产环境配置
├── 📂 data/                    # 📊 数据目录
│   ├── input/                  #    ├── 输入文件
│   ├── output/                 #    ├── 输出结果
│   └── cache/                  #    └── 缓存数据
├── 📄 requirements.txt         # 📦 Python依赖
├── 📄 setup.py                # 🔧 安装配置
├── 📄 run_backend.py          # 🚀 启动脚本
└── 📄 README.md               # 📖 项目说明
```

---

## 💻 开发指南

### 🛠️ 开发环境设置

```bash
# 1. 克隆项目
git clone <repository-url>
cd oracleSPParaser

# 2. 创建开发环境
python3 -m venv venv
source venv/bin/activate

# 3. 安装开发依赖
pip install -r requirements.txt
pip install pytest black flake8  # 开发工具

# 4. 运行开发服务器
python3 run_backend.py
```

### 🧪 测试

```bash
# 运行测试（如果有测试文件）
python -m pytest

# 代码格式化
black src/ backend/

# 代码检查
flake8 src/ backend/
```

### 🔧 核心模块说明

#### 1. 分析器 (`src/analyzer/`)

- **oracle_sp_analyzer.py**: 主分析器，协调各个分析模块
- **parameter_analyzer.py**: 分析存储过程参数
- **table_analyzer.py**: 分析表结构和使用情况
- **condition_analyzer.py**: 分析WHERE条件和JOIN关系

#### 2. 解析器 (`src/parser/`)

- **sp_parser.py**: 解析存储过程结构
- **sql_parser.py**: 解析SQL语句

#### 3. 数据模型 (`src/models/`)

- **data_models.py**: 定义所有数据结构和模型

### 📊 扩展开发

#### 添加新的分析功能

1. 在 `src/analyzer/` 目录下创建新的分析器
2. 继承基础分析器类
3. 实现分析逻辑
4. 在主分析器中集成

#### 添加新的可视化

1. 在 `src/visualizer/` 目录下添加新的可视化模块
2. 实现数据转换和图形生成
3. 在API中暴露新的端点

---

## 🔍 使用示例

### 示例1: 简单存储过程分析

```sql
CREATE OR REPLACE PROCEDURE update_employee_salary(
    p_emp_id IN NUMBER,
    p_new_salary IN NUMBER
) AS
BEGIN
    UPDATE employees 
    SET salary = p_new_salary 
    WHERE employee_id = p_emp_id;
    
    INSERT INTO salary_history (
        employee_id, 
        old_salary, 
        new_salary, 
        change_date
    ) 
    SELECT 
        p_emp_id,
        e.salary,
        p_new_salary,
        SYSDATE
    FROM employees e 
    WHERE e.employee_id = p_emp_id;
END;
```

**分析结果**:
- 参数: `p_emp_id` (IN NUMBER), `p_new_salary` (IN NUMBER)
- 涉及表: `employees`, `salary_history`
- 操作类型: UPDATE, INSERT
- 数据流向: employees → salary_history

### 示例2: 复杂报表存储过程

```sql
CREATE OR REPLACE PROCEDURE generate_department_report(
    p_dept_id IN NUMBER,
    p_start_date IN DATE,
    p_end_date IN DATE
) AS
BEGIN
    -- 创建临时表
    CREATE GLOBAL TEMPORARY TABLE temp_dept_stats AS
    SELECT 
        d.department_name,
        COUNT(e.employee_id) as employee_count,
        AVG(e.salary) as avg_salary,
        SUM(e.salary) as total_salary
    FROM departments d
    LEFT JOIN employees e ON d.department_id = e.department_id
    WHERE d.department_id = p_dept_id
      AND e.hire_date BETWEEN p_start_date AND p_end_date
    GROUP BY d.department_name;
    
    -- 插入报表数据
    INSERT INTO department_reports (
        report_date,
        department_id,
        employee_count,
        avg_salary,
        total_salary
    )
    SELECT 
        SYSDATE,
        p_dept_id,
        employee_count,
        avg_salary,
        total_salary
    FROM temp_dept_stats;
END;
```

**分析结果**:
- 参数: 3个输入参数
- 物理表: `departments`, `employees`, `department_reports`
- 临时表: `temp_dept_stats`
- JOIN关系: departments ⟷ employees
- 数据流向: departments + employees → temp_dept_stats → department_reports

---

## 🤝 贡献指南

我们欢迎社区贡献！请遵循以下步骤：

1. **Fork** 项目
2. **创建**特性分支 (`git checkout -b feature/AmazingFeature`)
3. **提交**更改 (`git commit -m 'Add some AmazingFeature'`)
4. **推送**到分支 (`git push origin feature/AmazingFeature`)
5. **打开** Pull Request

### 📝 提交规范

- `feat`: 新功能
- `fix`: 修复bug
- `docs`: 文档更新
- `style`: 代码格式
- `refactor`: 重构
- `test`: 测试
- `chore`: 构建过程或辅助工具变动

---

## 📄 许可证

本项目基于 MIT 许可证开源 - 查看 [LICENSE](LICENSE) 文件了解详情。

---

## 📞 支持与反馈

- **Issues**: [GitHub Issues](https://github.com/yourusername/oracleSPParaser/issues)
- **Discussions**: [GitHub Discussions](https://github.com/yourusername/oracleSPParaser/discussions)
- **Email**: your-email@example.com

---

## 🎉 致谢

感谢所有为这个项目做出贡献的开发者和社区成员！

---

<div align="center">

**[⬆ 返回顶部](#oracle-sp-parser)**

Made with ❤️ by the Oracle SP Parser Team

</div>

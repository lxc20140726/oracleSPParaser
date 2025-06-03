# Oracle存储过程分析工具

这是一个用于分析Oracle存储过程的工具，专注于数据流向、表间字段联系和匹配条件分析，生成交互式可视化图表。

## 功能特点

1. **存储过程解析**
   - 智能解析存储过程结构
   - 识别参数、变量、游标声明
   - 分离SQL语句并分类

2. **表关系分析**  
   - 自动区分实体表和临时表
   - 分析表之间的数据流向
   - 构建表字段对象模型

3. **条件分析**
   - 提取JOIN连接条件
   - 分析WHERE过滤条件
   - 识别参数使用情况

4. **交互式可视化**
   - 实时数据流向图
   - 可交互的Web界面
   - 支持点击查看详情
   - 实时反映原存储过程

## 逻辑过程
根据您的需求，我们的分析逻辑如下：

1. **获取完整存储过程，开始分析**
   - 预处理和清理SQL文本
   - 解析存储过程基本结构

2. **识别并确认外来参数**
   - 提取参数定义（IN/OUT/INOUT）
   - 分析参数在SQL中的使用

3. **SQL解析sql语句并确认参与实体表与临时表，构建实体表与临时表对象**
   - 识别CREATE TEMPORARY TABLE语句
   - 区分物理表和临时表
   - 构建表对象模型

4. **检查sql涉及的实体表与临时表字段是否存在于存储中，如不存在，则添加到实体表与临时表对象中**
   - 从SQL语句中提取字段信息
   - 动态扩展表对象的字段列表
   - 建立字段血缘关系

5. **分别存储匹配条件和sql逻辑**
   - 提取JOIN条件和字段对应关系
   - 分析WHERE条件和参数绑定
   - 识别控制流（IF/WHILE/FOR）

6. **使用实体表、临时表对象，sql逻辑和匹配条件进行可视化，并确保生成的图形可以交互并实时反应到原本的存储过程当中**
   - 生成交互式网络图
   - 支持节点点击查看详情
   - 实时映射到原始SQL代码

## 项目架构

```
src/
├── models/           # 数据模型定义
│   └── data_models.py
├── parser/           # 存储过程解析器
│   └── sp_parser.py
├── analyzer/         # 分析器模块
│   ├── parameter_analyzer.py
│   ├── table_field_analyzer.py
│   └── condition_analyzer.py
├── visualizer/       # 可视化模块
│   └── interactive_visualizer.py
└── main.py          # 主程序入口
```

## 技术特色

- **无需元数据**: 不依赖数据库连接和表结构信息
- **专注字段联系**: 重点分析表间字段的对应和转换关系
- **智能解析**: 支持复杂的Oracle PL/SQL语法
- **交互式可视化**: 基于Streamlit和Plotly的现代Web界面
- **实时映射**: 可视化图形可以直接映射回原始代码

## 安装要求

- Python 3.8+
- 无需Oracle客户端库
- 现代Web浏览器

## 安装步骤

1. 克隆仓库
```bash
git clone https://github.com/yourusername/oracleSPParaser.git
cd oracleSPParaser
```

2. 安装依赖
```bash
pip install -r requirements.txt
```

## 使用方法

### 命令行使用
```bash
python run_analyzer.py
```

### 编程接口
```python
from src.main import OracleSPAnalyzer

analyzer = OracleSPAnalyzer()
result = analyzer.analyze(sp_text)

# 启动Web界面
analyzer.start_web_interface(result)
```

## 输出结果

工具会生成以下输出：
1. **控制台分析报告** - 详细的解析结果
2. **可视化数据文件** (visualization_data.json) - 可供其他工具使用
3. **交互式Web界面** - 实时可视化和探索
4. **字段血缘关系** - 完整的数据流向分析

## 示例

输入一个包含临时表、JOIN和参数的复杂存储过程：

```sql
CREATE OR REPLACE PROCEDURE process_employee_data(
    p_dept_id IN NUMBER,
    p_start_date IN DATE
) AS
BEGIN
    CREATE GLOBAL TEMPORARY TABLE temp_emp_summary (...);
    
    INSERT INTO temp_emp_summary
    SELECT e.employee_id, e.first_name || ' ' || e.last_name, 
           d.department_name, e.salary
    FROM employees e
    JOIN departments d ON e.department_id = d.department_id
    WHERE e.department_id = p_dept_id;
    
    -- 更多SQL语句...
END;
```

工具会自动：
- 识别参数 `p_dept_id`, `p_start_date`
- 区分物理表 `employees`, `departments` 和临时表 `temp_emp_summary`
- 分析JOIN条件 `e.department_id = d.department_id`
- 生成交互式数据流向图

## 未来规划

1. **支持嵌套存储过程** - 分析存储过程间的调用关系
2. **增强字段解析** - 更精确的字段血缘分析
3. **支持更多数据库** - 扩展到其他数据库系统
4. **导出功能** - 支持多种格式的图表导出

## 参考项目

本项目在设计上参考了 [SQLFlow](https://github.com/sqlparser/sqlflow_public) 的数据血缘分析思路，专注于Oracle存储过程的特定需求。

## 贡献指南

欢迎提交Issue和Pull Request来改进这个项目。

## 许可证

MIT License 
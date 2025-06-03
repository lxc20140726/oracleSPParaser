# Oracle SP Parser 测试套件

这是Oracle SP Parser项目的完整测试套件，包含单元测试、集成测试和API测试。

## 📁 测试目录结构

```
tests/
├── __init__.py                    # 测试包初始化
├── conftest.py                   # pytest配置和公共fixture
├── README.md                     # 测试文档 (本文件)
├── unit/                         # 单元测试
│   ├── __init__.py
│   ├── test_parser.py           # 解析器测试
│   ├── test_analyzer.py         # 分析器测试
│   └── test_models.py           # 数据模型测试
├── integration/                  # 集成测试
│   ├── __init__.py
│   └── test_end_to_end.py       # 端到端测试
├── api/                          # API测试
│   ├── __init__.py
│   └── test_api_endpoints.py    # API端点测试
└── data/                         # 测试数据
    └── sample_procedures.sql     # 示例存储过程
```

## 🚀 快速开始

### 安装测试依赖

```bash
# 安装测试所需的依赖包
pip install -r test_requirements.txt
```

### 运行测试

```bash
# 运行所有测试
python run_tests.py

# 或者使用pytest直接运行
pytest tests/
```

## 🔧 测试运行选项

### 使用测试脚本 (推荐)

```bash
# 运行完整测试套件
python run_tests.py --all

# 运行单元测试
python run_tests.py --unit

# 运行集成测试
python run_tests.py --integration

# 运行API测试
python run_tests.py --api

# 运行冒烟测试
python run_tests.py --smoke

# 运行性能测试
python run_tests.py --performance

# 运行特定测试文件
python run_tests.py --test tests/unit/test_parser.py

# 详细输出
python run_tests.py --verbose

# 生成测试报告
python run_tests.py --report

# 代码质量检查
python run_tests.py --lint

# 安装测试依赖
python run_tests.py --install-deps
```

### 使用pytest直接运行

```bash
# 运行所有测试
pytest tests/

# 运行特定目录
pytest tests/unit/
pytest tests/integration/
pytest tests/api/

# 运行特定测试文件
pytest tests/unit/test_parser.py

# 运行特定测试类
pytest tests/unit/test_parser.py::TestStoredProcedureParser

# 运行特定测试方法
pytest tests/unit/test_parser.py::TestStoredProcedureParser::test_parse_simple_procedure

# 使用标记运行测试
pytest -m unit           # 单元测试
pytest -m integration    # 集成测试
pytest -m api            # API测试
pytest -m smoke          # 冒烟测试
pytest -m slow           # 慢速测试

# 详细输出
pytest tests/ -v -s

# 生成覆盖率报告
pytest tests/ --cov=src --cov=backend --cov-report=html

# 并行运行测试
pytest tests/ -n auto
```

## 📊 测试类型说明

### 单元测试 (`tests/unit/`)

测试各个独立组件的功能：

- **解析器测试** (`test_parser.py`)
  - 存储过程解析器功能
  - SQL语句解析器功能
  - 参数提取和验证
  - 错误处理

- **分析器测试** (`test_analyzer.py`)
  - 参数分析器
  - 表分析器
  - 条件分析器
  - 字段分析器

- **模型测试** (`test_models.py`)
  - 数据模型验证
  - 模型方法测试
  - 序列化/反序列化

### 集成测试 (`tests/integration/`)

测试组件间的集成：

- **端到端测试** (`test_end_to_end.py`)
  - 完整分析流程
  - 数据流向验证
  - 复杂场景处理
  - 性能测试

### API测试 (`tests/api/`)

测试REST API接口：

- **API端点测试** (`test_api_endpoints.py`)
  - 健康检查接口
  - 存储过程分析接口
  - 文件上传接口
  - 错误处理和响应格式

## 🎯 测试标记

项目使用pytest标记来分类测试：

- `@pytest.mark.unit` - 单元测试
- `@pytest.mark.integration` - 集成测试
- `@pytest.mark.api` - API测试
- `@pytest.mark.slow` - 慢速测试
- `@pytest.mark.smoke` - 冒烟测试
- `@pytest.mark.performance` - 性能测试
- `@pytest.mark.regression` - 回归测试

### 使用示例

```python
import pytest

@pytest.mark.unit
def test_simple_function():
    """简单的单元测试"""
    pass

@pytest.mark.integration
@pytest.mark.slow
def test_complex_workflow():
    """复杂的集成测试"""
    pass
```

## 📝 测试数据

### 测试fixture

在 `conftest.py` 中定义了多个公共fixture：

- `sample_simple_procedure` - 简单存储过程示例
- `sample_complex_procedure` - 复杂存储过程示例
- `sample_procedure_with_joins` - 包含JOIN的存储过程
- `invalid_procedure` - 无效存储过程示例
- `mock_database_schema` - 模拟数据库架构

### 测试数据文件

`tests/data/sample_procedures.sql` 包含了各种类型的存储过程示例：

1. 简单更新操作
2. 复杂数据处理过程
3. 多表关联报表生成
4. 动态SQL和游标处理

## 📈 覆盖率报告

### 生成覆盖率报告

```bash
# 生成HTML覆盖率报告
pytest tests/ --cov=src --cov=backend --cov-report=html:tests/coverage_html

# 生成终端覆盖率报告
pytest tests/ --cov=src --cov=backend --cov-report=term-missing

# 生成XML覆盖率报告
pytest tests/ --cov=src --cov=backend --cov-report=xml:tests/coverage.xml
```

### 查看覆盖率报告

```bash
# 在浏览器中打开HTML报告
open tests/coverage_html/index.html
```

## 🔍 调试测试

### 调试失败的测试

```bash
# 显示完整的traceback
pytest tests/unit/test_parser.py -v --tb=long

# 进入调试模式
pytest tests/unit/test_parser.py --pdb

# 在第一个失败时停止
pytest tests/ -x

# 显示最慢的10个测试
pytest tests/ --durations=10
```

### 运行特定模式的测试

```bash
# 运行包含特定关键字的测试
pytest tests/ -k "parse"

# 排除慢速测试
pytest tests/ -m "not slow"

# 只运行失败的测试 (需要之前运行过)
pytest tests/ --lf
```

## 🚦 持续集成

### GitHub Actions

项目可以配置GitHub Actions来自动运行测试：

```yaml
# .github/workflows/test.yml
name: Tests
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v3
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.8'
    - name: Install dependencies
      run: |
        pip install -r requirements.txt
        pip install -r test_requirements.txt
    - name: Run tests
      run: python run_tests.py --all
```

### 本地pre-commit hooks

```bash
# 安装pre-commit
pip install pre-commit

# 设置hooks
pre-commit install

# 运行所有hooks
pre-commit run --all-files
```

## 📋 最佳实践

### 编写测试

1. **测试命名**：使用描述性的测试函数名
   ```python
   def test_parse_simple_procedure_with_two_parameters():
       pass
   ```

2. **测试结构**：遵循AAA模式 (Arrange, Act, Assert)
   ```python
   def test_something():
       # Arrange - 准备测试数据
       input_data = "CREATE PROCEDURE..."
       
       # Act - 执行被测试的代码
       result = parser.parse(input_data)
       
       # Assert - 验证结果
       assert result.success is True
   ```

3. **使用fixture**：充分利用pytest fixture来复用测试数据

4. **参数化测试**：使用`@pytest.mark.parametrize`测试多个输入
   ```python
   @pytest.mark.parametrize("input,expected", [
       ("SELECT * FROM table1", "table1"),
       ("SELECT * FROM table2", "table2"),
   ])
   def test_extract_table_name(input, expected):
       result = extract_table_name(input)
       assert result == expected
   ```

### 性能测试

使用pytest-benchmark进行性能测试：

```python
def test_parser_performance(benchmark):
    result = benchmark(parser.parse, large_procedure)
    assert result.success is True
```

## 🔧 故障排除

### 常见问题

1. **模块导入错误**
   ```bash
   # 确保PYTHONPATH正确设置
   export PYTHONPATH=src:backend:$PYTHONPATH
   ```

2. **测试数据库连接问题**
   ```bash
   # 确保测试环境变量正确设置
   export TESTING=true
   ```

3. **依赖包版本冲突**
   ```bash
   # 使用虚拟环境
   python -m venv test_env
   source test_env/bin/activate
   pip install -r test_requirements.txt
   ```

### 获取帮助

```bash
# 查看pytest帮助
pytest --help

# 查看可用的标记
pytest --markers

# 查看测试运行脚本帮助
python run_tests.py --help
```

## 📞 支持

如果您在运行测试时遇到问题，请：

1. 检查测试环境设置
2. 查看测试日志输出
3. 参考本文档的故障排除部分
4. 在项目Issues中报告问题

---

**祝您测试愉快！** 🧪✨ 
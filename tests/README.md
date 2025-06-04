# Oracle存储过程分析工具 - 测试文档

## 📋 测试概览

本项目包含了全面的测试套件，涵盖单元测试、集成测试、API测试、性能测试等多个方面，确保Oracle存储过程分析工具的质量和可靠性。

## 🧪 测试结构

```
tests/
├── __init__.py                 # 测试包初始化
├── conftest.py                 # pytest配置和公共fixtures
├── README.md                   # 测试说明文档（本文件）
├── unit/                       # 单元测试
│   ├── test_parser.py         # 存储过程解析器测试
│   └── test_analyzers.py      # 分析器组件测试
├── integration/                # 集成测试
│   ├── test_end_to_end.py     # 端到端集成测试
│   ├── test_complex_sp.py     # 复杂存储过程测试（已存在）
│   └── debug_*.py             # 调试脚本（已存在）
├── api/                        # API测试
│   └── test_backend_api.py    # 后端API测试
├── performance/                # 性能测试
│   └── test_performance.py    # 性能和压力测试
└── data/                       # 测试数据
    └── sample_procedures.py   # 示例存储过程数据
```

## 🚀 快速开始

### 1. 安装测试依赖

```bash
# 安装测试依赖
pip install -r requirements-test.txt

# 或者使用测试脚本自动安装
python run_tests.py --setup
```

### 2. 运行测试

```bash
# 运行所有测试
python run_tests.py --all

# 运行特定类型的测试
python run_tests.py --unit        # 单元测试
python run_tests.py --integration # 集成测试
python run_tests.py --api         # API测试
python run_tests.py --performance # 性能测试

# 生成覆盖率报告
python run_tests.py --coverage
```

## 📊 测试类型详解

### 🔧 单元测试 (Unit Tests)

**位置**: `tests/unit/`

**目标**: 测试各个组件的独立功能

**包含测试**:
- **解析器测试** (`test_parser.py`)
  - 存储过程结构解析
  - 参数提取
  - SQL语句识别
  - 错误处理
  - 性能测试

- **分析器测试** (`test_analyzers.py`)
  - 参数分析器
  - 表字段分析器
  - 条件分析器
  - 数据流分析

**运行方式**:
```bash
python run_tests.py --unit
# 或者
pytest tests/unit/ -v
```

### 🔗 集成测试 (Integration Tests)

**位置**: `tests/integration/`

**目标**: 测试组件间的协作和完整工作流

**包含测试**:
- **端到端测试** (`test_end_to_end.py`)
  - 完整分析工作流
  - 复杂存储过程处理
  - 错误恢复测试
  - 数据流分析
  - 参数传播测试
  - 并发分析测试
  - 内存使用测试

**运行方式**:
```bash
python run_tests.py --integration
# 或者
pytest tests/integration/ -v
```

### 🌐 API测试 (API Tests)

**位置**: `tests/api/`

**目标**: 测试后端API接口的功能和性能

**包含测试**:
- **后端API测试** (`test_backend_api.py`)
  - 健康检查端点
  - 存储过程分析端点
  - 文件上传分析
  - 错误处理
  - 输入验证
  - 并发请求处理
  - API安全性
  - 响应格式验证

**运行方式**:
```bash
python run_tests.py --api
# 或者
pytest tests/api/ -v
```

### ⚡ 性能测试 (Performance Tests)

**位置**: `tests/performance/`

**目标**: 测试系统的性能、内存使用和稳定性

**包含测试**:
- **分析性能测试**
  - 单次分析性能
  - 大型存储过程处理
  - 内存使用监控
  - 并发分析性能
  - CPU密集型测试
  - 内存泄漏检测

- **API性能测试**
  - 响应时间测试
  - 并发请求测试
  - 吞吐量测试

**运行方式**:
```bash
python run_tests.py --performance
# 或者
pytest tests/performance/ -v -s
```

## 🔧 测试配置

### pytest.ini 配置

测试配置文件包含以下设置：
- 测试路径和文件模式
- 覆盖率报告配置
- 超时设置
- 测试标记定义
- 警告过滤

### 测试标记 (Markers)

项目使用以下测试标记来分类测试：

- `@pytest.mark.unit` - 单元测试
- `@pytest.mark.integration` - 集成测试
- `@pytest.mark.api` - API测试
- `@pytest.mark.performance` - 性能测试
- `@pytest.mark.slow` - 慢速测试
- `@pytest.mark.smoke` - 冒烟测试

**使用示例**:
```bash
# 只运行单元测试
pytest -m "unit"

# 排除慢速测试
pytest -m "not slow"

# 运行特定标记的测试
pytest -m "api and not slow"
```

### 公共Fixtures

`conftest.py` 提供了以下公共fixtures：

- `oracle_sp_analyzer` - OracleSPAnalyzer实例
- `fastapi_app` - FastAPI应用实例
- `sample_stored_procedure` - 示例存储过程
- `complex_stored_procedure` - 复杂存储过程
- `mock_database_tables` - 模拟数据库表结构
- `test_data_generator` - 测试数据生成器

## 📈 覆盖率报告

### 生成覆盖率报告

```bash
# 生成HTML覆盖率报告
python run_tests.py --coverage

# 查看覆盖率报告
open test_results/coverage_html/index.html
```

### 覆盖率目标

- **整体覆盖率**: > 85%
- **核心模块覆盖率**: > 90%
- **关键路径覆盖率**: 100%

## 🎯 测试最佳实践

### 1. 测试命名规范

```python
def test_功能描述_期望结果():
    """测试描述"""
    pass

# 示例
def test_parse_simple_procedure_returns_correct_structure():
    """测试解析简单存储过程返回正确结构"""
    pass
```

### 2. 使用参数化测试

```python
@pytest.mark.parametrize("input_value,expected_output", [
    ("input1", "output1"),
    ("input2", "output2"),
])
def test_parametrized_function(input_value, expected_output):
    assert function(input_value) == expected_output
```

### 3. 模拟外部依赖

```python
@patch('module.external_dependency')
def test_with_mock(mock_dependency):
    mock_dependency.return_value = "mocked_result"
    # 测试代码
```

### 4. 异步测试

```python
@pytest.mark.asyncio
async def test_async_function():
    result = await async_function()
    assert result is not None
```

## 🚨 常见问题解决

### 1. 测试环境问题

**问题**: 依赖包安装失败
```bash
# 解决方案：更新pip和setuptools
pip install --upgrade pip setuptools
pip install -r requirements-test.txt
```

**问题**: 路径导入错误
```bash
# 解决方案：确保项目根目录在Python路径中
export PYTHONPATH="${PYTHONPATH}:$(pwd)"
```

### 2. 测试失败分析

**查看详细错误信息**:
```bash
pytest --tb=long -v
```

**只运行失败的测试**:
```bash
pytest --lf
```

**调试单个测试**:
```bash
pytest tests/unit/test_parser.py::TestStoredProcedureParser::test_parse_simple_procedure -v -s
```

### 3. 性能测试问题

**问题**: 性能测试超时
- 增加超时时间: `pytest --timeout=600`
- 检查系统资源使用情况

**问题**: 内存使用过高
- 检查是否有内存泄漏
- 减少测试数据规模

## 📋 测试检查清单

在提交代码前，请确保：

- [ ] 所有新功能都有对应的单元测试
- [ ] 测试覆盖率达到要求
- [ ] 所有测试都能通过
- [ ] 性能测试没有回归
- [ ] API测试验证了所有端点
- [ ] 错误处理有相应测试
- [ ] 测试代码遵循项目规范

## 🔄 持续集成

项目支持持续集成，每次代码提交都会自动运行：

1. **快速检查** - 冒烟测试和单元测试
2. **全面测试** - 包括集成测试和API测试
3. **性能回归** - 性能基准测试
4. **覆盖率报告** - 生成并更新覆盖率报告

## 📞 支持和反馈

如果在测试过程中遇到问题：

1. 查看本文档的常见问题部分
2. 检查测试日志和错误信息
3. 在项目仓库中提交issue
4. 联系开发团队获取支持

---

**记住**: 好的测试是高质量软件的基础！ 🚀 
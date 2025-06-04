#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
分析器组件单元测试
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
import sys
from pathlib import Path
from typing import List, Dict, Any

# 添加src路径
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from analyzer.parameter_analyzer import ParameterAnalyzer
from analyzer.table_field_analyzer import TableFieldAnalyzer
from analyzer.condition_analyzer import ConditionAnalyzer
from models.data_models import (
    StoredProcedureStructure, Parameter, SQLStatement, StatementType,
    TableFieldAnalysis, ConditionsAndLogic, JoinCondition
)

@pytest.mark.unit
class TestParameterAnalyzer:
    """参数分析器测试类"""
    
    @pytest.fixture
    def analyzer(self):
        """创建参数分析器实例"""
        return ParameterAnalyzer()
    
    @pytest.fixture
    def mock_sp_structure(self):
        """模拟存储过程结构"""
        return Mock(spec=StoredProcedureStructure)
    
    def test_init(self, analyzer):
        """测试分析器初始化"""
        assert analyzer is not None
        assert hasattr(analyzer, 'extract_parameters')
    
    def test_extract_simple_parameters(self, analyzer, mock_sp_structure):
        """测试提取简单参数"""
        # 设置模拟数据
        param1 = Parameter(name="p_id", direction="IN", data_type="NUMBER")
        param2 = Parameter(name="p_name", direction="OUT", data_type="VARCHAR2")
        mock_sp_structure.parameters = [param1, param2]
        
        result = analyzer.extract_parameters(mock_sp_structure)
        
        assert len(result) == 2
        assert result[0].name == "p_id"
        assert result[0].direction == "IN"
        assert result[1].name == "p_name"
        assert result[1].direction == "OUT"
    
    def test_extract_parameters_with_usage_analysis(self, analyzer):
        """测试参数使用情况分析"""
        # 创建真实的存储过程结构用于测试
        param1 = Parameter(name="p_dept_id", direction="IN", data_type="NUMBER")
        param2 = Parameter(name="p_result", direction="OUT", data_type="NUMBER")
        
        stmt1 = Mock(spec=SQLStatement)
        stmt1.parameters_used = ["p_dept_id"]
        stmt1.statement_id = "stmt_1"
        
        stmt2 = Mock(spec=SQLStatement)
        stmt2.parameters_used = ["p_dept_id", "p_result"]
        stmt2.statement_id = "stmt_2"
        
        sp_structure = Mock(spec=StoredProcedureStructure)
        sp_structure.parameters = [param1, param2]
        sp_structure.sql_statements = [stmt1, stmt2]
        
        result = analyzer.extract_parameters(sp_structure)
        
        # 验证使用情况分析
        p_dept_id = next(p for p in result if p.name == "p_dept_id")
        assert len(p_dept_id.used_in_statements) == 2
        assert "stmt_1" in p_dept_id.used_in_statements
        assert "stmt_2" in p_dept_id.used_in_statements
        
        p_result = next(p for p in result if p.name == "p_result")
        assert len(p_result.used_in_statements) == 1
        assert "stmt_2" in p_result.used_in_statements
    
    def test_extract_parameters_with_default_values(self, analyzer):
        """测试带默认值的参数提取"""
        param_with_default = Parameter(
            name="p_mode", 
            direction="IN", 
            data_type="VARCHAR2",
            default_value="'NORMAL'"
        )
        
        sp_structure = Mock(spec=StoredProcedureStructure)
        sp_structure.parameters = [param_with_default]
        sp_structure.sql_statements = []
        
        result = analyzer.extract_parameters(sp_structure)
        
        assert len(result) == 1
        assert result[0].default_value == "'NORMAL'"
    
    def test_parameter_validation(self, analyzer):
        """测试参数验证"""
        # 测试无效参数
        invalid_param = Parameter(name="", direction="INVALID", data_type="")
        
        sp_structure = Mock(spec=StoredProcedureStructure)
        sp_structure.parameters = [invalid_param]
        sp_structure.sql_statements = []
        
        result = analyzer.extract_parameters(sp_structure)
        
        # 应该能处理无效参数而不崩溃
        assert isinstance(result, list)


@pytest.mark.unit
class TestTableFieldAnalyzer:
    """表字段分析器测试类"""
    
    @pytest.fixture
    def analyzer(self):
        """创建表字段分析器实例"""
        return TableFieldAnalyzer()
    
    def test_init(self, analyzer):
        """测试分析器初始化"""
        assert analyzer is not None
        assert hasattr(analyzer, 'analyze')
    
    def test_analyze_simple_tables(self, analyzer):
        """测试分析简单表结构"""
        # 创建模拟SQL语句
        stmt1 = Mock(spec=SQLStatement)
        stmt1.source_tables = ["employees"]
        stmt1.target_tables = ["employees"]
        stmt1.statement_id = "stmt_1"
        stmt1.statement_type = StatementType.UPDATE
        
        stmt2 = Mock(spec=SQLStatement)
        stmt2.source_tables = ["employees", "departments"]
        stmt2.target_tables = ["employee_reports"]
        stmt2.statement_id = "stmt_2"
        stmt2.statement_type = StatementType.INSERT
        
        sp_structure = Mock(spec=StoredProcedureStructure)
        sp_structure.sql_statements = [stmt1, stmt2]
        
        result = analyzer.analyze(sp_structure)
        
        assert isinstance(result, TableFieldAnalysis)
        
        # 验证物理表识别
        physical_table_names = list(result.physical_tables.keys())
        assert "employees" in physical_table_names
        assert "departments" in physical_table_names
        assert "employee_reports" in physical_table_names
    
    def test_analyze_temporary_tables(self, analyzer):
        """测试临时表分析"""
        # 创建包含临时表的SQL语句
        create_stmt = Mock(spec=SQLStatement)
        create_stmt.source_tables = []
        create_stmt.target_tables = ["temp_emp_summary"]
        create_stmt.statement_id = "stmt_create"
        create_stmt.statement_type = StatementType.CREATE_TABLE
        create_stmt.raw_sql = "CREATE GLOBAL TEMPORARY TABLE temp_emp_summary"
        
        insert_stmt = Mock(spec=SQLStatement)
        insert_stmt.source_tables = ["employees"]
        insert_stmt.target_tables = ["temp_emp_summary"]
        insert_stmt.statement_id = "stmt_insert"
        insert_stmt.statement_type = StatementType.INSERT
        
        sp_structure = Mock(spec=StoredProcedureStructure)
        sp_structure.sql_statements = [create_stmt, insert_stmt]
        
        result = analyzer.analyze(sp_structure)
        
        # 验证临时表识别
        temp_table_names = list(result.temp_tables.keys())
        assert "temp_emp_summary" in temp_table_names
        
        # 验证物理表识别
        physical_table_names = list(result.physical_tables.keys())
        assert "employees" in physical_table_names
    
    def test_field_extraction_from_sql(self, analyzer):
        """测试从SQL中提取字段"""
        stmt = Mock(spec=SQLStatement)
        stmt.source_tables = ["employees"]
        stmt.target_tables = []
        stmt.statement_id = "stmt_1"
        stmt.statement_type = StatementType.SELECT
        stmt.raw_sql = "SELECT employee_id, first_name, last_name, salary FROM employees"
        
        sp_structure = Mock(spec=StoredProcedureStructure)
        sp_structure.sql_statements = [stmt]
        
        result = analyzer.analyze(sp_structure)
        
        # 验证字段提取
        employees_table = result.physical_tables.get("employees")
        if employees_table:
            expected_fields = ["employee_id", "first_name", "last_name", "salary"]
            for field in expected_fields:
                assert field in employees_table.fields
    
    def test_table_relationships(self, analyzer):
        """测试表关系分析"""
        join_stmt = Mock(spec=SQLStatement)
        join_stmt.source_tables = ["employees", "departments"]
        join_stmt.target_tables = []
        join_stmt.statement_id = "stmt_join"
        join_stmt.statement_type = StatementType.SELECT
        join_stmt.raw_sql = """
        SELECT e.employee_id, d.department_name 
        FROM employees e 
        JOIN departments d ON e.department_id = d.department_id
        """
        
        sp_structure = Mock(spec=StoredProcedureStructure)
        sp_structure.sql_statements = [join_stmt]
        
        result = analyzer.analyze(sp_structure)
        
        # 验证表关系
        assert "employees" in result.physical_tables
        assert "departments" in result.physical_tables
        
        # 验证字段提取
        emp_table = result.physical_tables["employees"]
        dept_table = result.physical_tables["departments"]
        
        assert "employee_id" in emp_table.fields
        assert "department_id" in emp_table.fields
        assert "department_name" in dept_table.fields
        assert "department_id" in dept_table.fields


@pytest.mark.unit
class TestConditionAnalyzer:
    """条件分析器测试类"""
    
    @pytest.fixture
    def analyzer(self):
        """创建条件分析器实例"""
        return ConditionAnalyzer()
    
    def test_init(self, analyzer):
        """测试分析器初始化"""
        assert analyzer is not None
        assert hasattr(analyzer, 'analyze')
    
    def test_analyze_join_conditions(self, analyzer):
        """测试连接条件分析"""
        join_stmt = Mock(spec=SQLStatement)
        join_stmt.statement_id = "stmt_1"
        join_stmt.statement_type = StatementType.SELECT
        join_stmt.raw_sql = """
        SELECT e.employee_id, d.department_name 
        FROM employees e 
        INNER JOIN departments d ON e.department_id = d.department_id
        LEFT JOIN locations l ON d.location_id = l.location_id
        """
        
        sp_structure = Mock(spec=StoredProcedureStructure)
        sp_structure.sql_statements = [join_stmt]
        
        result = analyzer.analyze(sp_structure)
        
        assert isinstance(result, ConditionsAndLogic)
        assert len(result.join_conditions) >= 2
        
        # 验证第一个连接条件
        join_cond1 = result.join_conditions[0]
        assert join_cond1.left_table == "employees"
        assert join_cond1.left_field == "department_id"
        assert join_cond1.right_table == "departments"
        assert join_cond1.right_field == "department_id"
        assert join_cond1.join_type == "INNER"
        
        # 验证第二个连接条件
        join_cond2 = result.join_conditions[1]
        assert join_cond2.left_table == "departments"
        assert join_cond2.left_field == "location_id"
        assert join_cond2.right_table == "locations"
        assert join_cond2.right_field == "location_id"
        assert join_cond2.join_type == "LEFT"
    
    def test_analyze_where_conditions(self, analyzer):
        """测试WHERE条件分析"""
        where_stmt = Mock(spec=SQLStatement)
        where_stmt.statement_id = "stmt_1"
        where_stmt.statement_type = StatementType.SELECT
        where_stmt.raw_sql = """
        SELECT * FROM employees 
        WHERE department_id = 10 
        AND salary > 50000 
        AND hire_date >= '2020-01-01'
        """
        
        sp_structure = Mock(spec=StoredProcedureStructure)
        sp_structure.sql_statements = [where_stmt]
        
        result = analyzer.analyze(sp_structure)
        
        # 验证WHERE条件提取
        assert len(result.where_conditions) >= 3
        
        # 检查条件内容
        condition_texts = [cond.condition_text for cond in result.where_conditions]
        assert any("department_id = 10" in text for text in condition_texts)
        assert any("salary > 50000" in text for text in condition_texts)
        assert any("hire_date >= '2020-01-01'" in text for text in condition_texts)
    
    def test_analyze_complex_conditions(self, analyzer):
        """测试复杂条件分析"""
        complex_stmt = Mock(spec=SQLStatement)
        complex_stmt.statement_id = "stmt_1"
        complex_stmt.statement_type = StatementType.SELECT
        complex_stmt.raw_sql = """
        SELECT e.employee_id, d.department_name
        FROM employees e
        JOIN departments d ON e.department_id = d.department_id
        WHERE e.salary BETWEEN 30000 AND 80000
        AND d.location_id IN (SELECT location_id FROM locations WHERE country_id = 'US')
        AND EXISTS (SELECT 1 FROM job_history jh WHERE jh.employee_id = e.employee_id)
        """
        
        sp_structure = Mock(spec=StoredProcedureStructure)
        sp_structure.sql_statements = [complex_stmt]
        
        result = analyzer.analyze(sp_structure)
        
        # 验证复杂条件处理
        assert len(result.join_conditions) >= 1
        assert len(result.where_conditions) >= 3
        
        # 验证子查询识别
        subquery_conditions = [
            cond for cond in result.where_conditions 
            if "SELECT" in cond.condition_text.upper()
        ]
        assert len(subquery_conditions) >= 2  # IN子查询和EXISTS子查询
    
    def test_analyze_merge_conditions(self, analyzer):
        """测试MERGE语句条件分析"""
        merge_stmt = Mock(spec=SQLStatement)
        merge_stmt.statement_id = "stmt_1"
        merge_stmt.statement_type = StatementType.MERGE
        merge_stmt.raw_sql = """
        MERGE INTO target_table t
        USING source_table s ON (t.id = s.id AND t.status = 'ACTIVE')
        WHEN MATCHED THEN
            UPDATE SET t.value = s.value
        WHEN NOT MATCHED THEN
            INSERT (id, value, status) VALUES (s.id, s.value, 'NEW')
        """
        
        sp_structure = Mock(spec=StoredProcedureStructure)
        sp_structure.sql_statements = [merge_stmt]
        
        result = analyzer.analyze(sp_structure)
        
        # 验证MERGE条件
        merge_conditions = [
            cond for cond in result.merge_conditions 
            if cond.statement_id == "stmt_1"
        ]
        assert len(merge_conditions) >= 1
        
        # 验证ON条件
        on_condition = merge_conditions[0]
        assert "t.id = s.id" in on_condition.on_condition
        assert "t.status = 'ACTIVE'" in on_condition.on_condition
    
    def test_parameter_usage_in_conditions(self, analyzer):
        """测试条件中的参数使用"""
        param_stmt = Mock(spec=SQLStatement)
        param_stmt.statement_id = "stmt_1"
        param_stmt.statement_type = StatementType.UPDATE
        param_stmt.raw_sql = """
        UPDATE employees 
        SET salary = salary * 1.1 
        WHERE department_id = p_dept_id 
        AND hire_date >= p_start_date
        """
        param_stmt.parameters_used = ["p_dept_id", "p_start_date"]
        
        sp_structure = Mock(spec=StoredProcedureStructure)
        sp_structure.sql_statements = [param_stmt]
        
        result = analyzer.analyze(sp_structure)
        
        # 验证参数在条件中的使用
        param_conditions = [
            cond for cond in result.where_conditions 
            if any(param in cond.condition_text for param in ["p_dept_id", "p_start_date"])
        ]
        assert len(param_conditions) >= 2
    
    def test_error_handling(self, analyzer):
        """测试错误处理"""
        # 测试空输入
        empty_sp = Mock(spec=StoredProcedureStructure)
        empty_sp.sql_statements = []
        
        result = analyzer.analyze(empty_sp)
        
        assert isinstance(result, ConditionsAndLogic)
        assert len(result.join_conditions) == 0
        assert len(result.where_conditions) == 0
        
        # 测试无效SQL
        invalid_stmt = Mock(spec=SQLStatement)
        invalid_stmt.statement_id = "stmt_1"
        invalid_stmt.statement_type = StatementType.SELECT
        invalid_stmt.raw_sql = "INVALID SQL SYNTAX {{{"
        
        invalid_sp = Mock(spec=StoredProcedureStructure)
        invalid_sp.sql_statements = [invalid_stmt]
        
        result = analyzer.analyze(invalid_sp)
        
        # 应该能处理无效SQL而不崩溃
        assert isinstance(result, ConditionsAndLogic)
    
    @pytest.mark.parametrize("join_type,expected", [
        ("INNER JOIN", "INNER"),
        ("LEFT JOIN", "LEFT"),
        ("LEFT OUTER JOIN", "LEFT OUTER"),
        ("RIGHT JOIN", "RIGHT"),
        ("FULL OUTER JOIN", "FULL OUTER"),
        ("CROSS JOIN", "CROSS"),
    ])
    def test_join_type_recognition(self, analyzer, join_type, expected):
        """测试连接类型识别"""
        join_stmt = Mock(spec=SQLStatement)
        join_stmt.statement_id = "stmt_1"
        join_stmt.raw_sql = f"""
        SELECT * FROM table1 t1 
        {join_type} table2 t2 ON t1.id = t2.id
        """
        
        sp_structure = Mock(spec=StoredProcedureStructure)
        sp_structure.sql_statements = [join_stmt]
        
        result = analyzer.analyze(sp_structure)
        
        if result.join_conditions:
            join_condition = result.join_conditions[0]
            assert join_condition.join_type == expected 
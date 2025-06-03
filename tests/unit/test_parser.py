"""
测试存储过程解析器功能
"""

import pytest
import sys
import os
from pathlib import Path

# 添加项目路径
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from parser.sp_parser import StoredProcedureParser
from parser.sql_parser import SQLStatementParser
from models.data_models import StoredProcedure, SQLStatement, Parameter


class TestStoredProcedureParser:
    """测试存储过程解析器"""
    
    def setup_method(self):
        """测试前的设置"""
        self.parser = StoredProcedureParser()
    
    def test_parse_simple_procedure(self, sample_simple_procedure):
        """测试解析简单存储过程"""
        result = self.parser.parse(sample_simple_procedure)
        
        assert result is not None
        assert result.name == "update_employee_salary"
        assert len(result.parameters) == 2
        assert result.parameters[0].name == "p_emp_id"
        assert result.parameters[0].direction == "IN"
        assert result.parameters[0].data_type == "NUMBER"
        assert len(result.sql_statements) >= 1
    
    def test_parse_complex_procedure(self, sample_complex_procedure):
        """测试解析复杂存储过程"""
        result = self.parser.parse(sample_complex_procedure)
        
        assert result is not None
        assert result.name == "process_employee_data"
        assert len(result.parameters) == 3
        assert len(result.sql_statements) >= 3  # CREATE, UPDATE, INSERT
    
    def test_parse_procedure_with_joins(self, sample_procedure_with_joins):
        """测试解析包含JOIN的存储过程"""
        result = self.parser.parse(sample_procedure_with_joins)
        
        assert result is not None
        assert result.name == "generate_department_report"
        assert len(result.parameters) == 1
        assert result.parameters[0].name == "p_year"
    
    def test_parse_invalid_procedure(self, invalid_procedure):
        """测试解析无效存储过程"""
        with pytest.raises(Exception):
            self.parser.parse(invalid_procedure)
    
    def test_extract_procedure_name(self):
        """测试提取存储过程名称"""
        procedure_text = "CREATE OR REPLACE PROCEDURE test_proc AS BEGIN NULL; END;"
        name = self.parser._extract_procedure_name(procedure_text)
        assert name == "test_proc"
    
    def test_extract_parameters(self):
        """测试提取参数"""
        procedure_text = """
        CREATE OR REPLACE PROCEDURE test_proc(
            p_id IN NUMBER,
            p_name IN VARCHAR2,
            p_result OUT NUMBER
        ) AS BEGIN NULL; END;
        """
        params = self.parser._extract_parameters(procedure_text)
        assert len(params) == 3
        assert params[0].name == "p_id"
        assert params[0].direction == "IN"
        assert params[1].data_type == "VARCHAR2"
        assert params[2].direction == "OUT"


class TestSQLStatementParser:
    """测试SQL语句解析器"""
    
    def setup_method(self):
        """测试前的设置"""
        self.parser = SQLStatementParser()
    
    def test_parse_select_statement(self):
        """测试解析SELECT语句"""
        sql = "SELECT e.employee_id, e.name FROM employees e WHERE e.department_id = 10"
        result = self.parser.parse(sql)
        
        assert result.statement_type.value == "SELECT"
        assert "employees" in result.source_tables
        assert "e.department_id" in str(result.raw_sql)
    
    def test_parse_insert_statement(self):
        """测试解析INSERT语句"""
        sql = "INSERT INTO employee_reports (dept_id, emp_count) SELECT department_id, COUNT(*) FROM employees GROUP BY department_id"
        result = self.parser.parse(sql)
        
        assert result.statement_type.value == "INSERT"
        assert "employee_reports" in result.target_tables
        assert "employees" in result.source_tables
    
    def test_parse_update_statement(self):
        """测试解析UPDATE语句"""
        sql = "UPDATE employees SET salary = 5000 WHERE employee_id = 123"
        result = self.parser.parse(sql)
        
        assert result.statement_type.value == "UPDATE"
        assert "employees" in result.target_tables
    
    def test_parse_delete_statement(self):
        """测试解析DELETE语句"""
        sql = "DELETE FROM employees WHERE hire_date < '2020-01-01'"
        result = self.parser.parse(sql)
        
        assert result.statement_type.value == "DELETE"
        assert "employees" in result.target_tables
    
    def test_parse_create_table_statement(self):
        """测试解析CREATE TABLE语句"""
        sql = "CREATE GLOBAL TEMPORARY TABLE temp_emp AS SELECT * FROM employees"
        result = self.parser.parse(sql)
        
        assert result.statement_type.value == "CREATE_TABLE"
        assert "temp_emp" in result.target_tables
        assert "employees" in result.source_tables
    
    def test_extract_table_names(self):
        """测试提取表名"""
        sql = "SELECT * FROM employees e JOIN departments d ON e.dept_id = d.id"
        tables = self.parser._extract_table_names(sql)
        assert "employees" in tables
        assert "departments" in tables
    
    def test_extract_join_conditions(self):
        """测试提取JOIN条件"""
        sql = "SELECT * FROM employees e INNER JOIN departments d ON e.department_id = d.department_id"
        conditions = self.parser._extract_join_conditions(sql)
        assert len(conditions) > 0
        assert any("department_id" in str(condition) for condition in conditions)
    
    def test_parse_complex_join(self):
        """测试解析复杂JOIN"""
        sql = """
        SELECT d.name, e.name, j.title
        FROM departments d
        LEFT JOIN employees e ON d.department_id = e.department_id
        INNER JOIN jobs j ON e.job_id = j.job_id
        WHERE d.location_id = 100
        """
        result = self.parser.parse(sql)
        
        assert "departments" in result.source_tables
        assert "employees" in result.source_tables
        assert "jobs" in result.source_tables
    
    def test_handle_invalid_sql(self):
        """测试处理无效SQL"""
        invalid_sql = "INVALID SQL STATEMENT"
        with pytest.raises(Exception):
            self.parser.parse(invalid_sql) 
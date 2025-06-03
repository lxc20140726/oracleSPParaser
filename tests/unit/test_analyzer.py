"""
测试存储过程分析器功能
"""

import pytest
import sys
from pathlib import Path

# 添加项目路径
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from analyzer.parameter_analyzer import ParameterAnalyzer
from analyzer.table_analyzer import TableAnalyzer
from analyzer.condition_analyzer import ConditionAnalyzer
from analyzer.table_field_analyzer import TableFieldAnalyzer
from models.data_models import Parameter, SQLStatement, StatementType


class TestParameterAnalyzer:
    """测试参数分析器"""
    
    def setup_method(self):
        """测试前的设置"""
        self.analyzer = ParameterAnalyzer()
    
    def test_analyze_basic_parameters(self):
        """测试分析基本参数"""
        parameters = [
            Parameter("p_emp_id", "IN", "NUMBER"),
            Parameter("p_salary", "IN", "NUMBER"),
            Parameter("p_result", "OUT", "VARCHAR2")
        ]
        
        sql_statements = [
            SQLStatement(
                statement_id=1,
                statement_type=StatementType.UPDATE,
                raw_sql="UPDATE employees SET salary = p_salary WHERE employee_id = p_emp_id",
                source_tables=["employees"],
                target_tables=["employees"],
                parameters_used=["p_emp_id", "p_salary"]
            )
        ]
        
        result = self.analyzer.analyze(parameters, sql_statements)
        
        assert len(result) == 3
        # 检查参数使用情况
        emp_id_param = next(p for p in result if p.name == "p_emp_id")
        assert emp_id_param.used_in_statements == [1]
        
        salary_param = next(p for p in result if p.name == "p_salary")
        assert salary_param.used_in_statements == [1]
        
        result_param = next(p for p in result if p.name == "p_result")
        assert result_param.used_in_statements == []  # 未使用
    
    def test_parameter_usage_tracking(self):
        """测试参数使用跟踪"""
        parameters = [Parameter("p_dept_id", "IN", "NUMBER")]
        
        sql_statements = [
            SQLStatement(1, StatementType.SELECT, "SELECT * FROM employees WHERE department_id = p_dept_id", 
                        ["employees"], [], ["p_dept_id"]),
            SQLStatement(2, StatementType.INSERT, "INSERT INTO reports (dept_id) VALUES (p_dept_id)", 
                        [], ["reports"], ["p_dept_id"])
        ]
        
        result = self.analyzer.analyze(parameters, sql_statements)
        
        assert len(result) == 1
        assert set(result[0].used_in_statements) == {1, 2}


class TestTableAnalyzer:
    """测试表分析器"""
    
    def setup_method(self):
        """测试前的设置"""
        self.analyzer = TableAnalyzer()
    
    def test_analyze_table_usage(self):
        """测试分析表使用情况"""
        sql_statements = [
            SQLStatement(1, StatementType.SELECT, "SELECT * FROM employees", 
                        ["employees"], []),
            SQLStatement(2, StatementType.INSERT, "INSERT INTO employee_reports SELECT * FROM employees", 
                        ["employees"], ["employee_reports"]),
            SQLStatement(3, StatementType.CREATE_TABLE, "CREATE TEMP TABLE temp_emp AS SELECT * FROM employees", 
                        ["employees"], ["temp_emp"])
        ]
        
        result = self.analyzer.analyze(sql_statements)
        
        # 检查物理表
        assert "employees" in result.physical_tables
        assert "employee_reports" in result.physical_tables
        
        # 检查临时表
        assert "temp_emp" in result.temp_tables
        
        # 检查表的使用情况
        employees_table = result.physical_tables["employees"]
        assert set(employees_table.source_sql_ids) == {1, 2, 3}
        
        reports_table = result.physical_tables["employee_reports"]
        assert 2 in reports_table.target_sql_ids
    
    def test_identify_temporary_tables(self):
        """测试识别临时表"""
        sql_statements = [
            SQLStatement(1, StatementType.CREATE_TABLE, 
                        "CREATE GLOBAL TEMPORARY TABLE temp_data AS SELECT * FROM employees", 
                        ["employees"], ["temp_data"]),
            SQLStatement(2, StatementType.CREATE_TABLE, 
                        "CREATE TABLE permanent_table AS SELECT * FROM employees", 
                        ["employees"], ["permanent_table"])
        ]
        
        result = self.analyzer.analyze(sql_statements)
        
        assert "temp_data" in result.temp_tables
        assert "permanent_table" in result.physical_tables


class TestConditionAnalyzer:
    """测试条件分析器"""
    
    def setup_method(self):
        """测试前的设置"""
        self.analyzer = ConditionAnalyzer()
    
    def test_analyze_join_conditions(self):
        """测试分析JOIN条件"""
        sql_statements = [
            SQLStatement(1, StatementType.SELECT, 
                        """SELECT * FROM employees e 
                           INNER JOIN departments d ON e.department_id = d.department_id
                           LEFT JOIN jobs j ON e.job_id = j.job_id""", 
                        ["employees", "departments", "jobs"], [])
        ]
        
        result = self.analyzer.analyze(sql_statements)
        
        assert len(result.join_conditions) >= 2
        
        # 检查JOIN条件
        join_conds = result.join_conditions
        dept_join = next((jc for jc in join_conds if jc.left_table == "e" and jc.right_table == "d"), None)
        assert dept_join is not None
        assert dept_join.left_field == "department_id"
        assert dept_join.right_field == "department_id"
        assert dept_join.join_type == "INNER"
    
    def test_analyze_where_conditions(self):
        """测试分析WHERE条件"""
        sql_statements = [
            SQLStatement(1, StatementType.SELECT, 
                        "SELECT * FROM employees WHERE department_id = 10 AND salary > 5000", 
                        ["employees"], [])
        ]
        
        result = self.analyzer.analyze(sql_statements)
        
        assert len(result.where_conditions) >= 1
        # 应该检测到department_id和salary的过滤条件
    
    def test_complex_join_analysis(self):
        """测试复杂JOIN分析"""
        sql_statements = [
            SQLStatement(1, StatementType.SELECT, 
                        """SELECT d.name, COUNT(e.employee_id)
                           FROM departments d
                           LEFT JOIN employees e ON d.department_id = e.department_id
                           WHERE d.location_id = 100
                           GROUP BY d.name""", 
                        ["departments", "employees"], [])
        ]
        
        result = self.analyzer.analyze(sql_statements)
        
        join_conditions = result.join_conditions
        assert len(join_conditions) >= 1
        assert any(jc.join_type == "LEFT" for jc in join_conditions)


class TestTableFieldAnalyzer:
    """测试表字段分析器"""
    
    def setup_method(self):
        """测试前的设置"""
        self.analyzer = TableFieldAnalyzer()
    
    def test_analyze_field_usage(self):
        """测试分析字段使用情况"""
        sql_statements = [
            SQLStatement(1, StatementType.SELECT, 
                        "SELECT e.employee_id, e.first_name, e.salary FROM employees e", 
                        ["employees"], []),
            SQLStatement(2, StatementType.INSERT, 
                        "INSERT INTO employee_reports (emp_id, name, salary) SELECT employee_id, first_name, salary FROM employees", 
                        ["employees"], ["employee_reports"])
        ]
        
        result = self.analyzer.analyze(sql_statements)
        
        # 检查employees表的字段
        assert "employees" in result.physical_tables
        employees_fields = result.physical_tables["employees"].fields
        assert "employee_id" in employees_fields
        assert "first_name" in employees_fields
        assert "salary" in employees_fields
        
        # 检查employee_reports表的字段
        assert "employee_reports" in result.physical_tables
        reports_fields = result.physical_tables["employee_reports"].fields
        assert "emp_id" in reports_fields
        assert "name" in reports_fields
        assert "salary" in reports_fields
    
    def test_field_lineage_tracking(self):
        """测试字段血缘跟踪"""
        sql_statements = [
            SQLStatement(1, StatementType.INSERT, 
                        """INSERT INTO summary_table (dept_name, total_employees, avg_salary)
                           SELECT d.department_name, COUNT(e.employee_id), AVG(e.salary)
                           FROM departments d
                           JOIN employees e ON d.department_id = e.department_id
                           GROUP BY d.department_name""", 
                        ["departments", "employees"], ["summary_table"])
        ]
        
        result = self.analyzer.analyze(sql_statements)
        
        # 检查字段血缘关系
        summary_table = result.physical_tables["summary_table"]
        assert "dept_name" in summary_table.fields
        assert "total_employees" in summary_table.fields
        assert "avg_salary" in summary_table.fields
    
    def test_aggregate_function_detection(self):
        """测试聚合函数检测"""
        sql_statements = [
            SQLStatement(1, StatementType.SELECT, 
                        "SELECT department_id, COUNT(*), AVG(salary), MAX(hire_date) FROM employees GROUP BY department_id", 
                        ["employees"], [])
        ]
        
        result = self.analyzer.analyze(sql_statements)
        
        # 应该检测到聚合函数的使用
        employees_table = result.physical_tables["employees"]
        assert "department_id" in employees_table.fields
        assert "salary" in employees_table.fields
        assert "hire_date" in employees_table.fields 
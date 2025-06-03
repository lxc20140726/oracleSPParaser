"""
测试数据模型
"""

import pytest
import sys
from pathlib import Path
from typing import List

# 添加项目路径
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from models.data_models import (
    Parameter, SQLStatement, StatementType, StoredProcedure,
    TableInfo, JoinCondition, AnalysisResult
)


class TestParameter:
    """测试参数模型"""
    
    def test_parameter_creation(self):
        """测试参数创建"""
        param = Parameter("p_emp_id", "IN", "NUMBER", "Employee ID parameter")
        
        assert param.name == "p_emp_id"
        assert param.direction == "IN"
        assert param.data_type == "NUMBER"
        assert param.description == "Employee ID parameter"
        assert param.used_in_statements == []
    
    def test_parameter_defaults(self):
        """测试参数默认值"""
        param = Parameter("p_name", "IN", "VARCHAR2")
        
        assert param.description is None
        assert param.default_value is None
        assert param.used_in_statements == []
    
    def test_parameter_equality(self):
        """测试参数相等性"""
        param1 = Parameter("p_id", "IN", "NUMBER")
        param2 = Parameter("p_id", "IN", "NUMBER")
        param3 = Parameter("p_id", "OUT", "NUMBER")
        
        assert param1 == param2
        assert param1 != param3
    
    def test_parameter_usage_tracking(self):
        """测试参数使用跟踪"""
        param = Parameter("p_dept_id", "IN", "NUMBER")
        param.used_in_statements = [1, 3, 5]
        
        assert 1 in param.used_in_statements
        assert 2 not in param.used_in_statements
        assert len(param.used_in_statements) == 3


class TestSQLStatement:
    """测试SQL语句模型"""
    
    def test_sql_statement_creation(self):
        """测试SQL语句创建"""
        stmt = SQLStatement(
            statement_id=1,
            statement_type=StatementType.SELECT,
            raw_sql="SELECT * FROM employees",
            source_tables=["employees"],
            target_tables=[]
        )
        
        assert stmt.statement_id == 1
        assert stmt.statement_type == StatementType.SELECT
        assert stmt.raw_sql == "SELECT * FROM employees"
        assert stmt.source_tables == ["employees"]
        assert stmt.target_tables == []
    
    def test_statement_type_enum(self):
        """测试语句类型枚举"""
        assert StatementType.SELECT.value == "SELECT"
        assert StatementType.INSERT.value == "INSERT"
        assert StatementType.UPDATE.value == "UPDATE"
        assert StatementType.DELETE.value == "DELETE"
        assert StatementType.CREATE_TABLE.value == "CREATE_TABLE"
    
    def test_sql_statement_with_parameters(self):
        """测试带参数的SQL语句"""
        stmt = SQLStatement(
            statement_id=2,
            statement_type=StatementType.UPDATE,
            raw_sql="UPDATE employees SET salary = ? WHERE employee_id = ?",
            source_tables=["employees"],
            target_tables=["employees"],
            parameters_used=["p_salary", "p_emp_id"]
        )
        
        assert len(stmt.parameters_used) == 2
        assert "p_salary" in stmt.parameters_used
        assert "p_emp_id" in stmt.parameters_used
    
    def test_complex_sql_statement(self):
        """测试复杂SQL语句"""
        stmt = SQLStatement(
            statement_id=3,
            statement_type=StatementType.INSERT,
            raw_sql="""INSERT INTO reports (dept_id, emp_count) 
                       SELECT department_id, COUNT(*) 
                       FROM employees 
                       GROUP BY department_id""",
            source_tables=["employees"],
            target_tables=["reports"],
            join_conditions=[],
            where_conditions=[]
        )
        
        assert "employees" in stmt.source_tables
        assert "reports" in stmt.target_tables
        assert stmt.join_conditions == []


class TestStoredProcedure:
    """测试存储过程模型"""
    
    def test_stored_procedure_creation(self):
        """测试存储过程创建"""
        parameters = [
            Parameter("p_emp_id", "IN", "NUMBER"),
            Parameter("p_salary", "IN", "NUMBER")
        ]
        
        sql_statements = [
            SQLStatement(1, StatementType.UPDATE, 
                        "UPDATE employees SET salary = ? WHERE employee_id = ?",
                        ["employees"], ["employees"], ["p_salary", "p_emp_id"])
        ]
        
        procedure = StoredProcedure(
            name="update_salary",
            parameters=parameters,
            sql_statements=sql_statements,
            raw_code="CREATE OR REPLACE PROCEDURE..."
        )
        
        assert procedure.name == "update_salary"
        assert len(procedure.parameters) == 2
        assert len(procedure.sql_statements) == 1
        assert procedure.raw_code.startswith("CREATE OR REPLACE PROCEDURE")
    
    def test_procedure_parameter_lookup(self):
        """测试存储过程参数查找"""
        parameters = [
            Parameter("p_emp_id", "IN", "NUMBER"),
            Parameter("p_result", "OUT", "VARCHAR2")
        ]
        
        procedure = StoredProcedure("test_proc", parameters, [])
        
        # 按名称查找参数
        emp_id_param = next((p for p in procedure.parameters if p.name == "p_emp_id"), None)
        assert emp_id_param is not None
        assert emp_id_param.data_type == "NUMBER"
        
        result_param = next((p for p in procedure.parameters if p.name == "p_result"), None)
        assert result_param is not None
        assert result_param.direction == "OUT"


class TestTableInfo:
    """测试表信息模型"""
    
    def test_table_info_creation(self):
        """测试表信息创建"""
        table = TableInfo(
            name="employees",
            fields=["employee_id", "first_name", "last_name", "salary"],
            source_sql_ids=[1, 2],
            target_sql_ids=[3]
        )
        
        assert table.name == "employees"
        assert len(table.fields) == 4
        assert "employee_id" in table.fields
        assert table.source_sql_ids == [1, 2]
        assert table.target_sql_ids == [3]
    
    def test_table_field_management(self):
        """测试表字段管理"""
        table = TableInfo("departments")
        
        # 添加字段
        table.fields.extend(["department_id", "department_name", "manager_id"])
        
        assert len(table.fields) == 3
        assert "department_id" in table.fields
        assert "department_name" in table.fields
    
    def test_table_usage_tracking(self):
        """测试表使用跟踪"""
        table = TableInfo("employees")
        
        table.source_sql_ids = [1, 3, 5]  # 被这些语句读取
        table.target_sql_ids = [2, 4]     # 被这些语句修改
        
        assert len(table.source_sql_ids) == 3
        assert len(table.target_sql_ids) == 2
        assert 1 in table.source_sql_ids
        assert 2 in table.target_sql_ids


class TestJoinCondition:
    """测试JOIN条件模型"""
    
    def test_join_condition_creation(self):
        """测试JOIN条件创建"""
        join_cond = JoinCondition(
            left_table="e",
            left_field="department_id",
            right_table="d",
            right_field="department_id",
            join_type="INNER",
            condition="e.department_id = d.department_id"
        )
        
        assert join_cond.left_table == "e"
        assert join_cond.left_field == "department_id"
        assert join_cond.right_table == "d"
        assert join_cond.right_field == "department_id"
        assert join_cond.join_type == "INNER"
        assert join_cond.condition == "e.department_id = d.department_id"
    
    def test_join_types(self):
        """测试不同类型的JOIN"""
        inner_join = JoinCondition("a", "id", "b", "id", "INNER")
        left_join = JoinCondition("a", "id", "b", "id", "LEFT")
        right_join = JoinCondition("a", "id", "b", "id", "RIGHT")
        full_join = JoinCondition("a", "id", "b", "id", "FULL")
        
        assert inner_join.join_type == "INNER"
        assert left_join.join_type == "LEFT"
        assert right_join.join_type == "RIGHT"
        assert full_join.join_type == "FULL"


class TestAnalysisResult:
    """测试分析结果模型"""
    
    def test_analysis_result_creation(self):
        """测试分析结果创建"""
        procedure = StoredProcedure("test_proc", [], [])
        
        result = AnalysisResult(
            stored_procedure=procedure,
            success=True,
            message="分析成功"
        )
        
        assert result.stored_procedure.name == "test_proc"
        assert result.success is True
        assert result.message == "分析成功"
        assert result.physical_tables == {}
        assert result.temp_tables == {}
        assert result.join_conditions == []
    
    def test_analysis_result_with_data(self):
        """测试包含数据的分析结果"""
        procedure = StoredProcedure("complex_proc", [], [])
        
        physical_tables = {
            "employees": TableInfo("employees", ["id", "name", "salary"]),
            "departments": TableInfo("departments", ["id", "name"])
        }
        
        temp_tables = {
            "temp_summary": TableInfo("temp_summary", ["dept_id", "emp_count"])
        }
        
        join_conditions = [
            JoinCondition("e", "dept_id", "d", "id", "INNER")
        ]
        
        result = AnalysisResult(
            stored_procedure=procedure,
            success=True,
            message="复杂分析完成",
            physical_tables=physical_tables,
            temp_tables=temp_tables,
            join_conditions=join_conditions
        )
        
        assert len(result.physical_tables) == 2
        assert len(result.temp_tables) == 1
        assert len(result.join_conditions) == 1
        assert "employees" in result.physical_tables
        assert "temp_summary" in result.temp_tables
    
    def test_analysis_failure(self):
        """测试分析失败情况"""
        result = AnalysisResult(
            stored_procedure=None,
            success=False,
            message="解析失败：语法错误",
            error_details="无效的SQL语法"
        )
        
        assert result.success is False
        assert "语法错误" in result.message
        assert result.error_details is not None
        assert result.stored_procedure is None 
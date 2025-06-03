"""
端到端集成测试
测试完整的存储过程解析和分析流程
"""

import pytest
import sys
from pathlib import Path

# 添加项目路径
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from main import OracleSPAnalyzer
from models.data_models import AnalysisResult


class TestEndToEndAnalysis:
    """端到端分析测试"""
    
    def setup_method(self):
        """测试前的设置"""
        self.analyzer = OracleSPAnalyzer()
    
    def test_simple_procedure_full_analysis(self, sample_simple_procedure):
        """测试简单存储过程的完整分析"""
        result = self.analyzer.analyze(sample_simple_procedure)
        
        # 验证分析成功
        assert result.success is True
        assert result.stored_procedure is not None
        
        # 验证存储过程基本信息
        procedure = result.stored_procedure
        assert procedure.name == "update_employee_salary"
        assert len(procedure.parameters) == 2
        
        # 验证参数信息
        param_names = [p.name for p in procedure.parameters]
        assert "p_emp_id" in param_names
        assert "p_new_salary" in param_names
        
        # 验证SQL语句解析
        assert len(procedure.sql_statements) >= 1
        update_stmt = procedure.sql_statements[0]
        assert "employees" in update_stmt.target_tables
        
        # 验证表分析结果
        assert "employees" in result.physical_tables
        employees_table = result.physical_tables["employees"]
        assert "salary" in employees_table.fields
        assert "employee_id" in employees_table.fields
    
    def test_complex_procedure_full_analysis(self, sample_complex_procedure):
        """测试复杂存储过程的完整分析"""
        result = self.analyzer.analyze(sample_complex_procedure)
        
        # 验证分析成功
        assert result.success is True
        assert result.stored_procedure is not None
        
        procedure = result.stored_procedure
        assert procedure.name == "process_employee_data"
        assert len(procedure.parameters) == 3
        
        # 验证参数
        param_names = [p.name for p in procedure.parameters]
        assert "p_dept_id" in param_names
        assert "p_start_date" in param_names
        assert "p_end_date" in param_names
        
        # 验证SQL语句数量（CREATE, UPDATE, INSERT）
        assert len(procedure.sql_statements) >= 3
        
        # 验证表识别
        assert "departments" in result.physical_tables
        assert "employees" in result.physical_tables
        assert "employee_reports" in result.physical_tables
        
        # 验证临时表识别
        assert "temp_emp_summary" in result.temp_tables
        
        # 验证JOIN关系
        assert len(result.join_conditions) >= 1
        dept_join = next((jc for jc in result.join_conditions 
                         if "department_id" in jc.condition), None)
        assert dept_join is not None
    
    def test_procedure_with_joins_full_analysis(self, sample_procedure_with_joins):
        """测试包含JOIN的存储过程完整分析"""
        result = self.analyzer.analyze(sample_procedure_with_joins)
        
        assert result.success is True
        procedure = result.stored_procedure
        assert procedure.name == "generate_department_report"
        
        # 验证涉及的表
        expected_tables = ["departments", "employees", "job_history", "annual_reports"]
        for table in expected_tables:
            assert table in result.physical_tables
        
        # 验证JOIN条件
        assert len(result.join_conditions) >= 2
        
        # 验证LEFT JOIN识别
        left_joins = [jc for jc in result.join_conditions if jc.join_type == "LEFT"]
        assert len(left_joins) >= 2
        
        # 验证字段血缘关系
        annual_reports = result.physical_tables["annual_reports"]
        expected_fields = ["report_year", "department_name", "total_employees", "total_salary", "avg_salary"]
        for field in expected_fields:
            assert field in annual_reports.fields
    
    def test_data_flow_analysis(self, sample_complex_procedure):
        """测试数据流向分析"""
        result = self.analyzer.analyze(sample_complex_procedure)
        
        assert result.success is True
        
        # 验证数据流向：departments + employees → temp_emp_summary → employee_reports
        
        # 源表验证
        departments_table = result.physical_tables["departments"]
        employees_table = result.physical_tables["employees"]
        assert len(departments_table.source_sql_ids) > 0
        assert len(employees_table.source_sql_ids) > 0
        
        # 目标表验证
        reports_table = result.physical_tables["employee_reports"]
        assert len(reports_table.target_sql_ids) > 0
        
        # 临时表验证
        temp_table = result.temp_tables["temp_emp_summary"]
        assert len(temp_table.target_sql_ids) > 0  # 被创建
        assert len(temp_table.source_sql_ids) > 0  # 被读取
    
    def test_parameter_dependency_analysis(self, sample_complex_procedure):
        """测试参数依赖分析"""
        result = self.analyzer.analyze(sample_complex_procedure)
        
        assert result.success is True
        procedure = result.stored_procedure
        
        # 验证参数使用情况
        for param in procedure.parameters:
            if param.name in ["p_dept_id", "p_start_date", "p_end_date"]:
                assert len(param.used_in_statements) > 0
        
        # 验证参数在WHERE条件中的使用
        dept_id_param = next(p for p in procedure.parameters if p.name == "p_dept_id")
        assert len(dept_id_param.used_in_statements) >= 2  # 在CREATE和UPDATE语句中使用
    
    def test_error_handling(self, invalid_procedure):
        """测试错误处理"""
        result = self.analyzer.analyze(invalid_procedure)
        
        # 验证错误处理
        assert result.success is False
        assert result.message is not None
        assert "错误" in result.message or "失败" in result.message
        assert result.error_details is not None
    
    def test_empty_procedure(self):
        """测试空存储过程"""
        empty_proc = """
        CREATE OR REPLACE PROCEDURE empty_proc AS
        BEGIN
            NULL;
        END;
        """
        
        result = self.analyzer.analyze(empty_proc)
        
        assert result.success is True
        assert result.stored_procedure.name == "empty_proc"
        assert len(result.stored_procedure.parameters) == 0
        assert len(result.stored_procedure.sql_statements) == 0
        assert len(result.physical_tables) == 0
    
    def test_procedure_with_comments(self):
        """测试带注释的存储过程"""
        commented_proc = """
        -- 更新员工薪资的存储过程
        CREATE OR REPLACE PROCEDURE update_salary(
            p_emp_id IN NUMBER,  -- 员工ID
            p_new_salary IN NUMBER  -- 新薪资
        ) AS
        BEGIN
            -- 更新员工薪资
            UPDATE employees 
            SET salary = p_new_salary,
                last_update_date = SYSDATE
            WHERE employee_id = p_emp_id;
            
            /* 记录薪资变更历史 */
            INSERT INTO salary_history (
                employee_id,
                new_salary,
                change_date
            ) VALUES (
                p_emp_id,
                p_new_salary,
                SYSDATE
            );
        END;
        """
        
        result = self.analyzer.analyze(commented_proc)
        
        assert result.success is True
        assert result.stored_procedure.name == "update_salary"
        assert len(result.stored_procedure.parameters) == 2
        assert "employees" in result.physical_tables
        assert "salary_history" in result.physical_tables
    
    def test_performance_with_large_procedure(self):
        """测试大型存储过程的性能"""
        # 生成一个包含多个SQL语句的大型存储过程
        large_proc = """
        CREATE OR REPLACE PROCEDURE large_procedure(
            p_start_date IN DATE,
            p_end_date IN DATE
        ) AS
        BEGIN
        """
        
        # 添加多个SELECT语句
        for i in range(10):
            large_proc += f"""
            INSERT INTO report_table_{i} (id, name, value)
            SELECT e.employee_id, e.first_name, e.salary + {i * 1000}
            FROM employees e
            JOIN departments d ON e.department_id = d.department_id
            WHERE e.hire_date BETWEEN p_start_date AND p_end_date;
            """
        
        large_proc += "END;"
        
        import time
        start_time = time.time()
        result = self.analyzer.analyze(large_proc)
        end_time = time.time()
        
        # 验证分析成功且在合理时间内完成
        assert result.success is True
        assert end_time - start_time < 10  # 应该在10秒内完成
        assert len(result.physical_tables) >= 12  # employees, departments, report_table_0-9
        assert len(result.join_conditions) >= 10  # 每个INSERT都有JOIN 
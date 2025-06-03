"""
Pytest配置文件
提供测试的公共fixture和配置
"""

import pytest
import sys
import os
from pathlib import Path

# 添加src路径到Python路径
src_path = Path(__file__).parent.parent / "src"
sys.path.insert(0, str(src_path))

# 添加backend路径
backend_path = Path(__file__).parent.parent / "backend"
sys.path.insert(0, str(backend_path))


@pytest.fixture
def sample_simple_procedure():
    """简单的存储过程示例"""
    return """
    CREATE OR REPLACE PROCEDURE update_employee_salary(
        p_emp_id IN NUMBER,
        p_new_salary IN NUMBER
    ) AS
    BEGIN
        UPDATE employees 
        SET salary = p_new_salary 
        WHERE employee_id = p_emp_id;
    END;
    """


@pytest.fixture
def sample_complex_procedure():
    """复杂的存储过程示例"""
    return """
    CREATE OR REPLACE PROCEDURE process_employee_data(
        p_dept_id IN NUMBER,
        p_start_date IN DATE,
        p_end_date IN DATE
    ) AS
    BEGIN
        -- 创建临时表
        CREATE GLOBAL TEMPORARY TABLE temp_emp_summary AS
        SELECT 
            d.department_name,
            e.employee_id,
            e.first_name,
            e.last_name,
            e.salary,
            e.hire_date
        FROM departments d
        INNER JOIN employees e ON d.department_id = e.department_id
        WHERE d.department_id = p_dept_id
          AND e.hire_date BETWEEN p_start_date AND p_end_date;
        
        -- 更新员工信息
        UPDATE employees e
        SET e.last_update_date = SYSDATE
        WHERE e.department_id = p_dept_id;
        
        -- 插入报告数据
        INSERT INTO employee_reports (
            report_date,
            dept_id,
            emp_count,
            avg_salary
        )
        SELECT 
            SYSDATE,
            p_dept_id,
            COUNT(*) as emp_count,
            AVG(salary) as avg_salary
        FROM temp_emp_summary;
    END;
    """


@pytest.fixture
def sample_procedure_with_joins():
    """包含JOIN的存储过程示例"""
    return """
    CREATE OR REPLACE PROCEDURE generate_department_report(
        p_year IN NUMBER
    ) AS
    BEGIN
        INSERT INTO annual_reports (
            report_year,
            department_name,
            total_employees,
            total_salary,
            avg_salary
        )
        SELECT 
            p_year,
            d.department_name,
            COUNT(e.employee_id) as total_employees,
            SUM(e.salary) as total_salary,
            AVG(e.salary) as avg_salary
        FROM departments d
        LEFT JOIN employees e ON d.department_id = e.department_id
        LEFT JOIN job_history jh ON e.employee_id = jh.employee_id
        WHERE EXTRACT(YEAR FROM e.hire_date) = p_year
        GROUP BY d.department_name
        ORDER BY total_salary DESC;
    END;
    """


@pytest.fixture
def invalid_procedure():
    """无效的存储过程示例"""
    return """
    CREATE OR REPLACE PROCEDURE invalid_proc
    BEGIN
        INVALID SQL STATEMENT;
        SELECT * FROM non_existent_table;
    """


@pytest.fixture
def test_data_directory():
    """测试数据目录"""
    return Path(__file__).parent / "data"


@pytest.fixture
def mock_database_schema():
    """模拟数据库架构"""
    return {
        "tables": {
            "employees": {
                "columns": [
                    "employee_id", "first_name", "last_name", 
                    "email", "phone_number", "hire_date", "job_id",
                    "salary", "commission_pct", "manager_id", "department_id",
                    "last_update_date"
                ],
                "primary_key": "employee_id",
                "foreign_keys": {
                    "department_id": "departments.department_id",
                    "manager_id": "employees.employee_id",
                    "job_id": "jobs.job_id"
                }
            },
            "departments": {
                "columns": [
                    "department_id", "department_name", "manager_id", "location_id"
                ],
                "primary_key": "department_id",
                "foreign_keys": {
                    "manager_id": "employees.employee_id"
                }
            },
            "jobs": {
                "columns": [
                    "job_id", "job_title", "min_salary", "max_salary"
                ],
                "primary_key": "job_id"
            },
            "job_history": {
                "columns": [
                    "employee_id", "start_date", "end_date", "job_id", "department_id"
                ],
                "primary_key": ["employee_id", "start_date"],
                "foreign_keys": {
                    "employee_id": "employees.employee_id",
                    "job_id": "jobs.job_id",
                    "department_id": "departments.department_id"
                }
            },
            "employee_reports": {
                "columns": [
                    "report_id", "report_date", "dept_id", "emp_count", "avg_salary"
                ],
                "primary_key": "report_id"
            },
            "annual_reports": {
                "columns": [
                    "report_id", "report_year", "department_name", 
                    "total_employees", "total_salary", "avg_salary"
                ],
                "primary_key": "report_id"
            },
            "salary_history": {
                "columns": [
                    "history_id", "employee_id", "old_salary", "new_salary", "change_date"
                ],
                "primary_key": "history_id",
                "foreign_keys": {
                    "employee_id": "employees.employee_id"
                }
            }
        }
    } 
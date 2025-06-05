#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from core.main import OracleSPAnalyzer

sample_sp = """
CREATE OR REPLACE PROCEDURE process_employee_data(
    p_dept_id IN NUMBER,
    p_start_date IN DATE
) AS
BEGIN
    -- 创建临时表
    CREATE GLOBAL TEMPORARY TABLE temp_emp_summary (
        emp_id NUMBER,
        emp_name VARCHAR2(100),
        dept_name VARCHAR2(100),
        salary NUMBER
    );
    
    -- 插入数据到临时表
    INSERT INTO temp_emp_summary
    SELECT e.employee_id, e.first_name || ' ' || e.last_name, 
           d.department_name, e.salary
    FROM employees e
    JOIN departments d ON e.department_id = d.department_id
    WHERE e.department_id = p_dept_id
    AND e.hire_date >= p_start_date;
    
    -- 更新员工薪资
    UPDATE employees 
    SET salary = salary * 1.1
    WHERE department_id = p_dept_id;
    
    -- 生成报告
    INSERT INTO employee_reports (report_date, dept_id, emp_count, avg_salary)
    SELECT SYSDATE, p_dept_id, COUNT(*), AVG(salary)
    FROM temp_emp_summary;
    
END;
"""

analyzer = OracleSPAnalyzer()
result = analyzer.analyze(sample_sp)

# 打印第二个SQL语句的详细信息
stmt = result.sp_structure.sql_statements[1]
print('SQL语句:', stmt.raw_sql)
print('JOIN条件数量:', len(stmt.join_conditions))
for join_cond in stmt.join_conditions:
    print('JOIN条件:', join_cond) 
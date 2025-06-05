#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from core.main import OracleSPAnalyzer

def main():
    analyzer = OracleSPAnalyzer()
    
    # 示例存储过程
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
    
    print("开始分析存储过程...")
    result = analyzer.analyze(sample_sp)
    
    print("\n=== 分析结果 ===")
    print(f"存储过程名称: {result.sp_structure.name}")
    print(f"参数数量: {len(result.parameters)}")
    print(f"SQL语句数量: {len(result.sp_structure.sql_statements)}")
    print(f"物理表数量: {len(result.table_field_analysis.physical_tables)}")
    print(f"临时表数量: {len(result.table_field_analysis.temp_tables)}")
    print(f"连接条件数量: {len(result.conditions_and_logic.join_conditions)}")
    
    print("\n=== 参数列表 ===")
    for param in result.parameters:
        print(f"- {param.name} ({param.direction} {param.data_type})")
    
    print("\n=== 物理表 ===")
    for table_name, table in result.table_field_analysis.physical_tables.items():
        print(f"- {table_name}: {len(table.fields)} 个字段")
        for field in sorted(table.fields):
            print(f"  * {field}")
    
    print("\n=== 临时表 ===")
    for table_name, table in result.table_field_analysis.temp_tables.items():
        print(f"- {table_name}: {len(table.fields)} 个字段")
        for field in sorted(table.fields):
            print(f"  * {field}")
    
    print("\n=== JOIN条件 ===")
    for join_cond in result.conditions_and_logic.join_conditions:
        print(f"- {join_cond.left_table}.{join_cond.left_field} = {join_cond.right_table}.{join_cond.right_field} ({join_cond.join_type})")
    
    print("\n分析完成！生成的可视化数据已保存到 visualization_data.json")
    
    # 启动Web界面
    print("\n启动Web界面...")
    print("请在浏览器中访问显示的URL查看交互式可视化")
    analyzer.start_web_interface(result)

if __name__ == "__main__":
    main() 
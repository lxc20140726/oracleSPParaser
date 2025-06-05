#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import os
from pathlib import Path

# 添加当前目录到Python路径
current_dir = Path(__file__).parent
sys.path.insert(0, str(current_dir))

from core.main import OracleSPAnalyzer

def test_complex_field_parsing():
    """测试复合字段解析功能"""
    
    # 创建测试SQL
    test_sql = """
    CREATE OR REPLACE PROCEDURE process_employee_data(
        p_dept_id IN NUMBER,
        p_start_date IN DATE
    ) AS
    BEGIN
        INSERT INTO temp_emp_summary
        SELECT e.employee_id, e.first_name || ' ' || e.last_name, 
               d.department_name, e.salary
        FROM employees e
        JOIN departments d ON e.department_id = d.department_id
        WHERE e.department_id = p_dept_id
        AND e.hire_date >= p_start_date;
    END;
    """
    
    print("开始测试复合字段解析功能...")
    print("测试SQL:")
    print(test_sql)
    print("\n" + "="*60)
    
    analyzer = OracleSPAnalyzer()
    result = analyzer.analyze(test_sql)
    
    # 输出分析结果
    print('\n=== 分析结果 ===')
    print(f'解析到 {len(result.sp_structure.sql_statements)} 个SQL语句')
    
    # 查看表分析结果
    table_analysis = result.table_field_analysis
    print(f'\n实体表数量: {len(table_analysis.physical_tables)}')
    for table_name, table_info in table_analysis.physical_tables.items():
        print(f'  表: {table_name}')
        print(f'    字段: {table_info.fields}')
        if hasattr(table_info, 'computed_fields') and table_info.computed_fields:
            print(f'    计算字段: {len(table_info.computed_fields)} 个')
            for cf in table_info.computed_fields:
                print(f'      表达式: {cf.expression}')
                print(f'      目标字段: {cf.target_field_name}')
                component_fields_str = [f"{f.table_name}.{f.field_name}" for f in cf.component_fields]
                print(f'      组成字段: {component_fields_str}')
    
    print(f'\n临时表数量: {len(table_analysis.temp_tables)}')
    for table_name, table_info in table_analysis.temp_tables.items():
        print(f'  表: {table_name}')
        print(f'    字段: {table_info.fields}')
        if hasattr(table_info, 'computed_fields') and table_info.computed_fields:
            print(f'    计算字段: {len(table_info.computed_fields)} 个')
            for cf in table_info.computed_fields:
                print(f'      表达式: {cf.expression}')
                print(f'      目标字段: {cf.target_field_name}')
                component_fields_str = [f"{f.table_name}.{f.field_name}" for f in cf.component_fields]
                print(f'      组成字段: {component_fields_str}')
    
    # 显示字段识别详情
    print(f'\n=== 字段识别详情 ===')
    for stmt in result.sp_structure.sql_statements:
        print(f'\nSQL语句ID: {stmt.statement_id}')
        print(f'类型: {stmt.statement_type}')
        print(f'读取字段数量: {len(stmt.fields_read)}')
        for field in stmt.fields_read:
            print(f'  读取: {field.table_name}.{field.field_name}')
        print(f'写入字段数量: {len(stmt.fields_written)}')
        for field in stmt.fields_written:
            print(f'  写入: {field.table_name}.{field.field_name}')

if __name__ == "__main__":
    test_complex_field_parsing() 
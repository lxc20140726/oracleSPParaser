#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import os
import re
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from src.parser.sp_parser import StoredProcedureParser

def debug_join_parsing():
    """调试JOIN条件解析"""
    
    test_sql = """
    INSERT INTO temp_emp_summary
    SELECT e.employee_id, e.first_name || ' ' || e.last_name, 
           d.department_name, e.salary
    FROM employees e
    JOIN departments d ON e.department_id = d.department_id
    WHERE e.department_id = p_dept_id
    AND e.hire_date >= p_start_date;
    """
    
    print("="*80)
    print("调试JOIN条件解析")
    print("="*80)
    
    print("原始SQL:")
    print(test_sql)
    print("\n" + "-"*60)
    
    parser = StoredProcedureParser()
    
    # 测试JOIN条件提取
    join_conditions = parser._extract_join_conditions(test_sql)
    print(f"提取到的JOIN条件数量: {len(join_conditions)}")
    
    for i, join_cond in enumerate(join_conditions):
        print(f"JOIN条件 {i+1}:")
        print(f"  左表: {join_cond.left_table}")
        print(f"  左字段: {join_cond.left_field}")
        print(f"  右表: {join_cond.right_table}")
        print(f"  右字段: {join_cond.right_field}")
        print(f"  JOIN类型: {join_cond.join_type}")
        print(f"  条件文本: {join_cond.condition_text}")
    
    print("\n" + "-"*60)
    print("手动正则表达式测试:")
    
    # 测试不同的JOIN正则表达式
    join_patterns = [
        r'(?:INNER\s+)?JOIN\s+(\w+)(?:\s+(\w+))?\s+ON\s+([^WHERE|GROUP|ORDER|HAVING|UNION|;]+)',
        r'LEFT\s+(?:OUTER\s+)?JOIN\s+(\w+)(?:\s+(\w+))?\s+ON\s+([^WHERE|GROUP|ORDER|HAVING|UNION|;]+)',
        r'RIGHT\s+(?:OUTER\s+)?JOIN\s+(\w+)(?:\s+(\w+))?\s+ON\s+([^WHERE|GROUP|ORDER|HAVING|UNION|;]+)',
        r'FULL\s+(?:OUTER\s+)?JOIN\s+(\w+)(?:\s+(\w+))?\s+ON\s+([^WHERE|GROUP|ORDER|HAVING|UNION|;]+)',
    ]
    
    for i, pattern in enumerate(join_patterns):
        print(f"\n模式 {i+1}: {pattern}")
        matches = re.finditer(pattern, test_sql, re.IGNORECASE | re.DOTALL)
        match_count = 0
        for match in matches:
            match_count += 1
            print(f"  匹配 {match_count}:")
            print(f"    全匹配: '{match.group(0)}'")
            print(f"    组1 (表名): '{match.group(1)}'")
            if match.group(2):
                print(f"    组2 (别名): '{match.group(2)}'")
            print(f"    组3 (条件): '{match.group(3)}'")
        
        if match_count == 0:
            print("  无匹配")
    
    # 测试简化的JOIN模式
    print("\n" + "-"*60)
    print("简化JOIN模式测试:")
    simple_pattern = r'JOIN\s+(\w+)\s+(\w+)\s+ON\s+(.+?)(?=\s+WHERE|\s*$)'
    matches = re.finditer(simple_pattern, test_sql, re.IGNORECASE | re.DOTALL)
    
    for match in matches:
        print(f"简化模式匹配:")
        print(f"  表名: '{match.group(1)}'")
        print(f"  别名: '{match.group(2)}'")
        print(f"  条件: '{match.group(3)}'")
        
        # 解析条件
        condition_text = match.group(3).strip()
        condition_pattern = r'(\w+)\.(\w+)\s*=\s*(\w+)\.(\w+)'
        cond_match = re.search(condition_pattern, condition_text)
        if cond_match:
            print(f"  条件解析成功:")
            print(f"    左表.字段: {cond_match.group(1)}.{cond_match.group(2)}")
            print(f"    右表.字段: {cond_match.group(3)}.{cond_match.group(4)}")

if __name__ == "__main__":
    debug_join_parsing() 
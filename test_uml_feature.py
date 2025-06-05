#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
测试UML可视化功能
"""

import sys
import os
from pathlib import Path

# 添加core路径
core_path = Path(__file__).parent / "core"
sys.path.insert(0, str(core_path))

from core.main import OracleSPAnalyzer

def test_uml_visualization():
    """测试UML可视化功能"""
    
    # 创建分析器实例
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
    
    print("🔍 开始分析存储过程...")
    
    # 执行分析
    result = analyzer.analyze(sample_sp)
    
    print(f"✅ 分析完成！")
    print(f"📊 发现 {len(result.table_field_analysis.physical_tables)} 个物理表")
    print(f"🟡 发现 {len(result.table_field_analysis.temp_tables)} 个临时表")
    print(f"🔗 发现 {len(result.conditions_and_logic.join_conditions)} 个JOIN条件")
    
    # 检查UML可视化数据文件
    uml_file = Path("uml_visualization_data.json")
    if uml_file.exists():
        print(f"📁 UML可视化数据已保存到: {uml_file}")
        
        import json
        with open(uml_file, 'r', encoding='utf-8') as f:
            uml_data = json.load(f)
        
        print(f"🗂️ UML节点数: {len(uml_data.get('nodes', []))}")
        print(f"🔗 字段映射数: {len(uml_data.get('field_mappings', []))}")
        print(f"📋 表关系数: {len(uml_data.get('table_relations', []))}")
        
        # 显示表结构信息
        print("\n📋 表结构详情:")
        for node in uml_data.get('nodes', []):
            table_name = node['label']
            fields = node['properties']['fields']
            is_temp = node['properties']['is_temporary']
            table_type = "临时表" if is_temp else "物理表"
            
            print(f"  {table_type}: {table_name}")
            print(f"    字段数: {len(fields)}")
            for field in fields:
                field_type = "计算字段" if field['type'] == 'computed_field' else "普通字段"
                print(f"      - {field['name']} ({field_type})")
                if field['type'] == 'computed_field' and 'expression' in field:
                    print(f"        表达式: {field['expression']}")
        
        # 显示字段映射
        if uml_data.get('field_mappings'):
            print("\n🔗 字段映射关系:")
            for mapping in uml_data['field_mappings']:
                props = mapping['properties']
                print(f"  {props['source_field']} ({props['source_table']}) → {props['target_field']} ({props['target_table']})")
                if props.get('expression'):
                    print(f"    表达式: {props['expression']}")
    
    print("\n🎉 UML可视化功能测试完成！")
    print("💡 您可以通过以下方式查看结果：")
    print("   1. 查看控制台输出的ASCII UML图")
    print("   2. 打开 uml_visualization_data.json 文件")
    print("   3. 在Web界面中使用UML分析功能")

if __name__ == "__main__":
    test_uml_visualization() 
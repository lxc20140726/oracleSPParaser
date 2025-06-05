#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import requests
import json

def test_uml_api():
    """测试UML分析API"""
    
    sample_sp = """CREATE OR REPLACE PROCEDURE process_employee_data(
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
    
END;"""

    print("🔍 测试UML分析API...")
    
    try:
        # 发送API请求
        response = requests.post(
            "http://localhost:8000/api/analyze/uml",
            json={"stored_procedure": sample_sp},
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ API响应成功: {result.get('message', 'N/A')}")
            
            # 检查UML数据
            if 'uml_visualization' in result:
                uml_data = result['uml_visualization']
                print(f"📊 UML节点数: {len(uml_data.get('nodes', []))}")
                print(f"🔗 字段映射数: {len(uml_data.get('field_mappings', []))}")
                print(f"📋 表关系数: {len(uml_data.get('table_relations', []))}")
                
                # 显示字段映射关系
                print("\n🔗 字段映射关系:")
                for mapping in uml_data.get('field_mappings', []):
                    props = mapping.get('properties', {})
                    print(f"  {props.get('source_field')} ({props.get('source_table')}) → {props.get('target_field')} ({props.get('target_table')})")
                    if props.get('expression'):
                        print(f"    表达式: {props.get('expression')}")
                
                print("\n🎉 UML API测试成功！")
                return True
            else:
                print("❌ 响应中缺少UML数据")
                return False
        else:
            print(f"❌ API请求失败: {response.status_code}")
            print(f"错误信息: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ 测试出错: {e}")
        return False

if __name__ == "__main__":
    test_uml_api() 
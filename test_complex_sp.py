#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from src.main import OracleSPAnalyzer

def test_complex_stored_procedure():
    """测试复杂存储过程分析"""
    
    complex_sp = """
    CREATE OR REPLACE PROCEDURE complex_data_processing(
        p_start_date IN DATE,
        p_end_date IN DATE,
        p_department_id IN NUMBER,
        p_salary_threshold IN NUMBER,
        p_result_count OUT NUMBER
    ) AS
        -- 声明游标
        CURSOR emp_cursor IS
            SELECT e.employee_id, e.first_name, e.last_name, e.salary, e.department_id
            FROM employees e
            WHERE e.hire_date BETWEEN p_start_date AND p_end_date
            AND e.department_id = p_department_id;
        
        -- 声明变量
        v_emp_record emp_cursor%ROWTYPE;
        v_total_processed NUMBER := 0;
        v_high_salary_count NUMBER := 0;
        
    BEGIN
        -- 创建临时表存储处理结果
        CREATE GLOBAL TEMPORARY TABLE temp_processing_results (
            employee_id NUMBER,
            full_name VARCHAR2(200),
            original_salary NUMBER,
            adjusted_salary NUMBER,
            department_name VARCHAR2(100),
            processing_date DATE,
            salary_category VARCHAR2(20)
        );
        
        -- 创建另一个临时表存储统计信息
        CREATE GLOBAL TEMPORARY TABLE temp_statistics (
            dept_id NUMBER,
            total_employees NUMBER,
            avg_salary NUMBER,
            high_salary_count NUMBER,
            processing_timestamp TIMESTAMP
        );
        
        -- 打开游标并处理数据
        OPEN emp_cursor;
        LOOP
            FETCH emp_cursor INTO v_emp_record;
            EXIT WHEN emp_cursor%NOTFOUND;
            
            -- 根据薪资条件进行不同处理
            IF v_emp_record.salary > p_salary_threshold THEN
                -- 高薪员工处理
                INSERT INTO temp_processing_results
                SELECT 
                    e.employee_id,
                    e.first_name || ' ' || e.last_name,
                    e.salary,
                    e.salary * 1.05,  -- 5%加薪
                    d.department_name,
                    SYSDATE,
                    'HIGH_SALARY'
                FROM employees e
                JOIN departments d ON e.department_id = d.department_id
                WHERE e.employee_id = v_emp_record.employee_id;
                
                v_high_salary_count := v_high_salary_count + 1;
                
            ELSE
                -- 普通员工处理
                INSERT INTO temp_processing_results
                SELECT 
                    e.employee_id,
                    e.first_name || ' ' || e.last_name,
                    e.salary,
                    e.salary * 1.03,  -- 3%加薪
                    d.department_name,
                    SYSDATE,
                    'NORMAL_SALARY'
                FROM employees e
                JOIN departments d ON e.department_id = d.department_id
                WHERE e.employee_id = v_emp_record.employee_id;
            END IF;
            
            v_total_processed := v_total_processed + 1;
        END LOOP;
        CLOSE emp_cursor;
        
        -- 生成统计信息
        INSERT INTO temp_statistics
        SELECT 
            p_department_id,
            COUNT(*),
            AVG(adjusted_salary),
            SUM(CASE WHEN salary_category = 'HIGH_SALARY' THEN 1 ELSE 0 END),
            SYSTIMESTAMP
        FROM temp_processing_results;
        
        -- 更新原始员工表
        UPDATE employees e
        SET salary = (
            SELECT tpr.adjusted_salary
            FROM temp_processing_results tpr
            WHERE tpr.employee_id = e.employee_id
        )
        WHERE EXISTS (
            SELECT 1 
            FROM temp_processing_results tpr2
            WHERE tpr2.employee_id = e.employee_id
        );
        
        -- 插入处理日志
        INSERT INTO processing_log (
            processing_date,
            department_id,
            employees_processed,
            high_salary_employees,
            avg_new_salary
        )
        SELECT 
            SYSDATE,
            ts.dept_id,
            ts.total_employees,
            ts.high_salary_count,
            ts.avg_salary
        FROM temp_statistics ts;
        
        -- 如果处理的员工数量超过阈值，发送通知
        IF v_total_processed > 10 THEN
            INSERT INTO notifications (
                notification_type,
                message,
                created_date,
                department_id
            ) VALUES (
                'BULK_PROCESSING',
                'Processed ' || v_total_processed || ' employees in department ' || p_department_id,
                SYSDATE,
                p_department_id
            );
        END IF;
        
        -- 设置输出参数
        p_result_count := v_total_processed;
        
        -- 清理临时数据（可选）
        DELETE FROM temp_processing_results;
        DELETE FROM temp_statistics;
        
    EXCEPTION
        WHEN OTHERS THEN
            -- 错误处理
            INSERT INTO error_log (
                error_date,
                error_message,
                procedure_name,
                department_id
            ) VALUES (
                SYSDATE,
                SQLERRM,
                'complex_data_processing',
                p_department_id
            );
            RAISE;
    END;
    """
    
    print("="*80)
    print("测试复杂存储过程分析")
    print("="*80)
    
    analyzer = OracleSPAnalyzer()
    result = analyzer.analyze(complex_sp)
    
    print(f"\n📊 分析结果统计:")
    print(f"   存储过程名称: {result.sp_structure.name}")
    print(f"   参数数量: {len(result.parameters)} 个")
    print(f"   SQL语句数量: {len(result.sp_structure.sql_statements)} 个")
    print(f"   物理表数量: {len(result.table_field_analysis.physical_tables)} 个")
    print(f"   临时表数量: {len(result.table_field_analysis.temp_tables)} 个")
    print(f"   连接条件数量: {len(result.conditions_and_logic.join_conditions)} 个")
    
    print(f"\n📋 详细参数信息:")
    for param in result.parameters:
        print(f"   • {param.name} ({param.direction} {param.data_type})")
        if param.used_in_statements:
            print(f"     使用在SQL语句: {', '.join(param.used_in_statements)}")
    
    print(f"\n🗃️ 涉及的表:")
    print("   物理表:")
    for table_name, table in result.table_field_analysis.physical_tables.items():
        print(f"   • {table_name}")
        if table.fields:
            print(f"     字段: {', '.join(sorted(table.fields))}")
        if table.source_sql_ids:
            print(f"     涉及SQL: {', '.join(table.source_sql_ids)}")
    
    print("   临时表:")
    for table_name, table in result.table_field_analysis.temp_tables.items():
        print(f"   • {table_name}")
        if table.fields:
            print(f"     字段: {', '.join(sorted(table.fields))}")
        if table.source_sql_ids:
            print(f"     涉及SQL: {', '.join(table.source_sql_ids)}")
    
    print(f"\n🔗 JOIN条件:")
    if result.conditions_and_logic.join_conditions:
        for join_cond in result.conditions_and_logic.join_conditions:
            print(f"   • {join_cond.left_table}.{join_cond.left_field} = {join_cond.right_table}.{join_cond.right_field}")
            print(f"     类型: {join_cond.join_type}")
    else:
        print("   未检测到JOIN条件")
    
    print(f"\n💾 可视化数据已保存到: visualization_data.json")
    
    return result

if __name__ == "__main__":
    test_complex_stored_procedure() 
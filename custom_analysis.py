#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from src.main import OracleSPAnalyzer

def analyze_my_stored_procedure():
    """分析自定义存储过程"""
    
    # 1. 准备你的存储过程代码
    my_stored_procedure = """
    CREATE OR REPLACE PROCEDURE update_employee_salary(
        p_employee_id IN NUMBER,
        p_increase_percent IN NUMBER,
        p_effective_date IN DATE,
        p_updated_count OUT NUMBER
    ) AS
        v_old_salary NUMBER;
        v_new_salary NUMBER;
    BEGIN
        -- 获取当前薪资
        SELECT salary INTO v_old_salary
        FROM employees
        WHERE employee_id = p_employee_id;
        
        -- 计算新薪资
        v_new_salary := v_old_salary * (1 + p_increase_percent / 100);
        
        -- 更新薪资
        UPDATE employees
        SET salary = v_new_salary,
            last_updated = p_effective_date
        WHERE employee_id = p_employee_id;
        
        -- 记录变更历史
        INSERT INTO salary_history (
            employee_id,
            old_salary,
            new_salary,
            change_date,
            change_percent
        ) VALUES (
            p_employee_id,
            v_old_salary,
            v_new_salary,
            p_effective_date,
            p_increase_percent
        );
        
        p_updated_count := SQL%ROWCOUNT;
    END;
    """
    
    # 2. 创建分析器实例
    analyzer = OracleSPAnalyzer()
    
    # 3. 执行分析
    print("🔍 开始分析自定义存储过程...")
    result = analyzer.analyze(my_stored_procedure)
    
    # 4. 查看分析结果
    print(f"\n📊 分析完成！")
    print(f"存储过程名称: {result.sp_structure.name}")
    print(f"参数数量: {len(result.parameters)}")
    print(f"SQL语句数量: {len(result.sp_structure.sql_statements)}")
    
    # 5. 详细信息
    print(f"\n📋 参数详情:")
    for param in result.parameters:
        print(f"  • {param.name} ({param.direction} {param.data_type})")
    
    print(f"\n🗃️ 涉及的表:")
    for table_name, table in result.table_field_analysis.physical_tables.items():
        print(f"  • {table_name}")
    
    print(f"\n🔗 数据流向:")
    for stmt in result.sp_structure.sql_statements:
        if stmt.source_tables and stmt.target_tables:
            for source in stmt.source_tables:
                for target in stmt.target_tables:
                    print(f"  • {source} ──[{stmt.statement_type.value}]──> {target}")
    
    # 6. 保存结果（可选）
    print(f"\n💾 可视化数据已保存到 visualization_data.json")
    
    return result

if __name__ == "__main__":
    analyze_my_stored_procedure() 
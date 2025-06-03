#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import os
from pathlib import Path

# 添加当前目录到Python路径
current_dir = Path(__file__).parent
sys.path.insert(0, str(current_dir))

from parser.sp_parser import StoredProcedureParser
from analyzer.parameter_analyzer import ParameterAnalyzer
from analyzer.table_field_analyzer import TableFieldAnalyzer
from analyzer.condition_analyzer import ConditionAnalyzer
from visualizer.interactive_visualizer import InteractiveVisualizer
from models.data_models import StoredProcedureAnalysis

class OracleSPAnalyzer:
    """
    Oracle存储过程分析器
    专注于数据流向、字段联系和匹配条件分析
    """
    
    def __init__(self):
        self.sp_parser = StoredProcedureParser()
        self.param_analyzer = ParameterAnalyzer()
        self.table_field_analyzer = TableFieldAnalyzer()
        self.condition_analyzer = ConditionAnalyzer()
        self.visualizer = InteractiveVisualizer()

    def analyze(self, sp_text: str) -> StoredProcedureAnalysis:
        """
        按照用户定义的逻辑流程分析存储过程：
        1. 获取完整存储过程，开始分析
        2. 识别并确认外来参数
        3. SQL解析sql语句并确认参与实体表与临时表，构建实体表与临时表对象
        4. 检查sql涉及的实体表与临时表字段是否存在于存储中，如不存在，则添加到实体表与临时表对象中
        5. 分别存储匹配条件和sql逻辑
        6. 使用实体表、临时表对象，sql逻辑和匹配条件进行可视化
        """
        
        print("开始分析存储过程...")
        
        # 1. 解析存储过程结构
        sp_structure = self.sp_parser.parse(sp_text)
        print(f"解析完成，发现 {len(sp_structure.sql_statements)} 个SQL语句")
        
        # 2. 识别外来参数
        parameters = self.param_analyzer.extract_parameters(sp_structure)
        print(f"识别到 {len(parameters)} 个参数")
        
        # 3. 分析表和字段关系
        table_field_analysis = self.table_field_analyzer.analyze(sp_structure)
        print(f"分析完成，发现 {len(table_field_analysis.physical_tables)} 个实体表，{len(table_field_analysis.temp_tables)} 个临时表")
        
        # 4. 分析匹配条件和SQL逻辑
        conditions_and_logic = self.condition_analyzer.analyze(sp_structure)
        print(f"提取到 {len(conditions_and_logic.join_conditions)} 个连接条件")
        
        # 5. 构建最终分析结果
        analysis_result = StoredProcedureAnalysis(
            sp_structure=sp_structure,
            parameters=parameters,
            table_field_analysis=table_field_analysis,
            conditions_and_logic=conditions_and_logic
        )
        
        # 6. 生成交互式可视化
        self.visualizer.create_interactive_visualization(analysis_result)
        
        return analysis_result

    def start_web_interface(self, analysis_result: StoredProcedureAnalysis = None):
        """启动Web界面"""
        self.visualizer.start_web_interface(analysis_result)

if __name__ == "__main__":
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
    
    result = analyzer.analyze(sample_sp)
    print("\n分析完成！启动Web界面...")
    analyzer.start_web_interface(result) 
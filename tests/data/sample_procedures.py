#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试数据 - 示例存储过程
包含各种复杂度和类型的Oracle存储过程示例
"""

# 简单存储过程
SIMPLE_PROCEDURE = """
CREATE OR REPLACE PROCEDURE simple_employee_update(
    p_employee_id IN NUMBER,
    p_salary_increase IN NUMBER
) AS
BEGIN
    UPDATE employees 
    SET salary = salary + p_salary_increase 
    WHERE employee_id = p_employee_id;
    
    COMMIT;
END;
"""

# 中等复杂度存储过程
MEDIUM_PROCEDURE = """
CREATE OR REPLACE PROCEDURE department_salary_analysis(
    p_department_id IN NUMBER,
    p_analysis_date IN DATE,
    p_total_employees OUT NUMBER,
    p_average_salary OUT NUMBER
) AS
    v_min_salary NUMBER;
    v_max_salary NUMBER;
BEGIN
    -- 获取部门员工统计
    SELECT COUNT(*), AVG(salary), MIN(salary), MAX(salary)
    INTO p_total_employees, p_average_salary, v_min_salary, v_max_salary
    FROM employees e
    JOIN departments d ON e.department_id = d.department_id
    WHERE d.department_id = p_department_id
    AND e.hire_date <= p_analysis_date;
    
    -- 记录分析结果
    INSERT INTO salary_analysis_log (
        department_id, analysis_date, total_employees, 
        avg_salary, min_salary, max_salary, created_date
    ) VALUES (
        p_department_id, p_analysis_date, p_total_employees,
        p_average_salary, v_min_salary, v_max_salary, SYSDATE
    );
    
    -- 更新部门统计表
    MERGE INTO department_statistics ds
    USING (
        SELECT p_department_id as dept_id, 
               p_total_employees as emp_count,
               p_average_salary as avg_sal
        FROM dual
    ) src ON (ds.department_id = src.dept_id)
    WHEN MATCHED THEN
        UPDATE SET employee_count = src.emp_count,
                   average_salary = src.avg_sal,
                   last_updated = SYSDATE
    WHEN NOT MATCHED THEN
        INSERT (department_id, employee_count, average_salary, last_updated)
        VALUES (src.dept_id, src.emp_count, src.avg_sal, SYSDATE);
    
    COMMIT;
END;
"""

# 复杂存储过程（包含游标、异常处理、动态SQL）
COMPLEX_PROCEDURE = """
CREATE OR REPLACE PROCEDURE complex_payroll_processing(
    p_pay_period_start IN DATE,
    p_pay_period_end IN DATE,
    p_department_filter IN VARCHAR2 DEFAULT NULL,
    p_process_mode IN VARCHAR2 DEFAULT 'NORMAL',
    p_processed_count OUT NUMBER,
    p_error_count OUT NUMBER,
    p_total_amount OUT NUMBER
) AS
    -- 声明游标
    CURSOR emp_cursor IS
        SELECT e.employee_id, e.first_name, e.last_name, e.salary,
               e.department_id, d.department_name, e.hire_date,
               e.commission_pct, m.first_name as manager_name
        FROM employees e
        JOIN departments d ON e.department_id = d.department_id
        LEFT JOIN employees m ON e.manager_id = m.employee_id
        WHERE (p_department_filter IS NULL OR d.department_name = p_department_filter)
        AND e.hire_date <= p_pay_period_end
        ORDER BY d.department_id, e.employee_id;
    
    -- 记录类型定义
    TYPE emp_record_type IS RECORD (
        employee_id employees.employee_id%TYPE,
        full_name VARCHAR2(200),
        base_salary NUMBER,
        bonus_amount NUMBER,
        total_pay NUMBER,
        tax_amount NUMBER,
        net_pay NUMBER
    );
    
    TYPE emp_table_type IS TABLE OF emp_record_type INDEX BY PLS_INTEGER;
    emp_batch emp_table_type;
    
    -- 变量声明
    v_batch_size CONSTANT NUMBER := 100;
    v_current_batch NUMBER := 0;
    v_sql VARCHAR2(4000);
    v_error_msg VARCHAR2(4000);
    v_bonus_rate NUMBER := 0.05;
    v_tax_rate NUMBER := 0.20;
    
    -- 异常定义
    e_invalid_date EXCEPTION;
    e_processing_error EXCEPTION;
    
BEGIN
    -- 初始化输出参数
    p_processed_count := 0;
    p_error_count := 0;
    p_total_amount := 0;
    
    -- 参数验证
    IF p_pay_period_start >= p_pay_period_end THEN
        RAISE e_invalid_date;
    END IF;
    
    -- 根据处理模式设置参数
    CASE p_process_mode
        WHEN 'AGGRESSIVE' THEN
            v_bonus_rate := 0.08;
            v_tax_rate := 0.18;
        WHEN 'CONSERVATIVE' THEN
            v_bonus_rate := 0.03;
            v_tax_rate := 0.22;
        ELSE
            v_bonus_rate := 0.05;
            v_tax_rate := 0.20;
    END CASE;
    
    -- 创建临时表（动态SQL）
    BEGIN
        v_sql := 'CREATE GLOBAL TEMPORARY TABLE temp_payroll_' || 
                 TO_CHAR(SYSDATE, 'YYYYMMDD') || ' (
            employee_id NUMBER,
            full_name VARCHAR2(200),
            base_salary NUMBER,
            bonus_amount NUMBER,
            total_pay NUMBER,
            tax_amount NUMBER,
            net_pay NUMBER,
            process_date DATE
        )';
        EXECUTE IMMEDIATE v_sql;
    EXCEPTION
        WHEN OTHERS THEN
            IF SQLCODE != -955 THEN  -- 表已存在
                RAISE;
            END IF;
    END;
    
    -- 处理员工数据
    FOR emp_rec IN emp_cursor LOOP
        BEGIN
            v_current_batch := v_current_batch + 1;
            
            -- 计算薪资
            emp_batch(v_current_batch).employee_id := emp_rec.employee_id;
            emp_batch(v_current_batch).full_name := emp_rec.first_name || ' ' || emp_rec.last_name;
            emp_batch(v_current_batch).base_salary := emp_rec.salary;
            
            -- 计算奖金
            IF emp_rec.commission_pct IS NOT NULL THEN
                emp_batch(v_current_batch).bonus_amount := 
                    emp_rec.salary * emp_rec.commission_pct * v_bonus_rate;
            ELSE
                emp_batch(v_current_batch).bonus_amount := 
                    emp_rec.salary * v_bonus_rate;
            END IF;
            
            -- 计算总薪资
            emp_batch(v_current_batch).total_pay := 
                emp_batch(v_current_batch).base_salary + 
                emp_batch(v_current_batch).bonus_amount;
            
            -- 计算税款
            emp_batch(v_current_batch).tax_amount := 
                emp_batch(v_current_batch).total_pay * v_tax_rate;
            
            -- 计算净薪资
            emp_batch(v_current_batch).net_pay := 
                emp_batch(v_current_batch).total_pay - 
                emp_batch(v_current_batch).tax_amount;
            
            p_total_amount := p_total_amount + emp_batch(v_current_batch).net_pay;
            
            -- 批量处理
            IF v_current_batch >= v_batch_size THEN
                -- 插入到临时表
                FORALL i IN 1..emp_batch.COUNT
                    INSERT INTO temp_payroll_20240101 VALUES (
                        emp_batch(i).employee_id,
                        emp_batch(i).full_name,
                        emp_batch(i).base_salary,
                        emp_batch(i).bonus_amount,
                        emp_batch(i).total_pay,
                        emp_batch(i).tax_amount,
                        emp_batch(i).net_pay,
                        SYSDATE
                    );
                
                p_processed_count := p_processed_count + emp_batch.COUNT;
                emp_batch.DELETE;
                v_current_batch := 0;
                
                COMMIT;
            END IF;
            
        EXCEPTION
            WHEN OTHERS THEN
                p_error_count := p_error_count + 1;
                v_error_msg := 'Employee ID: ' || emp_rec.employee_id || 
                              ' Error: ' || SQLERRM;
                
                INSERT INTO payroll_error_log (
                    employee_id, error_message, process_date
                ) VALUES (
                    emp_rec.employee_id, v_error_msg, SYSDATE
                );
        END;
    END LOOP;
    
    -- 处理剩余批次
    IF emp_batch.COUNT > 0 THEN
        FORALL i IN 1..emp_batch.COUNT
            INSERT INTO temp_payroll_20240101 VALUES (
                emp_batch(i).employee_id,
                emp_batch(i).full_name,
                emp_batch(i).base_salary,
                emp_batch(i).bonus_amount,
                emp_batch(i).total_pay,
                emp_batch(i).tax_amount,
                emp_batch(i).net_pay,
                SYSDATE
            );
        
        p_processed_count := p_processed_count + emp_batch.COUNT;
    END IF;
    
    -- 生成汇总报告
    INSERT INTO payroll_summary (
        pay_period_start, pay_period_end, department_filter,
        processed_count, error_count, total_amount, process_date
    ) VALUES (
        p_pay_period_start, p_pay_period_end, p_department_filter,
        p_processed_count, p_error_count, p_total_amount, SYSDATE
    );
    
    COMMIT;
    
EXCEPTION
    WHEN e_invalid_date THEN
        ROLLBACK;
        RAISE_APPLICATION_ERROR(-20001, 'Invalid date range');
    
    WHEN e_processing_error THEN
        ROLLBACK;
        RAISE_APPLICATION_ERROR(-20002, 'Processing error occurred');
    
    WHEN OTHERS THEN
        ROLLBACK;
        v_error_msg := 'Unexpected error: ' || SQLERRM;
        INSERT INTO system_error_log (error_message, error_date)
        VALUES (v_error_msg, SYSDATE);
        COMMIT;
        RAISE;
END;
"""

# 包含多种SQL操作类型的存储过程
MULTI_OPERATION_PROCEDURE = """
CREATE OR REPLACE PROCEDURE comprehensive_data_operations(
    p_operation_mode IN VARCHAR2,
    p_reference_date IN DATE,
    p_result_status OUT VARCHAR2
) AS
    v_record_count NUMBER;
    v_operation_id NUMBER;
BEGIN
    -- 生成操作ID
    SELECT operation_seq.NEXTVAL INTO v_operation_id FROM dual;
    
    -- 记录操作开始
    INSERT INTO operation_log (operation_id, operation_type, start_time, status)
    VALUES (v_operation_id, p_operation_mode, SYSDATE, 'STARTED');
    
    -- 根据操作模式执行不同的数据操作
    IF p_operation_mode = 'REFRESH' THEN
        -- 删除旧数据
        DELETE FROM staging_data WHERE created_date < p_reference_date - 30;
        
        -- 插入新数据
        INSERT INTO staging_data (id, name, value, created_date)
        SELECT employee_id, first_name || ' ' || last_name, salary, SYSDATE
        FROM employees
        WHERE hire_date >= p_reference_date;
        
        -- 更新统计信息
        UPDATE data_statistics 
        SET last_refresh = SYSDATE, 
            record_count = (SELECT COUNT(*) FROM staging_data)
        WHERE table_name = 'STAGING_DATA';
        
    ELSIF p_operation_mode = 'ARCHIVE' THEN
        -- 创建归档表
        CREATE TABLE archive_data_backup AS
        SELECT * FROM archive_data WHERE 1=0;
        
        -- 移动数据到归档
        INSERT INTO archive_data_backup
        SELECT * FROM staging_data 
        WHERE created_date < p_reference_date - 365;
        
        -- 删除已归档的数据
        DELETE FROM staging_data 
        WHERE created_date < p_reference_date - 365;
        
        -- 更新归档统计
        MERGE INTO archive_statistics a
        USING (
            SELECT COUNT(*) as archived_count, SYSDATE as archive_date
            FROM archive_data_backup
        ) b ON (a.archive_date = TRUNC(b.archive_date))
        WHEN MATCHED THEN
            UPDATE SET record_count = record_count + b.archived_count
        WHEN NOT MATCHED THEN
            INSERT (archive_date, record_count) 
            VALUES (TRUNC(b.archive_date), b.archived_count);
            
    ELSIF p_operation_mode = 'ANALYZE' THEN
        -- 复杂分析查询
        INSERT INTO analysis_results (operation_id, analysis_type, result_value, created_date)
        SELECT v_operation_id, 'EMPLOYEE_COUNT', COUNT(*), SYSDATE
        FROM employees;
        
        INSERT INTO analysis_results (operation_id, analysis_type, result_value, created_date)
        SELECT v_operation_id, 'AVG_SALARY', AVG(salary), SYSDATE
        FROM employees;
        
        INSERT INTO analysis_results (operation_id, analysis_type, result_value, created_date)
        SELECT v_operation_id, 'DEPT_DISTRIBUTION', COUNT(*), SYSDATE
        FROM (
            SELECT department_id, COUNT(*) as emp_count
            FROM employees
            GROUP BY department_id
            HAVING COUNT(*) > 5
        );
        
        -- 创建分析视图
        EXECUTE IMMEDIATE 'CREATE OR REPLACE VIEW analysis_summary AS
            SELECT department_id, COUNT(*) as employee_count, 
                   AVG(salary) as avg_salary, SUM(salary) as total_salary
            FROM employees 
            GROUP BY department_id';
    END IF;
    
    -- 获取处理记录数
    SELECT COUNT(*) INTO v_record_count FROM staging_data;
    
    -- 更新操作日志
    UPDATE operation_log 
    SET end_time = SYSDATE, 
        status = 'COMPLETED',
        records_processed = v_record_count
    WHERE operation_id = v_operation_id;
    
    p_result_status := 'SUCCESS';
    
    COMMIT;
    
EXCEPTION
    WHEN OTHERS THEN
        ROLLBACK;
        
        UPDATE operation_log 
        SET end_time = SYSDATE, 
            status = 'FAILED',
            error_message = SQLERRM
        WHERE operation_id = v_operation_id;
        
        p_result_status := 'FAILED: ' || SQLERRM;
        COMMIT;
END;
"""

# 包含递归和层次查询的存储过程
HIERARCHICAL_PROCEDURE = """
CREATE OR REPLACE PROCEDURE process_employee_hierarchy(
    p_manager_id IN NUMBER,
    p_max_level IN NUMBER DEFAULT 5,
    p_total_subordinates OUT NUMBER
) AS
    TYPE emp_hierarchy_type IS RECORD (
        employee_id NUMBER,
        manager_id NUMBER,
        level_num NUMBER,
        path VARCHAR2(4000)
    );
    
    TYPE hierarchy_table_type IS TABLE OF emp_hierarchy_type;
    v_hierarchy hierarchy_table_type;
    
    v_current_level NUMBER := 1;
    v_sql VARCHAR2(4000);
BEGIN
    -- 创建临时层次结构表
    CREATE GLOBAL TEMPORARY TABLE temp_hierarchy (
        employee_id NUMBER,
        manager_id NUMBER,
        level_num NUMBER,
        employee_path VARCHAR2(4000),
        total_salary NUMBER
    );
    
    -- 使用层次查询填充数据
    INSERT INTO temp_hierarchy
    SELECT employee_id, manager_id, LEVEL, 
           SYS_CONNECT_BY_PATH(first_name || ' ' || last_name, '/') as path,
           salary
    FROM employees
    START WITH manager_id = p_manager_id OR (p_manager_id IS NULL AND manager_id IS NULL)
    CONNECT BY PRIOR employee_id = manager_id
    AND LEVEL <= p_max_level;
    
    -- 计算每个级别的统计信息
    FOR i IN 1..p_max_level LOOP
        INSERT INTO hierarchy_statistics (
            manager_id, level_num, employee_count, 
            total_salary, avg_salary, process_date
        )
        SELECT p_manager_id, i, COUNT(*), SUM(total_salary), AVG(total_salary), SYSDATE
        FROM temp_hierarchy
        WHERE level_num = i;
    END LOOP;
    
    -- 计算总下属数量
    SELECT COUNT(*) INTO p_total_subordinates
    FROM temp_hierarchy
    WHERE level_num > 1;
    
    -- 创建层次结构报告
    INSERT INTO hierarchy_report (
        manager_id, report_date, max_level, total_subordinates,
        direct_reports, total_salary_managed
    )
    SELECT p_manager_id, SYSDATE, p_max_level, p_total_subordinates,
           (SELECT COUNT(*) FROM temp_hierarchy WHERE level_num = 2),
           (SELECT SUM(total_salary) FROM temp_hierarchy)
    FROM dual;
    
    COMMIT;
    
EXCEPTION
    WHEN OTHERS THEN
        ROLLBACK;
        RAISE;
END;
"""

# 所有示例存储过程的字典
SAMPLE_PROCEDURES = {
    'simple': SIMPLE_PROCEDURE,
    'medium': MEDIUM_PROCEDURE,
    'complex': COMPLEX_PROCEDURE,
    'multi_operation': MULTI_OPERATION_PROCEDURE,
    'hierarchical': HIERARCHICAL_PROCEDURE
}

def get_procedure(procedure_type: str) -> str:
    """获取指定类型的示例存储过程"""
    return SAMPLE_PROCEDURES.get(procedure_type, SIMPLE_PROCEDURE)

def get_all_procedures() -> dict:
    """获取所有示例存储过程"""
    return SAMPLE_PROCEDURES.copy()

def get_procedure_types() -> list:
    """获取所有可用的存储过程类型"""
    return list(SAMPLE_PROCEDURES.keys()) 
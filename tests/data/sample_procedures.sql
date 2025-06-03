-- Oracle存储过程测试样例
-- 用于测试各种解析和分析功能

-- ============================================
-- 示例1: 简单的更新操作
-- ============================================
CREATE OR REPLACE PROCEDURE update_employee_salary(
    p_emp_id IN NUMBER,
    p_new_salary IN NUMBER
) AS
BEGIN
    UPDATE employees 
    SET salary = p_new_salary,
        last_update_date = SYSDATE
    WHERE employee_id = p_emp_id;
    
    -- 记录薪资变更历史
    INSERT INTO salary_history (
        employee_id,
        old_salary,
        new_salary,
        change_date
    ) 
    SELECT 
        p_emp_id,
        e.salary,
        p_new_salary,
        SYSDATE
    FROM employees e 
    WHERE e.employee_id = p_emp_id;
    
    COMMIT;
END update_employee_salary;
/

-- ============================================
-- 示例2: 复杂的数据处理过程
-- ============================================
CREATE OR REPLACE PROCEDURE process_department_data(
    p_dept_id IN NUMBER,
    p_start_date IN DATE,
    p_end_date IN DATE,
    p_process_type IN VARCHAR2 DEFAULT 'FULL'
) AS
    v_total_employees NUMBER;
    v_avg_salary NUMBER;
    v_error_msg VARCHAR2(4000);
BEGIN
    -- 创建临时表存储处理结果
    EXECUTE IMMEDIATE 'CREATE GLOBAL TEMPORARY TABLE temp_dept_summary (
        employee_id NUMBER,
        employee_name VARCHAR2(100),
        department_name VARCHAR2(50),
        salary NUMBER,
        hire_date DATE,
        years_of_service NUMBER
    ) ON COMMIT PRESERVE ROWS';
    
    -- 填充临时表
    INSERT INTO temp_dept_summary (
        employee_id,
        employee_name,
        department_name,
        salary,
        hire_date,
        years_of_service
    )
    SELECT 
        e.employee_id,
        e.first_name || ' ' || e.last_name as employee_name,
        d.department_name,
        e.salary,
        e.hire_date,
        ROUND(MONTHS_BETWEEN(SYSDATE, e.hire_date) / 12, 1) as years_of_service
    FROM employees e
    INNER JOIN departments d ON e.department_id = d.department_id
    LEFT JOIN job_history jh ON e.employee_id = jh.employee_id
    WHERE e.department_id = p_dept_id
      AND e.hire_date BETWEEN p_start_date AND p_end_date
      AND (p_process_type = 'FULL' OR e.salary > 5000);
    
    -- 计算统计信息
    SELECT COUNT(*), AVG(salary)
    INTO v_total_employees, v_avg_salary
    FROM temp_dept_summary;
    
    -- 更新部门统计表
    MERGE INTO department_statistics ds
    USING (
        SELECT 
            p_dept_id as dept_id,
            v_total_employees as emp_count,
            v_avg_salary as avg_salary,
            SYSDATE as last_update
        FROM dual
    ) src ON (ds.department_id = src.dept_id)
    WHEN MATCHED THEN
        UPDATE SET 
            employee_count = src.emp_count,
            average_salary = src.avg_salary,
            last_updated = src.last_update
    WHEN NOT MATCHED THEN
        INSERT (department_id, employee_count, average_salary, last_updated)
        VALUES (src.dept_id, src.emp_count, src.avg_salary, src.last_update);
    
    -- 生成详细报告
    INSERT INTO department_reports (
        report_id,
        department_id,
        report_date,
        total_employees,
        average_salary,
        report_type,
        report_data
    )
    SELECT 
        dept_report_seq.NEXTVAL,
        p_dept_id,
        SYSDATE,
        v_total_employees,
        v_avg_salary,
        p_process_type,
        CURSOR(
            SELECT employee_id, employee_name, salary, years_of_service
            FROM temp_dept_summary
            ORDER BY salary DESC
        )
    FROM dual;
    
    -- 清理临时表
    EXECUTE IMMEDIATE 'DROP TABLE temp_dept_summary';
    
    COMMIT;
    
EXCEPTION
    WHEN OTHERS THEN
        v_error_msg := SQLERRM;
        ROLLBACK;
        
        -- 记录错误日志
        INSERT INTO process_error_log (
            process_name,
            error_message,
            error_date,
            input_parameters
        ) VALUES (
            'process_department_data',
            v_error_msg,
            SYSDATE,
            'dept_id=' || p_dept_id || ', start_date=' || 
            TO_CHAR(p_start_date, 'YYYY-MM-DD') || 
            ', end_date=' || TO_CHAR(p_end_date, 'YYYY-MM-DD')
        );
        
        RAISE_APPLICATION_ERROR(-20001, '部门数据处理失败: ' || v_error_msg);
END process_department_data;
/

-- ============================================
-- 示例3: 多表关联报表生成
-- ============================================
CREATE OR REPLACE PROCEDURE generate_annual_report(
    p_year IN NUMBER,
    p_include_terminated IN VARCHAR2 DEFAULT 'N'
) AS
    TYPE dept_cursor_type IS REF CURSOR;
    dept_cursor dept_cursor_type;
    
    v_dept_id departments.department_id%TYPE;
    v_dept_name departments.department_name%TYPE;
    v_manager_name VARCHAR2(100);
    v_location_name VARCHAR2(100);
BEGIN
    -- 删除旧的年度报告数据
    DELETE FROM annual_summary_reports 
    WHERE report_year = p_year;
    
    -- 生成主报告数据
    INSERT INTO annual_summary_reports (
        report_year,
        department_id,
        department_name,
        manager_name,
        location_name,
        total_employees,
        active_employees,
        terminated_employees,
        total_salary_cost,
        average_salary,
        min_salary,
        max_salary,
        total_bonuses,
        turnover_rate,
        creation_date
    )
    SELECT 
        p_year,
        d.department_id,
        d.department_name,
        mgr.first_name || ' ' || mgr.last_name as manager_name,
        l.city || ', ' || l.country_id as location_name,
        COUNT(DISTINCT e.employee_id) as total_employees,
        COUNT(DISTINCT CASE WHEN e.end_date IS NULL THEN e.employee_id END) as active_employees,
        COUNT(DISTINCT CASE WHEN e.end_date IS NOT NULL THEN e.employee_id END) as terminated_employees,
        NVL(SUM(e.salary * 12), 0) as total_salary_cost,
        NVL(AVG(e.salary), 0) as average_salary,
        NVL(MIN(e.salary), 0) as min_salary,
        NVL(MAX(e.salary), 0) as max_salary,
        NVL(SUM(e.commission_pct * e.salary), 0) as total_bonuses,
        CASE 
            WHEN COUNT(DISTINCT e.employee_id) > 0 THEN
                ROUND(COUNT(DISTINCT CASE WHEN e.end_date IS NOT NULL THEN e.employee_id END) * 100.0 / 
                      COUNT(DISTINCT e.employee_id), 2)
            ELSE 0
        END as turnover_rate,
        SYSDATE
    FROM departments d
    LEFT JOIN employees mgr ON d.manager_id = mgr.employee_id
    LEFT JOIN locations l ON d.location_id = l.location_id
    LEFT JOIN employees e ON d.department_id = e.department_id
    LEFT JOIN job_history jh ON e.employee_id = jh.employee_id
    WHERE (p_include_terminated = 'Y' OR e.end_date IS NULL)
      AND (EXTRACT(YEAR FROM e.hire_date) <= p_year)
    GROUP BY 
        d.department_id,
        d.department_name,
        mgr.first_name || ' ' || mgr.last_name,
        l.city || ', ' || l.country_id
    ORDER BY d.department_name;
    
    -- 生成职位级别汇总
    INSERT INTO job_level_summary (
        report_year,
        job_id,
        job_title,
        total_positions,
        avg_salary_by_job,
        min_salary_by_job,
        max_salary_by_job
    )
    SELECT 
        p_year,
        j.job_id,
        j.job_title,
        COUNT(e.employee_id) as total_positions,
        AVG(e.salary) as avg_salary_by_job,
        MIN(e.salary) as min_salary_by_job,
        MAX(e.salary) as max_salary_by_job
    FROM jobs j
    LEFT JOIN employees e ON j.job_id = e.job_id
    WHERE (p_include_terminated = 'Y' OR e.end_date IS NULL)
      AND (EXTRACT(YEAR FROM e.hire_date) <= p_year)
    GROUP BY j.job_id, j.job_title
    HAVING COUNT(e.employee_id) > 0
    ORDER BY avg_salary_by_job DESC;
    
    -- 更新报告生成状态
    UPDATE report_generation_status 
    SET 
        last_run_date = SYSDATE,
        status = 'COMPLETED',
        records_processed = SQL%ROWCOUNT
    WHERE report_type = 'ANNUAL_SUMMARY'
      AND report_year = p_year;
    
    IF SQL%NOTFOUND THEN
        INSERT INTO report_generation_status (
            report_type,
            report_year,
            last_run_date,
            status,
            records_processed
        ) VALUES (
            'ANNUAL_SUMMARY',
            p_year,
            SYSDATE,
            'COMPLETED',
            SQL%ROWCOUNT
        );
    END IF;
    
    COMMIT;
    
END generate_annual_report;
/

-- ============================================
-- 示例4: 动态SQL和游标处理
-- ============================================
CREATE OR REPLACE PROCEDURE dynamic_data_analysis(
    p_table_name IN VARCHAR2,
    p_date_column IN VARCHAR2,
    p_analysis_date IN DATE,
    p_output_table IN VARCHAR2
) AS
    v_sql VARCHAR2(4000);
    v_count NUMBER;
    
    TYPE analysis_record IS RECORD (
        table_name VARCHAR2(128),
        column_name VARCHAR2(128),
        data_type VARCHAR2(128),
        null_count NUMBER,
        distinct_count NUMBER,
        min_value VARCHAR2(4000),
        max_value VARCHAR2(4000)
    );
    
    TYPE analysis_table IS TABLE OF analysis_record;
    v_analysis_results analysis_table := analysis_table();
    
    CURSOR column_cursor IS
        SELECT column_name, data_type
        FROM user_tab_columns
        WHERE table_name = UPPER(p_table_name)
        ORDER BY column_id;
BEGIN
    -- 验证输入表是否存在
    SELECT COUNT(*)
    INTO v_count
    FROM user_tables
    WHERE table_name = UPPER(p_table_name);
    
    IF v_count = 0 THEN
        RAISE_APPLICATION_ERROR(-20002, '表 ' || p_table_name || ' 不存在');
    END IF;
    
    -- 创建输出表（如果不存在）
    BEGIN
        v_sql := 'SELECT COUNT(*) FROM ' || p_output_table;
        EXECUTE IMMEDIATE v_sql INTO v_count;
    EXCEPTION
        WHEN OTHERS THEN
            v_sql := 'CREATE TABLE ' || p_output_table || ' (
                analysis_date DATE,
                table_name VARCHAR2(128),
                column_name VARCHAR2(128),
                data_type VARCHAR2(128),
                total_records NUMBER,
                null_count NUMBER,
                distinct_count NUMBER,
                min_value VARCHAR2(4000),
                max_value VARCHAR2(4000)
            )';
            EXECUTE IMMEDIATE v_sql;
    END;
    
    -- 分析每个列
    FOR col_rec IN column_cursor LOOP
        DECLARE
            v_null_count NUMBER;
            v_distinct_count NUMBER;
            v_min_value VARCHAR2(4000);
            v_max_value VARCHAR2(4000);
            v_total_records NUMBER;
        BEGIN
            -- 计算总记录数
            v_sql := 'SELECT COUNT(*) FROM ' || p_table_name || 
                     ' WHERE ' || p_date_column || ' <= :1';
            EXECUTE IMMEDIATE v_sql INTO v_total_records USING p_analysis_date;
            
            -- 计算空值数量
            v_sql := 'SELECT COUNT(*) FROM ' || p_table_name || 
                     ' WHERE ' || col_rec.column_name || ' IS NULL' ||
                     ' AND ' || p_date_column || ' <= :1';
            EXECUTE IMMEDIATE v_sql INTO v_null_count USING p_analysis_date;
            
            -- 计算不同值数量
            v_sql := 'SELECT COUNT(DISTINCT ' || col_rec.column_name || ') FROM ' || p_table_name ||
                     ' WHERE ' || col_rec.column_name || ' IS NOT NULL' ||
                     ' AND ' || p_date_column || ' <= :1';
            EXECUTE IMMEDIATE v_sql INTO v_distinct_count USING p_analysis_date;
            
            -- 获取最小值和最大值（转换为字符串）
            IF col_rec.data_type IN ('NUMBER', 'DATE', 'VARCHAR2', 'CHAR') THEN
                v_sql := 'SELECT TO_CHAR(MIN(' || col_rec.column_name || ')), ' ||
                         'TO_CHAR(MAX(' || col_rec.column_name || ')) FROM ' || p_table_name ||
                         ' WHERE ' || col_rec.column_name || ' IS NOT NULL' ||
                         ' AND ' || p_date_column || ' <= :1';
                EXECUTE IMMEDIATE v_sql INTO v_min_value, v_max_value USING p_analysis_date;
            END IF;
            
            -- 插入分析结果
            INSERT INTO dept_analysis_results VALUES (
                p_analysis_date,
                p_table_name,
                col_rec.column_name,
                col_rec.data_type,
                v_total_records,
                v_null_count,
                v_distinct_count,
                v_min_value,
                v_max_value
            );
            
        EXCEPTION
            WHEN OTHERS THEN
                -- 记录分析失败的列
                INSERT INTO analysis_error_log (
                    table_name,
                    column_name,
                    error_message,
                    analysis_date
                ) VALUES (
                    p_table_name,
                    col_rec.column_name,
                    SQLERRM,
                    SYSDATE
                );
        END;
    END LOOP;
    
    COMMIT;
    
END dynamic_data_analysis;
/ 
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
pytest配置和公共fixtures
"""

import sys
import os
import pytest
import pytest_asyncio
import asyncio
from pathlib import Path
from typing import Generator, Dict, Any
from unittest.mock import Mock, AsyncMock
import importlib.util
from httpx import AsyncClient, ASGITransport

# 设置项目路径
PROJECT_ROOT = Path(__file__).parent.parent
CORE_PATH = PROJECT_ROOT / "core"
BACKEND_PATH = PROJECT_ROOT / "backend"

# 添加路径到sys.path
sys.path.insert(0, str(CORE_PATH))
sys.path.insert(0, str(BACKEND_PATH))

# 导入项目模块
def load_module_from_path(module_name: str, file_path: Path):
    """动态加载模块"""
    spec = importlib.util.spec_from_file_location(module_name, file_path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module

# 配置asyncio事件循环
@pytest.fixture(scope="session")
def event_loop():
    """创建一个事件循环用于整个测试会话"""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()

@pytest.fixture(scope="session")
def core_main_module():
    """加载core/main.py模块"""
    return load_module_from_path("core_main", CORE_PATH / "main.py")

@pytest.fixture(scope="session")
def backend_main_module():
    """加载backend/main.py模块"""
    return load_module_from_path("backend_main", BACKEND_PATH / "main.py")

@pytest.fixture(scope="session")
def oracle_sp_analyzer(core_main_module):
    """创建OracleSPAnalyzer实例"""
    return core_main_module.OracleSPAnalyzer()

@pytest.fixture(scope="session")
def fastapi_app(backend_main_module):
    """获取FastAPI应用实例"""
    return backend_main_module.app

@pytest.fixture
def sample_stored_procedure() -> str:
    """示例存储过程"""
    return """
    CREATE OR REPLACE PROCEDURE process_employee_data(
        p_dept_id IN NUMBER,
        p_start_date IN DATE,
        p_salary_increase OUT NUMBER
    ) AS
        v_count NUMBER;
        v_avg_salary NUMBER;
    BEGIN
        -- 创建临时表
        CREATE GLOBAL TEMPORARY TABLE temp_emp_summary (
            emp_id NUMBER,
            emp_name VARCHAR2(100),
            dept_name VARCHAR2(100),
            salary NUMBER,
            hire_date DATE
        );
        
        -- 插入数据到临时表
        INSERT INTO temp_emp_summary
        SELECT e.employee_id, 
               e.first_name || ' ' || e.last_name as full_name, 
               d.department_name, 
               e.salary,
               e.hire_date
        FROM employees e
        INNER JOIN departments d ON e.department_id = d.department_id
        LEFT JOIN locations l ON d.location_id = l.location_id
        WHERE e.department_id = p_dept_id
        AND e.hire_date >= p_start_date
        AND e.salary > 30000;
        
        -- 计算员工数量
        SELECT COUNT(*), AVG(salary)
        INTO v_count, v_avg_salary
        FROM temp_emp_summary;
        
        -- 更新员工薪资
        UPDATE employees 
        SET salary = salary * 1.1,
            last_modified = SYSDATE
        WHERE department_id = p_dept_id
        AND employee_id IN (SELECT emp_id FROM temp_emp_summary);
        
        -- 删除低薪员工记录
        DELETE FROM employees 
        WHERE department_id = p_dept_id 
        AND salary < 25000;
        
        -- 生成报告
        INSERT INTO employee_reports (
            report_id, report_date, dept_id, emp_count, avg_salary, created_by
        )
        SELECT report_seq.NEXTVAL, SYSDATE, p_dept_id, v_count, v_avg_salary, USER
        FROM dual;
        
        -- 合并操作
        MERGE INTO salary_history sh
        USING (
            SELECT emp_id, salary 
            FROM temp_emp_summary
        ) t ON (sh.emp_id = t.emp_id AND sh.change_date = SYSDATE)
        WHEN MATCHED THEN
            UPDATE SET old_salary = t.salary
        WHEN NOT MATCHED THEN
            INSERT (emp_id, old_salary, change_date) 
            VALUES (t.emp_id, t.salary, SYSDATE);
        
        p_salary_increase := v_avg_salary * 0.1;
        
        COMMIT;
        
    EXCEPTION
        WHEN OTHERS THEN
            ROLLBACK;
            RAISE;
    END;
    """

@pytest.fixture
def complex_stored_procedure() -> str:
    """复杂存储过程示例"""
    return """
    CREATE OR REPLACE PROCEDURE complex_data_processing(
        p_region_id IN NUMBER,
        p_year IN NUMBER,
        p_process_mode IN VARCHAR2 DEFAULT 'NORMAL',
        p_result_count OUT NUMBER,
        p_error_message OUT VARCHAR2
    ) AS
    
        TYPE emp_rec_type IS RECORD (
            emp_id NUMBER,
            emp_name VARCHAR2(200),
            salary NUMBER
        );
        
        TYPE emp_table_type IS TABLE OF emp_rec_type INDEX BY PLS_INTEGER;
        v_emp_table emp_table_type;
        
        v_batch_size CONSTANT NUMBER := 1000;
        v_total_processed NUMBER := 0;
        v_error_count NUMBER := 0;
        
        CURSOR c_departments IS
            SELECT d.department_id, d.department_name, l.city, l.country_id
            FROM departments d
            JOIN locations l ON d.location_id = l.location_id
            JOIN countries c ON l.country_id = c.country_id
            JOIN regions r ON c.region_id = r.region_id
            WHERE r.region_id = p_region_id;
            
    BEGIN
        p_result_count := 0;
        p_error_message := NULL;
        
        -- 动态表创建
        EXECUTE IMMEDIATE 'CREATE GLOBAL TEMPORARY TABLE temp_processing_' || p_year || ' (
            process_id NUMBER,
            emp_id NUMBER,
            dept_id NUMBER,
            original_salary NUMBER,
            adjusted_salary NUMBER,
            adjustment_factor NUMBER,
            process_date DATE,
            status VARCHAR2(20)
        )';
        
        -- 循环处理各部门
        FOR dept_rec IN c_departments LOOP
            BEGIN
                -- 收集员工数据
                SELECT emp.employee_id, 
                       emp.first_name || ' ' || emp.last_name,
                       emp.salary
                BULK COLLECT INTO v_emp_table
                FROM employees emp
                WHERE emp.department_id = dept_rec.department_id
                AND EXTRACT(YEAR FROM emp.hire_date) <= p_year
                AND emp.salary IS NOT NULL;
                
                -- 批量处理
                FOR i IN 1..v_emp_table.COUNT LOOP
                    DECLARE
                        v_adjustment_factor NUMBER;
                        v_new_salary NUMBER;
                    BEGIN
                        -- 根据模式计算调整系数
                        CASE p_process_mode
                            WHEN 'AGGRESSIVE' THEN
                                v_adjustment_factor := 1.15;
                            WHEN 'CONSERVATIVE' THEN
                                v_adjustment_factor := 1.05;
                            ELSE
                                v_adjustment_factor := 1.10;
                        END CASE;
                        
                        v_new_salary := v_emp_table(i).salary * v_adjustment_factor;
                        
                        -- 插入处理记录
                        INSERT INTO temp_processing_${p_year} VALUES (
                            processing_seq.NEXTVAL,
                            v_emp_table(i).emp_id,
                            dept_rec.department_id,
                            v_emp_table(i).salary,
                            v_new_salary,
                            v_adjustment_factor,
                            SYSDATE,
                            'PROCESSED'
                        );
                        
                        v_total_processed := v_total_processed + 1;
                        
                        -- 分批提交
                        IF MOD(v_total_processed, v_batch_size) = 0 THEN
                            COMMIT;
                        END IF;
                        
                    EXCEPTION
                        WHEN OTHERS THEN
                            v_error_count := v_error_count + 1;
                            INSERT INTO error_log (error_date, error_message, context)
                            VALUES (SYSDATE, SQLERRM, 'Processing emp_id: ' || v_emp_table(i).emp_id);
                    END;
                END LOOP;
                
            EXCEPTION
                WHEN OTHERS THEN
                    p_error_message := 'Error processing department ' || dept_rec.department_id || ': ' || SQLERRM;
                    ROLLBACK;
                    RETURN;
            END;
        END LOOP;
        
        -- 最终统计和更新
        UPDATE employee_statistics 
        SET total_processed = v_total_processed,
            last_update = SYSDATE,
            process_year = p_year
        WHERE region_id = p_region_id;
        
        IF SQL%NOTFOUND THEN
            INSERT INTO employee_statistics (
                region_id, total_processed, last_update, process_year
            ) VALUES (
                p_region_id, v_total_processed, SYSDATE, p_year
            );
        END IF;
        
        p_result_count := v_total_processed;
        
        COMMIT;
        
    EXCEPTION
        WHEN OTHERS THEN
            ROLLBACK;
            p_error_message := 'Fatal error: ' || SQLERRM;
            p_result_count := -1;
    END;
    """

@pytest.fixture
def mock_database_tables() -> Dict[str, Dict[str, Any]]:
    """模拟数据库表结构"""
    return {
        "employees": {
            "fields": ["employee_id", "first_name", "last_name", "email", "salary", "hire_date", "department_id", "manager_id", "last_modified"],
            "primary_key": "employee_id",
            "foreign_keys": {"department_id": "departments.department_id", "manager_id": "employees.employee_id"}
        },
        "departments": {
            "fields": ["department_id", "department_name", "manager_id", "location_id"],
            "primary_key": "department_id",
            "foreign_keys": {"location_id": "locations.location_id", "manager_id": "employees.employee_id"}
        },
        "locations": {
            "fields": ["location_id", "street_address", "postal_code", "city", "state_province", "country_id"],
            "primary_key": "location_id",
            "foreign_keys": {"country_id": "countries.country_id"}
        },
        "countries": {
            "fields": ["country_id", "country_name", "region_id"],
            "primary_key": "country_id",
            "foreign_keys": {"region_id": "regions.region_id"}
        },
        "regions": {
            "fields": ["region_id", "region_name"],
            "primary_key": "region_id",
            "foreign_keys": {}
        },
        "employee_reports": {
            "fields": ["report_id", "report_date", "dept_id", "emp_count", "avg_salary", "created_by"],
            "primary_key": "report_id",
            "foreign_keys": {"dept_id": "departments.department_id"}
        },
        "salary_history": {
            "fields": ["history_id", "emp_id", "old_salary", "new_salary", "change_date", "change_reason"],
            "primary_key": "history_id",
            "foreign_keys": {"emp_id": "employees.employee_id"}
        },
        "employee_statistics": {
            "fields": ["stat_id", "region_id", "total_processed", "last_update", "process_year"],
            "primary_key": "stat_id",
            "foreign_keys": {"region_id": "regions.region_id"}
        },
        "error_log": {
            "fields": ["log_id", "error_date", "error_message", "context", "severity"],
            "primary_key": "log_id",
            "foreign_keys": {}
        }
    }

@pytest.fixture
def test_data_generator():
    """测试数据生成器"""
    from faker import Faker
    fake = Faker('zh_CN')
    
    class TestDataGenerator:
        def __init__(self):
            self.fake = fake
            
        def generate_employee_data(self, count: int = 10):
            """生成员工测试数据"""
            return [
                {
                    "employee_id": i + 1,
                    "first_name": self.fake.first_name(),
                    "last_name": self.fake.last_name(),
                    "email": self.fake.email(),
                    "salary": self.fake.random_int(min=30000, max=120000),
                    "hire_date": self.fake.date_between(start_date='-10y', end_date='today'),
                    "department_id": self.fake.random_int(min=1, max=5)
                }
                for i in range(count)
            ]
            
        def generate_stored_procedure(self, complexity: str = 'simple'):
            """生成不同复杂度的存储过程"""
            if complexity == 'simple':
                return f"""
                CREATE OR REPLACE PROCEDURE simple_proc(p_id IN NUMBER) AS
                BEGIN
                    UPDATE employees SET salary = salary * 1.1 WHERE employee_id = p_id;
                    COMMIT;
                END;
                """
            elif complexity == 'medium':
                return f"""
                CREATE OR REPLACE PROCEDURE medium_proc(p_dept_id IN NUMBER) AS
                    v_count NUMBER;
                BEGIN
                    SELECT COUNT(*) INTO v_count FROM employees WHERE department_id = p_dept_id;
                    
                    IF v_count > 0 THEN
                        UPDATE employees SET salary = salary * 1.1 WHERE department_id = p_dept_id;
                        INSERT INTO employee_reports (report_date, dept_id, emp_count) 
                        VALUES (SYSDATE, p_dept_id, v_count);
                    END IF;
                    
                    COMMIT;
                END;
                """
            else:  # complex
                return self.fake.text(max_nb_chars=2000)
    
    return TestDataGenerator()

# 测试标记
def pytest_configure(config):
    """配置pytest标记"""
    config.addinivalue_line("markers", "unit: 单元测试")
    config.addinivalue_line("markers", "integration: 集成测试")
    config.addinivalue_line("markers", "api: API测试")
    config.addinivalue_line("markers", "slow: 慢速测试")
    config.addinivalue_line("markers", "performance: 性能测试")
    config.addinivalue_line("markers", "smoke: 冒烟测试")

# 测试会话钩子
def pytest_sessionstart(session):
    """测试会话开始时的设置"""
    print("\n🚀 开始Oracle存储过程分析工具测试...")

def pytest_sessionfinish(session, exitstatus):
    """测试会话结束时的清理"""
    print(f"\n✅ 测试完成，退出码: {exitstatus}")

@pytest_asyncio.fixture
async def async_client(fastapi_app):
    """创建异步测试客户端"""
    async with AsyncClient(
        transport=ASGITransport(app=fastapi_app), 
        base_url="http://test"
    ) as client:
        yield client

@pytest.fixture
def async_transport():
    """创建一个ASGITransport实例"""
    return ASGITransport(base_url="http://localhost:8000") 
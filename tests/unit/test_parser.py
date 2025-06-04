#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
存储过程解析器单元测试
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
import sys
from pathlib import Path

# 添加src路径
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from parser.sp_parser import StoredProcedureParser
from models.data_models import SQLStatement, StatementType

@pytest.mark.unit
class TestStoredProcedureParser:
    """存储过程解析器测试类"""
    
    @pytest.fixture
    def parser(self):
        """创建解析器实例"""
        return StoredProcedureParser()
    
    def test_init(self, parser):
        """测试解析器初始化"""
        assert parser is not None
        assert hasattr(parser, 'parse')
    
    def test_parse_simple_procedure(self, parser):
        """测试解析简单存储过程"""
        simple_sp = """
        CREATE OR REPLACE PROCEDURE test_proc(p_id IN NUMBER) AS
        BEGIN
            UPDATE employees SET salary = salary * 1.1 WHERE employee_id = p_id;
            COMMIT;
        END;
        """
        
        result = parser.parse(simple_sp)
        
        # 验证基本结构
        assert result is not None
        assert result.name == "test_proc"
        assert len(result.parameters) == 1
        assert result.parameters[0].name == "p_id"
        assert result.parameters[0].direction == "IN"
        assert result.parameters[0].data_type == "NUMBER"
        
        # 验证SQL语句
        assert len(result.sql_statements) >= 1
        update_stmt = next((stmt for stmt in result.sql_statements 
                           if stmt.statement_type == StatementType.UPDATE), None)
        assert update_stmt is not None
        assert "employees" in update_stmt.target_tables
    
    def test_parse_complex_procedure(self, parser, complex_stored_procedure):
        """测试解析复杂存储过程"""
        result = parser.parse(complex_stored_procedure)
        
        # 验证存储过程名称
        assert result.name == "complex_data_processing"
        
        # 验证参数
        assert len(result.parameters) == 5
        param_names = [p.name for p in result.parameters]
        assert "p_region_id" in param_names
        assert "p_year" in param_names
        assert "p_process_mode" in param_names
        assert "p_result_count" in param_names
        assert "p_error_message" in param_names
        
        # 验证SQL语句类型
        stmt_types = [stmt.statement_type for stmt in result.sql_statements]
        assert StatementType.SELECT in stmt_types
        assert StatementType.INSERT in stmt_types
        assert StatementType.UPDATE in stmt_types
    
    def test_parse_procedure_with_temporary_tables(self, parser, sample_stored_procedure):
        """测试解析包含临时表的存储过程"""
        result = parser.parse(sample_stored_procedure)
        
        # 查找CREATE TABLE语句
        create_stmts = [stmt for stmt in result.sql_statements 
                       if stmt.statement_type == StatementType.CREATE_TABLE]
        assert len(create_stmts) >= 1
        
        # 验证临时表创建
        temp_table_stmt = create_stmts[0]
        assert "temp_emp_summary" in temp_table_stmt.target_tables
    
    def test_parse_invalid_sql(self, parser):
        """测试解析无效SQL"""
        invalid_sp = "INVALID SQL CONTENT"
        
        # 应该能处理无效SQL而不崩溃
        result = parser.parse(invalid_sp)
        # 根据具体实现调整断言
        assert result is not None
    
    def test_parse_empty_procedure(self, parser):
        """测试解析空存储过程"""
        empty_sp = ""
        
        result = parser.parse(empty_sp)
        assert result is not None
        assert len(result.sql_statements) == 0
    
    def test_extract_parameters(self, parser):
        """测试参数提取"""
        sp_with_params = """
        CREATE OR REPLACE PROCEDURE test_params(
            p_in_param IN NUMBER,
            p_out_param OUT VARCHAR2,
            p_inout_param IN OUT DATE
        ) AS
        BEGIN
            NULL;
        END;
        """
        
        result = parser.parse(sp_with_params)
        
        assert len(result.parameters) == 3
        
        # 验证IN参数
        in_param = next(p for p in result.parameters if p.name == "p_in_param")
        assert in_param.direction == "IN"
        assert in_param.data_type == "NUMBER"
        
        # 验证OUT参数
        out_param = next(p for p in result.parameters if p.name == "p_out_param")
        assert out_param.direction == "OUT"
        assert out_param.data_type == "VARCHAR2"
        
        # 验证IN OUT参数
        inout_param = next(p for p in result.parameters if p.name == "p_inout_param")
        assert inout_param.direction == "IN OUT"
        assert inout_param.data_type == "DATE"
    
    def test_identify_sql_statement_types(self, parser):
        """测试SQL语句类型识别"""
        mixed_sp = """
        CREATE OR REPLACE PROCEDURE mixed_operations AS
        BEGIN
            INSERT INTO test_table VALUES (1, 'test');
            UPDATE test_table SET name = 'updated' WHERE id = 1;
            DELETE FROM test_table WHERE id = 1;
            SELECT * FROM test_table;
            MERGE INTO target_table USING source_table ON (condition);
            CREATE TABLE temp_table (id NUMBER);
        END;
        """
        
        result = parser.parse(mixed_sp)
        
        stmt_types = [stmt.statement_type for stmt in result.sql_statements]
        
        assert StatementType.INSERT in stmt_types
        assert StatementType.UPDATE in stmt_types
        assert StatementType.DELETE in stmt_types
        assert StatementType.SELECT in stmt_types
        assert StatementType.MERGE in stmt_types
        assert StatementType.CREATE_TABLE in stmt_types
    
    def test_extract_table_names(self, parser):
        """测试表名提取"""
        sp_with_tables = """
        CREATE OR REPLACE PROCEDURE table_operations AS
        BEGIN
            INSERT INTO employees (id, name) VALUES (1, 'John');
            UPDATE departments SET name = 'IT' WHERE id = 1;
            SELECT e.name FROM employees e JOIN departments d ON e.dept_id = d.id;
            DELETE FROM temp_data WHERE status = 'expired';
        END;
        """
        
        result = parser.parse(sp_with_tables)
        
        # 收集所有涉及的表名
        all_tables = set()
        for stmt in result.sql_statements:
            all_tables.update(stmt.source_tables)
            all_tables.update(stmt.target_tables)
        
        assert "employees" in all_tables
        assert "departments" in all_tables
        assert "temp_data" in all_tables
    
    @pytest.mark.parametrize("sql_type,expected_type", [
        ("INSERT INTO test VALUES (1)", StatementType.INSERT),
        ("UPDATE test SET col = 1", StatementType.UPDATE),
        ("DELETE FROM test WHERE id = 1", StatementType.DELETE),
        ("SELECT * FROM test", StatementType.SELECT),
        ("CREATE TABLE test (id NUMBER)", StatementType.CREATE_TABLE),
        ("MERGE INTO test USING source", StatementType.MERGE),
    ])
    def test_statement_type_detection(self, parser, sql_type, expected_type):
        """测试语句类型检测"""
        # 这里需要根据实际的解析器实现来调整测试
        # 假设解析器有一个方法来识别语句类型
        pass  # 实际测试需要根据解析器的具体实现来编写
    
    def test_parse_procedure_with_cursors(self, parser):
        """测试解析包含游标的存储过程"""
        cursor_sp = """
        CREATE OR REPLACE PROCEDURE cursor_proc AS
            CURSOR emp_cursor IS
                SELECT employee_id, first_name FROM employees WHERE department_id = 10;
        BEGIN
            FOR emp_rec IN emp_cursor LOOP
                UPDATE employees SET salary = salary * 1.1 WHERE employee_id = emp_rec.employee_id;
            END LOOP;
        END;
        """
        
        result = parser.parse(cursor_sp)
        
        assert result is not None
        assert result.name == "cursor_proc"
        
        # 应该识别出游标中的SELECT语句
        select_stmts = [stmt for stmt in result.sql_statements 
                       if stmt.statement_type == StatementType.SELECT]
        assert len(select_stmts) >= 1
        
        # 应该识别出UPDATE语句
        update_stmts = [stmt for stmt in result.sql_statements 
                       if stmt.statement_type == StatementType.UPDATE]
        assert len(update_stmts) >= 1
    
    def test_parse_nested_procedures(self, parser):
        """测试解析嵌套调用的存储过程"""
        nested_sp = """
        CREATE OR REPLACE PROCEDURE main_proc AS
        BEGIN
            INSERT INTO log_table VALUES (SYSDATE, 'Starting process');
            
            -- 调用其他存储过程
            other_proc(p_param => 123);
            
            UPDATE status_table SET status = 'COMPLETED';
        END;
        """
        
        result = parser.parse(nested_sp)
        
        assert result is not None
        assert result.name == "main_proc"
        
        # 验证识别出的SQL语句
        stmt_types = [stmt.statement_type for stmt in result.sql_statements]
        assert StatementType.INSERT in stmt_types
        assert StatementType.UPDATE in stmt_types
    
    def test_error_handling(self, parser):
        """测试错误处理"""
        # 测试各种可能的错误情况
        test_cases = [
            None,  # None输入
            "",    # 空字符串
            "   ", # 只有空白字符
            "INVALID SYNTAX {{{}}}",  # 语法错误
        ]
        
        for test_case in test_cases:
            try:
                result = parser.parse(test_case)
                # 不应该抛出异常，应该返回有效结果或空结果
                assert result is not None
            except Exception as e:
                # 如果抛出异常，应该是预期的异常类型
                pytest.fail(f"解析器在处理 '{test_case}' 时抛出了意外异常: {e}")
    
    def test_performance_large_procedure(self, parser):
        """测试大型存储过程的解析性能"""
        # 生成一个较大的存储过程用于性能测试
        large_sp_parts = ["CREATE OR REPLACE PROCEDURE large_proc AS BEGIN"]
        
        # 添加多个SQL语句
        for i in range(100):
            large_sp_parts.append(f"INSERT INTO test_table_{i} VALUES ({i}, 'data_{i}');")
            large_sp_parts.append(f"UPDATE test_table_{i} SET status = 'processed' WHERE id = {i};")
        
        large_sp_parts.append("END;")
        large_sp = "\n".join(large_sp_parts)
        
        import time
        start_time = time.time()
        
        result = parser.parse(large_sp)
        
        end_time = time.time()
        parse_time = end_time - start_time
        
        # 解析时间应该在合理范围内（比如小于5秒）
        assert parse_time < 5.0, f"解析时间过长: {parse_time}秒"
        assert result is not None
        assert len(result.sql_statements) >= 100 
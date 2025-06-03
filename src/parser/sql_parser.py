#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sqlparse
from typing import List, Dict, Any
from models.data_models import SQLStatement, StatementType

class SQLParser:
    def __init__(self):
        self.parsed_statements = []

    def parse(self, sql_text: str) -> List[Dict[str, Any]]:
        """
        解析SQL文本，返回解析后的语句列表
        """
        statements = sqlparse.split(sql_text)
        parsed_results = []
        
        for stmt in statements:
            parsed = sqlparse.parse(stmt)[0]
            statement_type = self._get_statement_type(parsed)
            
            parsed_results.append({
                'raw': stmt,
                'parsed': parsed,
                'type': statement_type,
                'tables': self._extract_tables(parsed),
                'columns': self._extract_columns(parsed),
                'conditions': self._extract_conditions(parsed)
            })
        
        self.parsed_statements = parsed_results
        return parsed_results

    def _get_statement_type(self, parsed) -> str:
        """
        获取SQL语句类型
        """
        if parsed.get_type() == 'SELECT':
            return 'SELECT'
        elif parsed.get_type() == 'INSERT':
            return 'INSERT'
        elif parsed.get_type() == 'UPDATE':
            return 'UPDATE'
        elif parsed.get_type() == 'DELETE':
            return 'DELETE'
        else:
            return 'OTHER'

    def _extract_tables(self, parsed) -> List[str]:
        """
        提取SQL语句中涉及的表
        """
        tables = []
        for token in parsed.tokens:
            if token.is_keyword and token.value.upper() in ['FROM', 'JOIN', 'INTO']:
                # 这里需要更复杂的逻辑来提取表名
                pass
        return tables

    def _extract_columns(self, parsed) -> List[str]:
        """
        提取SQL语句中涉及的列
        """
        columns = []
        # 实现列提取逻辑
        return columns

    def _extract_conditions(self, parsed) -> List[str]:
        """
        提取SQL语句中的条件
        """
        conditions = []
        # 实现条件提取逻辑
        return conditions

class SQLStatementParser:
    """SQL语句解析器（兼容测试）"""
    
    def __init__(self):
        self.statement_counter = 0
    
    def parse(self, sql_text: str) -> SQLStatement:
        """解析单个SQL语句"""
        self.statement_counter += 1
        
        # 简单的语句类型检测
        sql_upper = sql_text.upper().strip()
        
        if sql_upper.startswith('SELECT'):
            stmt_type = StatementType.SELECT
            source_tables = self._extract_table_names(sql_text)
            target_tables = []
        elif sql_upper.startswith('INSERT'):
            stmt_type = StatementType.INSERT
            source_tables = self._extract_source_tables_from_insert(sql_text)
            target_tables = self._extract_target_tables_from_insert(sql_text)
        elif sql_upper.startswith('UPDATE'):
            stmt_type = StatementType.UPDATE
            target_tables = self._extract_table_names(sql_text)
            source_tables = target_tables  # UPDATE既读又写
        elif sql_upper.startswith('DELETE'):
            stmt_type = StatementType.DELETE
            target_tables = self._extract_table_names(sql_text)
            source_tables = []
        elif 'CREATE' in sql_upper and 'TABLE' in sql_upper:
            stmt_type = StatementType.CREATE_TABLE
            target_tables = self._extract_created_table_name(sql_text)
            source_tables = self._extract_source_tables_from_create(sql_text)
        else:
            stmt_type = StatementType.OTHER
            source_tables = []
            target_tables = []
        
        return SQLStatement(
            statement_id=self.statement_counter,
            statement_type=stmt_type,
            raw_sql=sql_text,
            source_tables=source_tables,
            target_tables=target_tables,
            join_conditions=self._extract_join_conditions(sql_text),
            parameters_used=self._extract_parameters(sql_text)
        )
    
    def _extract_table_names(self, sql_text: str) -> List[str]:
        """提取表名"""
        # 简化的表名提取逻辑
        tables = []
        words = sql_text.replace(',', ' ').split()
        
        # 查找FROM后面的表名
        for i, word in enumerate(words):
            if word.upper() in ['FROM', 'JOIN', 'INTO', 'UPDATE']:
                if i + 1 < len(words):
                    table_name = words[i + 1].strip('()')
                    if table_name and not table_name.upper() in ['SELECT', 'WHERE', 'GROUP', 'ORDER']:
                        tables.append(table_name)
        
        return list(set(tables))  # 去重
    
    def _extract_source_tables_from_insert(self, sql_text: str) -> List[str]:
        """从INSERT语句中提取源表"""
        if 'SELECT' in sql_text.upper():
            # INSERT ... SELECT 情况
            select_part = sql_text[sql_text.upper().find('SELECT'):]
            return self._extract_table_names(select_part)
        return []
    
    def _extract_target_tables_from_insert(self, sql_text: str) -> List[str]:
        """从INSERT语句中提取目标表"""
        words = sql_text.split()
        for i, word in enumerate(words):
            if word.upper() == 'INTO' and i + 1 < len(words):
                return [words[i + 1].strip('()')]
        return []
    
    def _extract_created_table_name(self, sql_text: str) -> List[str]:
        """从CREATE TABLE语句中提取表名"""
        words = sql_text.split()
        for i, word in enumerate(words):
            if word.upper() == 'TABLE' and i + 1 < len(words):
                return [words[i + 1].strip('()')]
        return []
    
    def _extract_source_tables_from_create(self, sql_text: str) -> List[str]:
        """从CREATE TABLE AS SELECT语句中提取源表"""
        if 'AS SELECT' in sql_text.upper() or 'AS (SELECT' in sql_text.upper():
            select_part = sql_text[sql_text.upper().find('SELECT'):]
            return self._extract_table_names(select_part)
        return []
    
    def _extract_join_conditions(self, sql_text: str) -> List[str]:
        """提取JOIN条件"""
        # 简化的JOIN条件提取
        conditions = []
        if 'JOIN' in sql_text.upper() and 'ON' in sql_text.upper():
            # 这里应该有更复杂的逻辑来解析JOIN条件
            conditions.append("JOIN condition extracted")
        return conditions
    
    def _extract_parameters(self, sql_text: str) -> List[str]:
        """提取参数"""
        # 查找?占位符或:参数名
        parameters = []
        import re
        
        # 查找:参数名格式
        param_matches = re.findall(r':(\w+)', sql_text)
        parameters.extend(param_matches)
        
        # 查找?占位符（假设按顺序命名）
        question_marks = sql_text.count('?')
        for i in range(question_marks):
            parameters.append(f"param_{i+1}")
        
        return parameters 
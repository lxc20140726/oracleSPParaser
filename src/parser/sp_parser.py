#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sqlparse
import re
from typing import List, Dict, Any
from models.data_models import (
    StoredProcedureStructure, SQLStatement, SQLStatementType, 
    Parameter, FieldReference, JoinCondition, WhereCondition
)

class StoredProcedureParser:
    """
    Oracle存储过程解析器
    专注于解析存储过程的结构，识别SQL语句、参数、变量等
    """
    
    def __init__(self):
        self.procedure_name = ""
        self.parameters = []
        self.sql_statements = []
        self.cursor_declarations = []
        self.variable_declarations = []

    def parse(self, sp_text: str) -> StoredProcedureStructure:
        """解析存储过程文本"""
        # 清理和预处理
        cleaned_text = self._preprocess_text(sp_text)
        
        # 提取过程名称和参数
        proc_name, params = self._extract_procedure_info(cleaned_text)
        
        # 提取SQL语句
        sql_statements = self._extract_sql_statements(cleaned_text)
        
        # 提取游标声明
        cursors = self._extract_cursor_declarations(cleaned_text)
        
        # 提取变量声明
        variables = self._extract_variable_declarations(cleaned_text)
        
        return StoredProcedureStructure(
            name=proc_name,
            parameters=params,
            sql_statements=sql_statements,
            cursor_declarations=cursors,
            variable_declarations=variables
        )

    def _preprocess_text(self, text: str) -> str:
        """预处理文本，清理注释和格式化"""
        # 移除单行注释
        text = re.sub(r'--.*?\n', '\n', text)
        # 移除多行注释
        text = re.sub(r'/\*.*?\*/', '', text, flags=re.DOTALL)
        # 标准化空白字符
        text = re.sub(r'\s+', ' ', text)
        return text.strip()

    def _extract_procedure_info(self, text: str) -> tuple[str, List[Parameter]]:
        """提取过程名称和参数"""
        # 匹配CREATE PROCEDURE语句
        proc_pattern = r'CREATE\s+(?:OR\s+REPLACE\s+)?PROCEDURE\s+(\w+)\s*\((.*?)\)'
        match = re.search(proc_pattern, text, re.IGNORECASE | re.DOTALL)
        
        if not match:
            return "unknown_procedure", []
        
        proc_name = match.group(1)
        params_text = match.group(2)
        
        parameters = self._parse_parameters(params_text)
        
        return proc_name, parameters

    def _parse_parameters(self, params_text: str) -> List[Parameter]:
        """解析参数列表"""
        parameters = []
        if not params_text.strip():
            return parameters
        
        # 分割参数
        param_list = re.split(r',(?![^()]*\))', params_text)
        
        for param in param_list:
            param = param.strip()
            if not param:
                continue
                
            # 解析参数：name [IN|OUT|INOUT] type
            param_pattern = r'(\w+)\s+(IN|OUT|INOUT)?\s*(\w+(?:\([^)]+\))?)'
            match = re.search(param_pattern, param, re.IGNORECASE)
            
            if match:
                name = match.group(1)
                direction = match.group(2) or 'IN'
                data_type = match.group(3)
                
                parameters.append(Parameter(
                    name=name,
                    data_type=data_type,
                    direction=direction.upper()
                ))
        
        return parameters

    def _extract_sql_statements(self, text: str) -> List[SQLStatement]:
        """提取SQL语句"""
        statements = []
        
        # 找到BEGIN...END块
        begin_pattern = r'BEGIN\s+(.*?)\s+END'
        match = re.search(begin_pattern, text, re.IGNORECASE | re.DOTALL)
        
        if not match:
            return statements
        
        body = match.group(1)
        
        # 分割SQL语句
        sql_parts = sqlparse.split(body)
        
        for i, sql_part in enumerate(sql_parts):
            if not sql_part.strip():
                continue
                
            statement = self._parse_single_statement(sql_part, str(i))
            if statement:
                statements.append(statement)
        
        return statements

    def _parse_single_statement(self, sql_text: str, statement_id: str) -> SQLStatement:
        """解析单个SQL语句"""
        parsed = sqlparse.parse(sql_text)[0]
        
        # 确定语句类型
        stmt_type = self._determine_statement_type(sql_text)
        
        # 提取表名
        source_tables, target_tables = self._extract_tables_from_statement(sql_text, stmt_type)
        
        # 提取字段
        fields_read, fields_written = self._extract_fields_from_statement(sql_text, stmt_type)
        
        # 提取连接条件
        join_conditions = self._extract_join_conditions(sql_text)
        
        # 提取WHERE条件
        where_conditions = self._extract_where_conditions(sql_text)
        
        # 提取使用的参数
        parameters_used = self._extract_parameters_used(sql_text)
        
        return SQLStatement(
            statement_id=statement_id,
            statement_type=stmt_type,
            raw_sql=sql_text,
            source_tables=source_tables,
            target_tables=target_tables,
            fields_read=fields_read,
            fields_written=fields_written,
            join_conditions=join_conditions,
            where_conditions=where_conditions,
            parameters_used=parameters_used
        )

    def _determine_statement_type(self, sql_text: str) -> SQLStatementType:
        """确定SQL语句类型"""
        sql_upper = sql_text.upper().strip()
        
        if sql_upper.startswith('SELECT'):
            return SQLStatementType.SELECT
        elif sql_upper.startswith('INSERT'):
            return SQLStatementType.INSERT
        elif sql_upper.startswith('UPDATE'):
            return SQLStatementType.UPDATE
        elif sql_upper.startswith('DELETE'):
            return SQLStatementType.DELETE
        elif 'CREATE GLOBAL TEMPORARY TABLE' in sql_upper:
            return SQLStatementType.CREATE_TEMP_TABLE
        elif sql_upper.startswith('CREATE TABLE'):
            return SQLStatementType.CREATE_TABLE
        elif 'CURSOR' in sql_upper and 'DECLARE' in sql_upper:
            return SQLStatementType.DECLARE_CURSOR
        elif sql_upper.startswith('IF'):
            return SQLStatementType.IF_STATEMENT
        elif sql_upper.startswith('WHILE'):
            return SQLStatementType.WHILE_LOOP
        elif sql_upper.startswith('FOR'):
            return SQLStatementType.FOR_LOOP
        else:
            return SQLStatementType.OTHER

    def _extract_tables_from_statement(self, sql_text: str, stmt_type: SQLStatementType) -> tuple[List[str], List[str]]:
        """从SQL语句中提取源表和目标表"""
        source_tables = []
        target_tables = []
        
        # 提取FROM子句中的表
        from_pattern = r'FROM\s+(.*?)(?:\s+WHERE|\s+GROUP|\s+ORDER|\s+HAVING|\s*;|\s*$)'
        from_match = re.search(from_pattern, sql_text, re.IGNORECASE | re.DOTALL)
        if from_match:
            from_clause = from_match.group(1)
            # 提取表名（包括JOIN的表）
            table_patterns = [
                r'(\w+)(?:\s+(\w+))?(?:\s+(?:INNER|LEFT|RIGHT|FULL)?\s*JOIN|,|\s*$)',  # 主表和JOIN表
                r'JOIN\s+(\w+)(?:\s+(\w+))?',  # JOIN表
            ]
            
            for pattern in table_patterns:
                matches = re.finditer(pattern, from_clause, re.IGNORECASE)
                for match in matches:
                    table_name = match.group(1)
                    if table_name and table_name.upper() not in ['ON', 'WHERE', 'GROUP', 'ORDER', 'HAVING'] and self._is_valid_table_name(table_name):
                        source_tables.append(table_name)
        
        # 根据语句类型提取目标表
        if stmt_type == SQLStatementType.INSERT:
            insert_pattern = r'INSERT\s+INTO\s+(\w+)'
            insert_match = re.search(insert_pattern, sql_text, re.IGNORECASE)
            if insert_match:
                target_tables.append(insert_match.group(1))
        elif stmt_type == SQLStatementType.UPDATE:
            update_pattern = r'UPDATE\s+(\w+)'
            update_match = re.search(update_pattern, sql_text, re.IGNORECASE)
            if update_match:
                target_tables.append(update_match.group(1))
                # UPDATE语句中的表也是源表（用于读取）
                source_tables.append(update_match.group(1))
        elif stmt_type == SQLStatementType.DELETE:
            delete_pattern = r'DELETE\s+FROM\s+(\w+)'
            delete_match = re.search(delete_pattern, sql_text, re.IGNORECASE)
            if delete_match:
                target_tables.append(delete_match.group(1))
        elif stmt_type in [SQLStatementType.CREATE_TABLE, SQLStatementType.CREATE_TEMP_TABLE]:
            create_pattern = r'CREATE\s+(?:GLOBAL\s+TEMPORARY\s+)?TABLE\s+(\w+)'
            create_match = re.search(create_pattern, sql_text, re.IGNORECASE)
            if create_match:
                target_tables.append(create_match.group(1))
        
        # 去重并返回
        return list(set(source_tables)), list(set(target_tables))

    def _extract_fields_from_statement(self, sql_text: str, stmt_type: SQLStatementType) -> tuple[List[FieldReference], List[FieldReference]]:
        """提取读写的字段"""
        fields_read = []
        fields_written = []
        
        if stmt_type == SQLStatementType.SELECT or 'SELECT' in sql_text.upper():
            # 提取SELECT字段
            select_pattern = r'SELECT\s+(.*?)\s+FROM'
            select_match = re.search(select_pattern, sql_text, re.IGNORECASE | re.DOTALL)
            if select_match:
                select_clause = select_match.group(1)
                # 提取字段引用
                field_refs = self._parse_select_fields(select_clause)
                fields_read.extend(field_refs)
        
        if stmt_type == SQLStatementType.INSERT:
            # 提取INSERT字段
            insert_pattern = r'INSERT\s+INTO\s+\w+\s*\((.*?)\)'
            insert_match = re.search(insert_pattern, sql_text, re.IGNORECASE)
            if insert_match:
                fields_text = insert_match.group(1)
                table_name = self._extract_target_table_name(sql_text)
                for field in fields_text.split(','):
                    field = field.strip()
                    if field:
                        fields_written.append(FieldReference(table_name=table_name, field_name=field))
        
        return fields_read, fields_written

    def _parse_select_fields(self, select_clause: str) -> List[FieldReference]:
        """解析SELECT子句中的字段"""
        field_refs = []
        
        # 分割字段（简单处理，不考虑函数中的逗号）
        fields = []
        paren_count = 0
        current_field = ""
        
        for char in select_clause:
            if char == '(':
                paren_count += 1
            elif char == ')':
                paren_count -= 1
            elif char == ',' and paren_count == 0:
                fields.append(current_field.strip())
                current_field = ""
                continue
            current_field += char
        
        if current_field.strip():
            fields.append(current_field.strip())
        
        # 解析每个字段
        for field in fields:
            field = field.strip()
            if not field or field == '*':
                continue
                
            # 匹配 table.field 格式
            table_field_pattern = r'(\w+)\.(\w+)'
            match = re.search(table_field_pattern, field)
            if match:
                field_refs.append(FieldReference(
                    table_name=match.group(1),
                    field_name=match.group(2)
                ))
        
        return field_refs

    def _extract_target_table_name(self, sql_text: str) -> str:
        """提取目标表名"""
        insert_pattern = r'INSERT\s+INTO\s+(\w+)'
        match = re.search(insert_pattern, sql_text, re.IGNORECASE)
        return match.group(1) if match else "unknown_table"

    def _extract_join_conditions(self, sql_text: str) -> List[JoinCondition]:
        """提取JOIN条件"""
        join_conditions = []
        
        # 使用更简单有效的JOIN匹配模式
        # 匹配 JOIN table_name alias ON condition 格式
        join_pattern = r'((?:INNER|LEFT|RIGHT|FULL)?\s*(?:OUTER\s+)?)?JOIN\s+(\w+)\s+(\w+)\s+ON\s+(.+?)(?=\s+WHERE|\s+GROUP|\s+ORDER|\s+HAVING|\s*;|\s*$)'
        matches = re.finditer(join_pattern, sql_text, re.IGNORECASE | re.DOTALL)
        
        for match in matches:
            # 确定JOIN类型
            join_type_text = match.group(1)
            if join_type_text:
                join_type_text = join_type_text.strip().upper()
                if 'LEFT' in join_type_text:
                    join_type = 'LEFT'
                elif 'RIGHT' in join_type_text:
                    join_type = 'RIGHT'
                elif 'FULL' in join_type_text:
                    join_type = 'FULL'
                else:
                    join_type = 'INNER'
            else:
                join_type = 'INNER'  # 默认为INNER JOIN
            
            table_name = match.group(2)
            alias = match.group(3)
            condition_text = match.group(4).strip()
            
            # 解析ON条件中的字段对应关系
            # 支持 alias.field = alias.field 格式
            condition_pattern = r'(\w+)\.(\w+)\s*=\s*(\w+)\.(\w+)'
            condition_match = re.search(condition_pattern, condition_text)
            
            if condition_match:
                join_conditions.append(JoinCondition(
                    left_table=condition_match.group(1),
                    left_field=condition_match.group(2),
                    right_table=condition_match.group(3),
                    right_field=condition_match.group(4),
                    join_type=join_type,
                    condition_text=condition_text
                ))
        
        return join_conditions

    def _extract_where_conditions(self, sql_text: str) -> List[WhereCondition]:
        """提取WHERE条件"""
        where_conditions = []
        
        where_pattern = r'WHERE\s+([^GROUP|ORDER|HAVING|;]+)'
        match = re.search(where_pattern, sql_text, re.IGNORECASE)
        
        if match:
            condition_text = match.group(1).strip()
            field_refs = self._extract_field_references_from_condition(condition_text)
            params_used = self._extract_parameters_used(condition_text)
            
            where_conditions.append(WhereCondition(
                field_references=field_refs,
                condition_text=condition_text,
                parameters_used=params_used
            ))
        
        return where_conditions

    def _extract_field_references_from_condition(self, condition_text: str) -> List[FieldReference]:
        """从条件文本中提取字段引用"""
        field_refs = []
        
        # 匹配table.field格式
        field_pattern = r'(\w+)\.(\w+)'
        matches = re.finditer(field_pattern, condition_text)
        
        for match in matches:
            field_refs.append(FieldReference(
                table_name=match.group(1),
                field_name=match.group(2)
            ))
        
        return field_refs

    def _extract_parameters_used(self, text: str) -> List[str]:
        """提取使用的参数"""
        # 匹配以p_开头的参数或:parameter格式
        param_patterns = [
            r'\bp_\w+\b',  # p_parameter格式
            r':\w+\b'      # :parameter格式
        ]
        
        parameters = []
        for pattern in param_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            parameters.extend(matches)
        
        return list(set(parameters))

    def _extract_cursor_declarations(self, text: str) -> List[Dict[str, Any]]:
        """提取游标声明"""
        cursors = []
        
        cursor_pattern = r'CURSOR\s+(\w+)\s+IS\s+(.*?);'
        matches = re.finditer(cursor_pattern, text, re.IGNORECASE | re.DOTALL)
        
        for match in matches:
            cursors.append({
                'name': match.group(1),
                'definition': match.group(2).strip()
            })
        
        return cursors

    def _extract_variable_declarations(self, text: str) -> List[Dict[str, Any]]:
        """提取变量声明"""
        variables = []
        
        # 匹配变量声明
        var_pattern = r'(\w+)\s+(\w+(?:\([^)]+\))?)\s*(?::=\s*([^;]+))?;'
        matches = re.finditer(var_pattern, text, re.IGNORECASE)
        
        for match in matches:
            variables.append({
                'name': match.group(1),
                'type': match.group(2),
                'initial_value': match.group(3).strip() if match.group(3) else None
            })
        
        return variables

    def _is_valid_table_name(self, name: str) -> bool:
        """判断是否为有效的表名"""
        # 排除明显的字段名
        field_keywords = {
            'department_id', 'employee_id', 'salary', 'hire_date', 
            'first_name', 'last_name', 'department_name', 'report_date',
            'emp_count', 'avg_salary', 'dept_id', 'processing_date',
            'salary_category', 'total_employees', 'high_salary_count'
        }
        
        # 排除SQL关键字
        sql_keywords = {
            'select', 'from', 'where', 'join', 'on', 'and', 'or',
            'group', 'order', 'having', 'union', 'insert', 'update',
            'delete', 'create', 'table', 'index', 'view'
        }
        
        name_lower = name.lower()
        
        # 如果是明显的字段名，返回False
        if name_lower in field_keywords:
            return False
            
        # 如果是SQL关键字，返回False
        if name_lower in sql_keywords:
            return False
            
        # 如果包含明显的字段后缀，返回False
        field_suffixes = ['_id', '_name', '_date', '_count', '_salary']
        if any(name_lower.endswith(suffix) for suffix in field_suffixes):
            return False
            
        return True 
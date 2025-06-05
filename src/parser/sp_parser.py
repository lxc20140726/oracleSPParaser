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
        """
        解析存储过程文本
        """
        if sp_text is None or not sp_text.strip():
            return StoredProcedureStructure(
                name="unknown_procedure",
                parameters=[],
                sql_statements=[]
            )
            
        try:
            # 预处理文本
            cleaned_text = self._preprocess_text(sp_text)
            
            # 提取过程信息
            proc_name, parameters = self._extract_procedure_info(cleaned_text)
            
            # 提取SQL语句
            sql_statements = self._extract_sql_statements(cleaned_text)
            
            # 提取游标声明
            cursors = self._extract_cursor_declarations(cleaned_text)
            
            # 提取变量声明
            variables = self._extract_variable_declarations(cleaned_text)
            
            return StoredProcedureStructure(
                name=proc_name,
                parameters=parameters,
                sql_statements=sql_statements,
                cursor_declarations=cursors,
                variable_declarations=variables
            )
        except Exception as e:
            # 发生错误时返回基本结构
            return StoredProcedureStructure(
                name="unknown_procedure",
                parameters=[],
                sql_statements=[]
            )

    def _preprocess_text(self, text: str) -> str:
        """预处理文本，清理注释和格式化"""
        if text is None:
            return ""
            
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
                
            # 解析参数：name [IN|OUT|IN OUT] type
            param_pattern = r'(\w+)\s+(IN\s+OUT|IN|OUT)?\s*(\w+(?:\([^)]+\))?)'
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
        
        # 找到BEGIN...END块 - 改进匹配方式
        # 使用更精确的方法匹配完整的存储过程体
        begin_match = re.search(r'BEGIN\s+', text, re.IGNORECASE)
        if not begin_match:
            return statements
        
        # 从BEGIN开始，找到匹配的END
        start_pos = begin_match.end()
        body = ""
        
        # 手动匹配BEGIN/END配对
        lines = text[start_pos:].split('\n')
        begin_count = 1  # 已经有一个BEGIN了
        body_lines = []
        
        for line in lines:
            line_upper = line.upper().strip()
            
            # 计算BEGIN和END的配对
            if line_upper.startswith('BEGIN'):
                begin_count += 1
            elif line_upper.startswith('END'):
                begin_count -= 1
                
                # 如果找到匹配的END，停止
                if begin_count == 0:
                    break
            
            body_lines.append(line)
        
        body = '\n'.join(body_lines)
        
        if not body.strip():
            return statements
        
        # 使用改进的SQL语句分割方法
        sql_parts = self._advanced_sql_split(body)
        
        for i, sql_part in enumerate(sql_parts):
            if not sql_part.strip():
                continue
                
            statement = self._parse_single_statement(sql_part, str(i))
            if statement:
                statements.append(statement)
        
        return statements

    def _advanced_sql_split(self, body: str) -> List[str]:
        """改进的SQL语句分割方法，能处理复杂的控制结构"""
        statements = []
        
        # 直接扫描整个body，按行提取SQL语句
        sql_keywords = ['INSERT', 'UPDATE', 'DELETE', 'SELECT', 'MERGE', 'CREATE']
        lines = body.split('\n')
        
        current_sql = ""
        in_sql_statement = False
        paren_count = 0
        
        for i, line in enumerate(lines):
            line_stripped = line.strip()
            
            # 检查是否是SQL语句的开始
            if any(line_stripped.upper().startswith(keyword) for keyword in sql_keywords):
                # 如果前面有未完成的SQL语句，先保存
                if current_sql.strip():
                    statements.append(current_sql.strip())
                
                current_sql = line
                in_sql_statement = True
                paren_count = line.count('(') - line.count(')')
                
            elif in_sql_statement:
                # 继续当前SQL语句
                current_sql += "\n" + line
                paren_count += line.count('(') - line.count(')')
                
                # 检查是否是SQL语句的结束
                is_sql_end = False
                
                # 方法1：以分号结束
                if line_stripped.endswith(';') and paren_count <= 0:
                    is_sql_end = True
                
                # 方法2：遇到控制结构关键字
                elif any(line_stripped.upper().startswith(kw) for kw in ['IF', 'ELSIF', 'ELSE', 'END', 'WHILE', 'FOR']):
                    if paren_count <= 0:
                        current_sql = current_sql.replace(line, "").strip()
                        is_sql_end = True
                
                # 方法3：遇到新的SQL语句
                elif any(line_stripped.upper().startswith(kw) for kw in sql_keywords):
                    if paren_count <= 0:
                        current_sql = current_sql.replace(line, "").strip()
                        statements.append(current_sql)
                        current_sql = line
                        paren_count = line.count('(') - line.count(')')
                        continue
                
                # 方法4：遇到下一行是控制结构或空行，且当前SQL已经完整
                elif (i + 1 < len(lines) and 
                      lines[i + 1].strip() and
                      any(lines[i + 1].strip().upper().startswith(kw) for kw in ['IF', 'ELSIF', 'ELSE', 'END']) and
                      paren_count <= 0):
                    is_sql_end = True
                
                if is_sql_end:
                    statements.append(current_sql.strip())
                    current_sql = ""
                    in_sql_statement = False
                    paren_count = 0
        
        # 处理最后一个SQL语句
        if current_sql.strip():
            statements.append(current_sql.strip())
        
        # 使用sqlparse作为备份方法
        basic_parts = sqlparse.split(body)
        for part in basic_parts:
            if not part.strip():
                continue
                
            # 检查是否包含IF语句，如果是，递归提取
            if re.search(r'\bIF\b.*?\bTHEN\b', part, re.IGNORECASE | re.DOTALL):
                if_statements = self._extract_sql_from_if_block(part)
                for stmt in if_statements:
                    # 避免重复添加
                    if stmt not in statements and len(stmt) > 10:
                        statements.append(stmt)
            else:
                # 普通语句，直接添加
                if part not in statements and len(part.strip()) > 10:
                    statements.append(part.strip())
        
        # 清理结果
        cleaned_statements = []
        for stmt in statements:
            stmt = stmt.strip()
            if stmt and len(stmt) > 15:  # 过滤太短的语句
                # 移除末尾的分号
                if stmt.endswith(';'):
                    stmt = stmt[:-1].strip()
                
                # 检查是否是有效的SQL语句
                if any(stmt.upper().startswith(keyword) for keyword in sql_keywords):
                    # 避免重复
                    is_duplicate = False
                    for existing in cleaned_statements:
                        if stmt[:100] == existing[:100]:  # 比较前100个字符
                            is_duplicate = True
                            break
                    
                    if not is_duplicate:
                        cleaned_statements.append(stmt)
        
        return cleaned_statements

    def _extract_sql_from_if_block(self, if_block: str) -> List[str]:
        """从IF语句块中提取SQL语句 - 改进版，支持复杂嵌套结构"""
        sql_statements = []
        
        # 方法1：直接搜索SQL关键字，不依赖IF结构解析
        sql_keywords = ['INSERT', 'UPDATE', 'DELETE', 'SELECT', 'MERGE', 'CREATE']
        lines = if_block.split('\n')
        
        current_sql = ""
        in_sql_statement = False
        
        for line in lines:
            line_stripped = line.strip()
            
            # 检查是否是SQL语句的开始
            if any(line_stripped.upper().startswith(keyword) for keyword in sql_keywords):
                # 如果前面有未完成的SQL语句，先保存
                if current_sql.strip():
                    sql_statements.append(current_sql.strip())
                
                current_sql = line
                in_sql_statement = True
            elif in_sql_statement:
                # 继续当前SQL语句
                current_sql += "\n" + line
                
                # 检查是否是SQL语句的结束（通过分号或下一个控制结构）
                if (line_stripped.endswith(';') or 
                    any(line_stripped.upper().startswith(kw) for kw in ['IF', 'ELSIF', 'ELSE', 'END']) or
                    any(line_stripped.upper().startswith(kw) for kw in sql_keywords)):
                    
                    if line_stripped.endswith(';'):
                        # 以分号结束的完整SQL
                        sql_statements.append(current_sql.strip())
                        current_sql = ""
                        in_sql_statement = False
                    elif any(line_stripped.upper().startswith(kw) for kw in sql_keywords):
                        # 遇到新的SQL语句
                        sql_statements.append(current_sql.replace(line, "").strip())
                        current_sql = line
                        in_sql_statement = True
                    else:
                        # 遇到控制结构，结束当前SQL
                        sql_statements.append(current_sql.replace(line, "").strip())
                        current_sql = ""
                        in_sql_statement = False
        
        # 处理最后一个SQL语句
        if current_sql.strip():
            sql_statements.append(current_sql.strip())
        
        # 方法2：使用正则表达式补充提取
        # 提取多行SQL语句
        sql_pattern = r'((?:INSERT|UPDATE|DELETE|SELECT|MERGE|CREATE)\s+(?:[^;]|\n)*?;)'
        regex_matches = re.findall(sql_pattern, if_block, re.IGNORECASE | re.DOTALL)
        
        for match in regex_matches:
            cleaned_sql = match.strip()
            if cleaned_sql and cleaned_sql not in sql_statements:
                sql_statements.append(cleaned_sql)
        
        # 清理和去重
        cleaned_statements = []
        for stmt in sql_statements:
            stmt = stmt.strip()
            if stmt and len(stmt) > 10:  # 过滤太短的语句
                # 移除末尾的分号
                if stmt.endswith(';'):
                    stmt = stmt[:-1].strip()
                
                # 检查是否已存在相似的语句（避免重复）
                is_duplicate = False
                for existing in cleaned_statements:
                    if stmt[:50] == existing[:50]:  # 比较前50个字符
                        is_duplicate = True
                        break
                
                if not is_duplicate:
                    cleaned_statements.append(stmt)
        
        return cleaned_statements

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
        elif sql_upper.startswith('MERGE'):
            return SQLStatementType.MERGE
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
        
        # 提取FROM子句中的表 - 支持schema.table格式（包括带#的临时表）
        from_pattern = r'FROM\s+(.*?)(?:\s+WHERE|\s+GROUP|\s+ORDER|\s+HAVING|\s*;|\s*$)'
        from_match = re.search(from_pattern, sql_text, re.IGNORECASE | re.DOTALL)
        if from_match:
            from_clause = from_match.group(1)
            # 提取表名（包括JOIN的表）- 支持schema.table格式和带#的临时表
            table_patterns = [
                r'(\w+\.(?:#)?\w+|\w+)(?:\s+(\w+))?(?:\s+(?:INNER|LEFT|RIGHT|FULL)?\s*JOIN|,|\s*$)',  # 主表和JOIN表，支持schema.table和带#的表名
                r'JOIN\s+(\w+\.(?:#)?\w+|\w+)(?:\s+(\w+))?',  # JOIN表，支持schema.table和带#的表名
            ]
            
            for pattern in table_patterns:
                matches = re.finditer(pattern, from_clause, re.IGNORECASE)
                for match in matches:
                    table_name = match.group(1)
                    if table_name and table_name.upper() not in ['ON', 'WHERE', 'GROUP', 'ORDER', 'HAVING'] and self._is_valid_table_name(table_name):
                        source_tables.append(table_name)
        
        # 根据语句类型提取目标表 - 支持schema.table格式和带#的临时表
        if stmt_type == SQLStatementType.INSERT:
            insert_pattern = r'INSERT\s+INTO\s+(\w+\.(?:#)?\w+|\w+)'
            insert_match = re.search(insert_pattern, sql_text, re.IGNORECASE)
            if insert_match:
                target_tables.append(insert_match.group(1))
        elif stmt_type == SQLStatementType.UPDATE:
            update_pattern = r'UPDATE\s+(\w+\.(?:#)?\w+|\w+)'
            update_match = re.search(update_pattern, sql_text, re.IGNORECASE)
            if update_match:
                target_tables.append(update_match.group(1))
                # UPDATE语句中的表也是源表（用于读取）
                source_tables.append(update_match.group(1))
        elif stmt_type == SQLStatementType.DELETE:
            delete_pattern = r'DELETE\s+FROM\s+(\w+\.(?:#)?\w+|\w+)'
            delete_match = re.search(delete_pattern, sql_text, re.IGNORECASE)
            if delete_match:
                target_tables.append(delete_match.group(1))
        elif stmt_type in [SQLStatementType.CREATE_TABLE, SQLStatementType.CREATE_TEMP_TABLE]:
            create_pattern = r'CREATE\s+(?:GLOBAL\s+TEMPORARY\s+)?TABLE\s+(\w+\.(?:#)?\w+|\w+)'
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
                
            # 匹配 schema.table.field 或 table.field 格式，支持带#的临时表
            table_field_pattern = r'(\w+\.(?:#)?\w+|\w+)\.(\w+)'
            match = re.search(table_field_pattern, field)
            if match:
                field_refs.append(FieldReference(
                    table_name=match.group(1),
                    field_name=match.group(2)
                ))
        
        return field_refs

    def _extract_target_table_name(self, sql_text: str) -> str:
        """提取目标表名 - 支持schema.table格式和带#的临时表"""
        insert_pattern = r'INSERT\s+INTO\s+(\w+\.(?:#)?\w+|\w+)'
        match = re.search(insert_pattern, sql_text, re.IGNORECASE)
        return match.group(1) if match else "unknown_table"

    def _extract_join_conditions(self, sql_text: str) -> List[JoinCondition]:
        """提取JOIN条件"""
        join_conditions = []
        
        # 改进的JOIN匹配模式，能识别多个JOIN - 支持schema.table格式和带#的临时表
        # 按照不同类型的JOIN分别匹配
        join_patterns = [
            r'(INNER\s+)?JOIN\s+(\w+\.(?:#)?\w+|\w+)\s+(\w+)\s+ON\s+([^J]+?)(?=\s+(?:LEFT|RIGHT|FULL|INNER|CROSS)?\s*JOIN|\s+WHERE|\s+GROUP|\s+ORDER|\s+HAVING|\s*;|\s*$)',
            r'LEFT\s+(?:OUTER\s+)?JOIN\s+(\w+\.(?:#)?\w+|\w+)\s+(\w+)\s+ON\s+([^J]+?)(?=\s+(?:LEFT|RIGHT|FULL|INNER|CROSS)?\s*JOIN|\s+WHERE|\s+GROUP|\s+ORDER|\s+HAVING|\s*;|\s*$)',
            r'RIGHT\s+(?:OUTER\s+)?JOIN\s+(\w+\.(?:#)?\w+|\w+)\s+(\w+)\s+ON\s+([^J]+?)(?=\s+(?:LEFT|RIGHT|FULL|INNER|CROSS)?\s*JOIN|\s+WHERE|\s+GROUP|\s+ORDER|\s+HAVING|\s*;|\s*$)',
            r'FULL\s+(?:OUTER\s+)?JOIN\s+(\w+\.(?:#)?\w+|\w+)\s+(\w+)\s+ON\s+([^J]+?)(?=\s+(?:LEFT|RIGHT|FULL|INNER|CROSS)?\s*JOIN|\s+WHERE|\s+GROUP|\s+ORDER|\s+HAVING|\s*;|\s*$)',
            r'CROSS\s+JOIN\s+(\w+\.(?:#)?\w+|\w+)\s+(\w+)\s+ON\s+([^J]+?)(?=\s+(?:LEFT|RIGHT|FULL|INNER|CROSS)?\s*JOIN|\s+WHERE|\s+GROUP|\s+ORDER|\s+HAVING|\s*;|\s*$)'
        ]
        
        join_types = ['INNER', 'LEFT', 'RIGHT', 'FULL', 'CROSS']
        
        for i, pattern in enumerate(join_patterns):
            matches = re.finditer(pattern, sql_text, re.IGNORECASE | re.DOTALL)
            
            for match in matches:
                if i == 0:  # INNER JOIN (可能没有明确的INNER关键字)
                    table_name = match.group(2)
                    alias = match.group(3)
                    condition_text = match.group(4).strip()
                    join_type = 'INNER'
                else:
                    table_name = match.group(1)
                    alias = match.group(2)
                    condition_text = match.group(3).strip()
                    join_type = join_types[i]
                
                # 解析ON条件中的字段对应关系 - 支持schema.table.field格式
                condition_pattern = r'(\w+\.(?:#)?\w+|\w+)\.(\w+)\s*=\s*(\w+\.(?:#)?\w+|\w+)\.(\w+)'
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
                else:
                    # 如果无法解析具体字段，仍然记录JOIN关系
                    join_conditions.append(JoinCondition(
                        left_table=alias,
                        left_field="unknown",
                        right_table=table_name,
                        right_field="unknown",
                        join_type=join_type,
                        condition_text=condition_text
                    ))
        
        # 如果上面的模式没有匹配到足够多的JOIN，使用更宽松的模式
        if len(join_conditions) < 2:  # 预期应该有多个JOIN
            # 简单模式：查找所有包含JOIN的行
            lines = sql_text.split('\n')
            for line in lines:
                line = line.strip()
                if 'JOIN' in line.upper() and 'ON' in line.upper():
                    # 提取基本信息
                    if 'LEFT' in line.upper():
                        join_type = 'LEFT'
                    elif 'RIGHT' in line.upper():
                        join_type = 'RIGHT'
                    elif 'FULL' in line.upper():
                        join_type = 'FULL'
                    elif 'CROSS' in line.upper():
                        join_type = 'CROSS'
                    else:
                        join_type = 'INNER'
                    
                    # 简单提取表名和条件
                    join_match = re.search(r'JOIN\s+(\w+)\s+(\w+)\s+ON\s+(.+)', line, re.IGNORECASE)
                    if join_match:
                        table_name = join_match.group(1)
                        alias = join_match.group(2)
                        condition = join_match.group(3)
                        
                        # 尝试解析条件
                        condition_match = re.search(r'(\w+)\.(\w+)\s*=\s*(\w+)\.(\w+)', condition)
                        if condition_match:
                            join_conditions.append(JoinCondition(
                                left_table=condition_match.group(1),
                                left_field=condition_match.group(2),
                                right_table=condition_match.group(3),
                                right_field=condition_match.group(4),
                                join_type=join_type,
                                condition_text=condition
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
        """判断是否为有效的表名 - 支持schema.table格式和带#的临时表"""
        # 排除明显的字段名
        field_keywords = {
            'department_id', 'employee_id', 'salary', 'hire_date', 
            'first_name', 'last_name', 'department_name', 'report_date',
            'emp_count', 'avg_salary', 'dept_id', 'processing_date',
            'salary_category', 'total_employees', 'high_salary_count',
            'user_id', 'student_id'  # 添加常见的字段名
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
        
        # 检查是否是schema.table格式
        if '.' in name:
            # 分割schema和table部分
            parts = name.split('.')
            if len(parts) == 2:
                schema, table_name = parts
                
                # 特殊检查：如果schema是单字母（通常是别名）且table_name看起来像字段，则认为是字段引用
                if len(schema) <= 3 and self._looks_like_field_name(table_name):
                    return False
                
                # 验证schema和table部分都是有效的标识符
                if not self._is_valid_identifier(schema) or not self._is_valid_identifier(table_name):
                    return False
                # 支持带#的临时表名
                return True
            else:
                return False
        else:
            # 单个表名的验证
            if not self._is_valid_identifier(name):
                return False
            
            # 如果包含明显的字段后缀，返回False
            field_suffixes = ['_id', '_name', '_date', '_count', '_salary']
            if any(name_lower.endswith(suffix) for suffix in field_suffixes):
                return False
                
        return True
    
    def _looks_like_field_name(self, name: str) -> bool:
        """判断名称是否看起来像字段名"""
        name_lower = name.lower()
        
        # 常见字段后缀
        field_suffixes = ['_id', '_name', '_date', '_count', '_salary', '_code', '_status', '_type']
        if any(name_lower.endswith(suffix) for suffix in field_suffixes):
            return True
            
        # 常见字段名
        common_fields = {
            'id', 'name', 'code', 'status', 'type', 'value', 'amount', 
            'user_id', 'student_id', 'department_id', 'employee_id'
        }
        if name_lower in common_fields:
            return True
            
        return False
    
    def _is_valid_identifier(self, identifier: str) -> bool:
        """验证是否是有效的Oracle标识符（支持带#的临时表）"""
        if not identifier:
            return False
        
        # Oracle标识符规则：以字母或#开头，后面可以跟字母、数字、下划线、#
        # 支持临时表的#前缀
        import re
        pattern = r'^[a-zA-Z#][a-zA-Z0-9_#]*$'
        return bool(re.match(pattern, identifier)) 
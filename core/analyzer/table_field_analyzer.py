#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import re
from typing import Dict, List
try:
    from ..models.data_models import (
        StoredProcedureStructure, TableFieldAnalysis, Table, 
        FieldReference, SQLStatementType, ComputedField
    )
except ImportError:
    from models.data_models import (
        StoredProcedureStructure, TableFieldAnalysis, Table, 
        FieldReference, SQLStatementType, ComputedField
    )

class TableFieldAnalyzer:
    """表字段分析器 - 分析表和字段的关系，构建表对象"""
    
    def analyze(self, sp_structure: StoredProcedureStructure) -> TableFieldAnalysis:
        """分析表和字段关系"""
        physical_tables = {}
        temp_tables = {}
        field_lineage = {}
        
        # 首先识别所有临时表
        temp_table_names = set()
        
        # 方法1：从CREATE TEMP TABLE语句中识别
        for stmt in sp_structure.sql_statements:
            if stmt.statement_type == SQLStatementType.CREATE_TEMP_TABLE:
                for table_name in stmt.target_tables:
                    temp_table_names.add(table_name)
        
        # 方法2：基于表名包含#判断临时表
        all_table_names = set()
        for stmt in sp_structure.sql_statements:
            all_table_names.update(stmt.source_tables)
            all_table_names.update(stmt.target_tables)
        
        for table_name in all_table_names:
            if self._is_temp_table_by_name(table_name):
                temp_table_names.add(table_name)
        
        # 遍历所有SQL语句，构建表和字段信息
        for stmt in sp_structure.sql_statements:
            # 处理目标表（被写入的表）
            for table_name in stmt.target_tables:
                is_temp = table_name in temp_table_names
                
                if is_temp:
                    if table_name not in temp_tables:
                        temp_tables[table_name] = Table(
                            name=table_name,
                            is_temporary=True
                        )
                    temp_tables[table_name].source_sql_ids.append(stmt.statement_id)
                else:
                    if table_name not in physical_tables:
                        physical_tables[table_name] = Table(
                            name=table_name,
                            is_temporary=False
                        )
                    physical_tables[table_name].source_sql_ids.append(stmt.statement_id)
            
            # 处理源表（被读取的表）
            for table_name in stmt.source_tables:
                is_temp = table_name in temp_table_names
                
                if is_temp:
                    if table_name not in temp_tables:
                        temp_tables[table_name] = Table(
                            name=table_name,
                            is_temporary=True
                        )
                else:
                    # 只有不是临时表且不在物理表中时才添加
                    if table_name not in physical_tables:
                        physical_tables[table_name] = Table(
                            name=table_name,
                            is_temporary=False
                        )
            
            # 添加字段信息
            self._add_fields_to_tables(stmt, physical_tables, temp_tables)
            
            # 分析字段血缘关系
            self._analyze_field_lineage(stmt, field_lineage)
        
        return TableFieldAnalysis(
            physical_tables=physical_tables,
            temp_tables=temp_tables,
            field_lineage=field_lineage
        )
    
    def _is_temp_table_by_name(self, table_name: str) -> bool:
        """基于表名判断是否为临时表"""
        if not table_name:
            return False
            
        # 检查表名是否包含#（临时表的典型标志）
        if '#' in table_name:
            return True
            
        # 检查是否以temp_开头
        if table_name.lower().startswith('temp_'):
            return True
            
        # 检查是否以tmp_开头
        if table_name.lower().startswith('tmp_'):
            return True
            
        # 如果是schema.table格式，检查table部分
        if '.' in table_name:
            parts = table_name.split('.')
            if len(parts) == 2:
                schema, table_part = parts
                return self._is_temp_table_by_name(table_part)
        
        return False
    
    def _add_fields_to_tables(self, stmt, physical_tables: Dict[str, Table], temp_tables: Dict[str, Table]):
        """向表对象添加字段信息，支持计算字段"""
        all_tables = {**physical_tables, **temp_tables}
        
        # 从读取的字段中推断表字段
        for field_ref in stmt.fields_read:
            if field_ref.table_name in all_tables:
                all_tables[field_ref.table_name].add_field(field_ref.field_name)
        
        # 从写入的字段中推断表字段
        for field_ref in stmt.fields_written:
            if field_ref.table_name in all_tables:
                all_tables[field_ref.table_name].add_field(field_ref.field_name)
        
        # 处理INSERT语句的复合表达式字段映射
        if hasattr(stmt, 'raw_sql') and 'INSERT' in stmt.raw_sql.upper():
            self._handle_insert_computed_fields(stmt, all_tables)
        
        # 从JOIN条件中推断字段
        for join_cond in stmt.join_conditions:
            if join_cond.left_table in all_tables:
                all_tables[join_cond.left_table].add_field(join_cond.left_field)
            if join_cond.right_table in all_tables:
                all_tables[join_cond.right_table].add_field(join_cond.right_field)
        
        # 从WHERE条件中推断字段
        for where_cond in stmt.where_conditions:
            for field_ref in where_cond.field_references:
                if field_ref.table_name in all_tables:
                    all_tables[field_ref.table_name].add_field(field_ref.field_name)
    
    def _handle_insert_computed_fields(self, stmt, all_tables: Dict[str, Table]):
        """处理INSERT语句中的计算字段，分析SELECT表达式"""
        if not stmt.raw_sql:
            return
            
        # 提取SELECT子句
        select_pattern = r'SELECT\s+(.*?)\s+FROM'
        select_match = re.search(select_pattern, stmt.raw_sql, re.IGNORECASE | re.DOTALL)
        if not select_match:
            return
            
        select_clause = select_match.group(1)
        
        # 提取INSERT目标字段
        insert_pattern = r'INSERT\s+INTO\s+(\w+)\s*(?:\((.*?)\))?'
        insert_match = re.search(insert_pattern, stmt.raw_sql, re.IGNORECASE)
        if not insert_match:
            return
            
        target_table_name = insert_match.group(1)
        target_fields_text = insert_match.group(2)
        
        # 解析目标字段列表
        target_fields = []
        if target_fields_text:
            target_fields = [f.strip() for f in target_fields_text.split(',')]
        
        # 按逗号分割SELECT字段
        select_fields = self._split_select_fields_by_comma(select_clause)
        
        # 将SELECT字段与INSERT字段建立映射关系
        for i, select_expr in enumerate(select_fields):
            select_expr = select_expr.strip()
            if not select_expr:
                continue
                
            # 确定目标字段名
            target_field_name = target_fields[i] if i < len(target_fields) else f"field_{i+1}"
            
            # 检查是否为复合表达式
            if '||' in select_expr:
                self._handle_computed_expression(select_expr, target_table_name, target_field_name, stmt, all_tables)
            else:
                # 简单字段映射
                self._handle_simple_field_mapping(select_expr, target_table_name, target_field_name, all_tables)
    
    def _split_select_fields_by_comma(self, select_clause: str) -> List[str]:
        """按逗号分割SELECT字段"""
        fields = []
        current_field = ""
        paren_count = 0
        in_quotes = False
        quote_char = None
        
        for char in select_clause:
            if char in ("'", '"') and not in_quotes:
                in_quotes = True
                quote_char = char
            elif char == quote_char and in_quotes:
                in_quotes = False
                quote_char = None
            elif char == '(' and not in_quotes:
                paren_count += 1
            elif char == ')' and not in_quotes:
                paren_count -= 1
            elif char == ',' and paren_count == 0 and not in_quotes:
                fields.append(current_field.strip())
                current_field = ""
                continue
            
            current_field += char
        
        if current_field.strip():
            fields.append(current_field.strip())
        
        return fields
    
    def _handle_computed_expression(self, expression: str, target_table: str, target_field: str, stmt, all_tables: Dict[str, Table]):
        """处理计算表达式，如 e.first_name || ' ' || e.last_name"""
        
        # 提取表达式中的字段引用
        component_fields = []
        field_pattern = r'(\w+)\.(\w+)'
        matches = re.finditer(field_pattern, expression)
        
        # 提取表别名映射
        alias_mapping = self._extract_table_aliases_from_sql(stmt.raw_sql)
        
        for match in matches:
            alias = match.group(1)
            field_name = match.group(2)
            
            # 转换别名为实际表名
            table_name = alias_mapping.get(alias, alias)
            
            # 将字段添加到源表
            if table_name in all_tables:
                all_tables[table_name].add_field(field_name)
            
            component_fields.append(FieldReference(
                table_name=table_name,
                field_name=field_name,
                alias=alias if alias != table_name else None
            ))
        
        # 在目标表中添加计算字段
        if target_table in all_tables:
            computed_field = ComputedField(
                expression=expression,
                component_fields=component_fields,
                target_field_name=target_field
            )
            all_tables[target_table].add_computed_field(computed_field)
            all_tables[target_table].add_field(target_field)
    
    def _handle_simple_field_mapping(self, field_expr: str, target_table: str, target_field: str, all_tables: Dict[str, Table]):
        """处理简单字段映射"""
        # 匹配 alias.field_name 格式
        field_pattern = r'(\w+)\.(\w+)'
        match = re.search(field_pattern, field_expr)
        
        if match and target_table in all_tables:
            # 只需要在目标表中添加字段
            all_tables[target_table].add_field(target_field)
    
    def _extract_table_aliases_from_sql(self, sql_text: str) -> Dict[str, str]:
        """从SQL中提取表别名映射"""
        alias_mapping = {}
        
        # 匹配FROM子句
        from_pattern = r'FROM\s+(.*?)(?:\s+WHERE|\s+GROUP|\s+ORDER|\s+HAVING|\s*;|\s*$)'
        from_match = re.search(from_pattern, sql_text, re.IGNORECASE | re.DOTALL)
        
        if from_match:
            from_clause = from_match.group(1)
            
            # 处理主表别名
            main_table_pattern = r'(\w+)\s+(\w+)(?:\s+(?:LEFT|RIGHT|INNER|FULL|CROSS)?\s*JOIN|$)'
            main_match = re.search(main_table_pattern, from_clause, re.IGNORECASE)
            if main_match:
                table_name = main_match.group(1)
                alias = main_match.group(2)
                if alias.upper() not in ('LEFT', 'RIGHT', 'INNER', 'FULL', 'CROSS', 'JOIN'):
                    alias_mapping[alias] = table_name
            
            # 处理JOIN表别名
            join_pattern = r'JOIN\s+(\w+)\s+(\w+)\s+ON'
            join_matches = re.finditer(join_pattern, from_clause, re.IGNORECASE)
            for match in join_matches:
                table_name = match.group(1)
                alias = match.group(2)
                alias_mapping[alias] = table_name
        
        return alias_mapping
    
    def _analyze_field_lineage(self, stmt, field_lineage: Dict[str, List[FieldReference]]):
        """分析字段血缘关系"""
        # 这里可以实现更复杂的字段血缘分析
        # 例如，INSERT语句中的字段映射关系
        if stmt.statement_type == SQLStatementType.INSERT:
            # 简化的血缘分析，实际需要更复杂的解析
            for written_field in stmt.fields_written:
                lineage_key = f"{written_field.table_name}.{written_field.field_name}"
                if lineage_key not in field_lineage:
                    field_lineage[lineage_key] = []
                field_lineage[lineage_key].extend(stmt.fields_read) 
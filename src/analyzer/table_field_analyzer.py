#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from typing import Dict, List
from models.data_models import (
    StoredProcedureStructure, TableFieldAnalysis, Table, 
    FieldReference, SQLStatementType
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
        for stmt in sp_structure.sql_statements:
            if stmt.statement_type == SQLStatementType.CREATE_TEMP_TABLE:
                for table_name in stmt.target_tables:
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
    
    def _add_fields_to_tables(self, stmt, physical_tables: Dict[str, Table], temp_tables: Dict[str, Table]):
        """向表对象添加字段信息"""
        all_tables = {**physical_tables, **temp_tables}
        
        # 从读取的字段中推断表字段
        for field_ref in stmt.fields_read:
            if field_ref.table_name in all_tables:
                all_tables[field_ref.table_name].add_field(field_ref.field_name)
        
        # 从写入的字段中推断表字段
        for field_ref in stmt.fields_written:
            if field_ref.table_name in all_tables:
                all_tables[field_ref.table_name].add_field(field_ref.field_name)
        
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
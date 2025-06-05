#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from typing import Dict, Any, List

try:
    import cx_Oracle
except ImportError:
    cx_Oracle = None

class MetadataExpander:
    def __init__(self, db_connection=None):
        self.db_connection = db_connection
        self.expanded_metadata = {}

    def expand(self, table_analysis: Dict[str, Any]) -> Dict[str, Any]:
        """
        扩展表的元数据信息
        """
        for table in table_analysis['physical_tables']:
            self._expand_table_metadata(table)
        
        return self.expanded_metadata

    def _expand_table_metadata(self, table_name: str):
        """
        扩展单个表的元数据
        """
        if not self.db_connection:
            return
        
        try:
            cursor = self.db_connection.cursor()
            
            # 获取表结构
            cursor.execute(f"""
                SELECT column_name, data_type, data_length, nullable
                FROM all_tab_columns
                WHERE table_name = :1
            """, [table_name.upper()])
            
            columns = []
            for row in cursor:
                columns.append({
                    'name': row[0],
                    'type': row[1],
                    'length': row[2],
                    'nullable': row[3]
                })
            
            # 获取主键信息
            cursor.execute(f"""
                SELECT cols.column_name
                FROM all_constraints cons, all_cons_columns cols
                WHERE cons.constraint_type = 'P'
                AND cons.constraint_name = cols.constraint_name
                AND cons.owner = cols.owner
                AND cols.table_name = :1
            """, [table_name.upper()])
            
            primary_keys = [row[0] for row in cursor]
            
            self.expanded_metadata[table_name] = {
                'columns': columns,
                'primary_keys': primary_keys,
                'foreign_keys': self._get_foreign_keys(table_name)
            }
            
        except Exception as error:
            if cx_Oracle and isinstance(error, cx_Oracle.Error):
                print(f"Error expanding metadata for table {table_name}: {error}")
            else:
                print(f"Error expanding metadata for table {table_name}: {error}")

    def _get_foreign_keys(self, table_name: str) -> List[Dict[str, str]]:
        """
        获取表的外键信息
        """
        if not self.db_connection:
            return []
        
        try:
            cursor = self.db_connection.cursor()
            cursor.execute(f"""
                SELECT a.constraint_name, a.r_constraint_name,
                       c_pk.table_name r_table_name,
                       c.column_name, c_pk.column_name r_column_name
                FROM all_constraints a
                JOIN all_cons_columns c ON a.constraint_name = c.constraint_name
                JOIN all_cons_columns c_pk ON a.r_constraint_name = c_pk.constraint_name
                WHERE a.constraint_type = 'R'
                AND a.table_name = :1
            """, [table_name.upper()])
            
            foreign_keys = []
            for row in cursor:
                foreign_keys.append({
                    'constraint_name': row[0],
                    'column': row[3],
                    'references_table': row[2],
                    'references_column': row[4]
                })
            
            return foreign_keys
            
        except Exception as error:
            if cx_Oracle and isinstance(error, cx_Oracle.Error):
                print(f"Error getting foreign keys for table {table_name}: {error}")
            else:
                print(f"Error getting foreign keys for table {table_name}: {error}")
            return [] 
#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sqlparse
import re
from typing import List, Dict, Any, Optional
from models.data_models import (
    StoredProcedureStructure, SQLStatement, SQLStatementType, 
    Parameter, FieldReference, JoinCondition, WhereCondition, StoredProcedure
)

class StoredProcedureParser:
    """
    Oracle存储过程解析器
    专注于解析存储过程的结构，识别SQL语句、参数、变量等
    """
    
    def __init__(self):
        """初始化解析器"""
        self.analysis_result = None
        self.logger = None
        self.procedure_name = None
        self.parameters = []
        self.sql_statements = []
        self.raw_code = ""
        self.cursor_declarations = []
        self.variable_declarations = []

    def parse(self, procedure_text: str) -> "StoredProcedure":
        """
        解析存储过程文本
        
        Args:
            procedure_text: 存储过程的SQL文本
            
        Returns:
            StoredProcedure: 解析后的存储过程对象
        """
        from models.data_models import StoredProcedure, Parameter, SQLStatement
        
        try:
            self.raw_code = procedure_text
            
            # 提取存储过程名称
            self.procedure_name = self._extract_procedure_name(procedure_text)
            
            # 提取参数
            self.parameters = self._extract_parameters(procedure_text)
            
            # 提取SQL语句
            self.sql_statements = self._extract_sql_statements(procedure_text)
            
            # 提取游标声明
            self.cursor_declarations = self._extract_cursor_declarations(procedure_text)
            
            # 提取变量声明
            self.variable_declarations = self._extract_variable_declarations(procedure_text)
            
            # 创建存储过程对象
            procedure = StoredProcedure(
                name=self.procedure_name,
                parameters=self.parameters,
                sql_statements=self.sql_statements,
                cursor_declarations=self.cursor_declarations,
                variable_declarations=self.variable_declarations,
                raw_code=procedure_text
            )
            
            return procedure
            
        except Exception as e:
            raise Exception(f"解析存储过程失败: {str(e)}")

    def _preprocess_text(self, text: str) -> str:
        """预处理文本，清理注释和格式化"""
        # 移除单行注释
        text = re.sub(r'--.*?\n', '\n', text)
        # 移除多行注释
        text = re.sub(r'/\*.*?\*/', '', text, flags=re.DOTALL)
        # 标准化空白字符
        text = re.sub(r'\s+', ' ', text)
        return text.strip()

    def _extract_procedure_name(self, procedure_text: str) -> str:
        """提取存储过程名称"""
        # 匹配 CREATE [OR REPLACE] PROCEDURE procedure_name
        pattern = r'CREATE\s+(?:OR\s+REPLACE\s+)?PROCEDURE\s+(\w+)'
        match = re.search(pattern, procedure_text, re.IGNORECASE)
        
        if match:
            return match.group(1)
        
        # 如果没有找到，返回默认名称
        return "unknown_procedure"

    def _extract_parameters(self, procedure_text: str) -> List["Parameter"]:
        """提取存储过程参数"""
        from models.data_models import Parameter
        import re
        
        parameters = []
        
        # 匹配参数定义 (param_name IN/OUT/INOUT datatype)
        # 简化的正则表达式，匹配括号内的参数
        param_pattern = r'\(\s*([^)]+)\s*\)'
        proc_match = re.search(r'PROCEDURE\s+\w+\s*' + param_pattern, procedure_text, re.IGNORECASE | re.DOTALL)
        
        if proc_match:
            param_text = proc_match.group(1)
            
            # 分割参数（按逗号）
            param_list = [p.strip() for p in param_text.split(',')]
            
            for param_def in param_list:
                if param_def.strip():
                    param = self._parse_single_parameter(param_def)
                    if param:
                        parameters.append(param)
        
        return parameters

    def _parse_single_parameter(self, param_def: str) -> Optional["Parameter"]:
        """解析单个参数定义"""
        from models.data_models import Parameter
        import re
        
        # 匹配格式: param_name [IN|OUT|INOUT] datatype
        pattern = r'(\w+)\s+(IN|OUT|INOUT)?\s*(\w+(?:\(\d+\))?)'
        match = re.search(pattern, param_def.strip(), re.IGNORECASE)
        
        if match:
            param_name = match.group(1)
            direction = (match.group(2) or "IN").upper()
            data_type = match.group(3)
            
            return Parameter(
                name=param_name,
                direction=direction,
                data_type=data_type
            )
        
        return None

    def _extract_sql_statements(self, procedure_text: str) -> List["SQLStatement"]:
        """提取存储过程中的SQL语句"""
        from models.data_models import SQLStatement, StatementType
        from parser.sql_parser import SQLStatementParser
        
        statements = []
        
        # 提取BEGIN...END之间的内容
        begin_match = re.search(r'BEGIN\s+(.*)\s+END', procedure_text, re.IGNORECASE | re.DOTALL)
        if begin_match:
            body = begin_match.group(1)
            
            # 简单地按分号分割语句
            sql_lines = [line.strip() for line in body.split(';') if line.strip()]
            
            parser = SQLStatementParser()
            
            for i, sql_line in enumerate(sql_lines):
                if sql_line.upper().strip() in ['', 'NULL', 'END']:
                    continue
                    
                try:
                    stmt = parser.parse(sql_line)
                    stmt.statement_id = i + 1  # 重新编号
                    statements.append(stmt)
                except:
                    # 如果解析失败，创建一个基本的语句对象
                    stmt = SQLStatement(
                        statement_id=i + 1,
                        statement_type=StatementType.OTHER,
                        raw_sql=sql_line,
                        source_tables=[],
                        target_tables=[]
                    )
                    statements.append(stmt)
        
        return statements

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
#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from typing import List
try:
    from ..models.data_models import StoredProcedureStructure, Parameter
except ImportError:
    from models.data_models import StoredProcedureStructure, Parameter

class ParameterAnalyzer:
    """参数分析器 - 识别和分析存储过程参数的使用情况"""
    
    def extract_parameters(self, sp_structure: StoredProcedureStructure) -> List[Parameter]:
        """提取并分析参数使用情况"""
        parameters = sp_structure.parameters
        
        # 分析每个参数在哪些SQL语句中被使用
        for param in parameters:
            param.used_in_statements = []
            for stmt in sp_structure.sql_statements:
                if param.name in stmt.parameters_used:
                    param.used_in_statements.append(stmt.statement_id)
        
        return parameters 
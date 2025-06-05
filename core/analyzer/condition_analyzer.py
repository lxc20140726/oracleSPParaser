#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from typing import List, Dict, Any
try:
    from ..models.data_models import (
        StoredProcedureStructure, ConditionsAndLogic, 
        JoinCondition, WhereCondition, SQLStatementType
    )
except ImportError:
    from models.data_models import (
        StoredProcedureStructure, ConditionsAndLogic, 
        JoinCondition, WhereCondition, SQLStatementType
    )

class ConditionAnalyzer:
    """条件分析器 - 分析匹配条件和SQL逻辑"""
    
    def analyze(self, sp_structure: StoredProcedureStructure) -> ConditionsAndLogic:
        """分析条件和逻辑"""
        join_conditions = []
        where_conditions = []
        control_flow = []
        
        for stmt in sp_structure.sql_statements:
            # 收集JOIN条件
            join_conditions.extend(stmt.join_conditions)
            
            # 收集WHERE条件
            where_conditions.extend(stmt.where_conditions)
            
            # 分析控制流
            if stmt.statement_type in [
                SQLStatementType.IF_STATEMENT, 
                SQLStatementType.WHILE_LOOP, 
                SQLStatementType.FOR_LOOP
            ]:
                control_flow.append({
                    'type': stmt.statement_type.value,
                    'statement_id': stmt.statement_id,
                    'raw_sql': stmt.raw_sql
                })
        
        return ConditionsAndLogic(
            join_conditions=join_conditions,
            where_conditions=where_conditions,
            control_flow=control_flow
        ) 
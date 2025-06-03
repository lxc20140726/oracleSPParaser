#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from typing import List, Dict, Any, Optional, Set
from pydantic import BaseModel, Field
from enum import Enum

class SQLStatementType(Enum):
    SELECT = "SELECT"
    INSERT = "INSERT"
    UPDATE = "UPDATE"
    DELETE = "DELETE"
    CREATE_TABLE = "CREATE_TABLE"
    CREATE_TEMP_TABLE = "CREATE_TEMP_TABLE"
    DECLARE_CURSOR = "DECLARE_CURSOR"
    IF_STATEMENT = "IF_STATEMENT"
    WHILE_LOOP = "WHILE_LOOP"
    FOR_LOOP = "FOR_LOOP"
    OTHER = "OTHER"

class FieldReference(BaseModel):
    """字段引用"""
    table_name: str
    field_name: str
    alias: Optional[str] = None

class JoinCondition(BaseModel):
    """连接条件"""
    left_table: str
    left_field: str
    right_table: str
    right_field: str
    join_type: str  # INNER, LEFT, RIGHT, FULL
    condition_text: str

class WhereCondition(BaseModel):
    """WHERE条件"""
    field_references: List[FieldReference]
    condition_text: str
    parameters_used: List[str]

class SQLStatement(BaseModel):
    """SQL语句"""
    statement_id: str
    statement_type: SQLStatementType
    raw_sql: str
    source_tables: List[str]
    target_tables: List[str]
    fields_read: List[FieldReference]
    fields_written: List[FieldReference]
    join_conditions: List[JoinCondition]
    where_conditions: List[WhereCondition]
    parameters_used: List[str]

class Table(BaseModel):
    """表对象"""
    name: str
    is_temporary: bool = False
    fields: List[str] = Field(default_factory=list)
    source_sql_ids: List[str] = Field(default_factory=list)
    
    def add_field(self, field_name: str):
        """添加字段（确保不重复）"""
        if field_name not in self.fields:
            self.fields.append(field_name)

class Parameter(BaseModel):
    """存储过程参数"""
    name: str
    data_type: str
    direction: str  # IN, OUT, INOUT
    used_in_statements: List[str] = Field(default_factory=list)

class StoredProcedureStructure(BaseModel):
    """存储过程结构"""
    name: str
    parameters: List[Parameter]
    sql_statements: List[SQLStatement]
    cursor_declarations: List[Dict[str, Any]] = Field(default_factory=list)
    variable_declarations: List[Dict[str, Any]] = Field(default_factory=list)

class TableFieldAnalysis(BaseModel):
    """表字段分析结果"""
    physical_tables: Dict[str, Table]
    temp_tables: Dict[str, Table]
    field_lineage: Dict[str, List[FieldReference]]  # 字段血缘关系

class ConditionsAndLogic(BaseModel):
    """条件和逻辑分析结果"""
    join_conditions: List[JoinCondition]
    where_conditions: List[WhereCondition]
    control_flow: List[Dict[str, Any]]  # IF/WHILE/FOR等控制流

class StoredProcedureAnalysis(BaseModel):
    """存储过程完整分析结果"""
    sp_structure: StoredProcedureStructure
    parameters: List[Parameter]
    table_field_analysis: TableFieldAnalysis
    conditions_and_logic: ConditionsAndLogic

class VisualizationNode(BaseModel):
    """可视化节点"""
    id: str
    label: str
    type: str  # table, field, condition, parameter
    properties: Dict[str, Any] = Field(default_factory=dict)

class VisualizationEdge(BaseModel):
    """可视化边"""
    source: str
    target: str
    label: str
    type: str  # data_flow, join, condition
    properties: Dict[str, Any] = Field(default_factory=dict) 
#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from typing import List, Dict, Any, Optional, Set, Union
from pydantic import BaseModel, Field
from enum import Enum

class SQLStatementType(Enum):
    SELECT = "SELECT"
    INSERT = "INSERT"
    UPDATE = "UPDATE"
    DELETE = "DELETE"
    MERGE = "MERGE"
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

class ComputedField(BaseModel):
    """计算字段或表达式字段"""
    expression: str  # 原始表达式，如 "e.first_name || ' ' || e.last_name"
    component_fields: List[FieldReference] = Field(default_factory=list)  # 组成字段
    alias: Optional[str] = None
    target_field_name: Optional[str] = None  # 在目标表中对应的字段名
    
class FieldExpression(BaseModel):
    """字段表达式 - 可以是简单字段引用或复杂表达式"""
    is_simple: bool = True  # 是否为简单字段引用
    simple_field: Optional[FieldReference] = None  # 简单字段引用
    computed_field: Optional[ComputedField] = None  # 复杂计算字段
    
    @classmethod
    def from_simple_field(cls, table_name: str, field_name: str, alias: str = None):
        """创建简单字段表达式"""
        return cls(
            is_simple=True,
            simple_field=FieldReference(
                table_name=table_name,
                field_name=field_name,
                alias=alias
            )
        )
    
    @classmethod
    def from_computed_field(cls, expression: str, component_fields: List[FieldReference], alias: str = None, target_field: str = None):
        """创建计算字段表达式"""
        return cls(
            is_simple=False,
            computed_field=ComputedField(
                expression=expression,
                component_fields=component_fields,
                alias=alias,
                target_field_name=target_field
            )
        )

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
    # 新增：支持复杂表达式的字段
    select_expressions: List[FieldExpression] = Field(default_factory=list)
    insert_field_mapping: Dict[str, FieldExpression] = Field(default_factory=dict)  # 目标字段名 -> 源表达式
    join_conditions: List[JoinCondition]
    where_conditions: List[WhereCondition]
    parameters_used: List[str]

class Table(BaseModel):
    """表对象"""
    name: str
    is_temporary: bool = False
    fields: List[str] = Field(default_factory=list)
    computed_fields: List[ComputedField] = Field(default_factory=list)  # 计算字段
    source_sql_ids: List[str] = Field(default_factory=list)
    
    def add_field(self, field_name: str):
        """添加字段（确保不重复）"""
        if field_name not in self.fields:
            self.fields.append(field_name)
    
    def add_computed_field(self, computed_field: ComputedField):
        """添加计算字段"""
        # 检查是否已经存在相同的计算字段
        for existing_field in self.computed_fields:
            if existing_field.expression == computed_field.expression:
                return
        self.computed_fields.append(computed_field)

class Parameter(BaseModel):
    """存储过程参数"""
    name: str
    data_type: str
    direction: str  # IN, OUT, INOUT
    default_value: Optional[str] = None
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
    computed_field_lineage: Dict[str, List[ComputedField]] = Field(default_factory=dict)  # 计算字段血缘关系

class ConditionsAndLogic(BaseModel):
    """条件和逻辑分析结果"""
    join_conditions: List[JoinCondition]
    where_conditions: List[WhereCondition]
    merge_conditions: List[Dict[str, Any]] = Field(default_factory=list)  # MERGE语句条件
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
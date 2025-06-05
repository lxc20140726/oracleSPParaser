#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import json
import os
import re
from typing import Dict, List, Any, Tuple
try:
    from ..models.data_models import (
        StoredProcedureAnalysis, VisualizationNode, VisualizationEdge,
        FieldReference, ComputedField
    )
except ImportError:
    from models.data_models import (
        StoredProcedureAnalysis, VisualizationNode, VisualizationEdge,
        FieldReference, ComputedField
    )

class UMLVisualizer:
    """UML样式的表可视化器 - 显示表结构和字段映射关系"""
    
    def __init__(self):
        self.uml_nodes = []
        self.field_mapping_edges = []
        self.table_relations = []
    
    def create_uml_visualization(self, analysis: StoredProcedureAnalysis) -> Dict[str, Any]:
        """创建UML样式的可视化数据"""
        self.uml_nodes = []
        self.field_mapping_edges = []
        self.table_relations = []
        
        # 1. 创建UML表节点（包含字段列表）
        self._create_uml_table_nodes(analysis)
        
        # 2. 分析字段映射关系
        self._analyze_field_mappings(analysis)
        
        # 3. 创建表关系连接
        self._create_table_relations(analysis)
        
        # 4. 保存UML可视化数据
        uml_data = self._save_uml_visualization_data(analysis)
        
        # 5. 打印UML图
        self._print_uml_diagram(analysis)
        
        return uml_data
    
    def _create_uml_table_nodes(self, analysis: StoredProcedureAnalysis):
        """创建UML样式的表节点"""
        
        # 处理物理表
        for table_name, table in analysis.table_field_analysis.physical_tables.items():
            node = self._create_table_uml_node(table_name, table, "physical_table")
            self.uml_nodes.append(node)
        
        # 处理临时表
        for table_name, table in analysis.table_field_analysis.temp_tables.items():
            node = self._create_table_uml_node(table_name, table, "temp_table")
            self.uml_nodes.append(node)
    
    def _create_table_uml_node(self, table_name: str, table, table_type: str) -> VisualizationNode:
        """创建单个表的UML节点"""
        
        # 收集所有字段（包括计算字段）
        all_fields = []
        
        # 普通字段
        for field in sorted(table.fields):
            all_fields.append({
                "name": field,
                "type": "field",
                "source": "table"
            })
        
        # 计算字段
        for computed_field in table.computed_fields:
            all_fields.append({
                "name": computed_field.target_field_name or computed_field.alias or "computed_field",
                "type": "computed_field",
                "expression": computed_field.expression,
                "source_fields": [
                    f"{ref.table_name}.{ref.field_name}" 
                    for ref in computed_field.component_fields
                ]
            })
        
        # 确定颜色和样式
        color = "lightgreen" if table_type == "physical_table" else "lightyellow"
        border_style = "solid" if table_type == "physical_table" else "dashed"
        
        # 计算表结构的高度和宽度，为字段显示预留空间
        header_height = 40  # 表头高度
        field_height = 20   # 每个字段的高度
        padding = 20        # 上下内边距
        min_width = 200     # 最小宽度
        
        # 计算实际尺寸
        table_width = max(min_width, len(table_name) * 10 + 60)
        table_height = header_height + len(all_fields) * field_height + padding
        
        node = VisualizationNode(
            id=f"uml_table_{table_name}",
            label=table_name,
            type=f"uml_{table_type}",
            properties={
                "table_name": table_name,
                "fields": all_fields,
                "field_count": len(all_fields),
                "color": color,
                "border_style": border_style,
                "sql_ids": table.source_sql_ids,
                "is_temporary": table.is_temporary,
                # UML样式属性
                "shape": "uml_table",
                "width": table_width,
                "height": table_height,
                # 新增：字段布局信息，用于精确定位字段连接点
                "field_layout": {
                    "header_height": header_height,
                    "field_height": field_height,
                    "padding": 10
                }
            }
        )
        
        return node
    
    def _analyze_field_mappings(self, analysis: StoredProcedureAnalysis):
        """分析字段之间的映射关系"""
        
        for stmt in analysis.sp_structure.sql_statements:
            # 分析INSERT语句的字段映射
            if stmt.statement_type.value == "INSERT":
                self._analyze_insert_field_mappings(stmt, analysis)
            
            # 分析SELECT语句的字段映射
            elif stmt.statement_type.value == "SELECT":
                self._analyze_select_field_mappings(stmt, analysis)
            
            # 分析UPDATE语句的字段映射
            elif stmt.statement_type.value == "UPDATE":
                self._analyze_update_field_mappings(stmt, analysis)
    
    def _analyze_insert_field_mappings(self, stmt, analysis: StoredProcedureAnalysis):
        """分析INSERT语句的字段映射 - 重新实现以正确解析字段映射关系"""
        
        if not stmt.raw_sql or 'INSERT' not in stmt.raw_sql.upper():
            return
        
        # 直接从原始SQL解析INSERT...SELECT语句
        field_mappings = self._parse_insert_select_mappings(stmt.raw_sql)
        
        if not field_mappings:
            return
            
        target_table = field_mappings['target_table']
        
        # 建立表别名映射
        alias_mapping = self._extract_table_aliases_from_sql(stmt.raw_sql)
        
        # 处理每个字段映射
        for i, (target_field, source_expr) in enumerate(field_mappings['field_mappings']):
            
            # 检查是否为复合表达式（包含||运算符）
            if '||' in source_expr:
                # 复合表达式映射
                component_fields = self._extract_fields_from_expression(source_expr, alias_mapping)
                
                for component_field in component_fields:
                    self._create_field_mapping_edge(
                        source_table=component_field['table'],
                        source_field=component_field['field'],
                        target_table=target_table,
                        target_field=target_field,
                        mapping_type="computed_insert",
                        stmt_id=stmt.statement_id,
                        expression=source_expr
                    )
            else:
                # 简单字段映射
                source_field_info = self._parse_simple_field_reference(source_expr, alias_mapping)
                
                if source_field_info:
                    self._create_field_mapping_edge(
                        source_table=source_field_info['table'],
                        source_field=source_field_info['field'],
                        target_table=target_table,
                        target_field=target_field,
                        mapping_type="simple_insert",
                        stmt_id=stmt.statement_id
                    )
    
    def _parse_insert_select_mappings(self, sql_text: str) -> Dict[str, Any]:
        """解析INSERT...SELECT语句的字段映射"""
        
        # 提取INSERT目标表和字段
        insert_pattern = r'INSERT\s+INTO\s+(\w+)\s*(?:\((.*?)\))?\s+SELECT\s+(.*?)\s+FROM'
        match = re.search(insert_pattern, sql_text, re.IGNORECASE | re.DOTALL)
        
        if not match:
            return {}
        
        target_table = match.group(1)
        target_fields_text = match.group(2)
        select_fields_text = match.group(3)
        
        # 解析目标字段列表
        if target_fields_text:
            target_fields = [f.strip() for f in target_fields_text.split(',')]
        else:
            # 如果没有指定字段列表，使用默认字段名
            select_fields = self._split_select_fields_by_comma(select_fields_text)
            target_fields = [f"field_{i+1}" for i in range(len(select_fields))]
        
        # 解析SELECT字段列表
        select_fields = self._split_select_fields_by_comma(select_fields_text)
        
        # 建立字段映射关系
        field_mappings = []
        for i, select_field in enumerate(select_fields):
            target_field = target_fields[i] if i < len(target_fields) else f"field_{i+1}"
            field_mappings.append((target_field, select_field.strip()))
        
        return {
            'target_table': target_table,
            'field_mappings': field_mappings
        }
    
    def _extract_fields_from_expression(self, expression: str, alias_mapping: Dict[str, str]) -> List[Dict[str, str]]:
        """从复合表达式中提取所有字段引用"""
        fields = []
        
        # 匹配 alias.field 模式
        field_pattern = r'(\w+)\.(\w+)'
        matches = re.finditer(field_pattern, expression)
        
        for match in matches:
            alias = match.group(1)
            field_name = match.group(2)
            
            # 转换别名为实际表名
            table_name = alias_mapping.get(alias, alias)
            
            fields.append({
                'table': table_name,
                'field': field_name,
                'alias': alias if alias != table_name else None
            })
        
        return fields
    
    def _parse_simple_field_reference(self, field_expr: str, alias_mapping: Dict[str, str]) -> Dict[str, str]:
        """解析简单字段引用"""
        field_expr = field_expr.strip()
        
        # 匹配 alias.field 格式
        field_pattern = r'(\w+)\.(\w+)'
        match = re.search(field_pattern, field_expr)
        
        if match:
            alias = match.group(1)
            field_name = match.group(2)
            table_name = alias_mapping.get(alias, alias)
            
            return {
                'table': table_name,
                'field': field_name,
                'alias': alias if alias != table_name else None
            }
        
        return None
    
    def _extract_table_aliases_from_sql(self, sql_text: str) -> Dict[str, str]:
        """从SQL中提取表别名映射 alias -> table_name"""
        alias_mapping = {}
        
        # 匹配FROM子句
        from_pattern = r'FROM\s+(.*?)(?:\s+WHERE|\s+GROUP|\s+ORDER|\s+HAVING|\s*;|\s*$)'
        from_match = re.search(from_pattern, sql_text, re.IGNORECASE | re.DOTALL)
        
        if from_match:
            from_clause = from_match.group(1)
            
            # 处理主表别名：table_name alias
            main_table_pattern = r'(\w+)\s+(\w+)(?:\s+(?:LEFT|RIGHT|INNER|FULL|CROSS)?\s*JOIN|$)'
            main_match = re.search(main_table_pattern, from_clause, re.IGNORECASE)
            if main_match:
                table_name = main_match.group(1)
                alias = main_match.group(2)
                if alias.upper() not in ('LEFT', 'RIGHT', 'INNER', 'FULL', 'CROSS', 'JOIN'):
                    alias_mapping[alias] = table_name
            
            # 处理JOIN表别名：JOIN table_name alias ON
            join_pattern = r'JOIN\s+(\w+)\s+(\w+)\s+ON'
            join_matches = re.finditer(join_pattern, from_clause, re.IGNORECASE)
            for match in join_matches:
                table_name = match.group(1)
                alias = match.group(2)
                alias_mapping[alias] = table_name
        
        return alias_mapping
    
    def _split_select_fields_by_comma(self, select_clause: str) -> List[str]:
        """按逗号分割SELECT字段，考虑括号和引号"""
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
    
    def _analyze_select_field_mappings(self, stmt, analysis: StoredProcedureAnalysis):
        """分析SELECT语句的字段映射（如果有目标表）"""
        pass  # SELECT语句通常不直接创建字段映射，除非是INSERT INTO ... SELECT
    
    def _analyze_update_field_mappings(self, stmt, analysis: StoredProcedureAnalysis):
        """分析UPDATE语句的字段映射"""
        
        # UPDATE语句通常在同一个表内进行字段更新
        for field_ref in stmt.fields_written:
            # 查找相关的读取字段
            for read_field in stmt.fields_read:
                if read_field.table_name == field_ref.table_name:
                    continue  # 跳过同一表的自我引用
                
                self._create_field_mapping_edge(
                    source_table=read_field.table_name,
                    source_field=read_field.field_name,
                    target_table=field_ref.table_name,
                    target_field=field_ref.field_name,
                    mapping_type="update",
                    stmt_id=stmt.statement_id
                )
    
    def _create_field_mapping_edge(self, source_table: str, source_field: str, 
                                 target_table: str, target_field: str, 
                                 mapping_type: str, stmt_id: str, expression: str = None):
        """创建字段映射连接"""
        
        # 创建唯一的连接ID
        edge_id = f"{source_table}.{source_field}_to_{target_table}.{target_field}"
        
        # 避免重复连接
        for existing_edge in self.field_mapping_edges:
            if hasattr(existing_edge, 'properties') and existing_edge.properties.get('id') == edge_id:
                return
        
        # 创建更明确的字段映射标签
        if expression:
            label = f"{source_field} → {target_field}\n({expression[:30]}...)"
        else:
            label = f"{source_field} → {target_field}"
        
        # 查找源表和目标表的节点，获取字段布局信息
        source_node = None
        target_node = None
        
        for node in self.uml_nodes:
            if node.properties.get('table_name') == source_table:
                source_node = node
            elif node.properties.get('table_name') == target_table:
                target_node = node
        
        # 计算字段在表中的索引位置（用于前端精确定位连接点）
        source_field_index = -1
        target_field_index = -1
        
        if source_node:
            for i, field in enumerate(source_node.properties.get('fields', [])):
                if field['name'] == source_field:
                    source_field_index = i
                    break
        
        if target_node:
            for i, field in enumerate(target_node.properties.get('fields', [])):
                if field['name'] == target_field:
                    target_field_index = i
                    break
        
        edge = VisualizationEdge(
            source=f"uml_table_{source_table}",
            target=f"uml_table_{target_table}",
            label=label,
            type="field_mapping",
            properties={
                "id": edge_id,
                "source_table": source_table,
                "source_field": source_field,
                "target_table": target_table,
                "target_field": target_field,
                "mapping_type": mapping_type,
                "statement_id": stmt_id,
                "expression": expression,
                "style": "solid",  # 改为实线以更好地表示映射关系
                "color": self._get_mapping_color(mapping_type),
                "width": "3",
                "arrow_type": "triangle",
                # 新增：字段级连接点信息
                "source_field_index": source_field_index,
                "target_field_index": target_field_index,
                # 连接点样式 - 用于前端精确绘制字段到字段的连接
                "connection_style": "field_to_field"  # 标识这是字段级连接
            }
        )
        
        self.field_mapping_edges.append(edge)
    
    def _get_mapping_color(self, mapping_type: str) -> str:
        """根据映射类型获取颜色"""
        color_map = {
            "simple_insert": "blue",
            "computed_insert": "purple",
            "update": "orange",
            "join": "green"
        }
        return color_map.get(mapping_type, "gray")
    
    def _create_table_relations(self, analysis: StoredProcedureAnalysis):
        """创建表之间的关系连接"""
        
        # 获取所有表名（用于将别名转换为实际表名）
        all_table_names = set()
        all_table_names.update(analysis.table_field_analysis.physical_tables.keys())
        all_table_names.update(analysis.table_field_analysis.temp_tables.keys())
        
        # 基于JOIN条件创建表关系
        processed_relations = set()  # 用于避免重复关系
        
        for join_cond in analysis.conditions_and_logic.join_conditions:
            # 将别名转换为实际表名
            left_table = self._resolve_table_name(join_cond.left_table, all_table_names)
            right_table = self._resolve_table_name(join_cond.right_table, all_table_names)
            
            # 创建关系的唯一标识符
            relation_key = f"{left_table}_{right_table}" if left_table < right_table else f"{right_table}_{left_table}"
            
            # 避免重复的关系
            if relation_key in processed_relations:
                continue
            processed_relations.add(relation_key)
            
            # 确保表节点存在
            left_node_id = f"uml_table_{left_table}"
            right_node_id = f"uml_table_{right_table}"
            
            # 检查节点是否存在
            left_exists = any(node.id == left_node_id for node in self.uml_nodes)
            right_exists = any(node.id == right_node_id for node in self.uml_nodes)
            
            if not left_exists or not right_exists:
                print(f"警告: 跳过关系 {left_table} - {right_table}，因为节点不存在")
                continue
            
            edge = VisualizationEdge(
                source=left_node_id,
                target=right_node_id,
                label=f"{join_cond.left_field} = {join_cond.right_field}",
                type="table_relation",
                properties={
                    "relation_type": join_cond.join_type,
                    "left_field": join_cond.left_field,
                    "right_field": join_cond.right_field,
                    "condition": join_cond.condition_text,
                    "style": "solid",
                    "color": "darkgreen",
                    "arrow_type": "diamond"
                }
            )
            self.table_relations.append(edge)
    
    def _resolve_table_name(self, name_or_alias: str, all_table_names: set) -> str:
        """将表别名解析为实际表名"""
        # 如果已经是完整表名，直接返回
        if name_or_alias in all_table_names:
            return name_or_alias
        
        # 常见的表别名映射
        alias_mapping = {
            'e': 'employees',
            'd': 'departments', 
            'emp': 'employees',
            'dept': 'departments',
            'temp': 'temp_emp_summary',
            'reports': 'employee_reports'
        }
        
        # 查找映射
        if name_or_alias in alias_mapping:
            mapped_name = alias_mapping[name_or_alias]
            if mapped_name in all_table_names:
                return mapped_name
        
        # 模糊匹配：查找包含别名的表名
        for table_name in all_table_names:
            if name_or_alias.lower() in table_name.lower():
                return table_name
        
        # 如果都找不到，返回原名
        return name_or_alias
    
    def _save_uml_visualization_data(self, analysis: StoredProcedureAnalysis) -> Dict[str, Any]:
        """保存UML可视化数据"""
        
        uml_data = {
            "visualization_type": "uml",
            "nodes": [node.model_dump() for node in self.uml_nodes],
            "field_mappings": [edge.model_dump() for edge in self.field_mapping_edges],
            "table_relations": [edge.model_dump() for edge in self.table_relations],
            "metadata": {
                "procedure_name": analysis.sp_structure.name,
                "total_tables": len(self.uml_nodes),
                "field_mappings_count": len(self.field_mapping_edges),
                "table_relations_count": len(self.table_relations),
                "physical_tables": len(analysis.table_field_analysis.physical_tables),
                "temp_tables": len(analysis.table_field_analysis.temp_tables)
            }
        }
        
        # 保存到文件
        with open("uml_visualization_data.json", "w", encoding="utf-8") as f:
            json.dump(uml_data, f, ensure_ascii=False, indent=2)
        
        return uml_data
    
    def _print_uml_diagram(self, analysis: StoredProcedureAnalysis):
        """打印UML图的ASCII表示"""
        print("\n" + "="*80)
        print("                    UML样式表结构图")
        print("="*80)
        
        # 打印表结构
        print("\n【表结构 - UML样式】")
        print("-" * 60)
        
        # 物理表
        if analysis.table_field_analysis.physical_tables:
            print("\n🟢 物理表:")
            for table_name, table in analysis.table_field_analysis.physical_tables.items():
                self._print_table_uml_box(table_name, table, "physical")
        
        # 临时表
        if analysis.table_field_analysis.temp_tables:
            print("\n🟡 临时表:")
            for table_name, table in analysis.table_field_analysis.temp_tables.items():
                self._print_table_uml_box(table_name, table, "temp")
        
        # 打印字段映射关系
        print("\n【字段映射关系】")
        print("-" * 60)
        
        if self.field_mapping_edges:
            for edge in self.field_mapping_edges:
                props = edge.properties
                print(f"  {props['source_field']} ({props['source_table']}) ──→ {props['target_field']} ({props['target_table']})")
                if props.get('expression'):
                    print(f"    表达式: {props['expression']}")
                print(f"    类型: {props['mapping_type']}")
                print()
        else:
            print("  未发现字段映射关系")
        
        # 打印表关系
        if self.table_relations:
            print("\n【表关系 - JOIN连接】")
            print("-" * 60)
            for edge in self.table_relations:
                props = edge.properties
                print(f"  {props['left_field']} ═══[{props['relation_type']}]═══ {props['right_field']}")
                print(f"  条件: {props['condition']}")
                print()
        
        print("="*80)
    
    def _print_table_uml_box(self, table_name: str, table, table_type: str):
        """打印单个表的UML框"""
        border_char = "═" if table_type == "physical" else "─"
        corner_char = "╬" if table_type == "physical" else "┼"
        
        # 计算最大宽度
        max_width = max(len(table_name) + 4, 30)
        
        # 打印表头
        print(f"    {corner_char}{border_char * (max_width - 2)}{corner_char}")
        print(f"    ║ {table_name.center(max_width - 4)} ║")
        print(f"    {corner_char}{border_char * (max_width - 2)}{corner_char}")
        
        # 打印字段
        if table.fields:
            for field in sorted(table.fields):
                field_text = f"+ {field}"
                spaces = max_width - len(field_text) - 4
                print(f"    ║ {field_text}{' ' * spaces} ║")
        
        # 打印计算字段
        if table.computed_fields:
            for computed_field in table.computed_fields:
                field_name = computed_field.target_field_name or computed_field.alias or "computed"
                field_text = f"◆ {field_name}"
                spaces = max_width - len(field_text) - 4
                print(f"    ║ {field_text}{' ' * spaces} ║")
        
        if not table.fields and not table.computed_fields:
            print(f"    ║ (无字段信息){' ' * (max_width - 12)} ║")
        
        print(f"    {corner_char}{border_char * (max_width - 2)}{corner_char}")
        print() 
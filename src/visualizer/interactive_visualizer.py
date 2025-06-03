#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import json
import networkx as nx
from typing import Dict, List, Any
from models.data_models import (
    StoredProcedureAnalysis, VisualizationNode, VisualizationEdge
)

class InteractiveVisualizer:
    """交互式可视化器 - 生成可视化数据和简单的图形输出"""
    
    def __init__(self):
        self.graph = nx.DiGraph()
        self.nodes = []
        self.edges = []
    
    def create_interactive_visualization(self, analysis: StoredProcedureAnalysis):
        """创建可视化数据"""
        self._build_graph(analysis)
        self._save_visualization_data(analysis)
        self._print_ascii_graph(analysis)
    
    def _build_graph(self, analysis: StoredProcedureAnalysis):
        """构建可视化图"""
        self.graph.clear()
        self.nodes = []
        self.edges = []
        
        # 添加表节点
        self._add_table_nodes(analysis)
        
        # 添加参数节点
        self._add_parameter_nodes(analysis)
        
        # 添加数据流边
        self._add_data_flow_edges(analysis)
        
        # 添加连接条件边
        self._add_join_edges(analysis)
    
    def _add_table_nodes(self, analysis: StoredProcedureAnalysis):
        """添加表节点"""
        # 物理表
        for table_name, table in analysis.table_field_analysis.physical_tables.items():
            node = VisualizationNode(
                id=f"table_{table_name}",
                label=table_name,
                type="physical_table",
                properties={
                    "fields": table.fields,
                    "sql_ids": table.source_sql_ids,
                    "color": "green"  # 绿色表示物理表
                }
            )
            self.nodes.append(node)
            self.graph.add_node(node.id, **node.properties)
        
        # 临时表
        for table_name, table in analysis.table_field_analysis.temp_tables.items():
            node = VisualizationNode(
                id=f"table_{table_name}",
                label=table_name,
                type="temp_table",
                properties={
                    "fields": table.fields,
                    "sql_ids": table.source_sql_ids,
                    "color": "orange"  # 橙色表示临时表
                }
            )
            self.nodes.append(node)
            self.graph.add_node(node.id, **node.properties)
    
    def _add_parameter_nodes(self, analysis: StoredProcedureAnalysis):
        """添加参数节点"""
        for param in analysis.parameters:
            node = VisualizationNode(
                id=f"param_{param.name}",
                label=param.name,
                type="parameter",
                properties={
                    "data_type": param.data_type,
                    "direction": param.direction,
                    "used_in": param.used_in_statements,
                    "color": "blue"  # 蓝色表示参数
                }
            )
            self.nodes.append(node)
            self.graph.add_node(node.id, **node.properties)
    
    def _add_data_flow_edges(self, analysis: StoredProcedureAnalysis):
        """添加数据流边"""
        for stmt in analysis.sp_structure.sql_statements:
            # 从源表到目标表的数据流
            for source_table in stmt.source_tables:
                for target_table in stmt.target_tables:
                    edge = VisualizationEdge(
                        source=f"table_{source_table}",
                        target=f"table_{target_table}",
                        label=f"SQL-{stmt.statement_id}",
                        type="data_flow",
                        properties={
                            "statement_type": stmt.statement_type.value,
                            "raw_sql": stmt.raw_sql
                        }
                    )
                    self.edges.append(edge)
                    self.graph.add_edge(edge.source, edge.target, **edge.properties)
            
            # 参数到表的关联
            for param_name in stmt.parameters_used:
                for table_name in stmt.source_tables + stmt.target_tables:
                    edge = VisualizationEdge(
                        source=f"param_{param_name}",
                        target=f"table_{table_name}",
                        label="uses",
                        type="parameter_usage",
                        properties={"statement_id": stmt.statement_id}
                    )
                    self.edges.append(edge)
                    self.graph.add_edge(edge.source, edge.target, **edge.properties)
    
    def _add_join_edges(self, analysis: StoredProcedureAnalysis):
        """添加JOIN连接边"""
        for join_cond in analysis.conditions_and_logic.join_conditions:
            edge = VisualizationEdge(
                source=f"table_{join_cond.left_table}",
                target=f"table_{join_cond.right_table}",
                label=f"{join_cond.join_type} JOIN",
                type="join_condition",
                properties={
                    "left_field": join_cond.left_field,
                    "right_field": join_cond.right_field,
                    "condition": join_cond.condition_text
                }
            )
            self.edges.append(edge)
            self.graph.add_edge(edge.source, edge.target, **edge.properties)
    
    def _save_visualization_data(self, analysis: StoredProcedureAnalysis):
        """保存可视化数据"""
        viz_data = {
            "nodes": [node.dict() for node in self.nodes],
            "edges": [edge.dict() for edge in self.edges],
            "metadata": {
                "procedure_name": analysis.sp_structure.name,
                "parameter_count": len(analysis.parameters),
                "statement_count": len(analysis.sp_structure.sql_statements),
                "table_count": len(analysis.table_field_analysis.physical_tables) + 
                             len(analysis.table_field_analysis.temp_tables)
            }
        }
        
        with open("visualization_data.json", "w", encoding="utf-8") as f:
            json.dump(viz_data, f, ensure_ascii=False, indent=2)
    
    def _print_ascii_graph(self, analysis: StoredProcedureAnalysis):
        """打印ASCII图形"""
        print("\n" + "="*60)
        print("           数据流向图 (ASCII 表示)")
        print("="*60)
        
        print("\n【节点】")
        print("-" * 40)
        
        # 打印参数节点
        if analysis.parameters:
            print("参数 (蓝色):")
            for param in analysis.parameters:
                print(f"  🔵 {param.name} ({param.direction} {param.data_type})")
        
        # 打印物理表节点
        if analysis.table_field_analysis.physical_tables:
            print("\n物理表 (绿色):")
            for table_name, table in analysis.table_field_analysis.physical_tables.items():
                fields_str = ", ".join(sorted(table.fields)) if table.fields else "未知字段"
                print(f"  🟢 {table_name}")
                print(f"     字段: {fields_str}")
        
        # 打印临时表节点
        if analysis.table_field_analysis.temp_tables:
            print("\n临时表 (橙色):")
            for table_name, table in analysis.table_field_analysis.temp_tables.items():
                fields_str = ", ".join(sorted(table.fields)) if table.fields else "未知字段"
                print(f"  🟠 {table_name}")
                print(f"     字段: {fields_str}")
        
        print("\n【边/关系】")
        print("-" * 40)
        
        # 打印数据流
        print("数据流向:")
        for stmt in analysis.sp_structure.sql_statements:
            for source_table in stmt.source_tables:
                for target_table in stmt.target_tables:
                    print(f"  {source_table} ──[{stmt.statement_type.value}]──> {target_table}")
        
        # 打印JOIN关系
        if analysis.conditions_and_logic.join_conditions:
            print("\nJOIN连接:")
            for join_cond in analysis.conditions_and_logic.join_conditions:
                print(f"  {join_cond.left_table}.{join_cond.left_field} ═══[{join_cond.join_type}]═══ {join_cond.right_table}.{join_cond.right_field}")
        
        print("\n" + "="*60)
    
    def start_web_interface(self, analysis: StoredProcedureAnalysis = None):
        """简化版界面，只打印信息"""
        print("\n📊 可视化完成！")
        print("💾 数据已保存到 visualization_data.json")
        print("📋 ASCII图形已在上方显示")
        print("\n💡 提示: 可以使用其他工具（如Gephi、Cytoscape等）导入 visualization_data.json 进行高级可视化") 
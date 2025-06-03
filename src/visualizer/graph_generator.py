#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import networkx as nx
import matplotlib.pyplot as plt
from typing import Dict, Any
import pygraphviz as pgv

class GraphGenerator:
    def __init__(self):
        self.graph = nx.DiGraph()

    def generate(self, metadata: Dict[str, Any]):
        """
        生成数据流向图和表关系图
        """
        self._create_table_relationship_graph(metadata)
        self._create_data_flow_graph(metadata)
        self._save_graphs()

    def _create_table_relationship_graph(self, metadata: Dict[str, Any]):
        """
        创建表关系图
        """
        for table_name, table_info in metadata.items():
            self.graph.add_node(table_name, type='table')
            
            # 添加外键关系
            for fk in table_info.get('foreign_keys', []):
                ref_table = fk['references_table']
                self.graph.add_edge(
                    table_name,
                    ref_table,
                    relationship='foreign_key',
                    label=f"{fk['column']} -> {fk['references_column']}"
                )

    def _create_data_flow_graph(self, metadata: Dict[str, Any]):
        """
        创建数据流向图
        """
        # 这里需要根据SQL语句分析数据流向
        # 目前是示例实现
        pass

    def _save_graphs(self):
        """
        保存生成的图表
        """
        # 使用pygraphviz生成更美观的图
        A = nx.nx_agraph.to_agraph(self.graph)
        A.layout(prog='dot')
        
        # 保存表关系图
        A.draw('table_relationships.png')
        
        # 保存数据流向图
        # 这里需要根据实际的数据流向分析结果来生成
        pass

    def _draw_graph(self, graph, filename):
        """
        绘制并保存图表
        """
        plt.figure(figsize=(12, 8))
        pos = nx.spring_layout(graph)
        nx.draw(
            graph,
            pos,
            with_labels=True,
            node_color='lightblue',
            node_size=2000,
            font_size=10,
            font_weight='bold'
        )
        plt.savefig(filename)
        plt.close() 
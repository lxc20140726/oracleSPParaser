#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import pytest
from unittest.mock import Mock, patch, MagicMock
import networkx as nx
from src.visualizer.graph_generator import GraphGenerator


class TestGraphGenerator:
    """GraphGenerator测试类"""
    
    def setup_method(self):
        """测试前置方法"""
        self.generator = GraphGenerator()
        
    def test_init(self):
        """测试初始化"""
        assert isinstance(self.generator.graph, nx.DiGraph)
        assert len(self.generator.graph.nodes) == 0
        assert len(self.generator.graph.edges) == 0
        
    @patch.object(GraphGenerator, '_save_graphs')
    @patch.object(GraphGenerator, '_create_data_flow_graph')
    @patch.object(GraphGenerator, '_create_table_relationship_graph')
    def test_generate(self, mock_table_graph, mock_data_flow, mock_save):
        """测试generate方法"""
        metadata = {
            'table1': {
                'columns': [{'name': 'id', 'type': 'NUMBER'}],
                'foreign_keys': []
            }
        }
        
        self.generator.generate(metadata)
        
        mock_table_graph.assert_called_once_with(metadata)
        mock_data_flow.assert_called_once_with(metadata)
        mock_save.assert_called_once()
        
    def test_create_table_relationship_graph_simple(self):
        """测试创建简单表关系图"""
        metadata = {
            'users': {
                'columns': [
                    {'name': 'id', 'type': 'NUMBER'},
                    {'name': 'name', 'type': 'VARCHAR2'}
                ],
                'foreign_keys': []
            },
            'orders': {
                'columns': [
                    {'name': 'id', 'type': 'NUMBER'},
                    {'name': 'user_id', 'type': 'NUMBER'}
                ],
                'foreign_keys': [
                    {
                        'column': 'user_id',
                        'references_table': 'users',
                        'references_column': 'id'
                    }
                ]
            }
        }
        
        self.generator._create_table_relationship_graph(metadata)
        
        # 验证节点
        assert 'users' in self.generator.graph.nodes
        assert 'orders' in self.generator.graph.nodes
        assert self.generator.graph.nodes['users']['type'] == 'table'
        assert self.generator.graph.nodes['orders']['type'] == 'table'
        
        # 验证边
        assert self.generator.graph.has_edge('orders', 'users')
        edge_data = self.generator.graph.get_edge_data('orders', 'users')
        assert edge_data['relationship'] == 'foreign_key'
        assert edge_data['label'] == 'user_id -> id'
        
    def test_create_table_relationship_graph_empty(self):
        """测试创建空元数据的表关系图"""
        metadata = {}
        
        self.generator._create_table_relationship_graph(metadata)
        
        assert len(self.generator.graph.nodes) == 0
        assert len(self.generator.graph.edges) == 0
        
    def test_create_table_relationship_graph_no_foreign_keys(self):
        """测试创建没有外键的表关系图"""
        metadata = {
            'table1': {
                'columns': [{'name': 'id', 'type': 'NUMBER'}],
                'foreign_keys': []
            },
            'table2': {
                'columns': [{'name': 'name', 'type': 'VARCHAR2'}],
                'foreign_keys': []
            }
        }
        
        self.generator._create_table_relationship_graph(metadata)
        
        # 应该有节点但没有边
        assert len(self.generator.graph.nodes) == 2
        assert len(self.generator.graph.edges) == 0
        assert 'table1' in self.generator.graph.nodes
        assert 'table2' in self.generator.graph.nodes
        
    def test_create_table_relationship_graph_multiple_foreign_keys(self):
        """测试创建多个外键的表关系图"""
        metadata = {
            'users': {
                'columns': [{'name': 'id', 'type': 'NUMBER'}],
                'foreign_keys': []
            },
            'departments': {
                'columns': [{'name': 'id', 'type': 'NUMBER'}],
                'foreign_keys': []
            },
            'employees': {
                'columns': [
                    {'name': 'id', 'type': 'NUMBER'},
                    {'name': 'user_id', 'type': 'NUMBER'},
                    {'name': 'dept_id', 'type': 'NUMBER'}
                ],
                'foreign_keys': [
                    {
                        'column': 'user_id',
                        'references_table': 'users',
                        'references_column': 'id'
                    },
                    {
                        'column': 'dept_id',
                        'references_table': 'departments',
                        'references_column': 'id'
                    }
                ]
            }
        }
        
        self.generator._create_table_relationship_graph(metadata)
        
        # 验证节点
        assert len(self.generator.graph.nodes) == 3
        
        # 验证边
        assert self.generator.graph.has_edge('employees', 'users')
        assert self.generator.graph.has_edge('employees', 'departments')
        assert len(self.generator.graph.edges) == 2
        
    def test_create_table_relationship_graph_missing_foreign_keys(self):
        """测试缺少foreign_keys字段的表元数据"""
        metadata = {
            'table1': {
                'columns': [{'name': 'id', 'type': 'NUMBER'}]
                # 缺少foreign_keys字段
            }
        }
        
        self.generator._create_table_relationship_graph(metadata)
        
        # 应该正常处理，使用默认空列表
        assert len(self.generator.graph.nodes) == 1
        assert len(self.generator.graph.edges) == 0
        
    def test_create_data_flow_graph(self):
        """测试创建数据流向图"""
        metadata = {
            'table1': {'columns': []},
            'table2': {'columns': []}
        }
        
        # 由于该方法目前为空实现，只测试调用不出错
        self.generator._create_data_flow_graph(metadata)
        
        # 验证方法可以正常调用
        assert True
        
    @patch('networkx.nx_agraph.to_agraph')
    def test_save_graphs(self, mock_to_agraph):
        """测试保存图表"""
        mock_agraph = MagicMock()
        mock_to_agraph.return_value = mock_agraph
        
        # 添加一些节点以触发保存逻辑
        self.generator.graph.add_node('test_table', type='table')
        
        # 模拟pygraphviz可用
        with patch('src.visualizer.graph_generator.pgv', True):
            self.generator._save_graphs()
        
        # 只在有节点的情况下才会调用to_agraph
        if len(self.generator.graph.nodes) > 0:
            mock_to_agraph.assert_called_once_with(self.generator.graph)
            mock_agraph.layout.assert_called_once_with(prog='dot')
            mock_agraph.draw.assert_called_once_with('table_relationships.png')
        
    @patch('matplotlib.pyplot.savefig')
    @patch('matplotlib.pyplot.close')
    @patch('matplotlib.pyplot.figure')
    @patch('networkx.spring_layout')
    @patch('networkx.draw')
    def test_draw_graph(self, mock_draw, mock_layout, mock_figure, mock_close, mock_savefig):
        """测试绘制图表"""
        mock_layout.return_value = {'node1': (0, 0), 'node2': (1, 1)}
        
        # 创建测试图
        test_graph = nx.DiGraph()
        test_graph.add_node('node1')
        test_graph.add_node('node2')
        test_graph.add_edge('node1', 'node2')
        
        self.generator._draw_graph(test_graph, 'test_output.png')
        
        mock_figure.assert_called_once_with(figsize=(12, 8))
        mock_layout.assert_called_once_with(test_graph)
        mock_draw.assert_called_once()
        mock_savefig.assert_called_once_with('test_output.png')
        mock_close.assert_called_once()
        
    def test_draw_graph_parameters(self):
        """测试绘制图表的参数"""
        with patch('matplotlib.pyplot.figure') as mock_figure, \
             patch('networkx.spring_layout') as mock_layout, \
             patch('networkx.draw') as mock_draw, \
             patch('matplotlib.pyplot.savefig'), \
             patch('matplotlib.pyplot.close'):
            
            mock_layout.return_value = {}
            
            test_graph = nx.DiGraph()
            test_graph.add_node('test_node')
            
            self.generator._draw_graph(test_graph, 'test.png')
            
            # 验证draw调用的参数
            call_args = mock_draw.call_args
            kwargs = call_args[1]
            
            assert kwargs['with_labels'] is True
            assert kwargs['node_color'] == 'lightblue'
            assert kwargs['node_size'] == 2000
            assert kwargs['font_size'] == 10
            assert kwargs['font_weight'] == 'bold'
            
    def test_complete_workflow(self):
        """测试完整的工作流程"""
        metadata = {
            'users': {
                'columns': [
                    {'name': 'id', 'type': 'NUMBER'},
                    {'name': 'email', 'type': 'VARCHAR2'}
                ],
                'foreign_keys': []
            },
            'posts': {
                'columns': [
                    {'name': 'id', 'type': 'NUMBER'},
                    {'name': 'user_id', 'type': 'NUMBER'},
                    {'name': 'title', 'type': 'VARCHAR2'}
                ],
                'foreign_keys': [
                    {
                        'column': 'user_id',
                        'references_table': 'users',
                        'references_column': 'id'
                    }
                ]
            }
        }
        
        with patch.object(self.generator, '_save_graphs') as mock_save:
            self.generator.generate(metadata)
            
            # 验证图的结构
            assert len(self.generator.graph.nodes) == 2
            assert len(self.generator.graph.edges) == 1
            
            # 验证节点属性
            assert self.generator.graph.nodes['users']['type'] == 'table'
            assert self.generator.graph.nodes['posts']['type'] == 'table'
            
            # 验证边属性
            edge_data = self.generator.graph.get_edge_data('posts', 'users')
            assert edge_data['relationship'] == 'foreign_key'
            assert 'user_id -> id' in edge_data['label']
            
            mock_save.assert_called_once()
            
    def test_complex_relationship_chain(self):
        """测试复杂的关系链"""
        metadata = {
            'countries': {
                'columns': [{'name': 'id', 'type': 'NUMBER'}],
                'foreign_keys': []
            },
            'states': {
                'columns': [
                    {'name': 'id', 'type': 'NUMBER'},
                    {'name': 'country_id', 'type': 'NUMBER'}
                ],
                'foreign_keys': [
                    {
                        'column': 'country_id',
                        'references_table': 'countries',
                        'references_column': 'id'
                    }
                ]
            },
            'cities': {
                'columns': [
                    {'name': 'id', 'type': 'NUMBER'},
                    {'name': 'state_id', 'type': 'NUMBER'}
                ],
                'foreign_keys': [
                    {
                        'column': 'state_id',
                        'references_table': 'states',
                        'references_column': 'id'
                    }
                ]
            }
        }
        
        self.generator._create_table_relationship_graph(metadata)
        
        # 验证链式关系
        assert self.generator.graph.has_edge('states', 'countries')
        assert self.generator.graph.has_edge('cities', 'states')
        
        # 验证图的连通性
        assert len(self.generator.graph.nodes) == 3
        assert len(self.generator.graph.edges) == 2 
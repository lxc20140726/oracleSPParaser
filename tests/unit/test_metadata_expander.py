#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import pytest
from unittest.mock import Mock, patch, MagicMock
from src.analyzer.metadata_expander import MetadataExpander


class TestMetadataExpander:
    """MetadataExpander测试类"""
    
    def setup_method(self):
        """测试前置方法"""
        self.mock_connection = Mock()
        self.mock_cursor = Mock()
        self.mock_connection.cursor.return_value = self.mock_cursor
        
    def test_init_without_connection(self):
        """测试初始化时没有数据库连接"""
        expander = MetadataExpander()
        assert expander.db_connection is None
        assert expander.expanded_metadata == {}
        
    def test_init_with_connection(self):
        """测试初始化时有数据库连接"""
        expander = MetadataExpander(self.mock_connection)
        assert expander.db_connection == self.mock_connection
        assert expander.expanded_metadata == {}
        
    def test_expand_with_no_connection(self):
        """测试没有数据库连接时的expand方法"""
        expander = MetadataExpander()
        table_analysis = {
            'physical_tables': ['table1', 'table2']
        }
        
        result = expander.expand(table_analysis)
        assert result == {}
        
    def test_expand_with_connection(self):
        """测试有数据库连接时的expand方法"""
        expander = MetadataExpander(self.mock_connection)
        
        # 模拟cursor.execute的返回值
        column_data = [
            ('ID', 'NUMBER', 10, 'N'),
            ('NAME', 'VARCHAR2', 50, 'Y')
        ]
        pk_data = [('ID',)]
        fk_data = [
            ('FK_CONSTRAINT', 'R_CONSTRAINT', 'PARENT_TABLE', 'CHILD_COL', 'PARENT_COL')
        ]
        
        def mock_execute_side_effect(query, params):
            if 'all_tab_columns' in query:
                self.mock_cursor.__iter__ = Mock(return_value=iter(column_data))
            elif 'all_constraints' in query and 'P' in query:
                self.mock_cursor.__iter__ = Mock(return_value=iter(pk_data))
            elif 'all_constraints' in query and 'R' in query:
                self.mock_cursor.__iter__ = Mock(return_value=iter(fk_data))
        
        self.mock_cursor.execute.side_effect = mock_execute_side_effect
        
        table_analysis = {
            'physical_tables': ['TEST_TABLE']
        }
        
        result = expander.expand(table_analysis)
        
        # 验证结果
        assert 'TEST_TABLE' in result
        assert result['TEST_TABLE']['columns'] == [
            {'name': 'ID', 'type': 'NUMBER', 'length': 10, 'nullable': 'N'},
            {'name': 'NAME', 'type': 'VARCHAR2', 'length': 50, 'nullable': 'Y'}
        ]
        assert result['TEST_TABLE']['primary_keys'] == ['ID']
        assert len(result['TEST_TABLE']['foreign_keys']) == 1
        
    def test_expand_table_metadata_without_connection(self):
        """测试没有数据库连接时的_expand_table_metadata方法"""
        expander = MetadataExpander()
        expander._expand_table_metadata('TEST_TABLE')
        
        # 应该没有添加任何元数据
        assert expander.expanded_metadata == {}
        
    @patch('src.analyzer.metadata_expander.cx_Oracle')
    def test_expand_table_metadata_with_db_error(self, mock_cx_oracle):
        """测试数据库错误时的_expand_table_metadata方法"""
        mock_cx_oracle.Error = Exception  # 模拟cx_Oracle.Error
        
        expander = MetadataExpander(self.mock_connection)
        
        # 模拟数据库错误
        self.mock_cursor.execute.side_effect = mock_cx_oracle.Error("Database error")
        
        with patch('builtins.print') as mock_print:
            expander._expand_table_metadata('TEST_TABLE')
            mock_print.assert_called_once()
            assert 'Error expanding metadata' in mock_print.call_args[0][0]
            
    def test_get_foreign_keys_without_connection(self):
        """测试没有数据库连接时的_get_foreign_keys方法"""
        expander = MetadataExpander()
        result = expander._get_foreign_keys('TEST_TABLE')
        
        assert result == []
        
    def test_get_foreign_keys_with_connection(self):
        """测试有数据库连接时的_get_foreign_keys方法"""
        expander = MetadataExpander(self.mock_connection)
        
        fk_data = [
            ('FK_CONSTRAINT', 'R_CONSTRAINT', 'PARENT_TABLE', 'CHILD_COL', 'PARENT_COL')
        ]
        self.mock_cursor.__iter__ = Mock(return_value=iter(fk_data))
        
        result = expander._get_foreign_keys('TEST_TABLE')
        
        assert len(result) == 1
        assert result[0] == {
            'constraint_name': 'FK_CONSTRAINT',
            'column': 'CHILD_COL',
            'references_table': 'PARENT_TABLE',
            'references_column': 'PARENT_COL'
        }
        
    @patch('src.analyzer.metadata_expander.cx_Oracle')
    def test_get_foreign_keys_with_db_error(self, mock_cx_oracle):
        """测试数据库错误时的_get_foreign_keys方法"""
        mock_cx_oracle.Error = Exception  # 模拟cx_Oracle.Error
        
        expander = MetadataExpander(self.mock_connection)
        
        # 模拟数据库错误
        self.mock_cursor.execute.side_effect = mock_cx_oracle.Error("Database error")
        
        with patch('builtins.print') as mock_print:
            result = expander._get_foreign_keys('TEST_TABLE')
            assert result == []
            mock_print.assert_called_once()
            assert 'Error getting foreign keys' in mock_print.call_args[0][0]
            
    def test_expand_multiple_tables(self):
        """测试扩展多个表的元数据"""
        expander = MetadataExpander(self.mock_connection)
        
        # 模拟不同表的数据
        def mock_execute_side_effect(query, params):
            table_name = params[0]
            if table_name == 'TABLE1':
                if 'all_tab_columns' in query:
                    self.mock_cursor.__iter__ = Mock(return_value=iter([
                        ('ID', 'NUMBER', 10, 'N')
                    ]))
                elif 'all_constraints' in query and 'P' in query:
                    self.mock_cursor.__iter__ = Mock(return_value=iter([('ID',)]))
                elif 'all_constraints' in query and 'R' in query:
                    self.mock_cursor.__iter__ = Mock(return_value=iter([]))
            elif table_name == 'TABLE2':
                if 'all_tab_columns' in query:
                    self.mock_cursor.__iter__ = Mock(return_value=iter([
                        ('NAME', 'VARCHAR2', 50, 'Y')
                    ]))
                elif 'all_constraints' in query and 'P' in query:
                    self.mock_cursor.__iter__ = Mock(return_value=iter([]))
                elif 'all_constraints' in query and 'R' in query:
                    self.mock_cursor.__iter__ = Mock(return_value=iter([]))
        
        self.mock_cursor.execute.side_effect = mock_execute_side_effect
        
        table_analysis = {
            'physical_tables': ['TABLE1', 'TABLE2']
        }
        
        result = expander.expand(table_analysis)
        
        assert 'TABLE1' in result
        assert 'TABLE2' in result
        assert len(result) == 2 
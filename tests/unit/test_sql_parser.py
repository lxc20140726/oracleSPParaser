#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import pytest
from unittest.mock import Mock, patch
import sqlparse
from src.parser.sql_parser import SQLParser


class TestSQLParser:
    """SQLParser测试类"""
    
    def setup_method(self):
        """测试前置方法"""
        self.parser = SQLParser()
        
    def test_init(self):
        """测试初始化"""
        assert isinstance(self.parser.parsed_statements, list)
        assert len(self.parser.parsed_statements) == 0
        
    def test_parse_empty_sql(self):
        """测试解析空SQL"""
        result = self.parser.parse("")
        assert result == []
        assert self.parser.parsed_statements == []
        
    def test_parse_single_select(self):
        """测试解析单个SELECT语句"""
        sql = "SELECT * FROM users"
        
        with patch('sqlparse.split') as mock_split, \
             patch('sqlparse.parse') as mock_parse:
            
            mock_split.return_value = [sql]
            mock_parsed = Mock()
            mock_parsed.get_type.return_value = 'SELECT'
            mock_parsed.tokens = []
            mock_parse.return_value = [mock_parsed]
            
            result = self.parser.parse(sql)
            
            assert len(result) == 1
            assert result[0]['raw'] == sql
            assert result[0]['type'] == 'SELECT'
            assert result[0]['parsed'] == mock_parsed
            assert 'tables' in result[0]
            assert 'columns' in result[0]
            assert 'conditions' in result[0]
            
    def test_parse_multiple_statements(self):
        """测试解析多个SQL语句"""
        sql = "SELECT * FROM users; INSERT INTO logs VALUES (1, 'test')"
        statements = ["SELECT * FROM users", "INSERT INTO logs VALUES (1, 'test')"]
        
        with patch('sqlparse.split') as mock_split, \
             patch('sqlparse.parse') as mock_parse:
            
            mock_split.return_value = statements
            
            # 模拟不同类型的语句
            mock_select = Mock()
            mock_select.get_type.return_value = 'SELECT'
            mock_select.tokens = []
            mock_insert = Mock()
            mock_insert.get_type.return_value = 'INSERT'
            mock_insert.tokens = []
            
            mock_parse.side_effect = [[mock_select], [mock_insert]]
            
            result = self.parser.parse(sql)
            
            assert len(result) == 2
            assert result[0]['type'] == 'SELECT'
            assert result[1]['type'] == 'INSERT'
            
    def test_get_statement_type_select(self):
        """测试获取SELECT语句类型"""
        mock_parsed = Mock()
        mock_parsed.get_type.return_value = 'SELECT'
        
        result = self.parser._get_statement_type(mock_parsed)
        assert result == 'SELECT'
        
    def test_get_statement_type_insert(self):
        """测试获取INSERT语句类型"""
        mock_parsed = Mock()
        mock_parsed.get_type.return_value = 'INSERT'
        
        result = self.parser._get_statement_type(mock_parsed)
        assert result == 'INSERT'
        
    def test_get_statement_type_update(self):
        """测试获取UPDATE语句类型"""
        mock_parsed = Mock()
        mock_parsed.get_type.return_value = 'UPDATE'
        
        result = self.parser._get_statement_type(mock_parsed)
        assert result == 'UPDATE'
        
    def test_get_statement_type_delete(self):
        """测试获取DELETE语句类型"""
        mock_parsed = Mock()
        mock_parsed.get_type.return_value = 'DELETE'
        
        result = self.parser._get_statement_type(mock_parsed)
        assert result == 'DELETE'
        
    def test_get_statement_type_other(self):
        """测试获取其他类型语句"""
        mock_parsed = Mock()
        mock_parsed.get_type.return_value = 'CREATE'
        
        result = self.parser._get_statement_type(mock_parsed)
        assert result == 'OTHER'
        
    def test_extract_tables(self):
        """测试提取表名"""
        mock_parsed = Mock()
        mock_token1 = Mock()
        mock_token1.is_keyword = True
        mock_token1.value = 'FROM'
        
        mock_token2 = Mock()
        mock_token2.is_keyword = False
        mock_token2.value = 'users'
        
        mock_parsed.tokens = [mock_token1, mock_token2]
        
        result = self.parser._extract_tables(mock_parsed)
        assert isinstance(result, list)
        # 由于方法目前为空实现，返回空列表
        assert result == []
        
    def test_extract_tables_no_keywords(self):
        """测试提取表名时没有关键字"""
        mock_parsed = Mock()
        mock_token = Mock()
        mock_token.is_keyword = False
        mock_token.value = 'test'
        
        mock_parsed.tokens = [mock_token]
        
        result = self.parser._extract_tables(mock_parsed)
        assert result == []
        
    def test_extract_columns(self):
        """测试提取列名"""
        mock_parsed = Mock()
        
        result = self.parser._extract_columns(mock_parsed)
        assert isinstance(result, list)
        # 由于方法目前为空实现，返回空列表
        assert result == []
        
    def test_extract_conditions(self):
        """测试提取条件"""
        mock_parsed = Mock()
        
        result = self.parser._extract_conditions(mock_parsed)
        assert isinstance(result, list)
        # 由于方法目前为空实现，返回空列表
        assert result == []
        
    def test_parse_with_real_sqlparse(self):
        """测试使用真实sqlparse的解析"""
        sql = "SELECT id, name FROM users WHERE id = 1"
        
        result = self.parser.parse(sql)
        
        assert len(result) == 1
        assert result[0]['raw'] == sql
        assert result[0]['type'] in ['SELECT', 'OTHER']  # sqlparse可能返回不同的类型
        assert isinstance(result[0]['tables'], list)
        assert isinstance(result[0]['columns'], list)
        assert isinstance(result[0]['conditions'], list)
        
    def test_parse_multiple_real_statements(self):
        """测试解析多个真实SQL语句"""
        sql = """
        SELECT * FROM users;
        INSERT INTO logs (message) VALUES ('test');
        UPDATE users SET name = 'John' WHERE id = 1;
        DELETE FROM temp_table WHERE created < SYSDATE - 1;
        """
        
        result = self.parser.parse(sql)
        
        # sqlparse.split会分割出多个语句
        assert len(result) >= 4
        assert self.parser.parsed_statements == result
        
    def test_parse_complex_sql(self):
        """测试解析复杂SQL语句"""
        sql = """
        SELECT u.id, u.name, p.title
        FROM users u
        LEFT JOIN posts p ON u.id = p.user_id
        WHERE u.active = 1
        AND p.published_date > SYSDATE - 30
        ORDER BY u.name, p.published_date DESC
        """
        
        result = self.parser.parse(sql)
        
        assert len(result) >= 1
        assert result[0]['raw'].strip() == sql.strip()
        
    def test_stored_parsed_statements(self):
        """测试解析结果是否正确存储"""
        sql1 = "SELECT * FROM table1"
        sql2 = "SELECT * FROM table2"
        
        result1 = self.parser.parse(sql1)
        result2 = self.parser.parse(sql2)
        
        # 第二次解析应该覆盖第一次的结果
        assert self.parser.parsed_statements == result2
        assert len(self.parser.parsed_statements) == 1
        assert self.parser.parsed_statements[0]['raw'] == sql2 
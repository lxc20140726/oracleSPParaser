#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import pytest
import os
import json
import tempfile
import hashlib
from unittest.mock import Mock, patch, mock_open
from pathlib import Path
from datetime import datetime
from src.utils.helpers import (
    ensure_dir, read_file, write_file, read_json, write_json,
    get_file_hash, format_file_size, get_timestamp, sanitize_filename,
    flatten_dict, chunk_list, safe_get, merge_dicts,
    is_valid_sql_identifier, normalize_sql_name
)


class TestHelpers:
    """辅助函数测试类"""
    
    def test_ensure_dir_new_directory(self):
        """测试创建新目录"""
        with tempfile.TemporaryDirectory() as temp_dir:
            new_dir = Path(temp_dir) / 'new_directory' / 'sub_dir'
            
            result = ensure_dir(new_dir)
            
            assert result == new_dir
            assert new_dir.exists()
            assert new_dir.is_dir()
            
    def test_ensure_dir_existing_directory(self):
        """测试确保已存在的目录"""
        with tempfile.TemporaryDirectory() as temp_dir:
            existing_dir = Path(temp_dir)
            
            result = ensure_dir(existing_dir)
            
            assert result == existing_dir
            assert existing_dir.exists()
            
    def test_ensure_dir_string_path(self):
        """测试使用字符串路径"""
        with tempfile.TemporaryDirectory() as temp_dir:
            new_dir = os.path.join(temp_dir, 'string_dir')
            
            result = ensure_dir(new_dir)
            
            assert result == Path(new_dir)
            assert Path(new_dir).exists()
            
    def test_read_file_success(self):
        """测试成功读取文件"""
        content = "测试文件内容\nSecond line"
        
        with tempfile.NamedTemporaryFile(mode='w', delete=False, encoding='utf-8') as temp_file:
            temp_file.write(content)
            temp_file_path = temp_file.name
            
        try:
            result = read_file(temp_file_path)
            assert result == content
        finally:
            os.unlink(temp_file_path)
            
    def test_read_file_with_encoding(self):
        """测试指定编码读取文件"""
        content = "测试内容"
        
        with tempfile.NamedTemporaryFile(mode='w', delete=False, encoding='gbk') as temp_file:
            temp_file.write(content)
            temp_file_path = temp_file.name
            
        try:
            result = read_file(temp_file_path, encoding='gbk')
            assert result == content
        finally:
            os.unlink(temp_file_path)
            
    def test_write_file_success(self):
        """测试成功写入文件"""
        content = "写入测试内容"
        
        with tempfile.TemporaryDirectory() as temp_dir:
            file_path = Path(temp_dir) / 'test_file.txt'
            
            write_file(file_path, content)
            
            assert file_path.exists()
            with open(file_path, 'r', encoding='utf-8') as f:
                assert f.read() == content
                
    def test_write_file_create_directory(self):
        """测试写入文件时创建目录"""
        content = "测试内容"
        
        with tempfile.TemporaryDirectory() as temp_dir:
            file_path = Path(temp_dir) / 'new_dir' / 'test_file.txt'
            
            write_file(file_path, content)
            
            assert file_path.exists()
            assert file_path.parent.exists()
            
    def test_read_json_success(self):
        """测试成功读取JSON文件"""
        data = {'name': '测试', 'value': 123}
        
        with tempfile.NamedTemporaryFile(mode='w', delete=False, encoding='utf-8') as temp_file:
            json.dump(data, temp_file, ensure_ascii=False)
            temp_file_path = temp_file.name
            
        try:
            result = read_json(temp_file_path)
            assert result == data
        finally:
            os.unlink(temp_file_path)
            
    def test_write_json_success(self):
        """测试成功写入JSON文件"""
        data = {'name': '测试数据', 'items': [1, 2, 3]}
        
        with tempfile.TemporaryDirectory() as temp_dir:
            file_path = Path(temp_dir) / 'test.json'
            
            write_json(file_path, data)
            
            assert file_path.exists()
            with open(file_path, 'r', encoding='utf-8') as f:
                loaded_data = json.load(f)
                assert loaded_data == data
                
    def test_write_json_with_indent(self):
        """测试写入带缩进的JSON文件"""
        data = {'key': 'value'}
        
        with tempfile.TemporaryDirectory() as temp_dir:
            file_path = Path(temp_dir) / 'test.json'
            
            write_json(file_path, data, indent=4)
            
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                assert '    ' in content  # 检查缩进
                
    def test_get_file_hash_md5(self):
        """测试获取文件MD5哈希"""
        content = b"test content for hashing"
        expected_hash = hashlib.md5(content).hexdigest()
        
        with tempfile.NamedTemporaryFile(delete=False) as temp_file:
            temp_file.write(content)
            temp_file_path = temp_file.name
            
        try:
            result = get_file_hash(temp_file_path, 'md5')
            assert result == expected_hash
        finally:
            os.unlink(temp_file_path)
            
    def test_get_file_hash_sha1(self):
        """测试获取文件SHA1哈希"""
        content = b"test content"
        expected_hash = hashlib.sha1(content).hexdigest()
        
        with tempfile.NamedTemporaryFile(delete=False) as temp_file:
            temp_file.write(content)
            temp_file_path = temp_file.name
            
        try:
            result = get_file_hash(temp_file_path, 'sha1')
            assert result == expected_hash
        finally:
            os.unlink(temp_file_path)
            
    def test_format_file_size_bytes(self):
        """测试格式化字节大小"""
        assert format_file_size(0) == "0B"
        assert format_file_size(512) == "512.0B"
        
    def test_format_file_size_kb(self):
        """测试格式化KB大小"""
        assert format_file_size(1024) == "1.0KB"
        assert format_file_size(1536) == "1.5KB"
        
    def test_format_file_size_mb(self):
        """测试格式化MB大小"""
        assert format_file_size(1024 * 1024) == "1.0MB"
        assert format_file_size(int(1.5 * 1024 * 1024)) == "1.5MB"
        
    def test_format_file_size_gb(self):
        """测试格式化GB大小"""
        assert format_file_size(1024 * 1024 * 1024) == "1.0GB"
        
    def test_format_file_size_tb(self):
        """测试格式化TB大小"""
        assert format_file_size(1024 * 1024 * 1024 * 1024) == "1.0TB"
        
    @patch('src.utils.helpers.datetime')
    def test_get_timestamp_default_format(self, mock_datetime):
        """测试获取默认格式时间戳"""
        mock_now = Mock()
        mock_now.strftime.return_value = "2023-06-04 15:30:45"
        mock_datetime.now.return_value = mock_now
        
        result = get_timestamp()
        
        assert result == "2023-06-04 15:30:45"
        mock_now.strftime.assert_called_once_with("%Y-%m-%d %H:%M:%S")
        
    @patch('src.utils.helpers.datetime')
    def test_get_timestamp_custom_format(self, mock_datetime):
        """测试获取自定义格式时间戳"""
        mock_now = Mock()
        mock_now.strftime.return_value = "20230604"
        mock_datetime.now.return_value = mock_now
        
        result = get_timestamp("%Y%m%d")
        
        assert result == "20230604"
        mock_now.strftime.assert_called_once_with("%Y%m%d")
        
    def test_sanitize_filename_valid(self):
        """测试清理有效文件名"""
        valid_name = "valid_filename.txt"
        result = sanitize_filename(valid_name)
        assert result == valid_name
        
    def test_sanitize_filename_invalid_chars(self):
        """测试清理包含非法字符的文件名"""
        invalid_name = 'file<name>with:invalid"chars/and\\more|?*'
        expected = 'file_name_with_invalid_chars_and_more___'
        
        result = sanitize_filename(invalid_name)
        assert result == expected
        
    def test_sanitize_filename_empty(self):
        """测试清理空文件名"""
        result = sanitize_filename("")
        assert result == ""
        
    def test_flatten_dict_simple(self):
        """测试扁平化简单字典"""
        data = {
            'a': 1,
            'b': {
                'c': 2,
                'd': 3
            }
        }
        expected = {
            'a': 1,
            'b.c': 2,
            'b.d': 3
        }
        
        result = flatten_dict(data)
        assert result == expected
        
    def test_flatten_dict_nested(self):
        """测试扁平化嵌套字典"""
        data = {
            'level1': {
                'level2': {
                    'level3': 'deep_value'
                },
                'another': 'value'
            }
        }
        expected = {
            'level1.level2.level3': 'deep_value',
            'level1.another': 'value'
        }
        
        result = flatten_dict(data)
        assert result == expected
        
    def test_flatten_dict_custom_separator(self):
        """测试使用自定义分隔符扁平化字典"""
        data = {'a': {'b': 1}}
        expected = {'a_b': 1}
        
        result = flatten_dict(data, sep='_')
        assert result == expected
        
    def test_flatten_dict_with_parent_key(self):
        """测试带父键的扁平化"""
        data = {'b': {'c': 1}}
        expected = {'a.b.c': 1}
        
        result = flatten_dict(data, parent_key='a')
        assert result == expected
        
    def test_chunk_list_even_division(self):
        """测试均等分块列表"""
        data = [1, 2, 3, 4, 5, 6]
        expected = [[1, 2], [3, 4], [5, 6]]
        
        result = chunk_list(data, 2)
        assert result == expected
        
    def test_chunk_list_uneven_division(self):
        """测试不均等分块列表"""
        data = [1, 2, 3, 4, 5]
        expected = [[1, 2, 3], [4, 5]]
        
        result = chunk_list(data, 3)
        assert result == expected
        
    def test_chunk_list_empty(self):
        """测试分块空列表"""
        result = chunk_list([], 3)
        assert result == []
        
    def test_chunk_list_single_chunk(self):
        """测试单个分块"""
        data = [1, 2, 3]
        expected = [[1, 2, 3]]
        
        result = chunk_list(data, 5)
        assert result == expected
        
    def test_safe_get_existing_path(self):
        """测试安全获取存在的路径"""
        data = {
            'level1': {
                'level2': {
                    'target': 'found'
                }
            }
        }
        
        result = safe_get(data, 'level1.level2.target')
        assert result == 'found'
        
    def test_safe_get_nonexistent_path(self):
        """测试安全获取不存在的路径"""
        data = {'level1': {'level2': 'value'}}
        
        result = safe_get(data, 'level1.nonexistent.target')
        assert result is None
        
    def test_safe_get_with_default(self):
        """测试带默认值的安全获取"""
        data = {'key': 'value'}
        
        result = safe_get(data, 'nonexistent.path', 'default_value')
        assert result == 'default_value'
        
    def test_safe_get_type_error(self):
        """测试类型错误时的安全获取"""
        data = {'key': 'string_value'}
        
        # 尝试从字符串中获取键，应该返回默认值
        result = safe_get(data, 'key.nonexistent', 'default')
        assert result == 'default'
        
    def test_merge_dicts_simple(self):
        """测试合并简单字典"""
        dict1 = {'a': 1, 'b': 2}
        dict2 = {'c': 3, 'd': 4}
        expected = {'a': 1, 'b': 2, 'c': 3, 'd': 4}
        
        result = merge_dicts(dict1, dict2)
        assert result == expected
        
    def test_merge_dicts_overlapping(self):
        """测试合并有重叠键的字典"""
        dict1 = {'a': 1, 'b': 2}
        dict2 = {'b': 3, 'c': 4}
        expected = {'a': 1, 'b': 3, 'c': 4}  # 后面的字典覆盖前面的
        
        result = merge_dicts(dict1, dict2)
        assert result == expected
        
    def test_merge_dicts_multiple(self):
        """测试合并多个字典"""
        dict1 = {'a': 1}
        dict2 = {'b': 2}
        dict3 = {'c': 3}
        expected = {'a': 1, 'b': 2, 'c': 3}
        
        result = merge_dicts(dict1, dict2, dict3)
        assert result == expected
        
    def test_merge_dicts_empty(self):
        """测试合并空字典"""
        result = merge_dicts()
        assert result == {}
        
        result = merge_dicts({}, {'a': 1}, {})
        assert result == {'a': 1}
        
    def test_is_valid_sql_identifier_valid(self):
        """测试有效的SQL标识符"""
        valid_identifiers = [
            'table_name',
            'COLUMN_NAME',
            '_private_field',
            'id123',
            'a',
            'A',
            '_',
            'camelCase',
            'snake_case_name'
        ]
        
        for identifier in valid_identifiers:
            assert is_valid_sql_identifier(identifier), f"应该是有效的: {identifier}"
            
    def test_is_valid_sql_identifier_invalid(self):
        """测试无效的SQL标识符"""
        invalid_identifiers = [
            '',  # 空字符串
            '123table',  # 以数字开头
            'table-name',  # 包含连字符
            'table name',  # 包含空格
            'table.name',  # 包含点
            'table@name',  # 包含特殊字符
            'table#name',  # 包含井号
        ]
        
        for identifier in invalid_identifiers:
            assert not is_valid_sql_identifier(identifier), f"应该是无效的: {identifier}"
            
    def test_normalize_sql_name_simple(self):
        """测试简单SQL名称规范化"""
        assert normalize_sql_name('table_name') == 'TABLE_NAME'
        assert normalize_sql_name('Column') == 'COLUMN'
        
    def test_normalize_sql_name_with_quotes(self):
        """测试带引号的SQL名称规范化"""
        assert normalize_sql_name('"table_name"') == 'TABLE_NAME'
        assert normalize_sql_name("'column_name'") == 'COLUMN_NAME'
        
    def test_normalize_sql_name_with_spaces(self):
        """测试带空格的SQL名称规范化"""
        assert normalize_sql_name('  table_name  ') == 'TABLE_NAME'
        assert normalize_sql_name(' "table" ') == 'TABLE'
        
    def test_normalize_sql_name_empty(self):
        """测试空SQL名称规范化"""
        assert normalize_sql_name('') == ''
        assert normalize_sql_name('  ') == ''
        assert normalize_sql_name('""') == '' 
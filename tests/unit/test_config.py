#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import pytest
import os
from unittest.mock import Mock, patch, mock_open
import tempfile
from pathlib import Path
from core.utils.config import Config, config


class TestConfig:
    """Config测试类"""
    
    def setup_method(self):
        """测试前置方法"""
        # 备份原始环境变量
        self.original_env = dict(os.environ)
        
    def teardown_method(self):
        """测试后置清理"""
        # 恢复原始环境变量
        os.environ.clear()
        os.environ.update(self.original_env)
        
    def test_init_without_config_file(self):
        """测试不指定配置文件的初始化"""
        with patch.object(Config, 'load_config') as mock_load:
            config_obj = Config()
            assert config_obj.config_file is None
            assert config_obj.config_data == {}
            mock_load.assert_called_once()
            
    def test_init_with_config_file(self):
        """测试指定配置文件的初始化"""
        with patch.object(Config, 'load_config') as mock_load:
            config_obj = Config('test.yml')
            assert config_obj.config_file == 'test.yml'
            mock_load.assert_called_once()
            
    def test_load_env_vars_defaults(self):
        """测试加载默认环境变量"""
        # 清除相关环境变量
        env_keys = ['DB_HOST', 'DB_PORT', 'DB_SERVICE_NAME', 'DB_USERNAME', 
                   'DB_PASSWORD', 'APP_ENV', 'APP_DEBUG', 'APP_PORT']
        for key in env_keys:
            os.environ.pop(key, None)
            
        config_obj = Config()
        
        assert config_obj.get('DB_HOST') == 'localhost'
        assert config_obj.get('DB_PORT') == 1521
        assert config_obj.get('DB_SERVICE_NAME') == 'ORCL'
        assert config_obj.get('DB_USERNAME') == ''
        assert config_obj.get('DB_PASSWORD') == ''
        assert config_obj.get('APP_ENV') == 'development'
        assert config_obj.get('APP_DEBUG') is False
        assert config_obj.get('APP_PORT') == 8000
        
    def test_load_env_vars_custom(self):
        """测试加载自定义环境变量"""
        os.environ.update({
            'DB_HOST': 'production-db',
            'DB_PORT': '1522',
            'DB_SERVICE_NAME': 'PROD',
            'DB_USERNAME': 'prod_user',
            'DB_PASSWORD': 'prod_pass',
            'APP_ENV': 'production',
            'APP_DEBUG': 'true',
            'APP_PORT': '9000'
        })
        
        config_obj = Config()
        
        assert config_obj.get('DB_HOST') == 'production-db'
        assert config_obj.get('DB_PORT') == 1522
        assert config_obj.get('DB_SERVICE_NAME') == 'PROD'
        assert config_obj.get('DB_USERNAME') == 'prod_user'
        assert config_obj.get('DB_PASSWORD') == 'prod_pass'
        assert config_obj.get('APP_ENV') == 'production'
        assert config_obj.get('APP_DEBUG') is True
        assert config_obj.get('APP_PORT') == 9000
        
    def test_load_env_vars_all_defaults(self):
        """测试所有环境变量的默认值"""
        # 清除所有相关环境变量
        for key in list(os.environ.keys()):
            if key.startswith(('DB_', 'APP_', 'LOG_', 'CACHE_', 'FRONTEND_', 'API_', 'MAX_', 'UPLOAD_')):
                del os.environ[key]
                
        config_obj = Config()
        
        # 验证所有默认值
        assert config_obj.get('LOG_LEVEL') == 'INFO'
        assert config_obj.get('LOG_FILE') == 'logs/app.log'
        assert config_obj.get('CACHE_ENABLED') is True
        assert config_obj.get('CACHE_TTL') == 3600
        assert config_obj.get('FRONTEND_URL') == 'http://localhost:3000'
        assert config_obj.get('API_BASE_URL') == 'http://localhost:8000/api'
        assert config_obj.get('MAX_FILE_SIZE') == '10MB'
        assert config_obj.get('UPLOAD_PATH') == 'data/input/'
        
    @patch('os.path.exists')
    def test_load_config_no_file(self, mock_exists):
        """测试没有配置文件时的加载过程"""
        mock_exists.return_value = False
        
        with patch.object(Config, 'load_env_vars') as mock_load_env, \
             patch.object(Config, 'load_yaml_config') as mock_load_yaml:
            
            config_obj = Config('nonexistent.yml')
            mock_load_env.assert_called_once()
            mock_load_yaml.assert_not_called()
            
    @patch('os.path.exists')
    def test_load_config_with_file(self, mock_exists):
        """测试有配置文件时的加载过程"""
        mock_exists.return_value = True
        
        with patch.object(Config, 'load_env_vars') as mock_load_env, \
             patch.object(Config, 'load_yaml_config') as mock_load_yaml:
            
            config_obj = Config('test.yml')
            mock_load_env.assert_called_once()
            mock_load_yaml.assert_called_once_with('test.yml')
            
    @patch('os.path.exists')
    def test_load_config_default_env_file(self, mock_exists):
        """测试加载默认环境配置文件"""
        def exists_side_effect(path):
            return path == 'config/development.yml'
            
        mock_exists.side_effect = exists_side_effect
        os.environ['APP_ENV'] = 'development'
        
        with patch.object(Config, 'load_env_vars') as mock_load_env, \
             patch.object(Config, 'load_yaml_config') as mock_load_yaml:
            
            config_obj = Config()
            mock_load_env.assert_called_once()
            mock_load_yaml.assert_called_once_with('config/development.yml')
            
    def test_load_yaml_config_success(self):
        """测试成功加载YAML配置"""
        yaml_content = """
        database:
          host: yaml-host
          port: 3306
        app:
          name: test-app
        """
        
        with patch('builtins.open', mock_open(read_data=yaml_content)), \
             patch('yaml.safe_load') as mock_yaml_load:
            
            mock_yaml_load.return_value = {
                'database': {'host': 'yaml-host', 'port': 3306},
                'app': {'name': 'test-app'}
            }
            
            config_obj = Config()
            config_obj.load_yaml_config('test.yml')
            
            assert config_obj.get('database') == {'host': 'yaml-host', 'port': 3306}
            assert config_obj.get('app') == {'name': 'test-app'}
            
    def test_load_yaml_config_file_error(self):
        """测试YAML文件加载错误"""
        with patch('builtins.open', side_effect=FileNotFoundError), \
             patch('builtins.print') as mock_print:
            
            config_obj = Config()
            config_obj.load_yaml_config('nonexistent.yml')
            
            # 验证至少调用了一次print（可能会有多次调用，因为初始化时也会尝试加载配置）
            assert mock_print.call_count >= 1
            # 验证最后一次调用包含我们期望的错误信息
            last_call = mock_print.call_args_list[-1]
            assert 'Warning: Failed to load config file' in last_call[0][0]
            assert 'nonexistent.yml' in last_call[0][0]
            
    def test_load_yaml_config_yaml_error(self):
        """测试YAML解析错误"""
        with patch('builtins.open', mock_open(read_data='invalid: yaml: content:')), \
             patch('yaml.safe_load', side_effect=Exception("YAML error")), \
             patch('builtins.print') as mock_print:
            
            config_obj = Config()
            config_obj.load_yaml_config('invalid.yml')
            
            # 验证至少调用了一次print（可能会有多次调用，因为初始化时也会尝试加载配置）
            assert mock_print.call_count >= 1
            # 验证最后一次调用包含我们期望的错误信息
            last_call = mock_print.call_args_list[-1]
            assert 'Warning: Failed to load config file' in last_call[0][0]
            assert 'invalid.yml' in last_call[0][0]
            
    def test_get_existing_key(self):
        """测试获取存在的配置键"""
        config_obj = Config()
        config_obj.config_data = {'test_key': 'test_value'}
        
        result = config_obj.get('test_key')
        assert result == 'test_value'
        
    def test_get_nonexistent_key_with_default(self):
        """测试获取不存在的配置键（有默认值）"""
        config_obj = Config()
        
        result = config_obj.get('nonexistent_key', 'default_value')
        assert result == 'default_value'
        
    def test_get_nonexistent_key_without_default(self):
        """测试获取不存在的配置键（无默认值）"""
        config_obj = Config()
        
        result = config_obj.get('nonexistent_key')
        assert result is None
        
    def test_set_config(self):
        """测试设置配置值"""
        config_obj = Config()
        
        config_obj.set('new_key', 'new_value')
        assert config_obj.get('new_key') == 'new_value'
        
    def test_get_database_config(self):
        """测试获取数据库配置"""
        config_obj = Config()
        config_obj.config_data.update({
            'DB_HOST': 'test-host',
            'DB_PORT': 1521,
            'DB_SERVICE_NAME': 'TEST',
            'DB_USERNAME': 'test_user',
            'DB_PASSWORD': 'test_pass'
        })
        
        db_config = config_obj.get_database_config()
        
        expected = {
            'host': 'test-host',
            'port': 1521,
            'service_name': 'TEST',
            'username': 'test_user',
            'password': 'test_pass'
        }
        assert db_config == expected
        
    def test_get_app_config(self):
        """测试获取应用配置"""
        config_obj = Config()
        config_obj.config_data.update({
            'APP_ENV': 'test',
            'APP_DEBUG': True,
            'APP_PORT': 8080
        })
        
        app_config = config_obj.get_app_config()
        
        expected = {
            'env': 'test',
            'debug': True,
            'port': 8080
        }
        assert app_config == expected
        
    def test_global_config_instance(self):
        """测试全局配置实例"""
        # 测试config模块级别的全局实例
        assert isinstance(config, Config)
        
    def test_boolean_env_var_parsing(self):
        """测试布尔环境变量的解析"""
        test_cases = [
            ('true', True),
            ('True', True),
            ('TRUE', True),
            ('false', False),
            ('False', False),
            ('FALSE', False),
            ('1', False),  # 不是 'true' 就是 False
            ('0', False),
            ('yes', False),
            ('', False)
        ]
        
        for env_value, expected in test_cases:
            os.environ['APP_DEBUG'] = env_value
            config_obj = Config()
            assert config_obj.get('APP_DEBUG') == expected, f"Failed for value: {env_value}"
            
    def test_integer_env_var_parsing(self):
        """测试整数环境变量的解析"""
        os.environ.update({
            'DB_PORT': '3306',
            'APP_PORT': '9000',
            'CACHE_TTL': '7200'
        })
        
        config_obj = Config()
        
        assert config_obj.get('DB_PORT') == 3306
        assert config_obj.get('APP_PORT') == 9000
        assert config_obj.get('CACHE_TTL') == 7200 
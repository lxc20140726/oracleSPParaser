#!/usr/bin/env python3
"""
配置管理模块
"""

import os
import yaml
from typing import Dict, Any, Optional
from pathlib import Path


class Config:
    """配置管理类"""
    
    def __init__(self, config_file: Optional[str] = None):
        self.config_data = {}
        self.config_file = config_file
        self.load_config()
    
    def load_config(self):
        """加载配置文件"""
        # 加载环境变量
        self.load_env_vars()
        
        # 加载YAML配置文件
        if self.config_file and os.path.exists(self.config_file):
            self.load_yaml_config(self.config_file)
        else:
            # 尝试加载默认配置文件
            env = os.getenv('APP_ENV', 'development')
            default_config = f"config/{env}.yml"
            if os.path.exists(default_config):
                self.load_yaml_config(default_config)
    
    def load_env_vars(self):
        """加载环境变量"""
        env_vars = {
            'DB_HOST': os.getenv('DB_HOST', 'localhost'),
            'DB_PORT': int(os.getenv('DB_PORT', '1521')),
            'DB_SERVICE_NAME': os.getenv('DB_SERVICE_NAME', 'ORCL'),
            'DB_USERNAME': os.getenv('DB_USERNAME', ''),
            'DB_PASSWORD': os.getenv('DB_PASSWORD', ''),
            'APP_ENV': os.getenv('APP_ENV', 'development'),
            'APP_DEBUG': os.getenv('APP_DEBUG', 'false').lower() == 'true',
            'APP_PORT': int(os.getenv('APP_PORT', '8000')),
            'LOG_LEVEL': os.getenv('LOG_LEVEL', 'INFO'),
            'LOG_FILE': os.getenv('LOG_FILE', 'logs/app.log'),
            'CACHE_ENABLED': os.getenv('CACHE_ENABLED', 'true').lower() == 'true',
            'CACHE_TTL': int(os.getenv('CACHE_TTL', '3600')),
            'FRONTEND_URL': os.getenv('FRONTEND_URL', 'http://localhost:3000'),
            'API_BASE_URL': os.getenv('API_BASE_URL', 'http://localhost:8000/api'),
            'MAX_FILE_SIZE': os.getenv('MAX_FILE_SIZE', '10MB'),
            'UPLOAD_PATH': os.getenv('UPLOAD_PATH', 'data/input/'),
        }
        self.config_data.update(env_vars)
    
    def load_yaml_config(self, config_file: str):
        """加载YAML配置文件"""
        try:
            with open(config_file, 'r', encoding='utf-8') as f:
                yaml_config = yaml.safe_load(f)
                if yaml_config:
                    self.config_data.update(yaml_config)
        except Exception as e:
            print(f"Warning: Failed to load config file {config_file}: {e}")
    
    def get(self, key: str, default: Any = None) -> Any:
        """获取配置值"""
        return self.config_data.get(key, default)
    
    def set(self, key: str, value: Any):
        """设置配置值"""
        self.config_data[key] = value
    
    def get_database_config(self) -> Dict[str, Any]:
        """获取数据库配置"""
        return {
            'host': self.get('DB_HOST'),
            'port': self.get('DB_PORT'),
            'service_name': self.get('DB_SERVICE_NAME'),
            'username': self.get('DB_USERNAME'),
            'password': self.get('DB_PASSWORD'),
        }
    
    def get_app_config(self) -> Dict[str, Any]:
        """获取应用配置"""
        return {
            'env': self.get('APP_ENV'),
            'debug': self.get('APP_DEBUG'),
            'port': self.get('APP_PORT'),
        }


# 全局配置实例
config = Config() 
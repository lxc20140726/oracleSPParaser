#!/usr/bin/env python3
"""
日志工具模块
"""

import logging
import os
from datetime import datetime
from pathlib import Path
from typing import Optional


class Logger:
    """日志管理类"""
    
    def __init__(self, name: str = "oracle_sp_parser", level: str = "INFO", log_file: Optional[str] = None):
        self.logger = logging.getLogger(name)
        self.logger.setLevel(getattr(logging, level.upper()))
        
        # 避免重复添加处理器
        if not self.logger.handlers:
            self._setup_handlers(log_file)
    
    def _setup_handlers(self, log_file: Optional[str] = None):
        """设置日志处理器"""
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        
        # 控制台处理器
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(formatter)
        self.logger.addHandler(console_handler)
        
        # 文件处理器
        if log_file:
            # 确保日志目录存在
            log_path = Path(log_file)
            log_path.parent.mkdir(parents=True, exist_ok=True)
            
            file_handler = logging.FileHandler(log_file, encoding='utf-8')
            file_handler.setFormatter(formatter)
            self.logger.addHandler(file_handler)
    
    def debug(self, message: str):
        """调试日志"""
        self.logger.debug(message)
    
    def info(self, message: str):
        """信息日志"""
        self.logger.info(message)
    
    def warning(self, message: str):
        """警告日志"""
        self.logger.warning(message)
    
    def error(self, message: str):
        """错误日志"""
        self.logger.error(message)
    
    def critical(self, message: str):
        """严重错误日志"""
        self.logger.critical(message)
    
    def exception(self, message: str):
        """异常日志（包含堆栈信息）"""
        self.logger.exception(message)


# 创建默认日志实例
def get_logger(name: str = "oracle_sp_parser", level: str = "INFO", log_file: Optional[str] = None) -> Logger:
    """获取日志实例"""
    return Logger(name, level, log_file)


# 全局日志实例
logger = get_logger() 
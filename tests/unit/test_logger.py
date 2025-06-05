#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import pytest
import logging
import tempfile
import os
from unittest.mock import Mock, patch, MagicMock
from pathlib import Path
from core.utils.logger import Logger, get_logger, logger


class TestLogger:
    """Logger测试类"""
    
    def setup_method(self):
        """测试前置方法"""
        # 清理现有的日志处理器
        logging.getLogger().handlers.clear()
        
    def teardown_method(self):
        """测试后置清理"""
        # 清理日志处理器
        for logger_name in list(logging.Logger.manager.loggerDict.keys()):
            test_logger = logging.getLogger(logger_name)
            test_logger.handlers.clear()
            
    def test_init_default_parameters(self):
        """测试默认参数初始化"""
        test_logger = Logger()
        
        assert test_logger.logger.name == "oracle_sp_parser"
        assert test_logger.logger.level == logging.INFO
        assert len(test_logger.logger.handlers) >= 1  # 至少有控制台处理器
        
    def test_init_custom_parameters(self):
        """测试自定义参数初始化"""
        with tempfile.NamedTemporaryFile(delete=False) as temp_file:
            log_file_path = temp_file.name
            
        try:
            test_logger = Logger(
                name="custom_logger",
                level="DEBUG",
                log_file=log_file_path
            )
            
            assert test_logger.logger.name == "custom_logger"
            assert test_logger.logger.level == logging.DEBUG
            assert len(test_logger.logger.handlers) == 2  # 控制台 + 文件处理器
        finally:
            os.unlink(log_file_path)
            
    def test_init_invalid_level(self):
        """测试无效日志级别"""
        # getattr会在无效级别时抛出AttributeError，这里测试默认行为
        with pytest.raises(AttributeError):
            Logger(level="INVALID_LEVEL")
            
    def test_setup_handlers_console_only(self):
        """测试只设置控制台处理器"""
        test_logger = Logger()
        
        # 应该有一个控制台处理器
        console_handlers = [h for h in test_logger.logger.handlers 
                          if isinstance(h, logging.StreamHandler) and not hasattr(h, 'baseFilename')]
        assert len(console_handlers) == 1
        
        # 检查格式器
        handler = console_handlers[0]
        assert handler.formatter is not None
        assert '%(asctime)s' in handler.formatter._fmt
        
    def test_setup_handlers_with_file(self):
        """测试设置文件处理器"""
        with tempfile.TemporaryDirectory() as temp_dir:
            log_file = os.path.join(temp_dir, 'test.log')
            test_logger = Logger(log_file=log_file)
            
            # 应该有控制台和文件处理器
            assert len(test_logger.logger.handlers) == 2
            
            # 检查文件处理器
            file_handlers = [h for h in test_logger.logger.handlers 
                           if isinstance(h, logging.FileHandler)]
            assert len(file_handlers) == 1
            
            # 验证日志文件已创建
            assert os.path.exists(log_file)
            
    def test_setup_handlers_create_log_directory(self):
        """测试创建日志目录"""
        with tempfile.TemporaryDirectory() as temp_dir:
            log_file = os.path.join(temp_dir, 'logs', 'app.log')
            test_logger = Logger(log_file=log_file)
            
            # 验证目录和文件已创建
            assert os.path.exists(os.path.dirname(log_file))
            assert os.path.exists(log_file)
            
    def test_no_duplicate_handlers(self):
        """测试不会重复添加处理器"""
        logger_name = "test_no_duplicate"
        
        # 第一次创建
        logger1 = Logger(name=logger_name)
        initial_handler_count = len(logger1.logger.handlers)
        
        # 第二次创建相同名称的logger
        logger2 = Logger(name=logger_name)
        
        # 处理器数量应该相同（不会重复添加）
        assert len(logger2.logger.handlers) == initial_handler_count
        
    def test_debug_method(self):
        """测试debug方法"""
        with patch('logging.Logger.debug') as mock_debug:
            test_logger = Logger()
            test_logger.debug("Debug message")
            
            mock_debug.assert_called_once_with("Debug message")
            
    def test_info_method(self):
        """测试info方法"""
        with patch('logging.Logger.info') as mock_info:
            test_logger = Logger()
            test_logger.info("Info message")
            
            mock_info.assert_called_once_with("Info message")
            
    def test_warning_method(self):
        """测试warning方法"""
        with patch('logging.Logger.warning') as mock_warning:
            test_logger = Logger()
            test_logger.warning("Warning message")
            
            mock_warning.assert_called_once_with("Warning message")
            
    def test_error_method(self):
        """测试error方法"""
        with patch('logging.Logger.error') as mock_error:
            test_logger = Logger()
            test_logger.error("Error message")
            
            mock_error.assert_called_once_with("Error message")
            
    def test_critical_method(self):
        """测试critical方法"""
        with patch('logging.Logger.critical') as mock_critical:
            test_logger = Logger()
            test_logger.critical("Critical message")
            
            mock_critical.assert_called_once_with("Critical message")
            
    def test_exception_method(self):
        """测试exception方法"""
        with patch('logging.Logger.exception') as mock_exception:
            test_logger = Logger()
            test_logger.exception("Exception message")
            
            mock_exception.assert_called_once_with("Exception message")
            
    def test_actual_logging_output(self):
        """测试实际的日志输出"""
        with tempfile.TemporaryDirectory() as temp_dir:
            log_file = os.path.join(temp_dir, 'test_output.log')
            test_logger = Logger(name="test_output", log_file=log_file)
            
            test_message = "测试日志消息"
            test_logger.info(test_message)
            
            # 读取日志文件内容
            with open(log_file, 'r', encoding='utf-8') as f:
                log_content = f.read()
                
            assert test_message in log_content
            assert "test_output" in log_content
            assert "INFO" in log_content
            
    def test_different_log_levels(self):
        """测试不同日志级别的过滤"""
        with tempfile.TemporaryDirectory() as temp_dir:
            log_file = os.path.join(temp_dir, 'level_test.log')
            
            # 创建ERROR级别的logger
            test_logger = Logger(name="level_test", level="ERROR", log_file=log_file)
            
            test_logger.debug("Debug message - should not appear")
            test_logger.info("Info message - should not appear")
            test_logger.warning("Warning message - should not appear")
            test_logger.error("Error message - should appear")
            test_logger.critical("Critical message - should appear")
            
            # 读取日志文件
            with open(log_file, 'r', encoding='utf-8') as f:
                log_content = f.read()
                
            assert "Debug message" not in log_content
            assert "Info message" not in log_content
            assert "Warning message" not in log_content
            assert "Error message" in log_content
            assert "Critical message" in log_content
            
    def test_get_logger_function_default(self):
        """测试get_logger函数默认参数"""
        test_logger = get_logger()
        
        assert isinstance(test_logger, Logger)
        assert test_logger.logger.name == "oracle_sp_parser"
        assert test_logger.logger.level == logging.INFO
        
    def test_get_logger_function_custom(self):
        """测试get_logger函数自定义参数"""
        with tempfile.NamedTemporaryFile(delete=False) as temp_file:
            log_file_path = temp_file.name
            
        try:
            test_logger = get_logger(
                name="custom_get_logger",
                level="WARNING",
                log_file=log_file_path
            )
            
            assert isinstance(test_logger, Logger)
            assert test_logger.logger.name == "custom_get_logger"
            assert test_logger.logger.level == logging.WARNING
        finally:
            os.unlink(log_file_path)
            
    def test_global_logger_instance(self):
        """测试全局logger实例"""
        assert isinstance(logger, Logger)
        assert logger.logger.name == "oracle_sp_parser"
        
    def test_unicode_messages(self):
        """测试Unicode消息"""
        with tempfile.TemporaryDirectory() as temp_dir:
            log_file = os.path.join(temp_dir, 'unicode_test.log')
            test_logger = Logger(log_file=log_file)
            
            unicode_message = "测试中文日志 🚀 Special chars: àáâãäå"
            test_logger.info(unicode_message)
            
            with open(log_file, 'r', encoding='utf-8') as f:
                log_content = f.read()
                
            assert unicode_message in log_content
            
    def test_formatter_format(self):
        """测试日志格式器格式"""
        test_logger = Logger()
        
        # 获取处理器的格式器
        handler = test_logger.logger.handlers[0]
        formatter = handler.formatter
        
        expected_format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        assert formatter._fmt == expected_format
        
    def test_file_handler_encoding(self):
        """测试文件处理器编码"""
        with tempfile.TemporaryDirectory() as temp_dir:
            log_file = os.path.join(temp_dir, 'encoding_test.log')
            test_logger = Logger(log_file=log_file)
            
            # 找到文件处理器
            file_handler = None
            for handler in test_logger.logger.handlers:
                if isinstance(handler, logging.FileHandler):
                    file_handler = handler
                    break
                    
            assert file_handler is not None
            assert file_handler.encoding == 'utf-8'
            
    def test_multiple_loggers_independence(self):
        """测试多个logger的独立性"""
        with tempfile.TemporaryDirectory() as temp_dir:
            log_file1 = os.path.join(temp_dir, 'logger1.log')
            log_file2 = os.path.join(temp_dir, 'logger2.log')
            
            logger1 = Logger(name="logger1", level="INFO", log_file=log_file1)
            logger2 = Logger(name="logger2", level="ERROR", log_file=log_file2)
            
            logger1.info("Message from logger1")
            logger1.error("Error from logger1")
            
            logger2.info("Message from logger2")  # 不应该记录（级别太低）
            logger2.error("Error from logger2")
            
            # 检查logger1的日志
            with open(log_file1, 'r', encoding='utf-8') as f:
                content1 = f.read()
            assert "Message from logger1" in content1
            assert "Error from logger1" in content1
            assert "logger2" not in content1
            
            # 检查logger2的日志
            with open(log_file2, 'r', encoding='utf-8') as f:
                content2 = f.read()
            assert "Message from logger2" not in content2  # INFO级别被过滤
            assert "Error from logger2" in content2
            assert "logger1" not in content2 
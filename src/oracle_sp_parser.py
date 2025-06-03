"""
Oracle SP Parser - Oracle存储过程解析和分析工具

这是一个企业级的Oracle存储过程分析平台，提供：
- 存储过程解析和语法分析
- 依赖关系分析和可视化
- Web API接口
- 批量处理和报告生成
"""

__version__ = "1.0.0"
__author__ = "Oracle SP Parser Team"
__email__ = "oracle-sp-parser@example.com"
__license__ = "MIT"

# 版本信息
VERSION_INFO = {
    "major": 1,
    "minor": 0,
    "patch": 0,
    "release": "stable"
}

# 导出主要组件
try:
    from .parser import StoredProcedureParser, SQLStatementParser
    from .analyzer import ParameterAnalyzer, TableAnalyzer, ConditionAnalyzer
    from .models import Parameter, SQLStatement, StoredProcedure, AnalysisResult
    from .utils import FileProcessor, ConfigManager
    from .visualizer import DependencyVisualizer
    
    __all__ = [
        # 解析器
        "StoredProcedureParser",
        "SQLStatementParser",
        
        # 分析器
        "ParameterAnalyzer", 
        "TableAnalyzer",
        "ConditionAnalyzer",
        
        # 数据模型
        "Parameter",
        "SQLStatement", 
        "StoredProcedure",
        "AnalysisResult",
        
        # 工具类
        "FileProcessor",
        "ConfigManager",
        "DependencyVisualizer",
        
        # 版本信息
        "__version__",
        "VERSION_INFO"
    ]
    
except ImportError:
    # 如果某些模块还未实现，暂时跳过
    __all__ = ["__version__", "VERSION_INFO"]


def get_version():
    """获取版本信息"""
    return __version__


def get_version_info():
    """获取详细版本信息"""
    return VERSION_INFO


def info():
    """显示包信息"""
    print(f"Oracle SP Parser v{__version__}")
    print(f"Author: {__author__}")
    print(f"License: {__license__}")
    print(f"Email: {__email__}")

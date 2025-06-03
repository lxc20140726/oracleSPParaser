#!/usr/bin/env python3
"""
辅助函数模块
"""

import os
import json
import hashlib
from typing import Any, Dict, List, Optional, Union
from pathlib import Path
from datetime import datetime


def ensure_dir(directory: Union[str, Path]) -> Path:
    """确保目录存在，如果不存在则创建"""
    path = Path(directory)
    path.mkdir(parents=True, exist_ok=True)
    return path


def read_file(file_path: Union[str, Path], encoding: str = 'utf-8') -> str:
    """读取文件内容"""
    with open(file_path, 'r', encoding=encoding) as f:
        return f.read()


def write_file(file_path: Union[str, Path], content: str, encoding: str = 'utf-8'):
    """写入文件内容"""
    path = Path(file_path)
    ensure_dir(path.parent)
    with open(path, 'w', encoding=encoding) as f:
        f.write(content)


def read_json(file_path: Union[str, Path]) -> Dict[str, Any]:
    """读取JSON文件"""
    with open(file_path, 'r', encoding='utf-8') as f:
        return json.load(f)


def write_json(file_path: Union[str, Path], data: Dict[str, Any], indent: int = 2):
    """写入JSON文件"""
    path = Path(file_path)
    ensure_dir(path.parent)
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=indent)


def get_file_hash(file_path: Union[str, Path], algorithm: str = 'md5') -> str:
    """获取文件哈希值"""
    hash_obj = hashlib.new(algorithm)
    with open(file_path, 'rb') as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_obj.update(chunk)
    return hash_obj.hexdigest()


def format_file_size(size_bytes: int) -> str:
    """格式化文件大小"""
    if size_bytes == 0:
        return "0B"
    
    size_names = ["B", "KB", "MB", "GB", "TB"]
    i = 0
    while size_bytes >= 1024 and i < len(size_names) - 1:
        size_bytes /= 1024.0
        i += 1
    
    return f"{size_bytes:.1f}{size_names[i]}"


def get_timestamp(format_str: str = "%Y-%m-%d %H:%M:%S") -> str:
    """获取当前时间戳"""
    return datetime.now().strftime(format_str)


def sanitize_filename(filename: str) -> str:
    """清理文件名，移除非法字符"""
    invalid_chars = '<>:"/\\|?*'
    for char in invalid_chars:
        filename = filename.replace(char, '_')
    return filename


def flatten_dict(d: Dict[str, Any], parent_key: str = '', sep: str = '.') -> Dict[str, Any]:
    """扁平化字典"""
    items = []
    for k, v in d.items():
        new_key = f"{parent_key}{sep}{k}" if parent_key else k
        if isinstance(v, dict):
            items.extend(flatten_dict(v, new_key, sep=sep).items())
        else:
            items.append((new_key, v))
    return dict(items)


def chunk_list(lst: List[Any], chunk_size: int) -> List[List[Any]]:
    """将列表分块"""
    return [lst[i:i + chunk_size] for i in range(0, len(lst), chunk_size)]


def safe_get(data: Dict[str, Any], key_path: str, default: Any = None) -> Any:
    """安全获取嵌套字典的值"""
    keys = key_path.split('.')
    current = data
    
    try:
        for key in keys:
            current = current[key]
        return current
    except (KeyError, TypeError):
        return default


def merge_dicts(*dicts: Dict[str, Any]) -> Dict[str, Any]:
    """合并多个字典"""
    result = {}
    for d in dicts:
        result.update(d)
    return result


def is_valid_sql_identifier(identifier: str) -> bool:
    """检查是否为有效的SQL标识符"""
    if not identifier:
        return False
    
    # SQL标识符规则：以字母或下划线开头，后续可以是字母、数字或下划线
    if not (identifier[0].isalpha() or identifier[0] == '_'):
        return False
    
    return all(c.isalnum() or c == '_' for c in identifier[1:])


def normalize_sql_name(name: str) -> str:
    """规范化SQL名称"""
    # 移除引号并转换为大写（Oracle默认）
    name = name.strip().strip('"').strip("'")
    return name.upper() if name else "" 
#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import os
from pathlib import Path
import re

# 添加src路径
src_path = Path(__file__).parent.parent / "src"
sys.path.insert(0, str(src_path))

from fastapi import FastAPI, HTTPException, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, FileResponse
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
import json
import logging

# 修复导入：明确从src目录导入，避免与当前文件名冲突
import importlib.util
spec = importlib.util.spec_from_file_location("src_main", src_path / "main.py")
src_main = importlib.util.module_from_spec(spec)
spec.loader.exec_module(src_main)
OracleSPAnalyzer = src_main.OracleSPAnalyzer

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 创建FastAPI应用
app = FastAPI(
    title="Oracle存储过程分析工具",
    description="分析Oracle存储过程的数据流向、表关系和字段血缘关系",
    version="2.0.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc"
)

# 配置CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 生产环境中应该限制具体域名
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 挂载静态文件服务（仅在目录存在时）
static_dir = Path(__file__).parent.parent / "frontend" / "build" / "static"
build_dir = Path(__file__).parent.parent / "frontend" / "build"

if static_dir.exists():
    app.mount("/static", StaticFiles(directory=str(static_dir)), name="static")
    logger.info(f"挂载静态文件目录: {static_dir}")
else:
    logger.warning(f"静态文件目录不存在，跳过挂载: {static_dir}")

# 挂载构建目录中的其他文件（manifest.json, favicon.ico等）
if build_dir.exists():
    app.mount("/assets", StaticFiles(directory=str(build_dir)), name="assets")
    logger.info(f"挂载构建文件目录: {build_dir}")

# 添加对根目录静态文件的支持
@app.get("/manifest.json")
async def manifest():
    """提供manifest.json文件"""
    try:
        manifest_path = Path(__file__).parent.parent / "frontend" / "build" / "manifest.json"
        if manifest_path.exists():
            with open(manifest_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        else:
            raise HTTPException(status_code=404, detail="manifest.json not found")
    except Exception as e:
        logger.error(f"Error serving manifest.json: {e}")
        raise HTTPException(status_code=404, detail="manifest.json not found")

@app.get("/favicon.ico")
async def favicon():
    """提供favicon文件"""
    try:
        favicon_path = Path(__file__).parent.parent / "frontend" / "public" / "favicon.ico"
        if not favicon_path.exists():
            # 如果public目录没有，尝试build目录
            favicon_path = Path(__file__).parent.parent / "frontend" / "build" / "favicon.ico"
        
        if favicon_path.exists():
            return FileResponse(favicon_path)
        else:
            raise HTTPException(status_code=404, detail="favicon.ico not found")
    except Exception as e:
        logger.error(f"Error serving favicon.ico: {e}")
        raise HTTPException(status_code=404, detail="favicon.ico not found")

# 请求模型
class AnalyzeRequest(BaseModel):
    stored_procedure: str
    options: Optional[Dict[str, Any]] = {}

class AnalyzeResponse(BaseModel):
    success: bool
    message: str
    data: Optional[Dict[str, Any]] = None
    visualization: Optional[Dict[str, Any]] = None

# 全局分析器实例
analyzer = OracleSPAnalyzer()

@app.get("/", response_class=HTMLResponse)
async def root():
    """首页"""
    try:
        # 尝试读取React构建的index.html
        frontend_path = Path(__file__).parent.parent / "frontend" / "build" / "index.html"
        if frontend_path.exists():
            return frontend_path.read_text(encoding='utf-8')
        else:
            # 如果没有构建的前端，返回简单的HTML
            return """
            <!DOCTYPE html>
            <html>
            <head>
                <title>Oracle存储过程分析工具</title>
                <meta charset="utf-8">
                <meta name="viewport" content="width=device-width, initial-scale=1">
            </head>
            <body>
                <h1>Oracle存储过程分析工具</h1>
                <p>API文档: <a href="/api/docs">/api/docs</a></p>
                <p>前端正在构建中...</p>
            </body>
            </html>
            """
    except Exception as e:
        logger.error(f"Error serving root page: {e}")
        return "<h1>Oracle存储过程分析工具</h1><p>服务正在启动...</p>"

@app.get("/api/health")
async def health_check():
    """健康检查"""
    return {"status": "healthy", "message": "Oracle存储过程分析服务运行正常"}

@app.post("/api/analyze", response_model=AnalyzeResponse)
async def analyze_stored_procedure(request: AnalyzeRequest):
    """分析存储过程"""
    try:
        logger.info("开始分析存储过程")
        
        # 验证输入
        if not request.stored_procedure.strip():
            raise HTTPException(status_code=400, detail="存储过程内容不能为空")
        
        # 执行分析
        result = analyzer.analyze(request.stored_procedure)
        
        # 转换为可视化数据
        visualization_data = convert_to_visualization_data(result)
        
        # 构建响应数据
        response_data = {
            "procedure_name": result.sp_structure.name,
            "parameters": [
                {
                    "name": p.name,
                    "direction": p.direction,
                    "data_type": p.data_type,
                    "used_in_statements": p.used_in_statements
                } for p in result.parameters
            ],
            "sql_statements": [
                {
                    "id": stmt.statement_id,
                    "type": stmt.statement_type.value,
                    "raw_sql": stmt.raw_sql,
                    "source_tables": stmt.source_tables,
                    "target_tables": stmt.target_tables,
                    "parameters_used": stmt.parameters_used
                } for stmt in result.sp_structure.sql_statements
            ],
            "tables": {
                "physical": {
                    name: {
                        "fields": table.fields,
                        "source_sql_ids": table.source_sql_ids
                    } for name, table in result.table_field_analysis.physical_tables.items()
                },
                "temporary": {
                    name: {
                        "fields": table.fields,
                        "source_sql_ids": table.source_sql_ids
                    } for name, table in result.table_field_analysis.temp_tables.items()
                }
            },
            "join_conditions": [
                {
                    "left_table": jc.left_table,
                    "left_field": jc.left_field,
                    "right_table": jc.right_table,
                    "right_field": jc.right_field,
                    "join_type": jc.join_type,
                    "condition_text": jc.condition_text
                } for jc in result.conditions_and_logic.join_conditions
            ],
            "statistics": {
                "parameter_count": len(result.parameters),
                "sql_statement_count": len(result.sp_structure.sql_statements),
                "physical_table_count": len(result.table_field_analysis.physical_tables),
                "temporary_table_count": len(result.table_field_analysis.temp_tables),
                "join_condition_count": len(result.conditions_and_logic.join_conditions)
            }
        }
        
        logger.info(f"分析完成: {result.sp_structure.name}")
        
        return AnalyzeResponse(
            success=True,
            message=f"成功分析存储过程 '{result.sp_structure.name}'",
            data=response_data,
            visualization=visualization_data
        )
        
    except Exception as e:
        logger.error(f"分析过程中发生错误: {str(e)}")
        raise HTTPException(status_code=500, detail=f"分析失败: {str(e)}")

@app.post("/api/analyze/file")
async def analyze_file(file: UploadFile = File(...)):
    """从文件上传分析存储过程"""
    try:
        # 检查文件类型
        if not file.filename.lower().endswith(('.sql', '.txt', '.pls')):
            raise HTTPException(status_code=400, detail="仅支持 .sql, .txt, .pls 文件格式")
        
        # 读取文件内容
        content = await file.read()
        stored_procedure = content.decode('utf-8')
        
        # 创建分析请求
        request = AnalyzeRequest(stored_procedure=stored_procedure)
        
        # 调用分析功能
        return await analyze_stored_procedure(request)
        
    except UnicodeDecodeError:
        raise HTTPException(status_code=400, detail="文件编码错误，请确保文件使用UTF-8编码")
    except Exception as e:
        logger.error(f"文件分析错误: {str(e)}")
        raise HTTPException(status_code=500, detail=f"文件分析失败: {str(e)}")

def convert_to_visualization_data(result) -> Dict[str, Any]:
    """转换分析结果为可视化数据格式"""
    nodes = []
    edges = []
    
    # 创建别名到实际表名的映射
    alias_to_table_map = {}
    
    # 构建别名映射关系
    for stmt in result.sp_structure.sql_statements:
        # 从 SQL 语句中提取别名信息
        sql_text = stmt.raw_sql.upper()
        
        # 匹配 FROM table_name alias 格式
        from_pattern = r'FROM\s+(\w+)\s+(\w+)'
        from_match = re.search(from_pattern, sql_text, re.IGNORECASE)
        if from_match:
            table_name = from_match.group(1).lower()
            alias = from_match.group(2).lower()
            alias_to_table_map[alias] = table_name
        
        # 匹配 JOIN table_name alias 格式
        join_pattern = r'JOIN\s+(\w+)\s+(\w+)'
        join_matches = re.finditer(join_pattern, sql_text, re.IGNORECASE)
        for match in join_matches:
            table_name = match.group(1).lower()
            alias = match.group(2).lower()
            alias_to_table_map[alias] = table_name
    
    # 添加参数节点
    for param in result.parameters:
        nodes.append({
            "id": f"param_{param.name}",
            "label": param.name,
            "type": "parameter",
            "group": "parameter",
            "data": {
                "direction": param.direction,
                "data_type": param.data_type,
                "used_in": param.used_in_statements
            }
        })
    
    # 添加物理表节点
    for table_name, table in result.table_field_analysis.physical_tables.items():
        nodes.append({
            "id": f"table_{table_name}",
            "label": table_name,
            "type": "physical_table",
            "group": "physical_table",
            "data": {
                "fields": table.fields,
                "sql_ids": table.source_sql_ids
            }
        })
    
    # 添加临时表节点
    for table_name, table in result.table_field_analysis.temp_tables.items():
        nodes.append({
            "id": f"table_{table_name}",
            "label": table_name,
            "type": "temp_table",
            "group": "temp_table",
            "data": {
                "fields": table.fields,
                "sql_ids": table.source_sql_ids
            }
        })
    
    # 添加数据流边
    for stmt in result.sp_structure.sql_statements:
        for source_table in stmt.source_tables:
            for target_table in stmt.target_tables:
                edges.append({
                    "id": f"flow_{stmt.statement_id}_{source_table}_{target_table}",
                    "source": f"table_{source_table}",
                    "target": f"table_{target_table}",
                    "type": "data_flow",
                    "label": stmt.statement_type.value,
                    "data": {
                        "statement_id": stmt.statement_id,
                        "statement_type": stmt.statement_type.value,
                        "raw_sql": stmt.raw_sql
                    }
                })
        
        # 添加参数使用边
        for param_name in stmt.parameters_used:
            for table_name in stmt.source_tables + stmt.target_tables:
                edges.append({
                    "id": f"param_{stmt.statement_id}_{param_name}_{table_name}",
                    "source": f"param_{param_name}",
                    "target": f"table_{table_name}",
                    "type": "parameter_usage",
                    "label": "uses",
                    "data": {
                        "statement_id": stmt.statement_id
                    }
                })
    
    # 添加JOIN条件边
    # 首先创建一个表名映射，将别名映射到实际表名
    table_alias_map = {}
    all_table_names = set()
    
    # 收集所有表名
    for table_name in result.table_field_analysis.physical_tables.keys():
        all_table_names.add(table_name)
    for table_name in result.table_field_analysis.temp_tables.keys():
        all_table_names.add(table_name)
    
    # 创建别名到表名的映射
    for table_name in all_table_names:
        # 尝试匹配别名（通常是表名的第一个字母或前几个字母）
        table_alias_map[table_name] = table_name  # 完整表名
        if len(table_name) > 0:
            table_alias_map[table_name[0]] = table_name  # 首字母别名
            table_alias_map[table_name[0].lower()] = table_name  # 小写首字母别名
    
    # 特殊处理常见的别名模式
    for table_name in all_table_names:
        if 'employees' in table_name.lower():
            table_alias_map['e'] = table_name
            table_alias_map['emp'] = table_name
        elif 'departments' in table_name.lower():
            table_alias_map['d'] = table_name
            table_alias_map['dept'] = table_name
        elif 'temp' in table_name.lower():
            table_alias_map['t'] = table_name
    
    for join_cond in result.conditions_and_logic.join_conditions:
<<<<<<< HEAD
        # 将别名转换为实际表名
        left_table = alias_to_table_map.get(join_cond.left_table.lower(), join_cond.left_table)
        right_table = alias_to_table_map.get(join_cond.right_table.lower(), join_cond.right_table)
        
        edges.append({
            "id": f"join_{left_table}_{right_table}",
            "source": f"table_{left_table}",
            "target": f"table_{right_table}",
            "type": "join_condition",
            "label": f"{join_cond.join_type} JOIN",
            "data": {
                "left_field": join_cond.left_field,
                "right_field": join_cond.right_field,
                "condition": join_cond.condition_text
            }
        })
=======
        # 解析表名，优先使用映射，如果没有则使用原名
        left_table = table_alias_map.get(join_cond.left_table, join_cond.left_table)
        right_table = table_alias_map.get(join_cond.right_table, join_cond.right_table)
        
        # 确保两个表都存在于节点列表中
        left_node_id = f"table_{left_table}"
        right_node_id = f"table_{right_table}"
        
        # 检查节点是否存在
        node_ids = {node["id"] for node in nodes}
        if left_node_id in node_ids and right_node_id in node_ids:
            edges.append({
                "id": f"join_{left_table}_{right_table}",
                "source": left_node_id,
                "target": right_node_id,
                "type": "join_condition",
                "label": f"{join_cond.join_type} JOIN",
                "data": {
                    "left_field": join_cond.left_field,
                    "right_field": join_cond.right_field,
                    "condition": join_cond.condition_text,
                    "left_table_alias": join_cond.left_table,
                    "right_table_alias": join_cond.right_table
                }
            })
        else:
            # 记录警告，但不创建边
            logger.warning(f"跳过JOIN条件：找不到表节点 {left_table} 或 {right_table}")
            logger.warning(f"可用节点: {[node['id'] for node in nodes]}")
>>>>>>> origin/dev
    
    return {
        "nodes": nodes,
        "edges": edges,
        "layout": "cose",  # 推荐的布局算法
        "metadata": {
            "node_count": len(nodes),
            "edge_count": len(edges),
            "generated_at": "2024-12-07"
        }
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app", 
        host="0.0.0.0", 
        port=8000, 
        reload=True,
        log_level="info"
    ) 
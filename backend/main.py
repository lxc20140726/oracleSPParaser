#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import os
from pathlib import Path

# 添加src路径
src_path = Path(__file__).parent.parent / "src"
sys.path.insert(0, str(src_path))

from fastapi import FastAPI, HTTPException, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
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
if static_dir.exists():
    app.mount("/static", StaticFiles(directory=str(static_dir)), name="static")
    logger.info(f"挂载静态文件目录: {static_dir}")
else:
    logger.warning(f"静态文件目录不存在，跳过挂载: {static_dir}")

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
    for join_cond in result.conditions_and_logic.join_conditions:
        edges.append({
            "id": f"join_{join_cond.left_table}_{join_cond.right_table}",
            "source": f"table_{join_cond.left_table}",
            "target": f"table_{join_cond.right_table}",
            "type": "join_condition",
            "label": f"{join_cond.join_type} JOIN",
            "data": {
                "left_field": join_cond.left_field,
                "right_field": join_cond.right_field,
                "condition": join_cond.condition_text
            }
        })
    
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
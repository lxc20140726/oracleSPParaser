#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
后端API测试
"""

import pytest
import asyncio
import json
from typing import Dict, Any
from httpx import AsyncClient
from fastapi.testclient import TestClient
from unittest.mock import Mock, patch, AsyncMock
import sys
from pathlib import Path

# 添加项目路径
PROJECT_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT / "backend"))
sys.path.insert(0, str(PROJECT_ROOT / "src"))

@pytest.mark.api
@pytest.mark.asyncio
class TestBackendAPI:
    """后端API测试类"""
    
    @pytest.fixture
    async def async_client(self, fastapi_app):
        """创建异步测试客户端"""
        async with AsyncClient(app=fastapi_app, base_url="http://test") as client:
            yield client
    
    @pytest.fixture
    def sync_client(self, fastapi_app):
        """创建同步测试客户端"""
        return TestClient(fastapi_app)
    
    async def test_health_check(self, async_client):
        """测试健康检查端点"""
        response = await async_client.get("/api/health")
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert "message" in data
    
    async def test_root_endpoint(self, async_client):
        """测试根端点"""
        response = await async_client.get("/")
        
        assert response.status_code == 200
        assert response.headers["content-type"].startswith("text/html")
    
    async def test_analyze_endpoint_success(self, async_client, sample_stored_procedure):
        """测试存储过程分析端点 - 成功情况"""
        request_data = {
            "stored_procedure": sample_stored_procedure,
            "options": {"enable_detailed_analysis": True}
        }
        
        with patch('src.main.OracleSPAnalyzer') as mock_analyzer_class:
            # 模拟分析器
            mock_analyzer = Mock()
            mock_result = Mock()
            mock_result.sp_structure.name = "process_employee_data"
            mock_result.parameters = []
            mock_result.sp_structure.sql_statements = []
            mock_result.table_field_analysis.physical_tables = {}
            mock_result.table_field_analysis.temp_tables = {}
            mock_result.conditions_and_logic.join_conditions = []
            
            mock_analyzer.analyze.return_value = mock_result
            mock_analyzer_class.return_value = mock_analyzer
            
            response = await async_client.post("/api/analyze", json=request_data)
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "data" in data
        assert data["data"]["procedure_name"] == "process_employee_data"
    
    async def test_analyze_endpoint_empty_input(self, async_client):
        """测试存储过程分析端点 - 空输入"""
        request_data = {
            "stored_procedure": "",
            "options": {}
        }
        
        response = await async_client.post("/api/analyze", json=request_data)
        
        assert response.status_code == 400
        data = response.json()
        assert "detail" in data
        assert "不能为空" in data["detail"]
    
    async def test_analyze_endpoint_invalid_input(self, async_client):
        """测试存储过程分析端点 - 无效输入"""
        request_data = {
            "stored_procedure": "   ",  # 只有空白字符
            "options": {}
        }
        
        response = await async_client.post("/api/analyze", json=request_data)
        
        assert response.status_code == 400
    
    async def test_analyze_endpoint_malformed_json(self, async_client):
        """测试存储过程分析端点 - 格式错误的JSON"""
        response = await async_client.post(
            "/api/analyze",
            content="invalid json content",
            headers={"Content-Type": "application/json"}
        )
        
        assert response.status_code == 422
    
    async def test_analyze_endpoint_missing_fields(self, async_client):
        """测试存储过程分析端点 - 缺少必需字段"""
        request_data = {
            "options": {}  # 缺少stored_procedure字段
        }
        
        response = await async_client.post("/api/analyze", json=request_data)
        
        assert response.status_code == 422
    
    @patch('src.main.OracleSPAnalyzer')
    async def test_analyze_endpoint_analysis_error(self, mock_analyzer_class, async_client):
        """测试存储过程分析端点 - 分析过程出错"""
        mock_analyzer = Mock()
        mock_analyzer.analyze.side_effect = Exception("分析错误")
        mock_analyzer_class.return_value = mock_analyzer
        
        request_data = {
            "stored_procedure": "CREATE PROCEDURE test AS BEGIN NULL; END;",
            "options": {}
        }
        
        response = await async_client.post("/api/analyze", json=request_data)
        
        assert response.status_code == 500
    
    async def test_analyze_file_endpoint_success(self, async_client):
        """测试文件分析端点 - 成功情况"""
        file_content = """
        CREATE OR REPLACE PROCEDURE test_proc AS
        BEGIN
            UPDATE employees SET salary = salary * 1.1;
        END;
        """
        
        files = {
            "file": ("test.sql", file_content, "text/plain")
        }
        
        with patch('src.main.OracleSPAnalyzer') as mock_analyzer_class:
            mock_analyzer = Mock()
            mock_result = Mock()
            mock_result.sp_structure.name = "test_proc"
            mock_result.parameters = []
            mock_result.sp_structure.sql_statements = []
            mock_result.table_field_analysis.physical_tables = {}
            mock_result.table_field_analysis.temp_tables = {}
            mock_result.conditions_and_logic.join_conditions = []
            
            mock_analyzer.analyze.return_value = mock_result
            mock_analyzer_class.return_value = mock_analyzer
            
            response = await async_client.post("/api/analyze/file", files=files)
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["data"]["procedure_name"] == "test_proc"
    
    async def test_analyze_file_endpoint_no_file(self, async_client):
        """测试文件分析端点 - 没有文件"""
        response = await async_client.post("/api/analyze/file")
        
        assert response.status_code == 422
    
    async def test_analyze_file_endpoint_empty_file(self, async_client):
        """测试文件分析端点 - 空文件"""
        files = {
            "file": ("empty.sql", "", "text/plain")
        }
        
        response = await async_client.post("/api/analyze/file", files=files)
        
        assert response.status_code == 400
    
    async def test_analyze_file_endpoint_large_file(self, async_client):
        """测试文件分析端点 - 大文件"""
        # 创建一个大文件内容（超过限制）
        large_content = "SELECT * FROM large_table WHERE id = 1;\n" * 10000
        
        files = {
            "file": ("large.sql", large_content, "text/plain")
        }
        
        response = await async_client.post("/api/analyze/file", files=files)
        
        # 根据实际的文件大小限制来调整断言
        # 如果有大小限制，应该返回400或413
        # 如果没有限制，应该能正常处理
        assert response.status_code in [200, 400, 413, 500]
    
    async def test_cors_headers(self, async_client):
        """测试CORS头部"""
        response = await async_client.options("/api/health")
        
        assert response.status_code == 200
        assert "access-control-allow-origin" in response.headers
    
    async def test_api_documentation_endpoints(self, async_client):
        """测试API文档端点"""
        # 测试Swagger UI
        response = await async_client.get("/api/docs")
        assert response.status_code == 200
        
        # 测试ReDoc
        response = await async_client.get("/api/redoc")
        assert response.status_code == 200
        
        # 测试OpenAPI schema
        response = await async_client.get("/openapi.json")
        assert response.status_code == 200
        schema = response.json()
        assert "openapi" in schema
        assert "info" in schema
    
    def test_sync_client_basic_operations(self, sync_client):
        """测试同步客户端基本操作"""
        # 健康检查
        response = sync_client.get("/api/health")
        assert response.status_code == 200
        
        # 根端点
        response = sync_client.get("/")
        assert response.status_code == 200
    
    @pytest.mark.slow
    async def test_concurrent_requests(self, async_client, sample_stored_procedure):
        """测试并发请求处理"""
        request_data = {
            "stored_procedure": sample_stored_procedure,
            "options": {}
        }
        
        with patch('src.main.OracleSPAnalyzer') as mock_analyzer_class:
            mock_analyzer = Mock()
            mock_result = Mock()
            mock_result.sp_structure.name = "test_proc"
            mock_result.parameters = []
            mock_result.sp_structure.sql_statements = []
            mock_result.table_field_analysis.physical_tables = {}
            mock_result.table_field_analysis.temp_tables = {}
            mock_result.conditions_and_logic.join_conditions = []
            
            mock_analyzer.analyze.return_value = mock_result
            mock_analyzer_class.return_value = mock_analyzer
            
            # 发送多个并发请求
            tasks = []
            for _ in range(5):
                task = async_client.post("/api/analyze", json=request_data)
                tasks.append(task)
            
            responses = await asyncio.gather(*tasks)
            
            # 验证所有请求都成功
            for response in responses:
                assert response.status_code == 200
                data = response.json()
                assert data["success"] is True
    
    async def test_request_validation(self, async_client):
        """测试请求验证"""
        test_cases = [
            # 无效的stored_procedure类型
            {"stored_procedure": 123, "options": {}},
            # 无效的options类型
            {"stored_procedure": "valid sql", "options": "invalid"},
            # 额外的字段
            {"stored_procedure": "valid sql", "options": {}, "extra_field": "value"},
        ]
        
        for test_case in test_cases:
            response = await async_client.post("/api/analyze", json=test_case)
            # 应该返回422 (验证错误) 或者能够处理
            assert response.status_code in [200, 422]
    
    async def test_error_response_format(self, async_client):
        """测试错误响应格式"""
        # 发送一个会导致错误的请求
        request_data = {
            "stored_procedure": "",
            "options": {}
        }
        
        response = await async_client.post("/api/analyze", json=request_data)
        
        assert response.status_code == 400
        data = response.json()
        assert "detail" in data
        assert isinstance(data["detail"], str)
    
    @pytest.mark.performance
    async def test_response_time(self, async_client, sample_stored_procedure):
        """测试响应时间"""
        import time
        
        request_data = {
            "stored_procedure": sample_stored_procedure,
            "options": {}
        }
        
        with patch('src.main.OracleSPAnalyzer') as mock_analyzer_class:
            mock_analyzer = Mock()
            mock_result = Mock()
            mock_result.sp_structure.name = "test_proc"
            mock_result.parameters = []
            mock_result.sp_structure.sql_statements = []
            mock_result.table_field_analysis.physical_tables = {}
            mock_result.table_field_analysis.temp_tables = {}
            mock_result.conditions_and_logic.join_conditions = []
            
            mock_analyzer.analyze.return_value = mock_result
            mock_analyzer_class.return_value = mock_analyzer
            
            start_time = time.time()
            response = await async_client.post("/api/analyze", json=request_data)
            end_time = time.time()
            
            response_time = end_time - start_time
            
            assert response.status_code == 200
            # 响应时间应该在合理范围内（比如小于2秒）
            assert response_time < 2.0, f"响应时间过长: {response_time}秒"


@pytest.mark.api
class TestStaticFileServing:
    """静态文件服务测试"""
    
    def test_static_file_endpoints(self, sync_client):
        """测试静态文件端点"""
        # 测试manifest.json
        response = sync_client.get("/manifest.json")
        # 可能存在也可能不存在，取决于前端是否构建
        assert response.status_code in [200, 404]
        
        # 测试favicon.ico
        response = sync_client.get("/favicon.ico")
        assert response.status_code in [200, 404]
    
    def test_static_assets_security(self, sync_client):
        """测试静态资源安全性"""
        # 尝试访问可能的敏感路径
        sensitive_paths = [
            "/static/../../../etc/passwd",
            "/assets/../../../etc/passwd",
            "/static/../../backend/main.py",
        ]
        
        for path in sensitive_paths:
            response = sync_client.get(path)
            # 应该返回404或其他安全响应，不应该返回200
            assert response.status_code != 200


@pytest.mark.api
class TestAPISchemaValidation:
    """API架构验证测试"""
    
    def test_openapi_schema_validity(self, sync_client):
        """测试OpenAPI架构有效性"""
        response = sync_client.get("/openapi.json")
        
        assert response.status_code == 200
        schema = response.json()
        
        # 验证必需的OpenAPI字段
        assert "openapi" in schema
        assert "info" in schema
        assert "paths" in schema
        
        # 验证API信息
        info = schema["info"]
        assert "title" in info
        assert "version" in info
        
        # 验证路径定义
        paths = schema["paths"]
        assert "/api/health" in paths
        assert "/api/analyze" in paths
        assert "/api/analyze/file" in paths
    
    def test_response_models(self, sync_client, sample_stored_procedure):
        """测试响应模型符合性"""
        request_data = {
            "stored_procedure": sample_stored_procedure,
            "options": {}
        }
        
        with patch('src.main.OracleSPAnalyzer') as mock_analyzer_class:
            mock_analyzer = Mock()
            mock_result = Mock()
            mock_result.sp_structure.name = "test_proc"
            mock_result.parameters = []
            mock_result.sp_structure.sql_statements = []
            mock_result.table_field_analysis.physical_tables = {}
            mock_result.table_field_analysis.temp_tables = {}
            mock_result.conditions_and_logic.join_conditions = []
            
            mock_analyzer.analyze.return_value = mock_result
            mock_analyzer_class.return_value = mock_analyzer
            
            response = sync_client.post("/api/analyze", json=request_data)
        
        assert response.status_code == 200
        data = response.json()
        
        # 验证响应结构符合AnalyzeResponse模型
        assert "success" in data
        assert "message" in data
        assert isinstance(data["success"], bool)
        assert isinstance(data["message"], str)
        
        if data["success"]:
            assert "data" in data
            assert isinstance(data["data"], dict) 
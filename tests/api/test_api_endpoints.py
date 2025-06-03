"""
API端点测试
测试FastAPI后端的各个接口
"""

import pytest
import sys
import json
import io
from pathlib import Path
from fastapi.testclient import TestClient

# 添加项目路径
backend_path = Path(__file__).parent.parent.parent / "backend"
sys.path.insert(0, str(backend_path))

from backend.main import app


class TestAPIEndpoints:
    """API端点测试"""
    
    def setup_method(self):
        """测试前的设置"""
        self.client = TestClient(app)
    
    def test_health_check(self):
        """测试健康检查接口"""
        response = self.client.get("/api/health")
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert "timestamp" in data
        assert "version" in data
    
    def test_analyze_simple_procedure(self, sample_simple_procedure):
        """测试分析简单存储过程"""
        payload = {
            "stored_procedure": sample_simple_procedure,
            "options": {
                "include_visualization": True,
                "detail_level": "full"
            }
        }
        
        response = self.client.post("/api/analyze", json=payload)
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "data" in data
        
        # 验证返回数据结构
        analysis_data = data["data"]
        assert analysis_data["procedure_name"] == "update_employee_salary"
        assert len(analysis_data["parameters"]) == 2
        assert "employees" in analysis_data["tables"]["physical"]
    
    def test_analyze_complex_procedure(self, sample_complex_procedure):
        """测试分析复杂存储过程"""
        payload = {
            "stored_procedure": sample_complex_procedure
        }
        
        response = self.client.post("/api/analyze", json=payload)
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        
        analysis_data = data["data"]
        assert analysis_data["procedure_name"] == "process_employee_data"
        assert len(analysis_data["parameters"]) == 3
        
        # 验证表分析结果
        tables = analysis_data["tables"]
        assert "departments" in tables["physical"]
        assert "employees" in tables["physical"]
        assert "temp_emp_summary" in tables["temporary"]
        
        # 验证JOIN条件
        assert len(analysis_data["join_conditions"]) >= 1
        
        # 验证统计信息
        stats = analysis_data["statistics"]
        assert stats["parameter_count"] == 3
        assert stats["sql_statement_count"] >= 3
        assert stats["physical_table_count"] >= 3
    
    def test_analyze_with_joins(self, sample_procedure_with_joins):
        """测试分析包含JOIN的存储过程"""
        payload = {
            "stored_procedure": sample_procedure_with_joins,
            "options": {
                "include_visualization": True
            }
        }
        
        response = self.client.post("/api/analyze", json=payload)
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        
        analysis_data = data["data"]
        assert analysis_data["procedure_name"] == "generate_department_report"
        
        # 验证JOIN条件
        join_conditions = analysis_data["join_conditions"]
        assert len(join_conditions) >= 2
        
        # 验证LEFT JOIN
        left_joins = [jc for jc in join_conditions if jc["join_type"] == "LEFT"]
        assert len(left_joins) >= 2
        
        # 验证可视化数据
        assert "visualization" in data
        viz_data = data["visualization"]
        assert "nodes" in viz_data
        assert "edges" in viz_data
    
    def test_analyze_invalid_procedure(self, invalid_procedure):
        """测试分析无效存储过程"""
        payload = {
            "stored_procedure": invalid_procedure
        }
        
        response = self.client.post("/api/analyze", json=payload)
        
        assert response.status_code == 200  # API应该返回200，但success=false
        data = response.json()
        assert data["success"] is False
        assert "error" in data["message"].lower() or "失败" in data["message"]
    
    def test_analyze_empty_request(self):
        """测试空请求"""
        response = self.client.post("/api/analyze", json={})
        
        assert response.status_code == 422  # 验证错误
    
    def test_analyze_missing_procedure(self):
        """测试缺少存储过程内容"""
        payload = {
            "options": {
                "include_visualization": True
            }
        }
        
        response = self.client.post("/api/analyze", json=payload)
        
        assert response.status_code == 422
    
    def test_file_upload_sql_file(self, sample_simple_procedure):
        """测试上传SQL文件"""
        # 创建临时SQL文件
        sql_content = sample_simple_procedure.encode('utf-8')
        files = {
            "file": ("test_procedure.sql", io.BytesIO(sql_content), "text/plain")
        }
        
        response = self.client.post("/api/analyze/file", files=files)
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["data"]["procedure_name"] == "update_employee_salary"
    
    def test_file_upload_txt_file(self, sample_complex_procedure):
        """测试上传TXT文件"""
        txt_content = sample_complex_procedure.encode('utf-8')
        files = {
            "file": ("procedure.txt", io.BytesIO(txt_content), "text/plain")
        }
        
        response = self.client.post("/api/analyze/file", files=files)
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["data"]["procedure_name"] == "process_employee_data"
    
    def test_file_upload_invalid_file_type(self):
        """测试上传无效文件类型"""
        files = {
            "file": ("test.pdf", io.BytesIO(b"fake pdf content"), "application/pdf")
        }
        
        response = self.client.post("/api/analyze/file", files=files)
        
        assert response.status_code == 400
        data = response.json()
        assert data["success"] is False
        assert "文件类型" in data["message"] or "file type" in data["message"].lower()
    
    def test_file_upload_empty_file(self):
        """测试上传空文件"""
        files = {
            "file": ("empty.sql", io.BytesIO(b""), "text/plain")
        }
        
        response = self.client.post("/api/analyze/file", files=files)
        
        assert response.status_code == 400
        data = response.json()
        assert data["success"] is False
        assert "空" in data["message"] or "empty" in data["message"].lower()
    
    def test_file_upload_large_file(self):
        """测试上传大文件"""
        # 创建一个大的SQL文件（模拟）
        large_content = "-- " + "x" * (10 * 1024 * 1024)  # 10MB
        files = {
            "file": ("large.sql", io.BytesIO(large_content.encode('utf-8')), "text/plain")
        }
        
        response = self.client.post("/api/analyze/file", files=files)
        
        # 应该返回文件过大错误
        assert response.status_code == 413 or (response.status_code == 400 and not response.json()["success"])
    
    def test_analyze_with_options(self, sample_simple_procedure):
        """测试带选项的分析"""
        payload = {
            "stored_procedure": sample_simple_procedure,
            "options": {
                "include_visualization": False,
                "detail_level": "basic",
                "analyze_parameters": True,
                "analyze_tables": True,
                "analyze_joins": True
            }
        }
        
        response = self.client.post("/api/analyze", json=payload)
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        
        # 验证不包含可视化数据
        assert "visualization" not in data or data["visualization"] is None
    
    def test_concurrent_requests(self, sample_simple_procedure):
        """测试并发请求"""
        import threading
        import time
        
        results = []
        
        def make_request():
            payload = {"stored_procedure": sample_simple_procedure}
            response = self.client.post("/api/analyze", json=payload)
            results.append(response.status_code)
        
        # 创建多个并发请求
        threads = []
        for i in range(5):
            thread = threading.Thread(target=make_request)
            threads.append(thread)
            thread.start()
        
        # 等待所有请求完成
        for thread in threads:
            thread.join()
        
        # 验证所有请求都成功
        assert len(results) == 5
        assert all(status == 200 for status in results)
    
    def test_api_error_handling(self):
        """测试API错误处理"""
        # 测试不存在的端点
        response = self.client.get("/api/nonexistent")
        assert response.status_code == 404
        
        # 测试错误的HTTP方法
        response = self.client.get("/api/analyze")  # 应该是POST
        assert response.status_code == 405
    
    def test_api_response_format(self, sample_simple_procedure):
        """测试API响应格式一致性"""
        payload = {"stored_procedure": sample_simple_procedure}
        response = self.client.post("/api/analyze", json=payload)
        
        assert response.status_code == 200
        data = response.json()
        
        # 验证响应格式
        required_fields = ["success", "message", "data"]
        for field in required_fields:
            assert field in data
        
        # 验证数据字段
        analysis_data = data["data"]
        required_data_fields = [
            "procedure_name", "parameters", "sql_statements", 
            "tables", "statistics"
        ]
        for field in required_data_fields:
            assert field in analysis_data
    
    def test_api_performance(self, sample_complex_procedure):
        """测试API性能"""
        import time
        
        payload = {"stored_procedure": sample_complex_procedure}
        
        start_time = time.time()
        response = self.client.post("/api/analyze", json=payload)
        end_time = time.time()
        
        assert response.status_code == 200
        assert end_time - start_time < 5  # 应该在5秒内完成 
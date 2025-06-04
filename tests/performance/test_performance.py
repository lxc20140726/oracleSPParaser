#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
性能测试
"""

import pytest
import time
import statistics
import sys
from pathlib import Path
from typing import List, Dict, Any
import memory_profiler
import psutil
import os
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor
import threading

# 添加项目路径
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

@pytest.mark.performance
class TestAnalysisPerformance:
    """分析性能测试"""
    
    def test_single_analysis_performance(self, oracle_sp_analyzer, sample_stored_procedure):
        """测试单次分析性能"""
        # 预热
        oracle_sp_analyzer.analyze(sample_stored_procedure)
        
        # 性能测试
        execution_times = []
        for _ in range(10):
            start_time = time.time()
            result = oracle_sp_analyzer.analyze(sample_stored_procedure)
            end_time = time.time()
            
            execution_times.append(end_time - start_time)
            assert result is not None
        
        # 统计分析
        avg_time = statistics.mean(execution_times)
        median_time = statistics.median(execution_times)
        min_time = min(execution_times)
        max_time = max(execution_times)
        
        print(f"\n单次分析性能统计:")
        print(f"平均时间: {avg_time:.4f}秒")
        print(f"中位时间: {median_time:.4f}秒")
        print(f"最小时间: {min_time:.4f}秒")
        print(f"最大时间: {max_time:.4f}秒")
        
        # 性能断言
        assert avg_time < 2.0, f"平均分析时间过长: {avg_time}秒"
        assert max_time < 5.0, f"最大分析时间过长: {max_time}秒"
    
    @pytest.mark.slow
    def test_large_procedure_performance(self, oracle_sp_analyzer):
        """测试大型存储过程性能"""
        # 生成大型存储过程
        large_sp_parts = [
            "CREATE OR REPLACE PROCEDURE large_perf_test AS",
            "    v_counter NUMBER := 0;",
            "    v_result VARCHAR2(4000);",
            "BEGIN"
        ]
        
        # 添加500个SQL语句
        for i in range(500):
            large_sp_parts.extend([
                f"    -- 操作组 {i+1}",
                f"    INSERT INTO performance_table_{i % 20} (id, data, status) VALUES ({i}, 'test_data_{i}', 'NEW');",
                f"    UPDATE performance_table_{i % 20} SET status = 'PROCESSING' WHERE id = {i};",
                f"    SELECT COUNT(*) INTO v_counter FROM performance_table_{i % 20} WHERE status = 'PROCESSING';",
                f"    IF v_counter > 10 THEN",
                f"        UPDATE performance_table_{i % 20} SET status = 'COMPLETED' WHERE status = 'PROCESSING';",
                f"    END IF;",
            ])
        
        large_sp_parts.extend([
            "    COMMIT;",
            "EXCEPTION",
            "    WHEN OTHERS THEN",
            "        ROLLBACK;",
            "        RAISE;",
            "END;"
        ])
        
        large_sp = "\n".join(large_sp_parts)
        
        # 性能测试
        start_time = time.time()
        result = oracle_sp_analyzer.analyze(large_sp)
        end_time = time.time()
        
        analysis_time = end_time - start_time
        
        print(f"\n大型存储过程分析:")
        print(f"存储过程行数: {len(large_sp.split(chr(10)))}")
        print(f"分析时间: {analysis_time:.4f}秒")
        print(f"识别的SQL语句数: {len(result.sp_structure.sql_statements)}")
        
        # 性能断言
        assert analysis_time < 30.0, f"大型存储过程分析时间过长: {analysis_time}秒"
        assert result is not None
        assert len(result.sp_structure.sql_statements) >= 400  # 应该识别出大部分SQL语句
    
    def test_memory_usage_analysis(self, oracle_sp_analyzer, sample_stored_procedure):
        """测试内存使用情况"""
        process = psutil.Process(os.getpid())
        
        # 记录初始内存
        initial_memory = process.memory_info().rss / 1024 / 1024  # MB
        
        # 执行多次分析，观察内存变化
        memory_readings = [initial_memory]
        
        for i in range(20):
            result = oracle_sp_analyzer.analyze(sample_stored_procedure)
            assert result is not None
            
            current_memory = process.memory_info().rss / 1024 / 1024  # MB
            memory_readings.append(current_memory)
        
        final_memory = memory_readings[-1]
        max_memory = max(memory_readings)
        memory_increase = final_memory - initial_memory
        
        print(f"\n内存使用分析:")
        print(f"初始内存: {initial_memory:.2f}MB")
        print(f"最终内存: {final_memory:.2f}MB")
        print(f"峰值内存: {max_memory:.2f}MB")
        print(f"内存增长: {memory_increase:.2f}MB")
        
        # 内存断言
        assert memory_increase < 50, f"内存增长过大: {memory_increase}MB"
        assert max_memory - initial_memory < 100, f"峰值内存使用过大: {max_memory - initial_memory}MB"
    
    @pytest.mark.slow
    def test_concurrent_analysis_performance(self, oracle_sp_analyzer, test_data_generator):
        """测试并发分析性能"""
        # 生成多个不同复杂度的存储过程
        procedures = []
        for complexity in ['simple', 'medium', 'simple', 'medium', 'simple']:
            sp = test_data_generator.generate_stored_procedure(complexity)
            procedures.append(sp)
        
        # 串行执行测试
        start_time = time.time()
        serial_results = []
        for sp in procedures:
            result = oracle_sp_analyzer.analyze(sp)
            serial_results.append(result)
        serial_time = time.time() - start_time
        
        # 并发执行测试
        def analyze_concurrent(sp):
            return oracle_sp_analyzer.analyze(sp)
        
        start_time = time.time()
        with ThreadPoolExecutor(max_workers=3) as executor:
            concurrent_results = list(executor.map(analyze_concurrent, procedures))
        concurrent_time = time.time() - start_time
        
        print(f"\n并发性能测试:")
        print(f"串行执行时间: {serial_time:.4f}秒")
        print(f"并发执行时间: {concurrent_time:.4f}秒")
        print(f"并发加速比: {serial_time / concurrent_time:.2f}x")
        
        # 验证结果正确性
        assert len(serial_results) == len(concurrent_results) == len(procedures)
        for result in serial_results + concurrent_results:
            assert result is not None
        
        # 性能断言 - 并发应该有一定程度的加速
        assert concurrent_time <= serial_time * 1.2, "并发执行没有性能优势"
    
    def test_memory_leak_detection(self, oracle_sp_analyzer):
        """测试内存泄漏检测"""
        import gc
        
        process = psutil.Process(os.getpid())
        
        # 基准内存测量
        gc.collect()  # 强制垃圾回收
        baseline_memory = process.memory_info().rss / 1024 / 1024  # MB
        
        # 执行大量分析操作
        for iteration in range(50):
            sp = f"""
            CREATE OR REPLACE PROCEDURE leak_test_{iteration} AS
            BEGIN
                INSERT INTO test_table_{iteration} VALUES ({iteration}, 'data');
                UPDATE test_table_{iteration} SET status = 'processed' WHERE id = {iteration};
                SELECT COUNT(*) FROM test_table_{iteration};
                DELETE FROM test_table_{iteration} WHERE id < {iteration - 10};
            END;
            """
            
            result = oracle_sp_analyzer.analyze(sp)
            assert result is not None
            
            # 每10次迭代检查一次内存
            if iteration % 10 == 9:
                gc.collect()
                current_memory = process.memory_info().rss / 1024 / 1024  # MB
                memory_growth = current_memory - baseline_memory
                
                print(f"迭代 {iteration + 1}: 内存增长 {memory_growth:.2f}MB")
                
                # 如果内存增长过快，可能存在内存泄漏
                assert memory_growth < 100, f"可能存在内存泄漏，内存增长: {memory_growth}MB"
        
        # 最终内存检查
        gc.collect()
        final_memory = process.memory_info().rss / 1024 / 1024  # MB
        total_growth = final_memory - baseline_memory
        
        print(f"\n内存泄漏检测结果:")
        print(f"基准内存: {baseline_memory:.2f}MB")
        print(f"最终内存: {final_memory:.2f}MB")
        print(f"总增长: {total_growth:.2f}MB")
        
        assert total_growth < 80, f"内存泄漏检测失败，总增长: {total_growth}MB"
    
    def test_cpu_intensive_analysis(self, oracle_sp_analyzer):
        """测试CPU密集型分析"""
        # 创建计算密集型的存储过程
        cpu_intensive_sp = """
        CREATE OR REPLACE PROCEDURE cpu_intensive_analysis AS
        BEGIN
            -- 大量的JOIN操作
            INSERT INTO result_table
            SELECT DISTINCT 
                t1.id, t1.name, t2.description, t3.category, t4.status,
                t5.amount, t6.date_created, t7.location, t8.priority
            FROM table1 t1
            INNER JOIN table2 t2 ON t1.ref_id = t2.id
            LEFT JOIN table3 t3 ON t2.category_id = t3.id
            RIGHT JOIN table4 t4 ON t3.status_id = t4.id
            FULL OUTER JOIN table5 t5 ON t4.amount_id = t5.id
            CROSS JOIN table6 t6 ON t5.date_id = t6.id
            INNER JOIN table7 t7 ON t6.location_id = t7.id
            LEFT JOIN table8 t8 ON t7.priority_id = t8.id
            WHERE t1.active = 1
            AND t2.deleted = 0
            AND t3.valid_from <= SYSDATE
            AND t3.valid_to >= SYSDATE
            AND (t4.status IN ('ACTIVE', 'PENDING', 'PROCESSING')
                 OR t4.status IS NULL)
            AND t5.amount BETWEEN 100 AND 100000
            AND t6.date_created >= ADD_MONTHS(SYSDATE, -12)
            AND t7.location LIKE '%OFFICE%'
            AND (t8.priority = 'HIGH' 
                 OR (t8.priority = 'MEDIUM' AND t5.amount > 1000)
                 OR (t8.priority = 'LOW' AND t5.amount > 5000));
            
            -- 复杂的聚合查询
            INSERT INTO summary_table
            SELECT 
                category,
                location,
                status,
                COUNT(*) as total_count,
                SUM(amount) as total_amount,
                AVG(amount) as avg_amount,
                MIN(amount) as min_amount,
                MAX(amount) as max_amount,
                STDDEV(amount) as stddev_amount,
                VARIANCE(amount) as var_amount
            FROM result_table
            GROUP BY CUBE(category, location, status)
            HAVING COUNT(*) > 10
            AND SUM(amount) > 1000
            ORDER BY category, location, status;
        END;
        """
        
        # CPU使用率监控
        process = psutil.Process(os.getpid())
        cpu_before = process.cpu_percent()
        
        start_time = time.time()
        result = oracle_sp_analyzer.analyze(cpu_intensive_sp)
        end_time = time.time()
        
        cpu_after = process.cpu_percent()
        analysis_time = end_time - start_time
        
        print(f"\nCPU密集型分析:")
        print(f"分析时间: {analysis_time:.4f}秒")
        print(f"CPU使用率变化: {cpu_before:.2f}% -> {cpu_after:.2f}%")
        print(f"识别的连接条件数: {len(result.conditions_and_logic.join_conditions)}")
        print(f"识别的WHERE条件数: {len(result.conditions_and_logic.where_conditions)}")
        
        # 验证分析质量
        assert result is not None
        assert len(result.conditions_and_logic.join_conditions) >= 7  # 应该识别出多个JOIN
        assert len(result.table_field_analysis.physical_tables) >= 8  # 应该识别出多个表
        assert analysis_time < 15.0, f"CPU密集型分析时间过长: {analysis_time}秒"


@pytest.mark.performance
class TestAPIPerformance:
    """API性能测试"""
    
    @pytest.mark.asyncio
    async def test_api_response_time(self, async_client, sample_stored_procedure):
        """测试API响应时间"""
        from unittest.mock import patch, Mock
        
        request_data = {
            "stored_procedure": sample_stored_procedure,
            "options": {}
        }
        
        with patch('src.main.OracleSPAnalyzer') as mock_analyzer_class:
            mock_analyzer = Mock()
            mock_result = Mock()
            mock_result.sp_structure.name = "performance_test"
            mock_result.parameters = []
            mock_result.sp_structure.sql_statements = []
            mock_result.table_field_analysis.physical_tables = {}
            mock_result.table_field_analysis.temp_tables = {}
            mock_result.conditions_and_logic.join_conditions = []
            
            mock_analyzer.analyze.return_value = mock_result
            mock_analyzer_class.return_value = mock_analyzer
            
            # 测试多次请求的响应时间
            response_times = []
            
            for _ in range(10):
                start_time = time.time()
                response = await async_client.post("/api/analyze", json=request_data)
                end_time = time.time()
                
                response_times.append(end_time - start_time)
                assert response.status_code == 200
            
            avg_response_time = statistics.mean(response_times)
            max_response_time = max(response_times)
            min_response_time = min(response_times)
            
            print(f"\nAPI响应时间统计:")
            print(f"平均响应时间: {avg_response_time:.4f}秒")
            print(f"最大响应时间: {max_response_time:.4f}秒")
            print(f"最小响应时间: {min_response_time:.4f}秒")
            
            # 性能断言
            assert avg_response_time < 1.0, f"平均API响应时间过长: {avg_response_time}秒"
            assert max_response_time < 2.0, f"最大API响应时间过长: {max_response_time}秒"
    
    @pytest.mark.asyncio
    @pytest.mark.slow
    async def test_api_concurrent_requests(self, async_client, sample_stored_procedure):
        """测试API并发请求性能"""
        import asyncio
        from unittest.mock import patch, Mock
        
        request_data = {
            "stored_procedure": sample_stored_procedure,
            "options": {}
        }
        
        with patch('src.main.OracleSPAnalyzer') as mock_analyzer_class:
            mock_analyzer = Mock()
            mock_result = Mock()
            mock_result.sp_structure.name = "concurrent_test"
            mock_result.parameters = []
            mock_result.sp_structure.sql_statements = []
            mock_result.table_field_analysis.physical_tables = {}
            mock_result.table_field_analysis.temp_tables = {}
            mock_result.conditions_and_logic.join_conditions = []
            
            mock_analyzer.analyze.return_value = mock_result
            mock_analyzer_class.return_value = mock_analyzer
            
            # 测试不同并发级别
            concurrency_levels = [1, 5, 10, 20]
            
            for concurrent_requests in concurrency_levels:
                start_time = time.time()
                
                # 创建并发请求
                tasks = []
                for _ in range(concurrent_requests):
                    task = async_client.post("/api/analyze", json=request_data)
                    tasks.append(task)
                
                # 等待所有请求完成
                responses = await asyncio.gather(*tasks, return_exceptions=True)
                
                end_time = time.time()
                total_time = end_time - start_time
                
                # 验证响应
                successful_responses = 0
                for response in responses:
                    if hasattr(response, 'status_code') and response.status_code == 200:
                        successful_responses += 1
                
                requests_per_second = concurrent_requests / total_time
                
                print(f"\n并发级别 {concurrent_requests}:")
                print(f"总时间: {total_time:.4f}秒")
                print(f"成功请求: {successful_responses}/{concurrent_requests}")
                print(f"吞吐量: {requests_per_second:.2f} 请求/秒")
                
                # 性能断言
                assert successful_responses >= concurrent_requests * 0.9, f"成功率过低: {successful_responses}/{concurrent_requests}"
                assert total_time < concurrent_requests * 0.5, f"并发性能不佳: {total_time}秒处理{concurrent_requests}个请求"
    
    @pytest.mark.benchmark
    def test_benchmark_comparison(self, oracle_sp_analyzer, test_data_generator):
        """基准测试比较"""
        import pytest_benchmark
        
        # 生成测试数据
        simple_sp = test_data_generator.generate_stored_procedure('simple')
        medium_sp = test_data_generator.generate_stored_procedure('medium')
        
        # 基准测试简单存储过程
        def analyze_simple():
            return oracle_sp_analyzer.analyze(simple_sp)
        
        # 基准测试中等复杂度存储过程
        def analyze_medium():
            return oracle_sp_analyzer.analyze(medium_sp)
        
        # 如果pytest-benchmark可用，使用它进行基准测试
        try:
            import pytest_benchmark
            # 这里可以添加具体的基准测试代码
            print("\n基准测试功能可用")
        except ImportError:
            # 手动进行基准测试
            print("\n手动基准测试:")
            
            # 简单存储过程基准
            simple_times = []
            for _ in range(20):
                start = time.time()
                result = analyze_simple()
                end = time.time()
                simple_times.append(end - start)
                assert result is not None
            
            # 中等复杂度存储过程基准
            medium_times = []
            for _ in range(20):
                start = time.time()
                result = analyze_medium()
                end = time.time()
                medium_times.append(end - start)
                assert result is not None
            
            simple_avg = statistics.mean(simple_times)
            medium_avg = statistics.mean(medium_times)
            
            print(f"简单存储过程平均时间: {simple_avg:.4f}秒")
            print(f"中等存储过程平均时间: {medium_avg:.4f}秒")
            print(f"复杂度比例: {medium_avg / simple_avg:.2f}x")
            
            # 性能回归检测
            assert simple_avg < 0.5, f"简单存储过程分析时间回归: {simple_avg}秒"
            assert medium_avg < 2.0, f"中等存储过程分析时间回归: {medium_avg}秒" 
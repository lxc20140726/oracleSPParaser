#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import os
from pathlib import Path
import json

# 添加src目录到Python路径
current_dir = Path(__file__).parent
sys.path.insert(0, str(current_dir / 'src'))

from parser.sp_parser import StoredProcedureParser
from analyzer.parameter_analyzer import ParameterAnalyzer
from analyzer.table_field_analyzer import TableFieldAnalyzer
from analyzer.condition_analyzer import ConditionAnalyzer

def test_large_stored_procedure():
    """测试大型存储过程的解析能力"""
    
    print("=" * 80)
    print("          大型存储过程解析能力测试")
    print("=" * 80)
    
    # 读取存储过程文件
    sp_file_path = current_dir / 'data' / 'sp.sql'
    
    if not sp_file_path.exists():
        print(f"❌ 错误: 找不到存储过程文件 {sp_file_path}")
        return False
    
    try:
        with open(sp_file_path, 'r', encoding='utf-8') as f:
            sp_content = f.read()
        
        print(f"✅ 成功读取存储过程文件")
        print(f"📏 文件大小: {len(sp_content)} 字符")
        print(f"📄 文件行数: {sp_content.count(chr(10)) + 1} 行")
        print()
        
        # 创建解析器
        parser = StoredProcedureParser()
        param_analyzer = ParameterAnalyzer()
        table_analyzer = TableFieldAnalyzer()
        condition_analyzer = ConditionAnalyzer()
        
        print("🔍 开始解析存储过程结构...")
        
        # 解析存储过程
        sp_structure = parser.parse(sp_content)
        
        print("✅ 存储过程解析完成!")
        print()
        
        # 显示基本解析结果
        print("=" * 60)
        print("             基本解析结果")
        print("=" * 60)
        print(f"🏷️  存储过程名称: {sp_structure.name}")
        print(f"📊 参数数量: {len(sp_structure.parameters)}")
        print(f"📝 SQL语句数量: {len(sp_structure.sql_statements)}")
        print(f"📋 游标声明: {len(sp_structure.cursor_declarations)}")
        print(f"🔧 变量声明: {len(sp_structure.variable_declarations)}")
        print()
        
        # 详细参数分析
        print("=" * 60)
        print("             参数详细分析")
        print("=" * 60)
        if sp_structure.parameters:
            for i, param in enumerate(sp_structure.parameters, 1):
                direction_icon = "⬇️" if param.direction == "IN" else "⬆️" if param.direction == "OUT" else "⬆️⬇️"
                print(f"{i:2d}. {direction_icon} {param.name:20s} ({param.direction:6s}) {param.data_type}")
        else:
            print("❌ 未检测到参数")
        print()
        
        # SQL语句分析
        print("=" * 60)
        print("           SQL语句详细分析")
        print("=" * 60)
        
        statement_types = {}
        total_tables = set()
        total_conditions = 0
        
        for i, stmt in enumerate(sp_structure.sql_statements, 1):
            print(f"📝 语句 {i}: {stmt.statement_type}")
            
            # 合并源表和目标表
            all_tables = list(set(stmt.source_tables + stmt.target_tables))
            print(f"   🗃️  涉及表: {', '.join(all_tables) if all_tables else '无'}")
            print(f"   📤 读取字段: {len(stmt.fields_read)} 个")
            print(f"   📥 写入字段: {len(stmt.fields_written)} 个")
            print(f"   🔗 连接条件: {len(stmt.join_conditions)} 个")
            print(f"   🔍 过滤条件: {len(stmt.where_conditions)} 个")
            
            # 统计信息
            stmt_type = stmt.statement_type.value
            statement_types[stmt_type] = statement_types.get(stmt_type, 0) + 1
            total_tables.update(all_tables)
            total_conditions += len(stmt.join_conditions) + len(stmt.where_conditions)
            print()
        
        # 高级分析
        print("=" * 60)
        print("             高级分析结果")
        print("=" * 60)
        
        print("🔍 进一步分析参数...")
        parameters = param_analyzer.extract_parameters(sp_structure)
        print(f"✅ 参数分析完成，识别到 {len(parameters)} 个参数")
        
        print("🔍 分析表和字段关系...")
        table_analysis = table_analyzer.analyze(sp_structure)
        print(f"✅ 表分析完成:")
        print(f"   📊 实体表: {len(table_analysis.physical_tables)} 个")
        print(f"   📊 临时表: {len(table_analysis.temp_tables)} 个")
        
        print("🔍 分析条件和逻辑...")
        conditions = condition_analyzer.analyze(sp_structure)
        print(f"✅ 条件分析完成:")
        print(f"   🔗 连接条件: {len(conditions.join_conditions)} 个")
        print(f"   🔍 过滤条件: {len(conditions.where_conditions)} 个")
        print()
        
        # 复杂度评估
        print("=" * 60)
        print("           存储过程复杂度评估")
        print("=" * 60)
        
        complexity_score = 0
        complexity_factors = []
        
        # 参数复杂度
        param_count = len(sp_structure.parameters)
        if param_count > 20:
            complexity_score += 3
            complexity_factors.append(f"参数数量很多 ({param_count})")
        elif param_count > 10:
            complexity_score += 2
            complexity_factors.append(f"参数数量较多 ({param_count})")
        elif param_count > 5:
            complexity_score += 1
            complexity_factors.append(f"参数数量中等 ({param_count})")
        
        # SQL语句复杂度
        sql_count = len(sp_structure.sql_statements)
        if sql_count > 15:
            complexity_score += 3
            complexity_factors.append(f"SQL语句很多 ({sql_count})")
        elif sql_count > 8:
            complexity_score += 2
            complexity_factors.append(f"SQL语句较多 ({sql_count})")
        elif sql_count > 3:
            complexity_score += 1
            complexity_factors.append(f"SQL语句中等 ({sql_count})")
        
        # 表数量复杂度
        table_count = len(total_tables)
        if table_count > 10:
            complexity_score += 3
            complexity_factors.append(f"涉及表很多 ({table_count})")
        elif table_count > 6:
            complexity_score += 2
            complexity_factors.append(f"涉及表较多 ({table_count})")
        elif table_count > 3:
            complexity_score += 1
            complexity_factors.append(f"涉及表中等 ({table_count})")
        
        # 条件复杂度
        if total_conditions > 50:
            complexity_score += 3
            complexity_factors.append(f"条件很复杂 ({total_conditions})")
        elif total_conditions > 20:
            complexity_score += 2
            complexity_factors.append(f"条件较复杂 ({total_conditions})")
        elif total_conditions > 10:
            complexity_score += 1
            complexity_factors.append(f"条件中等复杂 ({total_conditions})")
        
        # 显示复杂度结果
        if complexity_score >= 9:
            complexity_level = "🔴 极高"
        elif complexity_score >= 6:
            complexity_level = "🟡 高"
        elif complexity_score >= 3:
            complexity_level = "🟢 中等"
        else:
            complexity_level = "🔵 低"
        
        print(f"📊 复杂度等级: {complexity_level} (得分: {complexity_score}/12)")
        print("📋 复杂度因素:")
        for factor in complexity_factors:
            print(f"   • {factor}")
        print()
        
        # 解析质量评估
        print("=" * 60)
        print("           解析质量评估")
        print("=" * 60)
        
        quality_score = 0
        quality_issues = []
        
        # 检查是否成功识别过程名
        if sp_structure.name and sp_structure.name != "unknown_procedure":
            quality_score += 2
        else:
            quality_issues.append("未能正确识别存储过程名称")
        
        # 检查参数解析
        if sp_structure.parameters:
            quality_score += 2
        else:
            quality_issues.append("未能解析任何参数")
        
        # 检查SQL语句解析
        if sp_structure.sql_statements:
            quality_score += 3
        else:
            quality_issues.append("未能解析任何SQL语句")
        
        # 检查表识别
        if total_tables:
            quality_score += 2
        else:
            quality_issues.append("未能识别任何表")
        
        # 检查条件解析
        if total_conditions > 0:
            quality_score += 1
        else:
            quality_issues.append("未能解析任何条件")
        
        # 显示质量评估结果
        quality_percentage = (quality_score / 10) * 100
        
        if quality_percentage >= 90:
            quality_level = "🟢 优秀"
        elif quality_percentage >= 70:
            quality_level = "🟡 良好"
        elif quality_percentage >= 50:
            quality_level = "🟠 一般"
        else:
            quality_level = "🔴 需要改进"
        
        print(f"📊 解析质量: {quality_level} ({quality_percentage:.1f}%)")
        
        if quality_issues:
            print("⚠️  发现的问题:")
            for issue in quality_issues:
                print(f"   • {issue}")
        else:
            print("✅ 解析质量很好，未发现明显问题")
        print()
        
        # 生成测试报告
        test_report = {
            "procedure_name": sp_structure.name,
            "file_stats": {
                "size_chars": len(sp_content),
                "line_count": sp_content.count('\n') + 1
            },
            "parsing_results": {
                "parameters_count": len(sp_structure.parameters),
                "sql_statements_count": len(sp_structure.sql_statements),
                "cursors_count": len(sp_structure.cursor_declarations),
                "variables_count": len(sp_structure.variable_declarations),
                "tables_involved": len(total_tables),
                "total_conditions": total_conditions
            },
            "complexity": {
                "score": complexity_score,
                "level": complexity_level,
                "factors": complexity_factors
            },
            "quality": {
                "score": quality_score,
                "percentage": quality_percentage,
                "level": quality_level,
                "issues": quality_issues
            },
            "statement_types": statement_types
        }
        
        # 保存测试报告
        report_file = current_dir / 'test_results' / 'sp_parser_test_report.json'
        report_file.parent.mkdir(exist_ok=True)
        
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(test_report, f, ensure_ascii=False, indent=2)
        
        print(f"📄 测试报告已保存到: {report_file}")
        print()
        print("=" * 80)
        print("                  测试总结")
        print("=" * 80)
        
        if quality_percentage >= 70 and complexity_score >= 3:
            print("🎉 测试成功! 解析器能够有效处理大型复杂存储过程")
        elif quality_percentage >= 50:
            print("✅ 测试基本通过，解析器具备基本的大型存储过程处理能力")
        else:
            print("⚠️  测试发现问题，解析器需要改进以更好地处理大型存储过程")
        
        return True
        
    except Exception as e:
        print(f"❌ 测试过程中发生错误: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_large_stored_procedure()
    sys.exit(0 if success else 1) 
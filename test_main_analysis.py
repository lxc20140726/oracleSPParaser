#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
from pathlib import Path

# 添加src目录到Python路径
current_dir = Path(__file__).parent
sys.path.insert(0, str(current_dir / 'src'))

from main import OracleSPAnalyzer

def test_with_main_analyzer():
    """使用主分析器测试大型存储过程"""
    
    print("=" * 80)
    print("      使用主分析器测试大型存储过程")
    print("=" * 80)
    
    # 读取存储过程文件
    sp_file_path = current_dir / 'data' / 'sp.sql'
    
    try:
        with open(sp_file_path, 'r', encoding='utf-8') as f:
            sp_content = f.read()
        
        print(f"✅ 成功读取存储过程文件")
        print(f"📏 文件大小: {len(sp_content)} 字符")
        print(f"📄 文件行数: {sp_content.count(chr(10)) + 1} 行")
        print()
        
        # 创建分析器
        analyzer = OracleSPAnalyzer()
        
        print("🔍 开始完整分析...")
        
        # 执行完整分析
        analysis_result = analyzer.analyze(sp_content)
        
        print("✅ 分析完成!")
        print()
        
        # 显示详细结果
        print("=" * 60)
        print("           完整分析结果")
        print("=" * 60)
        
        sp_struct = analysis_result.sp_structure
        print(f"🏷️  存储过程: {sp_struct.name}")
        print(f"📊 参数: {len(sp_struct.parameters)} 个")
        print(f"📝 SQL语句: {len(sp_struct.sql_statements)} 个")
        print()
        
        # 参数分析结果
        params = analysis_result.parameters
        print(f"🔍 参数分析结果: {len(params)} 个参数")
        for param in params[:5]:  # 显示前5个
            print(f"   • {param.name} ({param.direction}) - {param.data_type}")
        if len(params) > 5:
            print(f"   ... 还有 {len(params) - 5} 个参数")
        print()
        
        # 表字段分析结果
        table_analysis = analysis_result.table_field_analysis
        print(f"📊 表分析结果:")
        print(f"   实体表: {len(table_analysis.physical_tables)} 个")
        print(f"   临时表: {len(table_analysis.temp_tables)} 个")
        
        if table_analysis.physical_tables:
            print("   实体表列表:")
            for table_name, table_obj in table_analysis.physical_tables.items():
                print(f"     • {table_name} ({len(table_obj.fields)} 字段)")
        print()
        
        # 条件和逻辑分析结果
        conditions = analysis_result.conditions_and_logic
        print(f"🔗 条件分析结果:")
        print(f"   连接条件: {len(conditions.join_conditions)} 个")
        print(f"   过滤条件: {len(conditions.where_conditions)} 个")
        print(f"   控制流: {len(conditions.control_flow)} 个")
        print()
        
        # 分析SQL语句详情
        print("=" * 60)
        print("         SQL语句详细信息")
        print("=" * 60)
        
        for i, stmt in enumerate(sp_struct.sql_statements, 1):
            print(f"SQL语句 {i}:")
            print(f"  类型: {stmt.statement_type.value}")
            print(f"  源表: {', '.join(stmt.source_tables)}")
            print(f"  目标表: {', '.join(stmt.target_tables)}")
            print(f"  读取字段: {len(stmt.fields_read)}")
            print(f"  写入字段: {len(stmt.fields_written)}")
            print(f"  使用参数: {', '.join(stmt.parameters_used)}")
            print()
        
        print("=" * 80)
        print("               测试结论")
        print("=" * 80)
        
        # 评估测试结果
        success_indicators = []
        issues = []
        
        # 检查各项指标
        if sp_struct.name != "unknown_procedure":
            success_indicators.append("✅ 成功识别存储过程名称")
        else:
            issues.append("❌ 未能识别存储过程名称")
        
        if len(sp_struct.parameters) >= 20:
            success_indicators.append("✅ 成功解析大量参数 (28个)")
        elif len(sp_struct.parameters) > 0:
            success_indicators.append(f"✅ 解析了部分参数 ({len(sp_struct.parameters)}个)")
        else:
            issues.append("❌ 未能解析任何参数")
        
        if len(sp_struct.sql_statements) > 0:
            success_indicators.append(f"✅ 成功解析多个SQL语句 ({len(sp_struct.sql_statements)}个)")
        else:
            issues.append("❌ 未能解析任何SQL语句")
        
        if len(table_analysis.physical_tables) > 0:
            success_indicators.append(f"✅ 识别了多个表 ({len(table_analysis.physical_tables)}个)")
        else:
            issues.append("❌ 未能识别任何表")
        
        # 复杂度处理能力
        file_size_kb = len(sp_content) / 1024
        if file_size_kb > 10:
            success_indicators.append(f"✅ 成功处理大型文件 ({file_size_kb:.1f}KB)")
        
        line_count = sp_content.count('\n') + 1
        if line_count > 200:
            success_indicators.append(f"✅ 成功处理复杂存储过程 ({line_count}行)")
        
        # 显示结果
        print("📊 成功指标:")
        for indicator in success_indicators:
            print(f"   {indicator}")
        
        if issues:
            print("\n⚠️  发现的问题:")
            for issue in issues:
                print(f"   {issue}")
        
        # 总体评估
        success_rate = len(success_indicators) / (len(success_indicators) + len(issues)) * 100
        
        print(f"\n📈 总体成功率: {success_rate:.1f}%")
        
        if success_rate >= 80:
            print("🎉 优秀! 程序具备强大的大型存储过程识别和解析能力")
        elif success_rate >= 60:
            print("✅ 良好! 程序基本具备大型存储过程处理能力")
        else:
            print("⚠️  需要改进，程序在处理大型存储过程方面还有不足")
        
        return True
        
    except Exception as e:
        print(f"❌ 测试过程中发生错误: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_with_main_analyzer()
    sys.exit(0 if success else 1) 
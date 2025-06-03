#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from src.main import OracleSPAnalyzer

def analyze_stored_procedure_from_file(file_path: str):
    """从文件读取存储过程并分析"""
    
    try:
        # 读取存储过程文件
        with open(file_path, 'r', encoding='utf-8') as f:
            sp_content = f.read()
        
        print(f"📄 正在分析文件: {file_path}")
        print(f"文件大小: {len(sp_content)} 字符")
        
        # 创建分析器并执行分析
        analyzer = OracleSPAnalyzer()
        result = analyzer.analyze(sp_content)
        
        # 输出分析结果
        print(f"\n✅ 分析完成！")
        print(f"存储过程名称: {result.sp_structure.name}")
        print(f"参数数量: {len(result.parameters)}")
        print(f"SQL语句数量: {len(result.sp_structure.sql_statements)}")
        print(f"物理表数量: {len(result.table_field_analysis.physical_tables)}")
        print(f"临时表数量: {len(result.table_field_analysis.temp_tables)}")
        print(f"JOIN条件数量: {len(result.conditions_and_logic.join_conditions)}")
        
        return result
        
    except FileNotFoundError:
        print(f"❌ 错误: 找不到文件 {file_path}")
        return None
    except Exception as e:
        print(f"❌ 分析过程中发生错误: {str(e)}")
        return None

def main():
    """主函数"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Oracle存储过程分析工具')
    parser.add_argument('file', help='存储过程文件路径')
    parser.add_argument('--output', '-o', help='输出文件路径（可选）')
    
    args = parser.parse_args()
    
    # 分析存储过程
    result = analyze_stored_procedure_from_file(args.file)
    
    if result and args.output:
        # 如果指定了输出文件，保存分析结果
        import json
        
        output_data = {
            "procedure_name": result.sp_structure.name,
            "parameters": [
                {
                    "name": p.name,
                    "direction": p.direction,
                    "data_type": p.data_type
                } for p in result.parameters
            ],
            "tables": {
                "physical": list(result.table_field_analysis.physical_tables.keys()),
                "temporary": list(result.table_field_analysis.temp_tables.keys())
            },
            "sql_statements": len(result.sp_structure.sql_statements),
            "join_conditions": len(result.conditions_and_logic.join_conditions)
        }
        
        with open(args.output, 'w', encoding='utf-8') as f:
            json.dump(output_data, f, ensure_ascii=False, indent=2)
        
        print(f"\n💾 分析结果已保存到: {args.output}")

if __name__ == "__main__":
    # 如果没有命令行参数，显示使用说明
    if len(sys.argv) == 1:
        print("📖 使用方法:")
        print("  python analyze_from_file.py <存储过程文件路径>")
        print("  python analyze_from_file.py procedure.sql")
        print("  python analyze_from_file.py procedure.sql --output result.json")
        print("\n💡 提示: 请确保存储过程文件使用UTF-8编码")
    else:
        main() 
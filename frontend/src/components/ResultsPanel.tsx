import React, { useState } from 'react';
import { AnalysisResult } from '../types';

interface ResultsPanelProps {
  analysisResult: AnalysisResult;
}

const ResultsPanel: React.FC<ResultsPanelProps> = ({ analysisResult }) => {
  const [activeTab, setActiveTab] = useState<'overview' | 'parameters' | 'tables' | 'statements' | 'joins'>('overview');

  const { data } = analysisResult;

  return (
    <div className="bg-white rounded-lg shadow-sm border border-gray-200">
      {/* 头部 */}
      <div className="px-4 py-3 border-b border-gray-200">
        <h2 className="text-lg font-semibold text-gray-800">分析结果详情</h2>
        <p className="text-sm text-gray-600 mt-1">
          存储过程：{data.procedure_name}
        </p>
      </div>

      {/* 标签页 */}
      <div className="border-b border-gray-200">
        <nav className="flex space-x-8 px-4">
          {[
            { key: 'overview', label: '概览', count: null },
            { key: 'parameters', label: '参数', count: data.statistics.parameter_count },
            { key: 'tables', label: '表', count: data.statistics.physical_table_count + data.statistics.temporary_table_count },
            { key: 'statements', label: 'SQL语句', count: data.statistics.sql_statement_count },
            { key: 'joins', label: 'JOIN条件', count: data.statistics.join_condition_count },
          ].map((tab) => (
            <button
              key={tab.key}
              onClick={() => setActiveTab(tab.key as any)}
              className={`py-2 px-1 border-b-2 font-medium text-sm flex items-center space-x-1 ${
                activeTab === tab.key
                  ? 'border-blue-500 text-blue-600'
                  : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
              }`}
            >
              <span>{tab.label}</span>
              {tab.count !== null && (
                <span className={`px-2 py-0.5 rounded-full text-xs ${
                  activeTab === tab.key ? 'bg-blue-100 text-blue-800' : 'bg-gray-100 text-gray-600'
                }`}>
                  {tab.count}
                </span>
              )}
            </button>
          ))}
        </nav>
      </div>

      {/* 内容区域 */}
      <div className="p-4 max-h-96 overflow-y-auto">
        {activeTab === 'overview' && (
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            <div className="bg-blue-50 rounded-lg p-4 text-center">
              <div className="text-2xl font-bold text-blue-600">{data.statistics.parameter_count}</div>
              <div className="text-sm text-blue-800">参数</div>
            </div>
            <div className="bg-green-50 rounded-lg p-4 text-center">
              <div className="text-2xl font-bold text-green-600">{data.statistics.physical_table_count}</div>
              <div className="text-sm text-green-800">物理表</div>
            </div>
            <div className="bg-yellow-50 rounded-lg p-4 text-center">
              <div className="text-2xl font-bold text-yellow-600">{data.statistics.temporary_table_count}</div>
              <div className="text-sm text-yellow-800">临时表</div>
            </div>
            <div className="bg-purple-50 rounded-lg p-4 text-center">
              <div className="text-2xl font-bold text-purple-600">{data.statistics.sql_statement_count}</div>
              <div className="text-sm text-purple-800">SQL语句</div>
            </div>
          </div>
        )}

        {activeTab === 'parameters' && (
          <div className="space-y-3">
            {data.parameters.length === 0 ? (
              <p className="text-gray-500 text-center py-4">无参数定义</p>
            ) : (
              data.parameters.map((param, index) => (
                <div key={index} className="border rounded-lg p-3">
                  <div className="flex items-center justify-between mb-2">
                    <h4 className="font-medium text-gray-900">{param.name}</h4>
                    <span className={`px-2 py-1 rounded text-xs font-medium ${
                      param.direction === 'IN' ? 'bg-blue-100 text-blue-800' :
                      param.direction === 'OUT' ? 'bg-green-100 text-green-800' :
                      'bg-purple-100 text-purple-800'
                    }`}>
                      {param.direction}
                    </span>
                  </div>
                  <div className="text-sm text-gray-600">
                    <p>类型: {param.data_type}</p>
                    {param.used_in_statements.length > 0 && (
                      <p>使用语句: {param.used_in_statements.join(', ')}</p>
                    )}
                  </div>
                </div>
              ))
            )}
          </div>
        )}

        {activeTab === 'tables' && (
          <div className="space-y-4">
            {Object.keys(data.tables.physical).length > 0 && (
              <div>
                <h4 className="font-medium text-gray-900 mb-2 flex items-center">
                  <span className="w-3 h-3 bg-green-500 rounded mr-2"></span>
                  物理表
                </h4>
                <div className="space-y-2">
                  {Object.entries(data.tables.physical).map(([tableName, table]) => (
                    <div key={tableName} className="border rounded-lg p-3">
                      <h5 className="font-medium text-gray-800">{tableName}</h5>
                      {table.fields.length > 0 && (
                        <div className="mt-2">
                          <p className="text-xs text-gray-600 mb-1">字段:</p>
                          <div className="flex flex-wrap gap-1">
                            {table.fields.map((field, idx) => (
                              <span key={idx} className="px-2 py-1 bg-gray-100 text-gray-700 rounded text-xs">
                                {field}
                              </span>
                            ))}
                          </div>
                        </div>
                      )}
                    </div>
                  ))}
                </div>
              </div>
            )}

            {Object.keys(data.tables.temporary).length > 0 && (
              <div>
                <h4 className="font-medium text-gray-900 mb-2 flex items-center">
                  <span className="w-3 h-3 bg-yellow-500 rounded mr-2"></span>
                  临时表
                </h4>
                <div className="space-y-2">
                  {Object.entries(data.tables.temporary).map(([tableName, table]) => (
                    <div key={tableName} className="border rounded-lg p-3 border-dashed">
                      <h5 className="font-medium text-gray-800">{tableName}</h5>
                      {table.fields.length > 0 && (
                        <div className="mt-2">
                          <p className="text-xs text-gray-600 mb-1">字段:</p>
                          <div className="flex flex-wrap gap-1">
                            {table.fields.map((field, idx) => (
                              <span key={idx} className="px-2 py-1 bg-yellow-100 text-yellow-700 rounded text-xs">
                                {field}
                              </span>
                            ))}
                          </div>
                        </div>
                      )}
                    </div>
                  ))}
                </div>
              </div>
            )}

            {Object.keys(data.tables.physical).length === 0 && Object.keys(data.tables.temporary).length === 0 && (
              <p className="text-gray-500 text-center py-4">无表定义</p>
            )}
          </div>
        )}

        {activeTab === 'statements' && (
          <div className="space-y-3">
            {data.sql_statements.length === 0 ? (
              <p className="text-gray-500 text-center py-4">无SQL语句</p>
            ) : (
              data.sql_statements.map((stmt, index) => (
                <div key={index} className="border rounded-lg p-3">
                  <div className="flex items-center justify-between mb-2">
                    <h4 className="font-medium text-gray-900">语句 {stmt.id}</h4>
                    <span className="px-2 py-1 bg-indigo-100 text-indigo-800 rounded text-xs font-medium">
                      {stmt.type}
                    </span>
                  </div>
                  <div className="text-sm text-gray-600 space-y-1">
                    {stmt.source_tables.length > 0 && (
                      <p>源表: {stmt.source_tables.join(', ')}</p>
                    )}
                    {stmt.target_tables.length > 0 && (
                      <p>目标表: {stmt.target_tables.join(', ')}</p>
                    )}
                    {stmt.parameters_used.length > 0 && (
                      <p>使用参数: {stmt.parameters_used.join(', ')}</p>
                    )}
                  </div>
                  <details className="mt-2">
                    <summary className="text-xs text-gray-500 cursor-pointer hover:text-gray-700">
                      查看SQL代码
                    </summary>
                    <pre className="mt-2 p-2 bg-gray-50 rounded text-xs overflow-x-auto">
                      {stmt.raw_sql}
                    </pre>
                  </details>
                </div>
              ))
            )}
          </div>
        )}

        {activeTab === 'joins' && (
          <div className="space-y-3">
            {data.join_conditions.length === 0 ? (
              <p className="text-gray-500 text-center py-4">无JOIN条件</p>
            ) : (
              data.join_conditions.map((join, index) => (
                <div key={index} className="border rounded-lg p-3">
                  <div className="flex items-center justify-between mb-2">
                    <h4 className="font-medium text-gray-900">
                      {join.left_table} ↔ {join.right_table}
                    </h4>
                    <span className="px-2 py-1 bg-red-100 text-red-800 rounded text-xs font-medium">
                      {join.join_type}
                    </span>
                  </div>
                  <div className="text-sm text-gray-600">
                    <p>连接字段: {join.left_field} = {join.right_field}</p>
                    <p className="mt-1 font-mono text-xs bg-gray-50 p-2 rounded">
                      {join.condition_text}
                    </p>
                  </div>
                </div>
              ))
            )}
          </div>
        )}
      </div>
    </div>
  );
};

export default ResultsPanel; 
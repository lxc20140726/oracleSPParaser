import React, { useEffect, useRef, useState, useMemo } from 'react';
import cytoscape from 'cytoscape';
import cose from 'cytoscape-cose-bilkent';
import { UMLVisualizationData, UMLNode } from '../types';

// 注册布局算法
cytoscape.use(cose);

interface UMLVisualizationPanelProps {
  umlData: UMLVisualizationData | null;
  isLoading: boolean;
}

const UMLVisualizationPanel: React.FC<UMLVisualizationPanelProps> = ({
  umlData,
  isLoading,
}) => {
  const containerRef = useRef<HTMLDivElement>(null);
  const cyRef = useRef<cytoscape.Core | null>(null);
  const timeoutRef = useRef<NodeJS.Timeout | null>(null);
  const layoutRef = useRef<any>(null);
  const isMountedRef = useRef(true);
  const [selectedNode, setSelectedNode] = useState<UMLNode | null>(null);
  const [showFieldMappings, setShowFieldMappings] = useState(true);
  const [showTableRelations, setShowTableRelations] = useState(true);

  // 组件挂载状态管理
  useEffect(() => {
    isMountedRef.current = true;
    return () => {
      isMountedRef.current = false;
    };
  }, []);

  // UML样式的Cytoscape配置
  const cytoscapeStyle = useMemo(() => [
    // 物理表表头样式
    {
      selector: 'node[group = "physical_table_header"]',
      style: {
        'shape': 'rectangle',
        'background-color': '#4CAF50',
        'border-width': '0px',
        'label': 'data(label)',
        'color': '#ffffff',
        'text-valign': 'center',
        'text-halign': 'center',
        'font-size': '14px',
        'font-weight': 'bold',
        'font-family': 'Inter, -apple-system, sans-serif',
        'width': '180px',
        'height': '35px',
        'text-wrap': 'wrap',
      },
    },
    // 临时表表头样式
    {
      selector: 'node[group = "temp_table_header"]',
      style: {
        'shape': 'rectangle',
        'background-color': '#FF9800',
        'border-width': '0px',
        'label': (ele: any) => {
          try {
            const label = ele.data('label') || 'Temp Table';
            return `⏱ ${label}`;
          } catch (error) {
            return 'Temp Table';
          }
        },
        'color': '#ffffff',
        'text-valign': 'center',
        'text-halign': 'center',
        'font-size': '14px',
        'font-weight': 'bold',
        'font-family': 'Inter, -apple-system, sans-serif',
        'width': '180px',
        'height': '35px',
        'text-wrap': 'wrap',
      },
    },
    // 物理表字段样式
    {
      selector: 'node[group = "physical_table_field"]',
      style: {
        'shape': 'rectangle',
        'background-color': '#ffffff',
        'border-width': '1px',
        'border-color': '#4CAF50',
        'border-style': 'solid',
        'label': (ele: any) => {
          try {
            const label = ele.data('label') || 'field';
            const fieldType = ele.data('fieldType');
            const prefix = fieldType === 'computed_field' ? '◆ ' : '• ';
            return `${prefix}${label}`;
          } catch (error) {
            return '• field';
          }
        },
        'color': '#2E7D32',
        'text-valign': 'center',
        'text-halign': 'left',
        'text-margin-x': '8px',
        'font-size': '12px',
        'font-weight': 'normal',
        'font-family': 'Inter, -apple-system, sans-serif',
        'width': '180px',
        'height': '24px',
      },
    },
    // 临时表字段样式
    {
      selector: 'node[group = "temp_table_field"]',
      style: {
        'shape': 'rectangle',
        'background-color': '#FFF9C4',
        'border-width': '1px',
        'border-color': '#FF9800',
        'border-style': 'solid',
        'label': (ele: any) => {
          try {
            const label = ele.data('label') || 'field';
            const fieldType = ele.data('fieldType');
            const prefix = fieldType === 'computed_field' ? '◆ ' : '• ';
            return `${prefix}${label}`;
          } catch (error) {
            return '• field';
          }
        },
        'color': '#E65100',
        'text-valign': 'center',
        'text-halign': 'left',
        'text-margin-x': '8px',
        'font-size': '12px',
        'font-weight': 'normal',
        'font-family': 'Inter, -apple-system, sans-serif',
        'width': '180px',
        'height': '24px',
      },
    },
    // 计算字段特殊样式
    {
      selector: 'node[fieldType = "computed_field"]',
      style: {
        'background-color': '#E8F5E9',
        'border-style': 'dashed',
        'font-style': 'italic',
      },
    },
    // 字段映射连线样式
    {
      selector: 'edge[type = "field_mapping"]',
      style: {
        'width': 2,
        'line-color': 'data(color)',
        'target-arrow-color': 'data(color)',
        'target-arrow-shape': 'triangle',
        'target-arrow-size': '8px',
        'curve-style': 'bezier',
        'line-style': 'solid',
        'label': 'data(label)',
        'font-size': '10px',
        'font-weight': '500',
        'font-family': 'Inter, -apple-system, sans-serif',
        'text-background-color': '#ffffff',
        'text-background-opacity': 0.9,
        'text-background-padding': '3px',
        'text-border-color': 'data(color)',
        'text-border-width': '1px',
        'text-border-opacity': 0.3,
        'opacity': 0.9,
      },
    },
    // 计算字段映射样式（复合表达式）
    {
      selector: 'edge[type = "field_mapping"][mapping_type = "computed_insert"]',
      style: {
        'line-style': 'dashed',
        'width': 2.5,
        'target-arrow-size': '10px',
        'opacity': 0.8,
        'line-dash-pattern': [8, 4],
        'text-background-color': '#E8F5E9',
      },
    },
    // 表关系连线样式
    {
      selector: 'edge[type = "table_relation"]',
      style: {
        'width': 3,
        'line-color': '#2E7D32',
        'target-arrow-color': '#2E7D32',
        'target-arrow-shape': 'diamond',
        'target-arrow-size': '12px',
        'curve-style': 'bezier',
        'line-style': 'solid',
        'label': 'data(label)',
        'font-size': '11px',
        'font-family': 'Inter, -apple-system, sans-serif',
        'font-weight': '600',
        'color': '#1B5E20',
        'text-background-color': '#E8F5E9',
        'text-background-opacity': 0.9,
        'text-background-padding': '4px',
        'opacity': 0.9,
      },
    },
    // 选中状态
    {
      selector: ':selected',
      style: {
        'border-width': '3px',
        'border-color': '#2196F3',
        'z-index': 999,
      },
    },
  ] as any[], []);

  // 初始化Cytoscape
  useEffect(() => {
    if (!containerRef.current) return;

    try {
      cyRef.current = cytoscape({
        container: containerRef.current,
        style: cytoscapeStyle,
              layout: {
        name: 'preset',  // 使用预设布局避免动画
        animate: false,
        fit: false
      },
        minZoom: 0.1,
        maxZoom: 3,
        wheelSensitivity: 0.1,
      });

      // 添加节点点击事件
      cyRef.current.on('tap', 'node', (event) => {
        try {
          const node = event.target;
          const nodeData = node.data();
          
          if (nodeData) {
            const nodeType = nodeData.nodeType;
            
            if (nodeType === 'table_header') {
              // 点击表头，显示整个表的信息
              setSelectedNode(nodeData as UMLNode);
            } else if (nodeType === 'table_field') {
              // 点击字段，创建字段信息对象
              const fieldInfo = {
                id: nodeData.id,
                label: nodeData.properties?.table_name || 'Unknown Table',
                type: nodeData.group?.includes('temp') ? 'temp_table' : 'physical_table',
                group: nodeData.group,
                properties: {
                  ...nodeData.properties,
                  selected_field: {
                    name: nodeData.label,
                    type: nodeData.fieldType,
                    index: nodeData.fieldIndex,
                    is_computed: nodeData.properties?.is_computed,
                    expression: nodeData.properties?.expression
                  }
                }
              };
              setSelectedNode(fieldInfo as UMLNode);
            }
          }
        } catch (error) {
          console.warn('处理节点点击事件时出错:', error);
        }
      });

      // 添加画布点击事件（取消选择）
      cyRef.current.on('tap', (event) => {
        try {
          if (event.target === cyRef.current) {
            setSelectedNode(null);
          }
        } catch (error) {
          console.warn('处理画布点击事件时出错:', error);
        }
      });
    } catch (error) {
      console.error('初始化Cytoscape时出错:', error);
    }

    return () => {
      isMountedRef.current = false;
      
      // 清理定时器
      if (timeoutRef.current) {
        clearTimeout(timeoutRef.current);
        timeoutRef.current = null;
      }
      
      // 停止布局
      if (layoutRef.current) {
        try {
          layoutRef.current.stop();
        } catch (error) {
          console.warn('停止布局时出错:', error);
        }
        layoutRef.current = null;
      }
      
      // 销毁Cytoscape实例
      if (cyRef.current) {
        try {
          // 先移除所有事件监听器
          cyRef.current.removeAllListeners();
          // 停止所有动画
          cyRef.current.stop();
          // 销毁实例
          cyRef.current.destroy();
        } catch (error) {
          console.warn('销毁Cytoscape实例时出错:', error);
        }
        cyRef.current = null;
      }
    };
  }, [cytoscapeStyle]);

  // 更新图形数据
  useEffect(() => {
    if (!cyRef.current || !umlData) return;

    console.log('开始更新UML图形数据...');

    // 清理之前的定时器
    if (timeoutRef.current) {
      clearTimeout(timeoutRef.current);
      timeoutRef.current = null;
    }

    try {
      // 清除现有元素
      cyRef.current.elements().remove();

      // 准备节点数据 - 字段级节点架构
      const nodes: any[] = [];
      
      if (umlData.nodes && Array.isArray(umlData.nodes)) {
        umlData.nodes.forEach((table: any) => {
          if (table && table.id) {
            const fields = table.properties?.fields || [];
            const isTemporary = table.properties?.is_temporary || false;
            
            // 1. 添加表头节点
            nodes.push({
              data: {
                id: `${table.id}_header`,
                label: String(table.label || 'Table'),
                group: isTemporary ? 'temp_table_header' : 'physical_table_header',
                tableId: table.id,
                nodeType: 'table_header',
                properties: {
                  ...table.properties,
                  is_temporary: isTemporary,
                  field_count: fields.length
                }
              }
            });

            // 2. 为每个字段创建独立节点
            fields.forEach((field: any, index: number) => {
              if (field && field.name) {
                nodes.push({
                  data: {
                    id: `${table.id}_field_${index}`,
                    label: String(field.name),
                    group: isTemporary ? 'temp_table_field' : 'physical_table_field',
                    tableId: table.id,
                    fieldIndex: index,
                    nodeType: 'table_field',
                    fieldType: field.type || 'normal',
                    properties: {
                      field: field,
                      table_name: table.label,
                      is_computed: field.type === 'computed_field',
                      expression: field.expression || null
                    }
                  }
                });
              }
            });
          }
        });
      }

      console.log(`准备了 ${nodes.length} 个节点（表头和字段）`);

      // 准备边数据 - 连接到具体的字段节点
      const edges: any[] = [];
      
      // 添加字段映射 - 连接具体字段节点
      if (showFieldMappings && umlData.field_mappings && Array.isArray(umlData.field_mappings)) {
        umlData.field_mappings.forEach((edge: any) => {
          if (edge && edge.source && edge.target) {
            const sourceFieldIndex = edge.properties?.source_field_index;
            const targetFieldIndex = edge.properties?.target_field_index;
            
            // 构造字段节点ID
            const sourceNodeId = typeof sourceFieldIndex === 'number' && sourceFieldIndex >= 0 
              ? `${edge.source}_field_${sourceFieldIndex}` 
              : `${edge.source}_header`; // 如果没有字段索引，连接到表头
            
            const targetNodeId = typeof targetFieldIndex === 'number' && targetFieldIndex >= 0 
              ? `${edge.target}_field_${targetFieldIndex}` 
              : `${edge.target}_header`;

            edges.push({
              data: {
                id: String(edge.properties?.id || `${edge.source}_${edge.target}_${Date.now()}`),
                source: sourceNodeId,
                target: targetNodeId,
                label: String(edge.label || ''),
                type: String(edge.type || 'field_mapping'),
                color: String(edge.properties?.color || 'blue'),
                mapping_type: String(edge.properties?.mapping_type || ''),
                sourceTable: edge.source,
                targetTable: edge.target
              }
            });
          }
        });
      }

      // 添加表关系 - 连接表头节点
      if (showTableRelations && umlData.table_relations && Array.isArray(umlData.table_relations)) {
        umlData.table_relations.forEach((edge: any) => {
          if (edge && edge.source && edge.target) {
            edges.push({
              data: {
                id: String(edge.properties?.id || `relation_${edge.source}_${edge.target}`),
                source: `${edge.source}_header`,
                target: `${edge.target}_header`,
                label: String(edge.label || ''),
                type: String(edge.type || 'table_relation'),
                color: String(edge.properties?.color || 'darkgreen')
              }
            });
          }
        });
      }

      console.log(`准备了 ${edges.length} 个连线`);

      // 添加节点到图中
      if (nodes.length > 0) {
        cyRef.current.add(nodes);
      }

      // 添加边到图中
      if (edges.length > 0) {
        cyRef.current.add(edges);
      }

      // 停止之前的布局
      if (layoutRef.current) {
        try {
          layoutRef.current.stop();
        } catch (error) {
          console.warn('停止之前的布局时出错:', error);
        }
      }

      // 应用网格布局 - 适合字段级节点
      layoutRef.current = cyRef.current.layout({
        name: 'grid',
        fit: true,
        padding: 30,
        rows: undefined,
        cols: undefined,
        sort: (a: any, b: any) => {
          // 按表分组排序
          const aTableId = a.data('tableId') || a.data('id');
          const bTableId = b.data('tableId') || b.data('id');
          
          if (aTableId !== bTableId) {
            return aTableId.localeCompare(bTableId);
          }
          
          // 同一个表内，表头在前，字段按索引排序
          const aType = a.data('nodeType');
          const bType = b.data('nodeType');
          
          if (aType === 'table_header' && bType === 'table_field') return -1;
          if (aType === 'table_field' && bType === 'table_header') return 1;
          
          if (aType === 'table_field' && bType === 'table_field') {
            return (a.data('fieldIndex') || 0) - (b.data('fieldIndex') || 0);
          }
          
          return 0;
        },
        stop: () => {
          if (isMountedRef.current && cyRef.current && !cyRef.current.destroyed()) {
            try {
              // 应用自定义定位逻辑
              layoutFieldNodes();
            } catch (error) {
              console.warn('字段定位时出错:', error);
            }
          }
        }
      });

      layoutRef.current.run();

      console.log('UML图形数据更新完成');

    } catch (error) {
      console.error('更新UML图形数据时出错:', error);
    }

    // 清理函数
    return () => {
      if (timeoutRef.current) {
        clearTimeout(timeoutRef.current);
        timeoutRef.current = null;
      }
      
      if (layoutRef.current) {
        try {
          layoutRef.current.stop();
        } catch (error) {
          console.warn('清理布局时出错:', error);
        }
        layoutRef.current = null;
      }
    };

  }, [umlData, showFieldMappings, showTableRelations]);

  // 字段节点定位函数
  const layoutFieldNodes = () => {
    if (!cyRef.current) return;

    try {
      // 按表分组节点
      const tableGroups: { [key: string]: any[] } = {};
      
      cyRef.current.nodes().forEach((node: any) => {
        const tableId = node.data('tableId') || node.data('id');
        if (!tableGroups[tableId]) {
          tableGroups[tableId] = [];
        }
        tableGroups[tableId].push(node);
      });

      // 为每个表组织字段布局
      Object.keys(tableGroups).forEach((tableId, tableIndex) => {
        const tableNodes = tableGroups[tableId];
        const headerNode = tableNodes.find(n => n.data('nodeType') === 'table_header');
        const fieldNodes = tableNodes.filter(n => n.data('nodeType') === 'table_field');

        if (headerNode) {
          // 计算表的基准位置
          const baseX = (tableIndex % 3) * 300 + 150; // 3列布局
          const baseY = Math.floor(tableIndex / 3) * 200 + 100;

          // 定位表头
          headerNode.position({ x: baseX, y: baseY });

          // 定位字段节点
          fieldNodes.forEach((fieldNode: any, fieldIndex: number) => {
            fieldNode.position({
              x: baseX,
              y: baseY + 40 + (fieldIndex * 25) // 表头下方，每个字段25px间距
            });
          });
        }
      });

      // 重新fit视图
      setTimeout(() => {
        if (cyRef.current && !cyRef.current.destroyed()) {
          cyRef.current.fit(undefined, 50);
        }
      }, 100);

    } catch (error) {
      console.warn('定位字段节点时出错:', error);
    }
  };

  const handleToggleFieldMappings = () => {
    setShowFieldMappings(!showFieldMappings);
  };

  const handleToggleTableRelations = () => {
    setShowTableRelations(!showTableRelations);
  };

  const handleResetView = () => {
    try {
      if (isMountedRef.current && cyRef.current && !cyRef.current.destroyed()) {
        cyRef.current.fit(undefined, 50);
      }
    } catch (error) {
      console.warn('重置视图时出错:', error);
    }
  };

  const handleExportImage = () => {
    try {
      if (isMountedRef.current && cyRef.current && !cyRef.current.destroyed()) {
        const png64 = cyRef.current.png({ scale: 2, bg: 'white' });
        const link = document.createElement('a');
        link.download = 'uml-diagram.png';
        link.href = png64;
        link.click();
      }
    } catch (error) {
      console.warn('导出图像时出错:', error);
    }
  };

  if (isLoading) {
    return (
      <div className="visualization-panel h-full flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-16 w-16 border-b-2 border-blue-600 mx-auto mb-4"></div>
          <p className="text-gray-600">正在生成UML图...</p>
        </div>
      </div>
    );
  }

  if (!umlData) {
    return (
      <div className="visualization-panel h-full flex items-center justify-center">
        <div className="text-center">
          <div className="text-6xl mb-4">🗂️</div>
          <h3 className="text-xl font-semibold text-gray-700 mb-2">UML表结构图</h3>
          <p className="text-gray-500">请输入存储过程代码并点击"UML分析"按钮</p>
        </div>
      </div>
    );
  }

  return (
    <div className="visualization-panel h-full flex flex-col bg-white rounded-lg shadow-sm border">
      {/* 工具栏 */}
      <div className="flex items-center justify-between p-4 border-b bg-gray-50">
        <div className="flex items-center space-x-2">
          <h3 className="text-lg font-semibold text-gray-800 flex items-center">
            🗂️ UML表结构图
          </h3>
          <div className="text-sm text-gray-500">
            ({umlData.metadata.total_tables} 个表, {umlData.metadata.field_mappings_count} 个字段映射)
          </div>
        </div>
        
        <div className="flex items-center space-x-2">
          <button
            onClick={handleToggleFieldMappings}
            className={`px-3 py-1 text-sm rounded transition-colors ${
              showFieldMappings 
                ? 'bg-blue-500 text-white' 
                : 'bg-gray-200 text-gray-700 hover:bg-gray-300'
            }`}
          >
            字段映射
          </button>
          <button
            onClick={handleToggleTableRelations}
            className={`px-3 py-1 text-sm rounded transition-colors ${
              showTableRelations 
                ? 'bg-green-500 text-white' 
                : 'bg-gray-200 text-gray-700 hover:bg-gray-300'
            }`}
          >
            表关系
          </button>
          <button
            onClick={handleResetView}
            className="px-3 py-1 text-sm bg-gray-200 text-gray-700 rounded hover:bg-gray-300 transition-colors"
          >
            重置视图
          </button>
          <button
            onClick={handleExportImage}
            className="px-3 py-1 text-sm bg-indigo-500 text-white rounded hover:bg-indigo-600 transition-colors"
          >
            导出图片
          </button>
        </div>
      </div>

      {/* 主要可视化区域 */}
      <div className="flex-1 relative">
        <div ref={containerRef} className="w-full h-full" />
        
        {/* 右侧详情面板 */}
        {selectedNode && selectedNode.properties && (
          <div className="absolute top-4 right-4 w-80 bg-white border border-gray-200 rounded-lg shadow-lg p-4 max-h-96 overflow-y-auto">
            <div className="flex items-center justify-between mb-3">
              <h4 className="font-semibold text-gray-800 flex items-center">
                {selectedNode.properties?.is_temporary ? '🟡' : '🟢'} {selectedNode.label || 'Unknown'}
                {selectedNode.properties?.selected_field && (
                  <span className="ml-2 text-sm bg-blue-100 px-2 py-1 rounded">
                    字段: {selectedNode.properties.selected_field.name}
                  </span>
                )}
              </h4>
              <button
                onClick={() => setSelectedNode(null)}
                className="text-gray-400 hover:text-gray-600"
              >
                ✕
              </button>
            </div>
            
            <div className="space-y-2">
              <div className="text-sm">
                <span className="font-medium">类型:</span> {selectedNode.properties?.is_temporary ? '临时表' : '物理表'}
              </div>
              
              {selectedNode.properties?.selected_field ? (
                // 字段详细信息
                <div className="space-y-2">
                  <div className="text-sm font-medium border-t pt-2">字段详情:</div>
                  <div className="text-sm">
                    <span className="font-medium">字段名:</span> {selectedNode.properties.selected_field.name}
                  </div>
                  <div className="text-sm">
                    <span className="font-medium">字段类型:</span> {
                      selectedNode.properties.selected_field.is_computed ? '计算字段' : '普通字段'
                    }
                  </div>
                  <div className="text-sm">
                    <span className="font-medium">字段索引:</span> {selectedNode.properties.selected_field.index}
                  </div>
                  {selectedNode.properties.selected_field.is_computed && selectedNode.properties.selected_field.expression && (
                    <div className="text-sm">
                      <span className="font-medium">计算表达式:</span>
                      <div className="bg-gray-50 p-2 rounded text-xs font-mono mt-1">
                        {selectedNode.properties.selected_field.expression}
                      </div>
                    </div>
                  )}
                </div>
              ) : (
                // 表级信息
                <>
                  <div className="text-sm">
                    <span className="font-medium">字段数:</span> {selectedNode.properties?.field_count || 0}
                  </div>
                  
                  {selectedNode.properties?.fields && selectedNode.properties.fields.length > 0 && (
                    <div>
                      <div className="font-medium text-sm mb-2">字段列表:</div>
                      <div className="space-y-1 max-h-48 overflow-y-auto">
                        {selectedNode.properties.fields.map((field: any, index: number) => (
                          <div key={index} className="text-xs bg-gray-50 p-2 rounded">
                            <div className="flex items-center">
                              <span className={`mr-2 ${field.type === 'computed_field' ? 'text-purple-600' : 'text-blue-600'}`}>
                                {field.type === 'computed_field' ? '◆' : '•'}
                              </span>
                              <span className="font-mono">{field.name || 'Unknown Field'}</span>
                            </div>
                            {field.type === 'computed_field' && field.expression && (
                              <div className="mt-1 text-gray-600">
                                <div className="text-xs">表达式: {field.expression}</div>
                                {field.source_fields && field.source_fields.length > 0 && (
                                  <div className="text-xs">来源: {field.source_fields.join(', ')}</div>
                                )}
                              </div>
                            )}
                          </div>
                        ))}
                      </div>
                    </div>
                  )}
                </>
              )}
            </div>
          </div>
        )}

        {/* 图例 */}
        <div className="absolute bottom-4 left-4 bg-white border border-gray-200 rounded-lg shadow-lg p-4">
          <div className="text-sm font-semibold mb-2">图例</div>
          <div className="space-y-2 text-xs">
            <div className="flex items-center">
              <div className="w-4 h-3 border-2 border-green-600 bg-green-100 mr-2"></div>
              <span>物理表</span>
            </div>
            <div className="flex items-center">
              <div className="w-4 h-3 border-2 border-orange-500 border-dashed bg-yellow-100 mr-2"></div>
              <span>临时表</span>
            </div>
            <div className="flex items-center">
              <div className="w-4 h-1 bg-blue-500 border-dashed mr-2"></div>
              <span>字段映射</span>
            </div>
            <div className="flex items-center">
              <div className="w-4 h-1 bg-green-600 mr-2"></div>
              <span>表关系(JOIN)</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default UMLVisualizationPanel; 
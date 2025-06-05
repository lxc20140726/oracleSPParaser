import React, { useCallback, useMemo, useState, useEffect } from 'react';
import ReactFlow, {
  Node,
  Edge,
  addEdge,
  useNodesState,
  useEdgesState,
  Controls,
  MiniMap,
  Background,
  Connection,
  Handle,
  Position,
  NodeProps,
  MarkerType,
} from 'reactflow';
import 'reactflow/dist/style.css';
import { UMLVisualizationData, UMLNode as UMLNodeType } from '../types';

interface ReactFlowUMLPanelProps {
  umlData: UMLVisualizationData | null;
  isLoading: boolean;
}

// 表头组件
const TableHeaderNode: React.FC<NodeProps> = ({ data, selected }) => {
  const { label, isTemporary } = data;
  
  return (
    <div className={`px-4 py-2 rounded-t-lg font-bold text-white text-center min-w-[200px] ${
      isTemporary ? 'bg-orange-500' : 'bg-green-500'
    } ${selected ? 'ring-2 ring-blue-400' : ''}`}>
      {isTemporary && '⏱ '}{label}
      <Handle type="source" position={Position.Top} style={{ opacity: 0 }} />
      <Handle type="target" position={Position.Top} style={{ opacity: 0 }} />
    </div>
  );
};

// 字段组件
const TableFieldNode: React.FC<NodeProps> = ({ data, selected }) => {
  const { label, isComputed, isTemporary, isFirst, isLast, onMouseEnter, onMouseLeave } = data;
  
  const bgColor = isTemporary ? 'bg-yellow-50' : 'bg-white';
  const borderColor = isTemporary ? 'border-orange-500' : 'border-green-500';
  const textColor = isTemporary ? 'text-orange-800' : 'text-green-800';
  
  const roundedClass = isFirst && isLast 
    ? 'rounded-lg' 
    : isFirst 
      ? 'rounded-t-lg' 
      : isLast 
        ? 'rounded-b-lg' 
        : '';

  return (
    <div 
      className={`relative px-3 py-2 border-l border-r min-w-[200px] cursor-pointer transition-all duration-200 ${
        bgColor
      } ${borderColor} ${
        isLast ? 'border-b' : ''
      } ${roundedClass} ${
        selected ? 'ring-2 ring-blue-400' : ''
      } ${isComputed ? 'border-dashed italic' : 'border-solid'} hover:shadow-md hover:scale-105`}
      onMouseEnter={onMouseEnter}
      onMouseLeave={onMouseLeave}
    >
      <div className={`flex items-center ${textColor}`}>
        <span className="mr-2 font-mono">
          {isComputed ? '◆' : '•'}
        </span>
        <span className="font-mono text-sm">{label}</span>
      </div>
      
      {/* 连接点 */}
      <Handle
        type="source"
        position={Position.Right}
        style={{
          right: -6,
          width: 12,
          height: 12,
          borderRadius: '50%',
          border: '2px solid #fff',
          backgroundColor: isComputed ? '#9C27B0' : '#2196F3',
        }}
      />
      <Handle
        type="target"
        position={Position.Left}
        style={{
          left: -6,
          width: 12,
          height: 12,
          borderRadius: '50%',
          border: '2px solid #fff',
          backgroundColor: isComputed ? '#9C27B0' : '#2196F3',
        }}
      />
    </div>
  );
};

// 节点类型注册
const nodeTypes = {
  tableHeader: TableHeaderNode,
  tableField: TableFieldNode,
};

const ReactFlowUMLPanel: React.FC<ReactFlowUMLPanelProps> = ({
  umlData,
  isLoading,
}) => {
  const [nodes, setNodes, onNodesChange] = useNodesState([]);
  const [edges, setEdges, onEdgesChange] = useEdgesState([]);
  const [selectedNode, setSelectedNode] = useState<any>(null);
  const [showFieldMappings, setShowFieldMappings] = useState(true);
  const [showTableRelations, setShowTableRelations] = useState(true);
  const [hoveredField, setHoveredField] = useState<string | null>(null);

  // 处理连接
  const onConnect = useCallback(
    (params: Connection) => setEdges((eds) => addEdge(params, eds)),
    [setEdges]
  );

  // 节点点击处理
  const onNodeClick = useCallback((event: React.MouseEvent, node: Node) => {
    setSelectedNode(node.data);
  }, []);

  // 自定义节点变化处理 - 实现表头拖拽时字段跟随
  const customOnNodesChange = useCallback((changes: any[]) => {
    // 处理表头拖拽时字段跟随
    const updatedChanges = [...changes];
    
    changes.forEach((change) => {
      if (change.type === 'position' && change.position) {
        const draggedNode = nodes.find(n => n.id === change.id);
        if (draggedNode?.data.nodeType === 'header') {
          const tableId = draggedNode.data.tableId;
          const deltaX = change.position.x - draggedNode.position.x;
          const deltaY = change.position.y - draggedNode.position.y;
          
          // 为相关字段添加位置变化
          nodes.forEach((node) => {
            if (node.data.tableId === tableId && node.data.nodeType === 'field') {
              const existingChange = updatedChanges.find(c => c.id === node.id && c.type === 'position');
              if (!existingChange) {
                updatedChanges.push({
                  type: 'position',
                  id: node.id,
                  position: {
                    x: node.position.x + deltaX,
                    y: node.position.y + deltaY,
                  },
                });
              }
            }
          });
        }
      }
    });
    
    onNodesChange(updatedChanges);
  }, [nodes, onNodesChange]);

  // 生成React Flow数据
  useEffect(() => {
    if (!umlData) {
      setNodes([]);
      setEdges([]);
      return;
    }

    const flowNodes: Node[] = [];
    const flowEdges: Edge[] = [];

    // 为每个表生成节点
    umlData.nodes.forEach((table, tableIndex) => {
      const isTemporary = table.properties?.is_temporary || false;
      const fields = table.properties?.fields || [];
      
      const baseX = (tableIndex % 3) * 300;
      const baseY = Math.floor(tableIndex / 3) * 300;

      // 表头节点
      const headerNodeId = `header-${table.id}`;
      flowNodes.push({
        id: headerNodeId,
        type: 'tableHeader',
        position: { x: baseX, y: baseY },
        data: {
          label: table.label,
          isTemporary,
          tableId: table.id,
          nodeType: 'header',
          properties: table.properties,
        },
        draggable: true,
      });

      // 字段节点
      fields.forEach((field, fieldIndex) => {
        const fieldNodeId = `field-${table.id}-${fieldIndex}`;
        flowNodes.push({
          id: fieldNodeId,
          type: 'tableField',
          position: { 
            x: baseX, 
            y: baseY + 40 + (fieldIndex * 32) 
          },
          data: {
            label: field.name,
            isComputed: field.type === 'computed_field',
            isTemporary,
            isFirst: fieldIndex === 0,
            isLast: fieldIndex === fields.length - 1,
            tableId: table.id,
            fieldIndex,
            nodeType: 'field',
            field: field,
            tableName: table.label,
            onMouseEnter: () => setHoveredField(fieldNodeId),
            onMouseLeave: () => setHoveredField(null),
          },
          draggable: false, // 字段不单独拖拽
        });
      });
    });

    // 生成连接线
    if (showFieldMappings && umlData.field_mappings) {
      umlData.field_mappings.forEach((mapping, index) => {
        const sourceFieldIndex = mapping.properties?.source_field_index;
        const targetFieldIndex = mapping.properties?.target_field_index;
        
        if (typeof sourceFieldIndex === 'number' && 
            typeof targetFieldIndex === 'number' &&
            sourceFieldIndex >= 0 && targetFieldIndex >= 0) {
          
          const sourceId = `field-${mapping.source}-${sourceFieldIndex}`;
          const targetId = `field-${mapping.target}-${targetFieldIndex}`;
          const isComputed = mapping.properties?.mapping_type === 'computed_insert';
          
          // 判断是否需要高亮
          const isHighlighted = hoveredField === sourceId || hoveredField === targetId;
          
          flowEdges.push({
            id: `field-mapping-${index}`,
            source: sourceId,
            target: targetId,
            type: 'default',
            animated: isHighlighted, // 悬停时显示动画
            style: {
              stroke: '#000000', // 统一使用黑色
              strokeWidth: isHighlighted ? 3 : 2,
              strokeDasharray: isComputed ? '8,4' : undefined, // 计算字段使用虚线
              opacity: isHighlighted ? 1 : 0.3, // 常态虚化，悬停高亮
              transition: 'all 0.2s ease-in-out',
            },
            label: isHighlighted ? mapping.label : '', // 悬停时显示标签
            labelStyle: {
              fontSize: 10,
              fontWeight: 500,
              fill: '#000000',
              backgroundColor: 'rgba(255, 255, 255, 0.8)',
              padding: '2px 6px',
              borderRadius: '4px',
            },
            markerEnd: {
              type: MarkerType.ArrowClosed,
              color: '#000000',
            },
          });
        }
      });
    }

    // 表关系连接
    if (showTableRelations && umlData.table_relations) {
      umlData.table_relations.forEach((relation, index) => {
        flowEdges.push({
          id: `table-relation-${index}`,
          source: `header-${relation.source}`,
          target: `header-${relation.target}`,
          type: 'straight',
          style: {
            stroke: '#4CAF50',
            strokeWidth: 3,
          },
          label: relation.label,
          labelStyle: {
            fontSize: 11,
            fontWeight: 600,
            color: '#2E7D32',
          },
          markerEnd: {
            type: MarkerType.ArrowClosed,
            color: '#4CAF50',
            width: 20,
            height: 20,
          },
        });
      });
    }

    setNodes(flowNodes);
    setEdges(flowEdges);
  }, [umlData, showFieldMappings, showTableRelations, setNodes, setEdges]);

  if (isLoading) {
    return (
      <div className="h-full flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-16 w-16 border-b-2 border-blue-600 mx-auto mb-4"></div>
          <p className="text-gray-600">正在生成UML图...</p>
        </div>
      </div>
    );
  }

  if (!umlData) {
    return (
      <div className="h-full flex items-center justify-center">
        <div className="text-center">
          <div className="text-6xl mb-4">🚀</div>
          <h3 className="text-xl font-semibold text-gray-700 mb-2">React Flow UML图表</h3>
          <p className="text-gray-500">请输入存储过程代码并点击"UML分析"按钮</p>
          <div className="mt-4 text-sm text-green-600">
            ✨ 全新的可视化引擎，支持精确的字段级连接
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="h-full flex flex-col bg-white rounded-lg shadow-sm border">
      {/* 工具栏 */}
      <div className="flex items-center justify-between p-4 border-b bg-gray-50">
        <div className="flex items-center space-x-2">
          <h3 className="text-lg font-semibold text-gray-800 flex items-center">
            🚀 React Flow UML图表
          </h3>
          <div className="text-sm text-gray-500">
            ({umlData.metadata.total_tables} 个表, {umlData.metadata.field_mappings_count} 个字段映射)
          </div>
        </div>
        
        <div className="flex items-center space-x-2">
          <button
            onClick={() => setShowFieldMappings(!showFieldMappings)}
            className={`px-3 py-1 text-sm rounded transition-colors ${
              showFieldMappings 
                ? 'bg-blue-500 text-white' 
                : 'bg-gray-200 text-gray-700 hover:bg-gray-300'
            }`}
          >
            字段映射
          </button>
          <button
            onClick={() => setShowTableRelations(!showTableRelations)}
            className={`px-3 py-1 text-sm rounded transition-colors ${
              showTableRelations 
                ? 'bg-green-500 text-white' 
                : 'bg-gray-200 text-gray-700 hover:bg-gray-300'
            }`}
          >
            表关系
          </button>
        </div>
      </div>

      {/* React Flow 画布 */}
      <div className="flex-1 relative">
        <ReactFlow
          nodes={nodes}
          edges={edges}
          onNodesChange={customOnNodesChange}
          onEdgesChange={onEdgesChange}
          onConnect={onConnect}
          onNodeClick={onNodeClick}
          nodeTypes={nodeTypes}
          fitView
          attributionPosition="bottom-left"
        >
          <Background />
          <Controls />
          <MiniMap 
            nodeStrokeColor="#374151"
            nodeColor="#9CA3AF"
            maskColor="rgba(0, 0, 0, 0.2)"
          />
        </ReactFlow>

        {/* 详情面板 */}
        {selectedNode && (
          <div className="absolute top-4 right-4 w-80 bg-white border border-gray-200 rounded-lg shadow-lg p-4 max-h-96 overflow-y-auto">
            <div className="flex items-center justify-between mb-3">
              <h4 className="font-semibold text-gray-800">
                {selectedNode.nodeType === 'field' ? (
                  <>
                    <span className="text-blue-600">字段:</span> {selectedNode.label}
                    <div className="text-sm text-gray-600">表: {selectedNode.tableName}</div>
                  </>
                ) : (
                  <>
                    {selectedNode.isTemporary ? '🟡' : '🟢'} {selectedNode.label}
                  </>
                )}
              </h4>
              <button
                onClick={() => setSelectedNode(null)}
                className="text-gray-400 hover:text-gray-600"
              >
                ✕
              </button>
            </div>
            
            {selectedNode.nodeType === 'field' ? (
              <div className="space-y-2">
                <div className="text-sm">
                  <span className="font-medium">字段类型:</span> {
                    selectedNode.isComputed ? '计算字段' : '普通字段'
                  }
                </div>
                <div className="text-sm">
                  <span className="font-medium">字段索引:</span> {selectedNode.fieldIndex}
                </div>
                {selectedNode.field?.expression && (
                  <div className="text-sm">
                    <span className="font-medium">计算表达式:</span>
                    <div className="bg-gray-50 p-2 rounded text-xs font-mono mt-1">
                      {selectedNode.field.expression}
                    </div>
                  </div>
                )}
              </div>
            ) : (
              <div className="space-y-2">
                <div className="text-sm">
                  <span className="font-medium">类型:</span> {selectedNode.isTemporary ? '临时表' : '物理表'}
                </div>
                <div className="text-sm">
                  <span className="font-medium">字段数:</span> {selectedNode.properties?.field_count || 0}
                </div>
              </div>
            )}
          </div>
        )}

        {/* 图例 */}
        <div className="absolute bottom-4 left-4 bg-white border border-gray-200 rounded-lg shadow-lg p-4">
          <div className="text-sm font-semibold mb-2">图例</div>
          <div className="space-y-2 text-xs">
            <div className="flex items-center">
              <div className="w-4 h-3 bg-green-500 mr-2 rounded"></div>
              <span>物理表</span>
            </div>
            <div className="flex items-center">
              <div className="w-4 h-3 bg-orange-500 mr-2 rounded"></div>
              <span>临时表</span>
            </div>
            <div className="flex items-center">
              <div className="w-4 h-1 bg-black mr-2"></div>
              <span>字段映射(实线)</span>
            </div>
            <div className="flex items-center">
              <div className="w-4 h-1 border-b-2 border-dashed border-black mr-2"></div>
              <span>计算字段(虚线)</span>
            </div>
            <div className="flex items-center">
              <div className="w-4 h-1 bg-green-600 mr-2"></div>
              <span>表关系(JOIN)</span>
            </div>
            <div className="text-gray-500 text-xs mt-2">
              💡 悬停字段查看相关连接
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default ReactFlowUMLPanel; 
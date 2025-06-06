import React, { useCallback, useMemo, useState, useEffect } from 'react';
import ReactFlow, {
  Node,
  Edge,
  useNodesState,
  useEdgesState,
  Controls,
  MiniMap,
  Background,
  Handle,
  Position,
  NodeProps,
  MarkerType,
} from 'reactflow';
import 'reactflow/dist/style.css';
import { AnalysisResult, VisualizationNode, VisualizationEdge } from '../types';

interface ReactFlowVisualizationPanelProps {
  analysisResult: AnalysisResult | null;
  isLoading: boolean;
}

// 参数节点组件
const ParameterNode: React.FC<NodeProps> = ({ data, selected }) => {
  const { label } = data;
  
  return (
    <div className={`px-4 py-2 rounded-lg text-white text-center min-w-[100px] ${
      selected ? 'ring-2 ring-red-400' : ''
    }`} style={{
      background: 'linear-gradient(135deg, #0c47d6, #0d3bb8)',
      boxShadow: '0 4px 8px rgba(12, 71, 214, 0.3)',
      border: '3px solid #0e1b47',
      fontFamily: 'Inter, sans-serif',
      fontWeight: 'bold',
      fontSize: '13px'
    }}>
      🔵 {label}
      <Handle type="source" position={Position.Right} style={{ opacity: 0 }} />
      <Handle type="target" position={Position.Left} style={{ opacity: 0 }} />
    </div>
  );
};

// 物理表节点组件
const PhysicalTableNode: React.FC<NodeProps> = ({ data, selected }) => {
  const { label } = data;
  
  return (
    <div className={`px-6 py-4 rounded text-white text-center min-w-[160px] ${
      selected ? 'ring-2 ring-red-400' : ''
    }`} style={{
      background: 'linear-gradient(135deg, #10b981, #047857)',
      boxShadow: '0 4px 12px rgba(16, 185, 129, 0.4)',
      border: '3px solid #064e3b',
      fontFamily: 'Inter, sans-serif',
      fontWeight: 'bold',
      fontSize: '14px'
    }}>
      🟢 {label}
      <Handle type="source" position={Position.Right} style={{ opacity: 0 }} />
      <Handle type="source" position={Position.Bottom} style={{ opacity: 0 }} />
      <Handle type="target" position={Position.Left} style={{ opacity: 0 }} />
      <Handle type="target" position={Position.Top} style={{ opacity: 0 }} />
    </div>
  );
};

// 临时表节点组件
const TempTableNode: React.FC<NodeProps> = ({ data, selected }) => {
  const { label } = data;
  
  return (
    <div className={`px-6 py-4 rounded text-white text-center min-w-[160px] ${
      selected ? 'ring-2 ring-red-400' : ''
    }`} style={{
      background: 'linear-gradient(135deg, #f59e0b, #d97706)',
      boxShadow: '0 4px 12px rgba(245, 158, 11, 0.4)',
      border: '3px dashed #92400e',
      fontFamily: 'Inter, sans-serif',
      fontWeight: 'bold',
      fontSize: '14px'
    }}>
      🟡 {label}
      <Handle type="source" position={Position.Right} style={{ opacity: 0 }} />
      <Handle type="source" position={Position.Bottom} style={{ opacity: 0 }} />
      <Handle type="target" position={Position.Left} style={{ opacity: 0 }} />
      <Handle type="target" position={Position.Top} style={{ opacity: 0 }} />
    </div>
  );
};

// 节点类型注册
const nodeTypes = {
  parameter: ParameterNode,
  physical_table: PhysicalTableNode,
  temp_table: TempTableNode,
};

const ReactFlowVisualizationPanel: React.FC<ReactFlowVisualizationPanelProps> = ({
  analysisResult,
  isLoading,
}) => {
  const [nodes, setNodes, onNodesChange] = useNodesState([]);
  const [edges, setEdges, onEdgesChange] = useEdgesState([]);
  const [selectedNode, setSelectedNode] = useState<any>(null);
  const [showDataFlow, setShowDataFlow] = useState(true);
  const [showJoinConditions, setShowJoinConditions] = useState(true);
  const [showParameterUsage, setShowParameterUsage] = useState(true);

  // 节点点击处理
  const onNodeClick = useCallback((event: React.MouseEvent, node: Node) => {
    setSelectedNode(node.data);
  }, []);

  // 计算节点层级的函数
  const calculateNodeLevels = useCallback((nodes: VisualizationNode[], edges: VisualizationEdge[]) => {
    const levels: Record<string, number> = {};
    const inDegree: Record<string, number> = {};
    const outEdges: Record<string, string[]> = {};
    
    // 初始化
    nodes.forEach(node => {
      levels[node.id] = 0;
      inDegree[node.id] = 0;
      outEdges[node.id] = [];
    });

    // 构建图结构，只考虑数据流向边
    edges.forEach(edge => {
      if (edge.type === 'data_flow') {
        inDegree[edge.target] = (inDegree[edge.target] || 0) + 1;
        outEdges[edge.source] = outEdges[edge.source] || [];
        outEdges[edge.source].push(edge.target);
      }
    });

    // 拓扑排序确定层级
    const queue: string[] = [];
    
    // 参数节点总是在第0层
    nodes.forEach(node => {
      if (node.group === 'parameter') {
        levels[node.id] = 0;
        queue.push(node.id);
      } else if (inDegree[node.id] === 0) {
        levels[node.id] = 1; // 没有输入的表节点放在第1层
        queue.push(node.id);
      }
    });

    // BFS计算层级
    while (queue.length > 0) {
      const current = queue.shift()!;
      const currentLevel = levels[current];
      
      outEdges[current]?.forEach(target => {
        levels[target] = Math.max(levels[target], currentLevel + 1);
        inDegree[target]--;
        
        if (inDegree[target] === 0) {
          queue.push(target);
        }
      });
    }

    return levels;
  }, []);

  // 生成React Flow节点数据（仅在数据变化时重新计算位置）
  useEffect(() => {
    if (!analysisResult?.visualization) {
      setNodes([]);
      return;
    }

    const flowNodes: Node[] = [];

    // 计算节点层级
    const nodeLevels = calculateNodeLevels(
      analysisResult.visualization.nodes,
      analysisResult.visualization.edges
    );

    // 按层级分组节点
    const nodesByLevel: Record<number, VisualizationNode[]> = {};
    analysisResult.visualization.nodes.forEach(node => {
      const level = nodeLevels[node.id];
      if (!nodesByLevel[level]) {
        nodesByLevel[level] = [];
      }
      nodesByLevel[level].push(node);
    });

    // 转换节点并按层级布局
    Object.keys(nodesByLevel).forEach(levelStr => {
      const level = parseInt(levelStr);
      const nodesInLevel = nodesByLevel[level];
      
      nodesInLevel.forEach((node, indexInLevel) => {
        let nodeType = 'physical_table';
        if (node.group === 'parameter') {
          nodeType = 'parameter';
        } else if (node.group === 'temp_table') {
          nodeType = 'temp_table';
        }

        // 层级布局：X轴按层级，Y轴按同层级内的索引
        const levelWidth = 300; // 每层之间的间距
        const nodeHeight = 120; // 每个节点之间的垂直间距
        const levelOffset = level * levelWidth + 100; // X坐标
        const verticalOffset = indexInLevel * nodeHeight + 100; // Y坐标
        
        // 如果同一层节点太多，可以分列排列
        const maxNodesPerColumn = 6;
        const column = Math.floor(indexInLevel / maxNodesPerColumn);
        const rowInColumn = indexInLevel % maxNodesPerColumn;
        
        const finalX = levelOffset + (column * 200);
        const finalY = verticalOffset - (column * maxNodesPerColumn * nodeHeight / 2) + (rowInColumn * nodeHeight);

        flowNodes.push({
          id: node.id,
          type: nodeType,
          position: { x: finalX, y: finalY },
          data: {
            label: node.label,
            nodeType: node.type,
            originalData: node.data,
            group: node.group,
            level: level,
          },
          draggable: true,
        });
      });
    });

    setNodes(flowNodes);
  }, [analysisResult, setNodes]);

  // 生成连接线数据（响应显示开关）
  useEffect(() => {
    if (!analysisResult?.visualization) {
      setEdges([]);
      return;
    }

    const flowEdges: Edge[] = [];

    // 转换边
    analysisResult.visualization.edges.forEach((edge, index) => {
      if (!showDataFlow && edge.type === 'data_flow') return;
      if (!showJoinConditions && edge.type === 'join_condition') return;
      if (!showParameterUsage && edge.type === 'parameter_usage') return;

      let edgeStyle: any = {};
      let markerEnd = { type: MarkerType.ArrowClosed, color: '#569bff' };
      let animated = false;

      switch (edge.type) {
        case 'data_flow':
          edgeStyle = {
            stroke: '#569bff',
            strokeWidth: 4,
          };
          markerEnd.color = '#569bff';
          break;
        case 'join_condition':
          edgeStyle = {
            stroke: '#ef4444',
            strokeWidth: 5,
          };
          markerEnd.color = '#ef4444';
          break;
        case 'parameter_usage':
          edgeStyle = {
            stroke: '#8b5cf6',
            strokeWidth: 3,
            strokeDasharray: '8,4',
          };
          markerEnd.color = '#8b5cf6';
          animated = true;
          break;
      }

      flowEdges.push({
        id: `edge-${index}`,
        source: edge.source,
        target: edge.target,
        type: 'default',
        animated,
        style: edgeStyle,
        label: edge.label,
        labelStyle: {
          fontSize: 11,
          fontWeight: 600,
          fontFamily: 'Inter, sans-serif',
          fill: '#374151',
          backgroundColor: 'rgba(255, 255, 255, 0.9)',
          padding: '2px 6px',
          borderRadius: '4px',
          border: `1px solid ${edgeStyle.stroke || '#569bff'}`,
        },
        markerEnd,
      });
    });

    setEdges(flowEdges);
  }, [analysisResult, showDataFlow, showJoinConditions, showParameterUsage, setEdges]);

  if (isLoading) {
    return (
      <div className="h-full flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-16 w-16 border-b-2 border-blue-600 mx-auto mb-4"></div>
          <p className="text-gray-600">正在进行智能分析...</p>
        </div>
      </div>
    );
  }

  if (!analysisResult) {
    return (
      <div className="h-full flex items-center justify-center">
        <div className="text-center">
          <div className="text-6xl mb-4">📊</div>
          <h3 className="text-xl font-semibold text-gray-700 mb-2">Oracle SP 智能分析</h3>
          <p className="text-gray-500">请输入存储过程代码并点击"智能分析"按钮</p>
          <div className="mt-4 text-sm text-blue-600">
            ✨ 支持数据流向的智能层级布局
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
            📊 智能分析 (层级布局)
          </h3>
          <div className="text-sm text-gray-500">
            ({analysisResult.visualization.metadata.node_count} 个节点, {analysisResult.visualization.metadata.edge_count} 个连接)
          </div>
        </div>
        
        <div className="flex items-center space-x-2">
          <button
            onClick={() => setShowDataFlow(!showDataFlow)}
            className={`px-3 py-1 text-sm rounded transition-colors ${
              showDataFlow 
                ? 'bg-blue-500 text-white' 
                : 'bg-gray-200 text-gray-700 hover:bg-gray-300'
            }`}
          >
            数据流向
          </button>
          <button
            onClick={() => setShowJoinConditions(!showJoinConditions)}
            className={`px-3 py-1 text-sm rounded transition-colors ${
              showJoinConditions 
                ? 'bg-red-500 text-white' 
                : 'bg-gray-200 text-gray-700 hover:bg-gray-300'
            }`}
          >
            JOIN关系
          </button>
          <button
            onClick={() => setShowParameterUsage(!showParameterUsage)}
            className={`px-3 py-1 text-sm rounded transition-colors ${
              showParameterUsage 
                ? 'bg-purple-500 text-white' 
                : 'bg-gray-200 text-gray-700 hover:bg-gray-300'
            }`}
          >
            参数使用
          </button>
        </div>
      </div>

      {/* React Flow 画布 */}
      <div className="flex-1 relative">
        <ReactFlow
          nodes={nodes}
          edges={edges}
          onNodesChange={onNodesChange}
          onEdgesChange={onEdgesChange}
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
                {selectedNode.group === 'parameter' ? (
                  <span className="text-blue-600">参数: {selectedNode.label}</span>
                ) : selectedNode.group === 'temp_table' ? (
                  <span className="text-orange-600">临时表: {selectedNode.label}</span>
                ) : (
                  <span className="text-green-600">物理表: {selectedNode.label}</span>
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
                <span className="font-medium">类型:</span> {selectedNode.nodeType}
              </div>
              {selectedNode.originalData && Object.keys(selectedNode.originalData).length > 0 && (
                <div className="text-sm">
                  <span className="font-medium">详细信息:</span>
                  <div className="bg-gray-50 p-2 rounded text-xs font-mono mt-1 max-h-32 overflow-y-auto">
                    {JSON.stringify(selectedNode.originalData, null, 2)}
                  </div>
                </div>
              )}
            </div>
          </div>
        )}

        {/* 图例 */}
        <div className="absolute bottom-4 left-4 bg-white border border-gray-200 rounded-lg shadow-lg p-4">
          <div className="text-sm font-semibold mb-2">图例</div>
          <div className="space-y-2 text-xs">
            <div className="flex items-center">
              <div className="w-4 h-3 rounded mr-2" style={{background: 'linear-gradient(135deg, #0c47d6, #0d3bb8)'}}></div>
              <span>参数</span>
            </div>
            <div className="flex items-center">
              <div className="w-4 h-3 rounded mr-2" style={{background: 'linear-gradient(135deg, #10b981, #047857)'}}></div>
              <span>物理表</span>
            </div>
            <div className="flex items-center">
              <div className="w-4 h-3 rounded mr-2" style={{background: 'linear-gradient(135deg, #f59e0b, #d97706)', border: '1px dashed #92400e'}}></div>
              <span>临时表</span>
            </div>
            <div className="flex items-center">
              <div className="w-4 h-1 bg-blue-500 mr-2"></div>
              <span>数据流向</span>
            </div>
            <div className="flex items-center">
              <div className="w-4 h-1 bg-red-500 mr-2"></div>
              <span>JOIN关系</span>
            </div>
            <div className="flex items-center">
              <div className="w-4 h-1 border-b-2 border-dashed border-purple-500 mr-2"></div>
              <span>参数使用</span>
            </div>
            <div className="text-gray-500 text-xs mt-2">
              💡 层级布局：数据流向从左到右
            </div>
          </div>
        </div>

        {/* 统计信息面板 */}
        {analysisResult.data.statistics && (
          <div className="absolute top-4 left-4 bg-white border border-gray-200 rounded-lg shadow-lg p-4">
            <div className="text-sm font-semibold mb-2">分析统计</div>
            <div className="space-y-1 text-xs">
              <div>📋 SQL语句: {analysisResult.data.statistics.sql_statement_count}</div>
              <div>🔵 参数: {analysisResult.data.statistics.parameter_count}</div>
              <div>🟢 物理表: {analysisResult.data.statistics.physical_table_count}</div>
              <div>🟡 临时表: {analysisResult.data.statistics.temporary_table_count}</div>
              <div>🔗 JOIN条件: {analysisResult.data.statistics.join_condition_count}</div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default ReactFlowVisualizationPanel; 
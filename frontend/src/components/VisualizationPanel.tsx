import React, { useEffect, useRef, useState } from 'react';
import cytoscape from 'cytoscape';
import cose from 'cytoscape-cose-bilkent';
import { AnalysisResult, VisualizationNode } from '../types';

// 注册布局算法
cytoscape.use(cose);

interface VisualizationPanelProps {
  analysisResult: AnalysisResult | null;
  isLoading: boolean;
}

const VisualizationPanel: React.FC<VisualizationPanelProps> = ({
  analysisResult,
  isLoading,
}) => {
  const containerRef = useRef<HTMLDivElement>(null);
  const cyRef = useRef<cytoscape.Core | null>(null);
  const [selectedNode, setSelectedNode] = useState<VisualizationNode | null>(null);

  // Cytoscape样式配置
  const cytoscapeStyle: any[] = [
    // 参数节点样式
    {
      selector: 'node[group = "parameter"]',
      style: {
        'background-color': '#3b82f6',
        'label': 'data(label)',
        'color': '#ffffff',
        'text-valign': 'center',
        'text-halign': 'center',
        'font-size': '12px',
        'font-weight': 'bold',
        'width': '80px',
        'height': '40px',
        'shape': 'round-rectangle',
        'border-width': '2px',
        'border-color': '#1e40af',
      },
    },
    // 物理表节点样式
    {
      selector: 'node[group = "physical_table"]',
      style: {
        'background-color': '#10b981',
        'label': 'data(label)',
        'color': '#ffffff',
        'text-valign': 'center',
        'text-halign': 'center',
        'font-size': '14px',
        'font-weight': 'bold',
        'width': '120px',
        'height': '60px',
        'shape': 'rectangle',
        'border-width': '3px',
        'border-color': '#047857',
      },
    },
    // 临时表节点样式
    {
      selector: 'node[group = "temp_table"]',
      style: {
        'background-color': '#f59e0b',
        'label': 'data(label)',
        'color': '#ffffff',
        'text-valign': 'center',
        'text-halign': 'center',
        'font-size': '14px',
        'font-weight': 'bold',
        'width': '120px',
        'height': '60px',
        'shape': 'rectangle',
        'border-width': '3px',
        'border-color': '#d97706',
        'border-style': 'dashed',
      },
    },
    // 数据流边样式
    {
      selector: 'edge[type = "data_flow"]',
      style: {
        'width': '3px',
        'line-color': '#6366f1',
        'target-arrow-color': '#6366f1',
        'target-arrow-shape': 'triangle',
        'curve-style': 'bezier',
        'label': 'data(label)',
        'font-size': '10px',
        'text-rotation': 'autorotate',
        'text-margin-y': '-10px',
      },
    },
    // JOIN条件边样式
    {
      selector: 'edge[type = "join_condition"]',
      style: {
        'width': '4px',
        'line-color': '#dc2626',
        'target-arrow-color': '#dc2626',
        'target-arrow-shape': 'triangle',
        'curve-style': 'bezier',
        'label': 'data(label)',
        'font-size': '10px',
        'text-rotation': 'autorotate',
        'text-margin-y': '-10px',
        'line-style': 'solid',
      },
    },
    // 参数使用边样式
    {
      selector: 'edge[type = "parameter_usage"]',
      style: {
        'width': '2px',
        'line-color': '#8b5cf6',
        'target-arrow-color': '#8b5cf6',
        'target-arrow-shape': 'triangle',
        'curve-style': 'bezier',
        'line-style': 'dashed',
        'opacity': 0.7,
      },
    },
    // 选中节点样式
    {
      selector: 'node:selected',
      style: {
        'border-width': '4px',
        'border-color': '#ef4444',
        'box-shadow': '0 0 20px rgba(239, 68, 68, 0.6)',
      },
    },
    // 悬停效果
    {
      selector: 'node:active',
      style: {
        'overlay-opacity': 0.2,
        'overlay-color': '#000000',
      },
    },
  ];

  // 初始化Cytoscape
  useEffect(() => {
    if (!containerRef.current) return;

    cyRef.current = cytoscape({
      container: containerRef.current,
      style: cytoscapeStyle,
      layout: {
        name: 'cose',
        animate: true,
        animationDuration: 1000,
        randomize: false,
      },
      minZoom: 0.1,
      maxZoom: 3,
      wheelSensitivity: 0.1,
    });

    // 添加节点点击事件
    cyRef.current.on('tap', 'node', (event) => {
      const node = event.target;
      const nodeData = node.data();
      setSelectedNode(nodeData);
    });

    // 添加背景点击事件（取消选择）
    cyRef.current.on('tap', (event) => {
      if (event.target === cyRef.current) {
        setSelectedNode(null);
        cyRef.current?.nodes().unselect();
      }
    });

    return () => {
      cyRef.current?.destroy();
    };
  }, []);

  // 更新图数据
  useEffect(() => {
    if (!cyRef.current || !analysisResult?.visualization) return;

    const { nodes, edges } = analysisResult.visualization;

    // 转换数据格式
    const cytoscapeElements = [
      ...nodes.map((node) => ({
        data: {
          id: node.id,
          label: node.label,
          type: node.type,
          group: node.group,
          ...node.data,
        },
      })),
      ...edges.map((edge) => ({
        data: {
          id: edge.id,
          source: edge.source,
          target: edge.target,
          type: edge.type,
          label: edge.label,
          ...edge.data,
        },
      })),
    ];

    // 更新图数据
    cyRef.current.elements().remove();
    cyRef.current.add(cytoscapeElements);

    // 重新布局
    const layout = cyRef.current.layout({
      name: 'cose',
      animate: true,
      animationDuration: 1000,
      randomize: false,
    });

    layout.run();

    // 适应视图
    setTimeout(() => {
      cyRef.current?.fit(undefined, 50);
    }, 1200);
  }, [analysisResult]);

  const handleResetView = () => {
    cyRef.current?.fit(undefined, 50);
  };

  const handleCenterSelected = () => {
    const selected = cyRef.current?.$(':selected');
    if (selected && selected.length > 0) {
      cyRef.current?.center(selected);
    }
  };

  const getNodeTypeIcon = (type: string) => {
    switch (type) {
      case 'parameter':
        return '📋';
      case 'physical_table':
        return '🗃️';
      case 'temp_table':
        return '📦';
      default:
        return '⚪';
    }
  };

  return (
    <div className="bg-white rounded-lg shadow-sm border border-gray-200 h-full">
      {/* 头部工具栏 */}
      <div className="px-4 py-3 border-b border-gray-200 flex justify-between items-center">
        <h2 className="text-lg font-semibold text-gray-800">数据流向图</h2>
        <div className="flex space-x-2">
          <button
            onClick={handleResetView}
            className="px-3 py-1 text-sm bg-gray-100 hover:bg-gray-200 rounded-md transition-colors"
            disabled={!analysisResult}
          >
            重置视图
          </button>
          <button
            onClick={handleCenterSelected}
            className="px-3 py-1 text-sm bg-blue-100 hover:bg-blue-200 text-blue-700 rounded-md transition-colors"
            disabled={!selectedNode}
          >
            居中选中
          </button>
        </div>
      </div>

      {/* 主要内容区域 */}
      <div className="flex h-96 lg:h-[600px]">
        {/* 可视化容器 */}
        <div className="flex-1 relative">
          {isLoading && (
            <div className="absolute inset-0 bg-gray-50 flex items-center justify-center z-10">
              <div className="text-center">
                <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto"></div>
                <p className="mt-2 text-gray-600">正在分析存储过程...</p>
              </div>
            </div>
          )}
          
          {!analysisResult && !isLoading && (
            <div className="absolute inset-0 bg-gray-50 flex items-center justify-center">
              <div className="text-center text-gray-500">
                <div className="text-6xl mb-4">📊</div>
                <p className="text-lg">请输入存储过程进行分析</p>
              </div>
            </div>
          )}
          
          <div ref={containerRef} className="w-full h-full" />
        </div>

        {/* 侧边信息面板 */}
        {selectedNode && (
          <div className="w-80 border-l border-gray-200 p-4 overflow-y-auto">
            <h3 className="text-lg font-semibold mb-3 flex items-center">
              <span className="mr-2">{getNodeTypeIcon(selectedNode.type)}</span>
              节点详情
            </h3>
            
            <div className="space-y-3">
              <div>
                <label className="block text-sm font-medium text-gray-700">名称</label>
                <p className="text-sm text-gray-900 bg-gray-50 p-2 rounded">{selectedNode.label}</p>
              </div>
              
              <div>
                <label className="block text-sm font-medium text-gray-700">类型</label>
                <p className="text-sm text-gray-900 bg-gray-50 p-2 rounded">
                  {selectedNode.type === 'parameter' ? '参数' :
                   selectedNode.type === 'physical_table' ? '物理表' :
                   selectedNode.type === 'temp_table' ? '临时表' : selectedNode.type}
                </p>
              </div>

              {selectedNode.type === 'parameter' && selectedNode.data && (
                <>
                  <div>
                    <label className="block text-sm font-medium text-gray-700">方向</label>
                    <p className="text-sm text-gray-900 bg-gray-50 p-2 rounded">
                      {selectedNode.data.direction}
                    </p>
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700">数据类型</label>
                    <p className="text-sm text-gray-900 bg-gray-50 p-2 rounded">
                      {selectedNode.data.data_type}
                    </p>
                  </div>
                </>
              )}

              {(selectedNode.type === 'physical_table' || selectedNode.type === 'temp_table') && selectedNode.data && (
                <>
                  {selectedNode.data.fields && selectedNode.data.fields.length > 0 && (
                    <div>
                      <label className="block text-sm font-medium text-gray-700">字段</label>
                      <div className="bg-gray-50 p-2 rounded text-sm">
                        {selectedNode.data.fields.map((field: string, index: number) => (
                          <div key={index} className="py-1">• {field}</div>
                        ))}
                      </div>
                    </div>
                  )}
                </>
              )}
            </div>
          </div>
        )}
      </div>

      {/* 图例 */}
      {analysisResult && (
        <div className="px-4 py-3 border-t border-gray-200 bg-gray-50">
          <h4 className="text-sm font-medium text-gray-700 mb-2">图例</h4>
          <div className="flex flex-wrap gap-4 text-xs">
            <div className="flex items-center">
              <div className="w-4 h-4 bg-blue-500 rounded mr-2"></div>
              <span>参数</span>
            </div>
            <div className="flex items-center">
              <div className="w-4 h-4 bg-green-500 mr-2"></div>
              <span>物理表</span>
            </div>
            <div className="flex items-center">
              <div className="w-4 h-4 bg-yellow-500 border-2 border-dashed border-yellow-600 mr-2"></div>
              <span>临时表</span>
            </div>
            <div className="flex items-center">
              <div className="w-6 h-0.5 bg-indigo-500 mr-2"></div>
              <span>数据流</span>
            </div>
            <div className="flex items-center">
              <div className="w-6 h-0.5 bg-red-500 mr-2"></div>
              <span>JOIN连接</span>
            </div>
            <div className="flex items-center">
              <div className="w-6 h-0.5 bg-purple-500 border-dashed mr-2" style={{borderTopWidth: '1px'}}></div>
              <span>参数使用</span>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default VisualizationPanel; 
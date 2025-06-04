import React, { useEffect, useRef, useState, useMemo } from 'react';
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
  const [showLegend, setShowLegend] = useState(true);

  // 克莱因蓝主题的Cytoscape样式配置 - 使用useMemo优化
  const cytoscapeStyle = useMemo(() => [
    // 参数节点样式
    {
      selector: 'node[group = "parameter"]',
      style: {
        'background-color': '#0c47d6',
        'background-gradient-stop-colors': '#0c47d6 #0d3bb8',
        'background-gradient-direction': 'to-bottom',
        'label': 'data(label)',
        'color': '#ffffff',
        'text-valign': 'center',
        'text-halign': 'center',
        'font-size': '13px',
        'font-weight': 'bold',
        'font-family': 'Inter, sans-serif',
        'width': '90px',
        'height': '45px',
        'shape': 'round-rectangle',
        'border-width': '3px',
        'border-color': '#0e1b47',
        'box-shadow': '0 4px 8px rgba(12, 71, 214, 0.3)',
      },
    },
    // 物理表节点样式
    {
      selector: 'node[group = "physical_table"]',
      style: {
        'background-color': '#10b981',
        'background-gradient-stop-colors': '#10b981 #047857',
        'background-gradient-direction': 'to-bottom',
        'label': 'data(label)',
        'color': '#ffffff',
        'text-valign': 'center',
        'text-halign': 'center',
        'font-size': '14px',
        'font-weight': 'bold',
        'font-family': 'Inter, sans-serif',
        'width': '140px',
        'height': '70px',
        'shape': 'rectangle',
        'border-width': '3px',
        'border-color': '#064e3b',
        'box-shadow': '0 4px 12px rgba(16, 185, 129, 0.4)',
      },
    },
    // 临时表节点样式
    {
      selector: 'node[group = "temp_table"]',
      style: {
        'background-color': '#f59e0b',
        'background-gradient-stop-colors': '#f59e0b #d97706',
        'background-gradient-direction': 'to-bottom',
        'label': 'data(label)',
        'color': '#ffffff',
        'text-valign': 'center',
        'text-halign': 'center',
        'font-size': '14px',
        'font-weight': 'bold',
        'font-family': 'Inter, sans-serif',
        'width': '140px',
        'height': '70px',
        'shape': 'rectangle',
        'border-width': '3px',
        'border-color': '#92400e',
        'border-style': 'dashed',
        'box-shadow': '0 4px 12px rgba(245, 158, 11, 0.4)',
      },
    },
    // 数据流边样式
    {
      selector: 'edge[type = "data_flow"]',
      style: {
        'width': '4px',
        'line-color': '#569bff',
        'target-arrow-color': '#569bff',
        'target-arrow-shape': 'triangle',
        'target-arrow-size': '12px',
        'curve-style': 'bezier',
        'label': 'data(label)',
        'font-size': '11px',
        'font-family': 'Inter, sans-serif',
        'font-weight': '600',
        'text-rotation': 'autorotate',
        'text-margin-y': '-12px',
        'text-background-color': '#ffffff',
        'text-background-opacity': 0.8,
        'text-background-padding': '3px',
        'text-border-color': '#569bff',
        'text-border-width': 1,
        'text-border-opacity': 0.5,
      },
    },
    // JOIN条件边样式
    {
      selector: 'edge[type = "join_condition"]',
      style: {
        'width': '5px',
        'line-color': '#ef4444',
        'target-arrow-color': '#ef4444',
        'target-arrow-shape': 'triangle',
        'target-arrow-size': '14px',
        'curve-style': 'bezier',
        'label': 'data(label)',
        'font-size': '11px',
        'font-family': 'Inter, sans-serif',
        'font-weight': '600',
        'text-rotation': 'autorotate',
        'text-margin-y': '-12px',
        'text-background-color': '#ffffff',
        'text-background-opacity': 0.9,
        'text-background-padding': '3px',
        'text-border-color': '#ef4444',
        'text-border-width': 1,
        'text-border-opacity': 0.5,
      },
    },
    // 参数使用边样式
    {
      selector: 'edge[type = "parameter_usage"]',
      style: {
        'width': '3px',
        'line-color': '#8b5cf6',
        'target-arrow-color': '#8b5cf6',
        'target-arrow-shape': 'triangle',
        'target-arrow-size': '10px',
        'curve-style': 'bezier',
        'line-style': 'dashed',
        'opacity': 0.8,
      },
    },
    // 选中节点样式
    {
      selector: 'node:selected',
      style: {
        'border-width': '5px',
        'border-color': '#ff6b6b',
        'border-opacity': 1,
        'z-index': 999,
        'overlay-opacity': 0.2,
        'overlay-color': '#ff6b6b',
      },
    },
    // 悬停效果
    {
      selector: 'node:active',
      style: {
        'overlay-opacity': 0.15,
        'overlay-color': '#0c47d6',
      },
    },
  ] as any[], []);

  // 初始化Cytoscape
  useEffect(() => {
    if (!containerRef.current) return;

    cyRef.current = cytoscape({
      container: containerRef.current,
      style: cytoscapeStyle,
      layout: {
        name: 'cose',
        animate: true,
        animationDuration: 1200,
        randomize: false,
        nodeRepulsion: () => 8000,
        idealEdgeLength: () => 80,
        edgeElasticity: () => 200,
      },
      minZoom: 0.1,
      maxZoom: 4,
      wheelSensitivity: 0.15,
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
  }, [cytoscapeStyle]);

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
      animationDuration: 1200,
      randomize: false,
      nodeRepulsion: () => 8000,
      idealEdgeLength: () => 80,
      edgeElasticity: () => 200,
    });

    layout.run();

    // 适应视图
    setTimeout(() => {
      cyRef.current?.fit(undefined, 50);
    }, 1400);
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

  const handleExportImage = () => {
    if (cyRef.current) {
      const png64 = cyRef.current.png({
        output: 'blob',
        bg: 'white',
        full: true,
        scale: 2,
      });
      
      const link = document.createElement('a');
      link.href = URL.createObjectURL(png64);
      link.download = 'data-flow-diagram.png';
      link.click();
    }
  };

  const getNodeTypeIcon = (type: string) => {
    switch (type) {
      case 'parameter':
        return (
          <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5H7a2 2 0 00-2 2v10a2 2 0 002 2h8a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2" />
          </svg>
        );
      case 'physical_table':
        return (
          <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 7v10c0 2.21 3.582 4 8 4s8-1.79 8-4V7M4 7c0 2.21 3.582 4 8 4s8-1.79 8-4M4 7c0-2.21 3.582-4 8-4s8 1.79 8 4" />
          </svg>
        );
      case 'temp_table':
        return (
          <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M20 7l-8-4-8 4m16 0l-8 4m8-4v10l-8 4m0-10L4 7m8 4v10M4 7v10l8 4" />
          </svg>
        );
      default:
        return (
          <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 11H5m14 0a2 2 0 012 2v6a2 2 0 01-2 2H5a2 2 0 01-2-2v-6a2 2 0 012-2m14 0V9a2 2 0 00-2-2M5 11V9a2 2 0 012-2m0 0V5a2 2 0 012-2h6a2 2 0 012 2v2M7 7h10" />
          </svg>
        );
    }
  };

  return (
    <div className="h-full flex flex-col">
      {/* 现代化头部工具栏 */}
      <div className="mb-4">
        <div className="flex items-center justify-between mb-3">
          <div className="flex items-center space-x-3">
            <div className="w-8 h-8 bg-gradient-klein-dark rounded-lg flex items-center justify-center">
              <svg className="w-5 h-5 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M11 3.055A9.001 9.001 0 1020.945 13H11V3.055z" />
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M20.488 9H15V3.512A9.025 9.025 0 0120.488 9z" />
              </svg>
            </div>
            <h2 className="text-xl font-bold text-klein-700">数据流向可视化</h2>
          </div>
          
          <div className="flex items-center space-x-2">
            <button
              onClick={() => setShowLegend(!showLegend)}
              className="btn btn-ghost btn-sm"
            >
              <svg className="w-4 h-4 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
              {showLegend ? '隐藏图例' : '显示图例'}
            </button>
            <button
              onClick={handleResetView}
              className="btn btn-secondary btn-sm"
              disabled={!analysisResult}
            >
              <svg className="w-4 h-4 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
              </svg>
              重置视图
            </button>
            <button
              onClick={handleCenterSelected}
              className="btn btn-secondary btn-sm"
              disabled={!selectedNode}
            >
              <svg className="w-4 h-4 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" />
              </svg>
              居中选中
            </button>
            <button
              onClick={handleExportImage}
              className="btn btn-primary btn-sm"
              disabled={!analysisResult}
            >
              <svg className="w-4 h-4 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 10v6m0 0l-3-3m3 3l3-3m2 8H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
              </svg>
              导出图片
            </button>
          </div>
        </div>
        
        {/* 分析结果概览 */}
        {analysisResult && (
          <div className="flex items-center space-x-6 text-sm">
            <div className="flex items-center space-x-2">
              <div className="w-3 h-3 bg-klein-500 rounded-full"></div>
              <span className="text-klein-600">
                {analysisResult.visualization?.nodes?.filter(n => n.group === 'parameter').length || 0} 个参数
              </span>
            </div>
            <div className="flex items-center space-x-2">
              <div className="w-3 h-3 bg-emerald-500 rounded-sm"></div>
              <span className="text-klein-600">
                {analysisResult.visualization?.nodes?.filter(n => n.group === 'physical_table').length || 0} 个物理表
              </span>
            </div>
            <div className="flex items-center space-x-2">
              <div className="w-3 h-3 bg-amber-500 rounded-sm border border-amber-600 border-dashed"></div>
              <span className="text-klein-600">
                {analysisResult.visualization?.nodes?.filter(n => n.group === 'temp_table').length || 0} 个临时表
              </span>
            </div>
            <div className="flex items-center space-x-2">
              <div className="w-4 h-0.5 bg-klein-400"></div>
              <span className="text-klein-600">
                {analysisResult.visualization?.edges?.length || 0} 个连接
              </span>
            </div>
          </div>
        )}
      </div>

      {/* 主要内容区域 */}
      <div className="flex-1 flex overflow-hidden rounded-2xl">
        {/* 可视化容器 */}
        <div className="flex-1 relative bg-gradient-to-br from-klein-50/30 to-accent-50/30 overflow-hidden">
          {isLoading && (
            <div className="absolute inset-0 bg-white/90 backdrop-blur-sm flex items-center justify-center z-10">
              <div className="text-center">
                <div className="loader-klein w-12 h-12 mx-auto mb-4"></div>
                <p className="text-klein-600 font-medium">正在分析存储过程...</p>
                <p className="text-klein-500 text-sm mt-1">构建数据流向图谱</p>
              </div>
            </div>
          )}
          
          {!analysisResult && !isLoading && (
            <div className="absolute inset-0 flex items-center justify-center">
              <div className="text-center">
                <div className="w-24 h-24 bg-gradient-klein-dark rounded-3xl flex items-center justify-center mx-auto mb-6 shadow-klein">
                  <svg className="w-12 h-12 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
                  </svg>
                </div>
                <h3 className="text-2xl font-bold text-klein-700 mb-2">等待分析</h3>
                <p className="text-klein-600">请在左侧输入存储过程代码开始分析</p>
              </div>
            </div>
          )}
          
          <div ref={containerRef} className="w-full h-full" />
        </div>

        {/* 节点详情侧边栏 */}
        {selectedNode && (
          <div className="w-80 bg-white/90 backdrop-blur-md border-l border-klein-200/50 p-6 overflow-y-auto scrollbar-klein animate-slide-up">
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-lg font-bold text-klein-700 flex items-center">
                <div className="text-klein-600 mr-3">{getNodeTypeIcon(selectedNode.type)}</div>
                节点详情
              </h3>
              <button
                onClick={() => setSelectedNode(null)}
                className="btn btn-ghost btn-sm w-8 h-8 p-0"
              >
                <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                </svg>
              </button>
            </div>
            
            <div className="space-y-4">
              <div>
                <label className="form-label">名称</label>
                <div className="form-input bg-klein-50/50 border-klein-200/50">
                  {selectedNode.label}
                </div>
              </div>
              
              <div>
                <label className="form-label">类型</label>
                <div className="form-input bg-klein-50/50 border-klein-200/50">
                  <div className="flex items-center space-x-2">
                    <div className="text-klein-600">{getNodeTypeIcon(selectedNode.type)}</div>
                    <span>
                      {selectedNode.type === 'parameter' ? '输入参数' :
                       selectedNode.type === 'physical_table' ? '物理表' :
                       selectedNode.type === 'temp_table' ? '临时表' : selectedNode.type}
                    </span>
                  </div>
                </div>
              </div>

              {selectedNode.type === 'parameter' && selectedNode.data && (
                <>
                  <div>
                    <label className="form-label">方向</label>
                    <div className="form-input bg-klein-50/50 border-klein-200/50">
                      <span className="badge badge-klein">
                        {selectedNode.data.direction}
                      </span>
                    </div>
                  </div>
                  <div>
                    <label className="form-label">数据类型</label>
                    <div className="form-input bg-klein-50/50 border-klein-200/50 font-mono text-sm">
                      {selectedNode.data.data_type}
                    </div>
                  </div>
                </>
              )}

              {(selectedNode.type === 'physical_table' || selectedNode.type === 'temp_table') && selectedNode.data && (
                <>
                  {selectedNode.data.fields && selectedNode.data.fields.length > 0 && (
                    <div>
                      <label className="form-label">字段列表</label>
                      <div className="bg-klein-50/50 border border-klein-200/50 rounded-xl p-3">
                        <div className="space-y-2">
                          {selectedNode.data.fields.map((field: string, index: number) => (
                            <div key={index} className="flex items-center space-x-2 text-sm">
                              <div className="w-1.5 h-1.5 bg-klein-400 rounded-full"></div>
                              <span className="font-mono text-klein-700">{field}</span>
                            </div>
                          ))}
                        </div>
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
      {analysisResult && showLegend && (
        <div className="mt-4 p-4 bg-gradient-to-r from-klein-50/50 to-accent-50/50 border border-klein-200/50 rounded-xl">
          <h4 className="text-sm font-bold text-klein-700 mb-3 flex items-center">
            <svg className="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4M7.835 4.697a3.42 3.42 0 001.946-.806 3.42 3.42 0 014.438 0 3.42 3.42 0 001.946.806 3.42 3.42 0 013.138 3.138 3.42 3.42 0 00.806 1.946 3.42 3.42 0 010 4.438 3.42 3.42 0 00-.806 1.946 3.42 3.42 0 01-3.138 3.138 3.42 3.42 0 00-1.946.806 3.42 3.42 0 01-4.438 0 3.42 3.42 0 00-1.946-.806 3.42 3.42 0 01-3.138-3.138 3.42 3.42 0 00-.806-1.946 3.42 3.42 0 010-4.438 3.42 3.42 0 00.806-1.946 3.42 3.42 0 013.138-3.138z" />
            </svg>
            图例说明
          </h4>
          <div className="grid grid-cols-2 lg:grid-cols-3 gap-4 text-sm">
            <div className="flex items-center space-x-3">
              <div className="w-5 h-5 bg-gradient-to-b from-klein-600 to-klein-700 rounded-lg border-2 border-klein-800"></div>
              <span className="text-klein-700 font-medium">参数节点</span>
            </div>
            <div className="flex items-center space-x-3">
              <div className="w-5 h-5 bg-gradient-to-b from-emerald-500 to-emerald-600 border-2 border-emerald-700"></div>
              <span className="text-klein-700 font-medium">物理表</span>
            </div>
            <div className="flex items-center space-x-3">
              <div className="w-5 h-5 bg-gradient-to-b from-amber-500 to-amber-600 border-2 border-amber-700 border-dashed"></div>
              <span className="text-klein-700 font-medium">临时表</span>
            </div>
            <div className="flex items-center space-x-3">
              <div className="flex items-center">
                <div className="w-6 h-1 bg-accent-500 rounded-full"></div>
                <div className="w-0 h-0 border-l-4 border-l-accent-500 border-t-2 border-b-2 border-t-transparent border-b-transparent ml-1"></div>
              </div>
              <span className="text-klein-700 font-medium">数据流向</span>
            </div>
            <div className="flex items-center space-x-3">
              <div className="flex items-center">
                <div className="w-6 h-1 bg-red-500 rounded-full"></div>
                <div className="w-0 h-0 border-l-4 border-l-red-500 border-t-2 border-b-2 border-t-transparent border-b-transparent ml-1"></div>
              </div>
              <span className="text-klein-700 font-medium">JOIN连接</span>
            </div>
            <div className="flex items-center space-x-3">
              <div className="flex items-center">
                <div className="w-6 h-0.5 bg-purple-500 border-t border-dashed border-purple-500"></div>
                <div className="w-0 h-0 border-l-3 border-l-purple-500 border-t-1.5 border-b-1.5 border-t-transparent border-b-transparent ml-1"></div>
              </div>
              <span className="text-klein-700 font-medium">参数使用</span>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default VisualizationPanel; 
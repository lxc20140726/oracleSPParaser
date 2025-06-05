import React, { useState } from 'react';
import { Toaster } from 'react-hot-toast';
import Header from './components/Header';
import InputPanel from './components/InputPanel';
import VisualizationPanel from './components/VisualizationPanel';
import UMLVisualizationPanel from './components/UMLVisualizationPanel';
import ResultsPanel from './components/ResultsPanel';
import { AnalysisResult } from './types';
import './App.css';

const App: React.FC = () => {
  const [analysisResult, setAnalysisResult] = useState<AnalysisResult | null>(null);
  const [umlAnalysisResult, setUMLAnalysisResult] = useState<AnalysisResult | null>(null);
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [activeView, setActiveView] = useState<'standard' | 'uml'>('standard');

  const handleAnalysisComplete = (result: AnalysisResult) => {
    setAnalysisResult(result);
    setActiveView('standard');
    setIsAnalyzing(false);
  };

  const handleUMLAnalysisComplete = (result: AnalysisResult) => {
    setUMLAnalysisResult(result);
    setActiveView('uml');
    setIsAnalyzing(false);
  };

  const handleAnalysisStart = () => {
    setIsAnalyzing(true);
    setAnalysisResult(null);
    setUMLAnalysisResult(null);
  };

  const handleAnalysisError = () => {
    setIsAnalyzing(false);
  };

  return (
    <div className="min-h-screen" style={{ background: 'linear-gradient(135deg, #e8f4ff 0%, #f0f9ff 100%)' }}>
      {/* 现代化头部 */}
      <Header />
      
      {/* 主内容区域 - 左侧输入，右侧可视化 */}
      <main className="container mx-auto px-6 py-8">
        <div className="flex gap-8 min-h-[calc(100vh-160px)]">
          {/* 左侧SP输入面板 - 固定宽度 */}
          <div className="w-96 flex-shrink-0">
            <div className="input-panel sticky top-8">
              <InputPanel
                onAnalysisStart={handleAnalysisStart}
                onAnalysisComplete={handleAnalysisComplete}
                onUMLAnalysisComplete={handleUMLAnalysisComplete}
                onAnalysisError={handleAnalysisError}
                isAnalyzing={isAnalyzing}
              />
            </div>
          </div>

          {/* 右侧可视化区域 - 占据剩余空间 */}
          <div className="flex-1 flex flex-col gap-6">
            {/* 视图切换按钮 */}
            {(analysisResult || umlAnalysisResult) && (
              <div className="flex justify-center">
                <div className="bg-white rounded-lg shadow-sm border p-1 flex">
                  <button
                    onClick={() => setActiveView('standard')}
                    className={`px-4 py-2 rounded-md text-sm font-medium transition-colors ${
                      activeView === 'standard'
                        ? 'bg-blue-500 text-white'
                        : 'text-gray-600 hover:text-gray-800'
                    }`}
                    disabled={!analysisResult}
                  >
                    📊 标准视图
                  </button>
                  <button
                    onClick={() => setActiveView('uml')}
                    className={`px-4 py-2 rounded-md text-sm font-medium transition-colors ${
                      activeView === 'uml'
                        ? 'bg-purple-500 text-white'
                        : 'text-gray-600 hover:text-gray-800'
                    }`}
                    disabled={!umlAnalysisResult}
                  >
                    🗂️ UML视图
                  </button>
                </div>
              </div>
            )}

            {/* 主要可视化面板 */}
            <div className="visualization-panel flex-1">
              {activeView === 'standard' ? (
                <VisualizationPanel
                  analysisResult={analysisResult}
                  isLoading={isAnalyzing}
                />
              ) : (
                <UMLVisualizationPanel
                  umlData={umlAnalysisResult?.uml_visualization || null}
                  isLoading={isAnalyzing}
                />
              )}
            </div>
            
            {/* 结果详情面板 - 仅在有结果时显示 */}
            {(analysisResult || umlAnalysisResult) && (
              <div className="animate-slide-up">
                <ResultsPanel analysisResult={activeView === 'standard' ? analysisResult : umlAnalysisResult} />
              </div>
            )}
          </div>
        </div>
      </main>

      {/* 优雅的通知系统 */}
      <Toaster
        position="top-right"
        toastOptions={{
          duration: 4000,
          style: {
            background: 'rgba(255, 255, 255, 0.95)',
            backdropFilter: 'blur(12px)',
            color: '#0c47d6',
            border: '1px solid rgba(12, 71, 214, 0.1)',
            borderRadius: '16px',
            boxShadow: '0 4px 20px -4px rgba(12, 71, 214, 0.25)',
          },
          success: {
            duration: 3000,
            iconTheme: {
              primary: '#10b981',
              secondary: '#ffffff',
            },
          },
          error: {
            duration: 5000,
            iconTheme: {
              primary: '#ef4444',
              secondary: '#ffffff',
            },
          },
        }}
      />
    </div>
  );
};

export default App; 
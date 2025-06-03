import React, { useState } from 'react';
import { Toaster } from 'react-hot-toast';
import Header from './components/Header';
import InputPanel from './components/InputPanel';
import VisualizationPanel from './components/VisualizationPanel';
import ResultsPanel from './components/ResultsPanel';
import { AnalysisResult } from './types';
import './App.css';

const App: React.FC = () => {
  const [analysisResult, setAnalysisResult] = useState<AnalysisResult | null>(null);
  const [isAnalyzing, setIsAnalyzing] = useState(false);

  const handleAnalysisComplete = (result: AnalysisResult) => {
    setAnalysisResult(result);
    setIsAnalyzing(false);
  };

  const handleAnalysisStart = () => {
    setIsAnalyzing(true);
    setAnalysisResult(null);
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
                onAnalysisError={handleAnalysisError}
                isAnalyzing={isAnalyzing}
              />
            </div>
          </div>

          {/* 右侧可视化区域 - 占据剩余空间 */}
          <div className="flex-1 flex flex-col gap-6">
            {/* 主要可视化面板 */}
            <div className="visualization-panel flex-1">
              <VisualizationPanel
                analysisResult={analysisResult}
                isLoading={isAnalyzing}
              />
            </div>
            
            {/* 结果详情面板 - 仅在有结果时显示 */}
            {analysisResult && (
              <div className="animate-slide-up">
                <ResultsPanel analysisResult={analysisResult} />
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
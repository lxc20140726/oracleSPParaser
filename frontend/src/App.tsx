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
    <div className="min-h-screen bg-gray-50">
      <Header />
      
      <main className="container mx-auto px-4 py-6">
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* 输入面板 */}
          <div className="lg:col-span-1">
            <InputPanel
              onAnalysisStart={handleAnalysisStart}
              onAnalysisComplete={handleAnalysisComplete}
              onAnalysisError={handleAnalysisError}
              isAnalyzing={isAnalyzing}
            />
          </div>

          {/* 可视化面板 */}
          <div className="lg:col-span-2">
            <VisualizationPanel
              analysisResult={analysisResult}
              isLoading={isAnalyzing}
            />
          </div>
        </div>

        {/* 结果详情面板 */}
        {analysisResult && (
          <div className="mt-6">
            <ResultsPanel analysisResult={analysisResult} />
          </div>
        )}
      </main>

      <Toaster
        position="top-right"
        toastOptions={{
          duration: 4000,
          style: {
            background: '#363636',
            color: '#fff',
          },
          success: {
            duration: 3000,
            iconTheme: {
              primary: '#4ade80',
              secondary: '#fff',
            },
          },
          error: {
            duration: 5000,
            iconTheme: {
              primary: '#ef4444',
              secondary: '#fff',
            },
          },
        }}
      />
    </div>
  );
};

export default App; 
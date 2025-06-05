import React, { useState, useRef } from 'react';
import { AnalysisResult, AnalyzeRequest } from '../types';
import { analyzeStoredProcedure, analyzeFile, analyzeWithUML } from '../services/api';
import toast from 'react-hot-toast';

interface InputPanelProps {
  onAnalysisStart: () => void;
  onAnalysisComplete: (result: AnalysisResult) => void;
  onAnalysisError: () => void;
  onUMLAnalysisComplete?: (result: AnalysisResult) => void;
  isAnalyzing: boolean;
}

const InputPanel: React.FC<InputPanelProps> = ({
  onAnalysisStart,
  onAnalysisComplete,
  onAnalysisError,
  onUMLAnalysisComplete,
  isAnalyzing,
}) => {
  const [inputText, setInputText] = useState('');
  const [activeTab, setActiveTab] = useState<'text' | 'file'>('text');
  const fileInputRef = useRef<HTMLInputElement>(null);

  // 示例存储过程
  const sampleProcedure = `CREATE OR REPLACE PROCEDURE process_employee_data(
    p_dept_id IN NUMBER,
    p_start_date IN DATE
) AS
BEGIN
    -- 创建临时表
    CREATE GLOBAL TEMPORARY TABLE temp_emp_summary (
        emp_id NUMBER,
        emp_name VARCHAR2(100),
        dept_name VARCHAR2(100),
        salary NUMBER
    );
    
    -- 插入数据到临时表
    INSERT INTO temp_emp_summary
    SELECT e.employee_id, e.first_name || ' ' || e.last_name, 
           d.department_name, e.salary
    FROM employees e
    JOIN departments d ON e.department_id = d.department_id
    WHERE e.department_id = p_dept_id
    AND e.hire_date >= p_start_date;
    
    -- 更新员工薪资
    UPDATE employees 
    SET salary = salary * 1.1
    WHERE department_id = p_dept_id;
    
    -- 生成报告
    INSERT INTO employee_reports (report_date, dept_id, emp_count, avg_salary)
    SELECT SYSDATE, p_dept_id, COUNT(*), AVG(salary)
    FROM temp_emp_summary;
    
END;`;

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!inputText.trim()) {
      toast.error('请输入存储过程内容');
      return;
    }

    try {
      onAnalysisStart();
      
      const request: AnalyzeRequest = {
        stored_procedure: inputText,
      };

      const result = await analyzeStoredProcedure(request);
      
      if (result.success) {
        toast.success(result.message);
        onAnalysisComplete(result);
      } else {
        throw new Error(result.message);
      }
    } catch (error) {
      console.error('Analysis error:', error);
      toast.error(error instanceof Error ? error.message : '分析失败，请检查存储过程格式');
      onAnalysisError();
    }
  };

  const handleFileUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;

    try {
      onAnalysisStart();
      
      const result = await analyzeFile(file);
      
      if (result.success) {
        toast.success(result.message);
        onAnalysisComplete(result);
        // 读取文件内容到文本框
        const content = await file.text();
        setInputText(content);
        setActiveTab('text');
      } else {
        throw new Error(result.message);
      }
    } catch (error) {
      console.error('File analysis error:', error);
      toast.error(error instanceof Error ? error.message : '文件分析失败');
      onAnalysisError();
    } finally {
      // 清空文件输入
      if (fileInputRef.current) {
        fileInputRef.current.value = '';
      }
    }
  };

  const handleLoadSample = () => {
    setInputText(sampleProcedure);
    setActiveTab('text');
    toast.success('已加载示例存储过程');
  };

  const handleClear = () => {
    setInputText('');
    toast.success('已清空输入内容');
  };

  const handleUMLAnalysis = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!inputText.trim()) {
      toast.error('请输入存储过程内容');
      return;
    }

    try {
      onAnalysisStart();
      
      const request: AnalyzeRequest = {
        stored_procedure: inputText,
      };

      const result = await analyzeWithUML(request);
      
      if (result.success) {
        toast.success(`${result.message} - 包含UML结构图`);
        if (onUMLAnalysisComplete) {
          onUMLAnalysisComplete(result);
        } else {
          onAnalysisComplete(result);
        }
      } else {
        throw new Error(result.message);
      }
    } catch (error) {
      console.error('UML Analysis error:', error);
      toast.error(error instanceof Error ? error.message : 'UML分析失败，请检查存储过程格式');
      onAnalysisError();
    }
  };

  return (
    <div className="h-full flex flex-col">
      {/* 优雅的头部 */}
      <div className="mb-6">
        <div className="flex items-center space-x-3 mb-2">
          <div className="w-8 h-8 bg-gradient-klein-dark rounded-lg flex items-center justify-center">
            <svg className="w-5 h-5 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10 20l4-16m4 4l4 4-4 4M6 16l-4-4 4-4" />
            </svg>
          </div>
          <h2 className="text-xl font-bold text-klein-700">存储过程输入</h2>
        </div>
        <p className="text-sm text-klein-600/80 font-medium">
          输入Oracle存储过程代码进行智能分析
        </p>
      </div>

      {/* 现代化标签页 */}
      <div className="mb-6">
        <div className="flex bg-klein-50/50 rounded-xl p-1">
          <button
            onClick={() => setActiveTab('text')}
            className={`flex-1 py-2 px-3 rounded-lg text-sm font-medium transition-all duration-200 ${
              activeTab === 'text'
                ? 'bg-white text-klein-700 shadow-soft'
                : 'text-klein-600 hover:text-klein-700'
            }`}
          >
            <div className="flex items-center justify-center space-x-2">
              <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z" />
              </svg>
              <span>文本输入</span>
            </div>
          </button>
          <button
            onClick={() => setActiveTab('file')}
            className={`flex-1 py-2 px-3 rounded-lg text-sm font-medium transition-all duration-200 ${
              activeTab === 'file'
                ? 'bg-white text-klein-700 shadow-soft'
                : 'text-klein-600 hover:text-klein-700'
            }`}
          >
            <div className="flex items-center justify-center space-x-2">
              <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12" />
              </svg>
              <span>文件上传</span>
            </div>
          </button>
        </div>
      </div>

      {/* 内容区域 */}
      <div className="flex-1 flex flex-col">
        {activeTab === 'text' ? (
          <div className="space-y-4 flex-1 flex flex-col">
            {/* 工具栏 */}
            <div className="flex justify-between items-center">
              <div className="flex space-x-2">
                <button
                  type="button"
                  onClick={handleLoadSample}
                  className="btn btn-ghost btn-sm"
                  disabled={isAnalyzing}
                >
                  <svg className="w-4 h-4 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" />
                  </svg>
                  示例
                </button>
                <button
                  type="button"
                  onClick={handleClear}
                  className="btn btn-ghost btn-sm"
                  disabled={isAnalyzing || !inputText}
                >
                  <svg className="w-4 h-4 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                  </svg>
                  清空
                </button>
              </div>
              <div className="text-xs text-klein-500 font-medium">
                {inputText.length} 字符
              </div>
            </div>

            {/* 代码输入区域 */}
            <form onSubmit={handleSubmit} className="flex-1 flex flex-col space-y-4">
              <div className="flex-1">
                <textarea
                  value={inputText}
                  onChange={(e) => setInputText(e.target.value)}
                  placeholder="请输入Oracle存储过程代码...&#10;&#10;例如：&#10;CREATE OR REPLACE PROCEDURE proc_name AS&#10;BEGIN&#10;  -- 你的代码&#10;END;"
                  className="code-editor w-full h-full min-h-[320px] scrollbar-klein"
                  disabled={isAnalyzing}
                />
              </div>

              <div className="space-y-3">
                <button
                  type="submit"
                  disabled={isAnalyzing || !inputText.trim()}
                  className={`btn w-full ${
                    isAnalyzing || !inputText.trim()
                      ? 'bg-gray-300 text-gray-500 cursor-not-allowed'
                      : 'btn-primary'
                  } btn-lg`}
                >
                  {isAnalyzing ? (
                    <div className="flex items-center justify-center">
                      <div className="loader-klein mr-3"></div>
                      正在分析存储过程...
                    </div>
                  ) : (
                    <div className="flex items-center justify-center">
                      <svg className="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z" />
                      </svg>
                      开始智能分析
                    </div>
                  )}
                </button>

                <button
                  type="button"
                  onClick={handleUMLAnalysis}
                  disabled={isAnalyzing || !inputText.trim()}
                  className={`btn w-full ${
                    isAnalyzing || !inputText.trim()
                      ? 'bg-gray-300 text-gray-500 cursor-not-allowed'
                      : 'bg-gradient-to-r from-purple-500 to-indigo-600 hover:from-purple-600 hover:to-indigo-700 text-white'
                  } btn-lg`}
                >
                  {isAnalyzing ? (
                    <div className="flex items-center justify-center">
                      <div className="loader-klein mr-3"></div>
                      正在生成UML图...
                    </div>
                  ) : (
                    <div className="flex items-center justify-center">
                      <svg className="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 11H5m14 0a2 2 0 012 2v6a2 2 0 01-2 2H5a2 2 0 01-2-2v-6a2 2 0 012-2m14 0V9a2 2 0 00-2-2M5 11V9a2 2 0 012-2m0 0V5a2 2 0 012-2h6a2 2 0 012 2v2M7 7h10" />
                      </svg>
                      UML结构分析
                    </div>
                  )}
                </button>
              </div>
            </form>
          </div>
        ) : (
          <div className="space-y-4 flex-1 flex flex-col">
            {/* 文件上传区域 */}
            <div className="flex-1 flex items-center justify-center">
              <div className="w-full">
                <div className="border-2 border-dashed border-klein-200 rounded-2xl p-8 text-center hover:border-klein-300 hover:bg-klein-50/30 transition-all duration-200 cursor-pointer group">
                  <div className="space-y-4">
                    <div className="w-16 h-16 bg-gradient-klein-dark rounded-2xl flex items-center justify-center mx-auto group-hover:scale-105 transition-transform">
                      <svg className="w-8 h-8 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12" />
                      </svg>
                    </div>
                    <div>
                      <label htmlFor="file-upload" className="font-semibold text-klein-700 hover:text-klein-800 cursor-pointer">
                        点击选择文件
                      </label>
                      <p className="text-klein-600/80 text-sm mt-1">
                        或拖拽文件到此处
                      </p>
                    </div>
                    <p className="text-xs text-klein-500">
                      支持 .sql, .txt, .pls 格式
                    </p>
                  </div>
                  <input
                    ref={fileInputRef}
                    id="file-upload"
                    name="file-upload"
                    type="file"
                    className="sr-only"
                    accept=".sql,.txt,.pls"
                    onChange={handleFileUpload}
                    disabled={isAnalyzing}
                  />
                </div>
              </div>
            </div>

            {/* 文件上传说明 */}
            <div className="bg-gradient-to-r from-klein-50 to-accent-50 border border-klein-200/50 rounded-xl p-4">
              <h4 className="text-sm font-semibold text-klein-700 mb-2 flex items-center">
                <svg className="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
                文件要求
              </h4>
              <ul className="text-xs text-klein-600 space-y-1">
                <li className="flex items-center">
                  <div className="w-1 h-1 bg-klein-400 rounded-full mr-2"></div>
                  文件大小不超过 10MB
                </li>
                <li className="flex items-center">
                  <div className="w-1 h-1 bg-klein-400 rounded-full mr-2"></div>
                  使用 UTF-8 编码
                </li>
                <li className="flex items-center">
                  <div className="w-1 h-1 bg-klein-400 rounded-full mr-2"></div>
                  包含完整的存储过程定义
                </li>
              </ul>
            </div>
          </div>
        )}
      </div>

      {/* 底部提示 */}
      <div className="mt-6 pt-4 border-t border-klein-100">
        <div className="flex items-start space-x-3 text-xs">
          <div className="w-6 h-6 bg-gradient-to-r from-amber-400 to-orange-400 rounded-lg flex items-center justify-center flex-shrink-0">
            <svg className="w-3 h-3 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
          </div>
          <div className="text-klein-600">
            <p className="font-semibold mb-1">使用提示</p>
            <p className="leading-relaxed">
              确保存储过程包含完整的 CREATE PROCEDURE 语句和 BEGIN...END 块，系统将自动识别表操作和数据流向。
            </p>
          </div>
        </div>
      </div>
    </div>
  );
};

export default InputPanel; 
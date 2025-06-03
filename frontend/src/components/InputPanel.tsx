import React, { useState, useRef } from 'react';
import { AnalysisResult, AnalyzeRequest } from '../types';
import { analyzeStoredProcedure, analyzeFile } from '../services/api';
import toast from 'react-hot-toast';

interface InputPanelProps {
  onAnalysisStart: () => void;
  onAnalysisComplete: (result: AnalysisResult) => void;
  onAnalysisError: () => void;
  isAnalyzing: boolean;
}

const InputPanel: React.FC<InputPanelProps> = ({
  onAnalysisStart,
  onAnalysisComplete,
  onAnalysisError,
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

  return (
    <div className="bg-white rounded-lg shadow-sm border border-gray-200 h-full">
      {/* 头部 */}
      <div className="px-4 py-3 border-b border-gray-200">
        <h2 className="text-lg font-semibold text-gray-800">存储过程输入</h2>
        <p className="text-sm text-gray-600 mt-1">
          输入Oracle存储过程代码或上传文件进行分析
        </p>
      </div>

      {/* 标签页 */}
      <div className="border-b border-gray-200">
        <nav className="flex space-x-8 px-4">
          <button
            onClick={() => setActiveTab('text')}
            className={`py-2 px-1 border-b-2 font-medium text-sm ${
              activeTab === 'text'
                ? 'border-blue-500 text-blue-600'
                : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
            }`}
          >
            文本输入
          </button>
          <button
            onClick={() => setActiveTab('file')}
            className={`py-2 px-1 border-b-2 font-medium text-sm ${
              activeTab === 'file'
                ? 'border-blue-500 text-blue-600'
                : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
            }`}
          >
            文件上传
          </button>
        </nav>
      </div>

      {/* 内容区域 */}
      <div className="p-4 flex-1">
        {activeTab === 'text' ? (
          <div className="space-y-4">
            {/* 快捷按钮 */}
            <div className="flex justify-between items-center">
              <div className="flex space-x-2">
                <button
                  type="button"
                  onClick={handleLoadSample}
                  className="px-3 py-1 text-sm bg-blue-100 hover:bg-blue-200 text-blue-700 rounded-md transition-colors"
                  disabled={isAnalyzing}
                >
                  加载示例
                </button>
                <button
                  type="button"
                  onClick={handleClear}
                  className="px-3 py-1 text-sm bg-gray-100 hover:bg-gray-200 text-gray-700 rounded-md transition-colors"
                  disabled={isAnalyzing || !inputText}
                >
                  清空
                </button>
              </div>
              <div className="text-xs text-gray-500">
                {inputText.length} 字符
              </div>
            </div>

            {/* 文本输入区域 */}
            <form onSubmit={handleSubmit} className="space-y-4">
              <div>
                <textarea
                  value={inputText}
                  onChange={(e) => setInputText(e.target.value)}
                  placeholder="请输入Oracle存储过程代码..."
                  className="w-full h-64 px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500 font-mono text-sm resize-none"
                  disabled={isAnalyzing}
                />
              </div>

              <button
                type="submit"
                disabled={isAnalyzing || !inputText.trim()}
                className={`w-full py-2 px-4 rounded-md font-medium transition-colors ${
                  isAnalyzing || !inputText.trim()
                    ? 'bg-gray-300 text-gray-500 cursor-not-allowed'
                    : 'bg-blue-600 hover:bg-blue-700 text-white shadow-sm'
                }`}
              >
                {isAnalyzing ? (
                  <div className="flex items-center justify-center">
                    <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white mr-2"></div>
                    正在分析...
                  </div>
                ) : (
                  '开始分析'
                )}
              </button>
            </form>
          </div>
        ) : (
          <div className="space-y-4">
            {/* 文件上传区域 */}
            <div className="border-2 border-dashed border-gray-300 rounded-lg p-6 text-center hover:border-gray-400 transition-colors">
              <div className="space-y-2">
                <div className="text-4xl text-gray-400">📁</div>
                <div className="text-sm text-gray-600">
                  <label htmlFor="file-upload" className="font-medium text-blue-600 hover:text-blue-500 cursor-pointer">
                    点击选择文件
                  </label>
                  <span> 或拖拽文件到此处</span>
                </div>
                <p className="text-xs text-gray-500">
                  支持 .sql, .txt, .pls 格式文件
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

            {/* 文件上传说明 */}
            <div className="bg-blue-50 border border-blue-200 rounded-md p-3">
              <h4 className="text-sm font-medium text-blue-800 mb-1">文件要求</h4>
              <ul className="text-xs text-blue-700 space-y-1">
                <li>• 文件大小不超过 10MB</li>
                <li>• 使用 UTF-8 编码</li>
                <li>• 包含完整的存储过程定义</li>
              </ul>
            </div>
          </div>
        )}
      </div>

      {/* 底部提示 */}
      <div className="px-4 py-3 border-t border-gray-200 bg-gray-50">
        <div className="flex items-start space-x-2 text-xs text-gray-600">
          <div className="text-yellow-500 mt-0.5">💡</div>
          <div>
            <p className="font-medium">提示：</p>
            <p>确保存储过程包含完整的 CREATE PROCEDURE 语句和 BEGIN...END 块</p>
          </div>
        </div>
      </div>
    </div>
  );
};

export default InputPanel; 
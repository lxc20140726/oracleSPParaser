import React from 'react';

const Header: React.FC = () => {
  return (
    <header className="bg-white shadow-sm border-b border-gray-200">
      <div className="container mx-auto px-4 py-4">
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-3">
            <div className="text-2xl">🔍</div>
            <div>
              <h1 className="text-xl font-bold text-gray-900">
                Oracle存储过程分析工具
              </h1>
              <p className="text-sm text-gray-600">
                智能分析数据流向和表关系
              </p>
            </div>
          </div>
          
          <div className="flex items-center space-x-4">
            <div className="text-sm text-gray-500">
              版本 2.0.0
            </div>
            <a
              href="/api/docs"
              target="_blank"
              rel="noopener noreferrer"
              className="px-3 py-1 text-sm bg-blue-100 hover:bg-blue-200 text-blue-700 rounded-md transition-colors"
            >
              API文档
            </a>
          </div>
        </div>
      </div>
    </header>
  );
};

export default Header; 
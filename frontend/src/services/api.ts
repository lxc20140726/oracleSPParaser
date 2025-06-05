import { AnalyzeRequest, AnalysisResult } from '../types';

const API_BASE_URL = process.env.REACT_APP_API_URL || '/api';

class ApiError extends Error {
  constructor(message: string, public status?: number) {
    super(message);
    this.name = 'ApiError';
  }
}

const handleResponse = async (response: Response): Promise<any> => {
  if (!response.ok) {
    const errorData = await response.json().catch(() => ({}));
    throw new ApiError(
      errorData.detail || errorData.message || `HTTP ${response.status}: ${response.statusText}`,
      response.status
    );
  }
  return response.json();
};

export const analyzeStoredProcedure = async (request: AnalyzeRequest): Promise<AnalysisResult> => {
  try {
    const response = await fetch(`${API_BASE_URL}/analyze`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(request),
    });

    return handleResponse(response);
  } catch (error) {
    if (error instanceof ApiError) {
      throw error;
    }
    throw new ApiError('网络错误或服务暂时不可用');
  }
};

export const analyzeFile = async (file: File): Promise<AnalysisResult> => {
  try {
    const formData = new FormData();
    formData.append('file', file);

    const response = await fetch(`${API_BASE_URL}/analyze/file`, {
      method: 'POST',
      body: formData,
    });

    return handleResponse(response);
  } catch (error) {
    if (error instanceof ApiError) {
      throw error;
    }
    throw new ApiError('文件上传失败或服务暂时不可用');
  }
};

export const analyzeWithUML = async (request: AnalyzeRequest): Promise<AnalysisResult> => {
  try {
    const response = await fetch(`${API_BASE_URL}/analyze/uml`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(request),
    });

    return handleResponse(response);
  } catch (error) {
    if (error instanceof ApiError) {
      throw error;
    }
    throw new ApiError('UML分析失败或服务暂时不可用');
  }
};

export const healthCheck = async (): Promise<{ status: string; message: string }> => {
  try {
    const response = await fetch(`${API_BASE_URL}/health`);
    return handleResponse(response);
  } catch (error) {
    if (error instanceof ApiError) {
      throw error;
    }
    throw new ApiError('健康检查失败');
  }
}; 
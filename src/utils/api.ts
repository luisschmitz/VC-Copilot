import axios from 'axios';
import { AnalysisResult, PaginatedResponse, SearchParams } from './analysisTypes';

// Create axios instance with default config
const api = axios.create({
  baseURL: process.env.NEXT_PUBLIC_API_URL || '/api',
  headers: {
    'Content-Type': 'application/json',
  },
});

// Analysis API functions
export const analyzeStartup = async (
  url: string, 
  dataSources: string[] = ['website'], 
  analysisTypes: string[] = ['swot']
): Promise<AnalysisResult> => {
  const response = await api.post('/analyze', {
    url,
    data_sources: dataSources,
    analysis_types: analysisTypes,
  });
  return response.data;
};

export const getAnalysis = async (id: string): Promise<AnalysisResult> => {
  const response = await api.get(`/analyses/${id}`);
  return response.data;
};

export const getAnalyses = async (
  page: number = 1,
  limit: number = 10
): Promise<PaginatedResponse<AnalysisResult>> => {
  const response = await api.get('/analyses', {
    params: { page, limit },
  });
  return response.data;
};

export const searchAnalyses = async (
  params: SearchParams
): Promise<PaginatedResponse<AnalysisResult>> => {
  const response = await api.get('/search', { params });
  return response.data;
};

export const deleteAnalysis = async (id: string): Promise<void> => {
  await api.delete(`/analyses/${id}`);
};

// Error handling helper
export const handleApiError = (error: any): string => {
  if (error.response) {
    // The request was made and the server responded with a status code
    // that falls out of the range of 2xx
    const { status, data } = error.response;
    if (status === 400) {
      return data.message || 'Invalid request. Please check your input.';
    } else if (status === 404) {
      return 'Resource not found.';
    } else if (status === 429) {
      return 'Too many requests. Please try again later.';
    } else if (status >= 500) {
      return 'Server error. Please try again later.';
    }
    return data.message || 'An error occurred. Please try again.';
  } else if (error.request) {
    // The request was made but no response was received
    return 'No response from server. Please check your internet connection.';
  } else {
    // Something happened in setting up the request that triggered an Error
    return error.message || 'An unknown error occurred.';
  }
};

// Request interceptor for adding auth token (for future use)
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('auth_token');
    if (token) {
      config.headers['Authorization'] = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Response interceptor for global error handling
api.interceptors.response.use(
  (response) => {
    return response;
  },
  (error) => {
    // Log errors centrally
    console.error('API Error:', error);
    
    // Handle token expiration (for future auth implementation)
    if (error.response && error.response.status === 401) {
      // Clear auth state and redirect to login
      localStorage.removeItem('auth_token');
      // window.location.href = '/login';
    }
    
    return Promise.reject(error);
  }
);

export default api;

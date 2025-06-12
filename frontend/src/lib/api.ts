import axios from 'axios';
type AxiosError = any; // Temporary type until we update axios version
import { AnalysisRequest, AnalysisResponse, ScrapedData, FounderResponse, FundingNewsResponse } from '@/types/api';

// Ensure EventSource is available in the global scope
declare global {
  interface Window {
    EventSource: typeof EventSource;
  }
}

// Create axios instance with base URL
const api = axios.create({
  baseURL: process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8001',
  headers: {
    'Content-Type': 'application/json',
  },
  timeout: 60000, // Increased timeout for potentially long API calls
});

// Error handler for API requests
const handleApiError = (error: AxiosError, context: string) => {
  if (error.response) {
    const { status, data } = error.response;
    
    // Handle specific error states
    switch (status) {
      case 404:
        throw new Error(`No data found: ${context} may be unavailable or private`);
      case 429:
        throw new Error('Rate limit exceeded. Please try again later.');
      case 503:
        throw new Error('Service temporarily unavailable. This could be due to data source limitations.');
      default:
        throw new Error(
          data.detail ||
          (data as any).message ||
          `Server error: ${status} - ${JSON.stringify(data)}`
        );
    }
  } else if (error.request) {
    throw new Error('No response from server. Please check if the backend is running.');
  } else {
    throw new Error(error.message || 'Failed to make request');
  }
};

interface AnalysisStartResponse {
  analysis_id: string;
}

interface ApiService {
  healthCheck: () => Promise<any>;
  analyzeStartup: (request: AnalysisRequest) => Promise<AnalysisResponse>;
  getFounderInfo: (url: string) => Promise<FounderResponse>;
  scrapeWebsite: (url: string, maxPages?: number) => Promise<ScrapedData>;
  getFundingNews: (url: string) => Promise<FundingNewsResponse>;
}

export const apiService: ApiService = {
  // Health check endpoint
  healthCheck: async () => {
    try {
      const response = await api.get('/health');
      return response.data as { status: string };
    } catch (error) {
      handleApiError(error as AxiosError, 'Health check');
      throw error;
    }
  },



  // Individual data source endpoints
  getFounderInfo: async (url: string): Promise<FounderResponse> => {
    try {
      const response = await api.post<FounderResponse>('/founders', null, { params: { url } });
      return response.data;
    } catch (error) {
      handleApiError(error as AxiosError, 'Founder information');
      throw error;
    }
  },

  scrapeWebsite: async (url: string, maxPages: number = 3): Promise<ScrapedData> => {
    try {
      const response = await api.post<ScrapedData>('/scrape', null, { params: { url, max_pages: maxPages } });
      return response.data;
    } catch (error) {
      handleApiError(error as AxiosError, 'Website scraping');
      throw error;
    }
  },

  getFundingNews: async (url: string): Promise<FundingNewsResponse> => {
    try {
      const response = await api.post<FundingNewsResponse>('/funding-news', null, { params: { url } });
      return response.data;
    } catch (error) {
      handleApiError(error as AxiosError, 'Funding news');
      throw error;
    }
  },

  // Full analysis endpoint
  analyzeStartup: async (request: AnalysisRequest): Promise<AnalysisResponse> => {
    try {
      const response = await api.post<AnalysisResponse>('/analyze', request);
      return response.data;
    } catch (error) {
      handleApiError(error as AxiosError, 'Startup analysis');
      throw error;
    }
  }
};
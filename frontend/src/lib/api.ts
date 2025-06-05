import axios from 'axios';
import { AnalysisRequest, AnalysisResponse, ScrapedData } from '@/types/api';

// Create axios instance with base URL
const api = axios.create({
  baseURL: process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8001',
  headers: {
    'Content-Type': 'application/json',
  },
});

// API service functions
export const apiService = {
  // Health check endpoint
  healthCheck: async () => {
    const response = await api.get('/health');
    return response.data;
  },

  // Analyze startup based on URL
  analyzeStartup: async (request: AnalysisRequest): Promise<AnalysisResponse> => {
    const response = await api.post('/analyze', request);
    return response.data;
  },

  // Scrape website without analysis
  scrapeWebsite: async (url: string, scrapeDepth: string = 'standard'): Promise<ScrapedData> => {
    const response = await api.post('/scrape', { url, scrape_depth: scrapeDepth });
    return response.data;
  },

  // Analyze previously scraped data
  analyzeScrapedData: async (
    scrapedData: ScrapedData, 
    analysisTypes: string[] = ['executive_summary', 'success_prediction']
  ): Promise<AnalysisResponse> => {
    const response = await api.post('/analyze-data', { 
      scraped_data: scrapedData, 
      analysis_types: analysisTypes 
    });
    return response.data;
  },
};

export default apiService;

import { create } from 'zustand';
import { AnalysisResponse, ScrapedData, FounderResponse, FundingNewsResponse } from '@/types/api';
import { apiService } from './api';

// Define the step types for our analysis flow
export type AnalysisStep = 'idle' | 'analyzing' | 'complete';

interface VCCopilotState {
  // Input
  url: string;
  
  // Flow control
  currentStep: AnalysisStep;
  isLoading: boolean;
  error: string | null;
  
  // Data
  analysisData: AnalysisResponse | null;
  
  // Actions
  setUrl: (url: string) => void;
  analyzeStartup: (url: string) => Promise<void>;
  reset: () => void;
}

export const useVCCopilotStore = create<VCCopilotState>((set) => ({
  // Initial state
  url: '',
  currentStep: 'idle',
  isLoading: false,
  error: null,
  analysisData: null,
  
  // Actions
  setUrl: (url) => set({ url }),
  
  analyzeStartup: async (url) => {
    try {
      // Reset any previous data and errors
      set({ 
        url, 
        error: null,
        isLoading: true,
        currentStep: 'analyzing',
        analysisData: null
      });

      // Call the analyze endpoint with all data sources and analysis types
      const analysisData = await apiService.analyzeStartup({
        url,
        data_sources: ['website', 'founders', 'funding_news'],
        analysis_types: ['deep_dive', 'founder_evaluation']
      });
      
      // Complete the process
      set({ 
        analysisData, 
        currentStep: 'complete',
        isLoading: false
      });
    } catch (error) {
      console.error('Error in analysis process:', error);
      set({ 
        error: error instanceof Error ? error.message : 'An unknown error occurred',
        isLoading: false
      });
    }
  },
  
  reset: () => set({
    url: '',
    currentStep: 'idle',
    isLoading: false,
    error: null,
    analysisData: null
  })
}));

import { create } from 'zustand';
import { AnalysisResponse, ScrapedData, FounderResponse, FundingNewsResponse } from '@/types/api';
import { apiService } from './api';

// Define the step types for our analysis flow
export type AnalysisStep = 'idle' | 'analyzing' | 'founders' | 'funding' | 'deep_dive' | 'evaluation' | 'complete';

interface VCCopilotState {
  // Input
  url: string;
  
  // Flow control
  currentStep: AnalysisStep;
  isLoading: boolean;
  error: string | null;
  
  // Section loading states
  summaryLoaded: boolean;
  foundersLoaded: boolean;
  fundingLoaded: boolean;
  evaluationLoaded: boolean;
  
  // Data
  analysisData: Partial<AnalysisResponse> | null;
  
  // Actions
  setUrl: (url: string) => void;
  updatePartialData: (partialData: Partial<AnalysisResponse>) => void;
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
  
  // Section loading states
  summaryLoaded: false,
  foundersLoaded: false,
  fundingLoaded: false,
  evaluationLoaded: false,
  
  // Actions
  setUrl: (url) => set({ url }),
  
  updatePartialData: (partialData: Partial<AnalysisResponse>) => {
    set((state) => {
      // Create new state with only the fields that are present in partialData
      const newAnalysisData = {
        ...state.analysisData,
        ...(partialData.website_data && { website_data: partialData.website_data }),
        ...(partialData.founder_data && { founder_data: partialData.founder_data }),
        ...(partialData.founding_story && { founding_story: partialData.founding_story }),
        ...(partialData.company_name && { company_name: partialData.company_name }),
        ...(partialData.url && { url: partialData.url }),
        ...(partialData.funding_data && { funding_data: partialData.funding_data }),
        ...(partialData.deep_dive_sections && { deep_dive_sections: partialData.deep_dive_sections }),
        ...(partialData.founder_evaluation && { founder_evaluation: partialData.founder_evaluation })
      };
      
      // Update loading states based on actual data presence
      // Keep flags true if they were true before or if new data is present
      const summaryLoaded = state.summaryLoaded || !!newAnalysisData.deep_dive_sections;
      const foundersLoaded = state.foundersLoaded || !!newAnalysisData.founder_data;
      const fundingLoaded = state.fundingLoaded || !!newAnalysisData.funding_data;
      const evaluationLoaded = state.evaluationLoaded || !!newAnalysisData.founder_evaluation;
      
      return {
        ...state,
        analysisData: newAnalysisData,
        summaryLoaded,
        foundersLoaded,
        fundingLoaded,
        evaluationLoaded
      };
    });
  },

  analyzeStartup: async (url) => {
    try {
      // Reset any previous data and errors
      set({ 
        url, 
        error: null,
        isLoading: true,
        currentStep: 'analyzing',
        analysisData: null,
        summaryLoaded: false,
        foundersLoaded: false,
        fundingLoaded: false,
        evaluationLoaded: false
      });

      // Load data progressively
      try {

        // Get website data
        const websiteData = await apiService.scrapeWebsite(url);
        useVCCopilotStore.getState().updatePartialData({ website_data: websiteData });

        // Get founder information
        set({ currentStep: 'founders' });
        const founderResponse = await apiService.getFounderInfo(url);
        set({ foundersLoaded: true }); // Set flag immediately
        useVCCopilotStore.getState().updatePartialData({
          founder_data: founderResponse.founders,
          founding_story: founderResponse.founding_story,
          company_name: founderResponse.company_name,
          url: founderResponse.url
        });

        // Get funding news
        set({ currentStep: 'funding' });
        const fundingData = await apiService.getFundingNews(url);
        useVCCopilotStore.getState().updatePartialData({ funding_data: fundingData });

        // Get full analysis
        set({ currentStep: 'deep_dive' });
        const analysis = await apiService.analyzeStartup({
          url,
          data_sources: ['website', 'founders', 'funding_news'],
          analysis_types: ['deep_dive', 'founder_evaluation']
        });

        // Update deep dive sections
        useVCCopilotStore.getState().updatePartialData({
          deep_dive_sections: analysis.deep_dive_sections
        });

        // Update founder evaluation
        set({ currentStep: 'evaluation' });
        useVCCopilotStore.getState().updatePartialData({
          founder_evaluation: analysis.founder_evaluation
        });

        // Mark analysis as complete
        set((state) => ({
          ...state,
          currentStep: 'complete',
          isLoading: false
        }));
      } catch (error) {
        set({ 
          error: error instanceof Error ? error.message : 'An error occurred',
          isLoading: false,
          currentStep: 'idle'
        });
      }


    } catch (error) {
      set({ 
        error: error instanceof Error ? error.message : 'An error occurred',
        isLoading: false,
        currentStep: 'idle'
      });
    }
  },
  
  reset: () => set({
    url: '',
    currentStep: 'idle',
    isLoading: false,
    error: null,
    analysisData: null,
    summaryLoaded: false,
    foundersLoaded: false,
    fundingLoaded: false,
    evaluationLoaded: false
  })
}));

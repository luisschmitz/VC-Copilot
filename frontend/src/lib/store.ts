import { create } from 'zustand';
import { AnalysisResponse, ScrapedData } from '@/types/api';

interface AppState {
  // Analysis state
  isAnalyzing: boolean;
  analysisResults: AnalysisResponse | null;
  analysisError: string | null;
  
  // Scraping state
  isScraping: boolean;
  scrapedData: ScrapedData | null;
  scrapingError: string | null;
  
  // UI state
  activeTab: string;
  
  // Actions
  setIsAnalyzing: (isAnalyzing: boolean) => void;
  setAnalysisResults: (results: AnalysisResponse | null) => void;
  setAnalysisError: (error: string | null) => void;
  setIsScraping: (isScraping: boolean) => void;
  setScrapedData: (data: ScrapedData | null) => void;
  setScrapingError: (error: string | null) => void;
  setActiveTab: (tab: string) => void;
  resetState: () => void;
}

export const useAppStore = create<AppState>((set) => ({
  // Initial state
  isAnalyzing: false,
  analysisResults: null,
  analysisError: null,
  isScraping: false,
  scrapedData: null,
  scrapingError: null,
  activeTab: 'analysis',
  
  // Actions
  setIsAnalyzing: (isAnalyzing) => set({ isAnalyzing }),
  setAnalysisResults: (results) => set({ analysisResults: results }),
  setAnalysisError: (error) => set({ analysisError: error }),
  setIsScraping: (isScraping) => set({ isScraping }),
  setScrapedData: (data) => set({ scrapedData: data }),
  setScrapingError: (error) => set({ scrapingError: error }),
  setActiveTab: (tab) => set({ activeTab: tab }),
  resetState: () => set({
    isAnalyzing: false,
    analysisResults: null,
    analysisError: null,
    isScraping: false,
    scrapedData: null,
    scrapingError: null,
  }),
}));

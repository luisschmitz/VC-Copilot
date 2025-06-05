// Types for API requests and responses based on the backend models

export interface AnalysisRequest {
  url: string;
  analysis_types: string[];
  scrape_depth: string;
  scrape_pages?: string[];
  additional_sources?: string[];
}

export interface AnalysisResponse {
  company_name: string;
  url?: string;
  sections?: Record<string, string>;  // Parsed markdown sections
  success_prediction?: boolean;
  overall_assessment?: string;
  evaluation_criteria?: Record<string, any>;
  raw_llm_response?: string;
  timestamp: string;
  id: string;
}

export interface ScrapedData {
  company_name: string;
  description: string;
  raw_text: string;
  team_info?: Array<Record<string, string>>;
  social_links?: Record<string, string>;
  about_page?: string;
  contact_info?: Record<string, string>;
  products_services?: Array<Record<string, string>>;
  news_data?: Array<Record<string, string>>;
  additional_sources?: Record<string, any>;
  scrape_depth: string;
  pages_scraped?: Array<Record<string, any>>;
  total_pages_found?: number;
}

export interface ApiError {
  detail: string;
  status_code: number;
}

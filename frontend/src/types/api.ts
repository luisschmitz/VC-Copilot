// Data source and analysis type enums
export type DataSource = 'website' | 'founders' | 'funding_news';
export type AnalysisType = 'deep_dive' | 'founder_evaluation';

// Analysis request types
export interface AnalysisRequest {
  url: string;
  data_sources: DataSource[];
  analysis_types: AnalysisType[];
  max_pages?: number;  // Default is 5
  scrape_pages?: string[];
  additional_sources?: string[];
  retry_on_error?: boolean;  // Whether to retry failed data sources
}

// Data source types
export interface TeamMember {
  name: string;
  title?: string;
  bio?: string;
  image_url?: string;
  social_profiles?: Record<string, string>;
}

export interface PageInfo {
  title: string;
  type: 'main' | 'products' | 'about' | 'team' | string;
  url: string;
  word_count: number;
}

export interface ScrapedData {
  company_name: string;
  description: string;
  raw_text: string;
  team_info?: Array<Record<string, string>>;
  social_links?: Record<string, string> | null;
  about_page?: string | null;
  contact_info?: Record<string, string> | null;
  products_services?: Record<string, string> | null;
  news_data?: Record<string, string> | null;
  pages_scraped: PageInfo[];
  total_pages_found: number;
}

export interface FounderInfo {
  name: string;
  title?: string;
  education?: Array<{ institution: string; degree: string; year?: string }>;
  work_experience?: Array<{ company: string; role: string; duration: string }>;
  achievements?: string[];
  previous_startups?: Array<{ name: string; outcome: string }>;
  expertise?: string[];
  location?: string;
  social_profiles?: Record<string, string>;
}

export interface FounderResponse {
  founders: FounderInfo[];
  founding_story?: string;
  company_name: string;
  url: string;
}

export interface FundingRound {
  date: string;
  round_type: string;
  amount: string;
  amount_usd: number;
  lead_investors: string[];
  other_investors: string[];
  valuation: string | 'Not available' | 'Not disclosed';
  valuation_usd: number | null;
  source_url: string;
}

export interface NewsItem {
  date?: string;
  title: string;
  summary: string;
  source?: string;
  url?: string;
  category?: string;
}

export interface FundingNewsResponse {
  company_name: string;
  url: string;
  total_funding?: string;
  total_funding_usd?: number;
  funding_rounds: FundingRound[];
  latest_news: NewsItem[];
  funding_status?: string;
  notable_investors?: string[];
  last_funding_date?: string;
}


export interface DeepDiveSections {
  'Executive Summary': string;
  'Key Insights': string;
  'Key Risks': string;
  'Team Info': string;
  'Problem & Market': string;
  'Solution & Product': string;
  'Competition': string;
  'Business Model': string;
  'Traction': string;
  'Funding and Investors': string;
  'Conclusion': string;
}

export interface AnalysisResponse {
  company_name: string;
  url: string;
  website_data: ScrapedData;
  founder_data: FounderInfo[];
  funding_data: FundingNewsResponse;
  founding_story: string;
  deep_dive_sections: DeepDiveSections;
  founder_evaluation: {
    overall_assessment: string;
    success_prediction: boolean;
  };
  timestamp: string;
  id: string;
  raw_llm_response?: string;
}

export interface ScrapedDataAnalysis extends Omit<ScrapedData, 'max_pages'> {
  max_pages?: number;  // Default is 5
  additional_sources?: Record<string, any>;
}

export interface ApiError {
  detail: string;
  status_code: number;
}

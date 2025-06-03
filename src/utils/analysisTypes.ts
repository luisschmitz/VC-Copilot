// Analysis data types and constants

// Data source options
export const DATA_SOURCES = [
  { id: 'website', label: 'Company Website', default: true },
  { id: 'crunchbase', label: 'Crunchbase', default: true },
  { id: 'linkedin', label: 'LinkedIn', default: false },
  { id: 'twitter', label: 'Twitter', default: false },
  { id: 'news', label: 'News Articles', default: false }
];

// Analysis type options
export const ANALYSIS_TYPES = [
  { id: 'swot', label: 'SWOT Analysis', default: true },
  { id: 'founder_evaluation', label: 'Founder Evaluation', default: true },
  { id: 'market', label: 'Market Analysis', default: false },
  { id: 'team', label: 'Team Assessment', default: false },
  { id: 'financial', label: 'Financial Health', default: false },
  { id: 'competition', label: 'Competitive Analysis', default: false }
];

// Analysis result interface
export interface AnalysisResult {
  id?: string;
  company_name: string;
  url: string;
  description: string;
  industry: string;
  team_size: string;
  funding_stage: string;
  strengths: string[];
  weaknesses: string[];
  opportunities: string[];
  threats: string[];
  score: number;
  recommendation: string;
  data_sources?: string[];
  analysis_types?: string[];
  created_at?: string;
  // Fields for future extensions
  market_analysis?: MarketAnalysis;
  team_assessment?: TeamAssessment;
  financial_health?: FinancialHealth;
  competitive_analysis?: CompetitiveAnalysis;
  founder_evaluation?: FounderEvaluation;
}

// Future extension interfaces
export interface MarketAnalysis {
  market_size: string;
  growth_rate: string;
  trends: string[];
  barriers_to_entry: string[];
  market_share: string;
}

export interface TeamAssessment {
  founders: Founder[];
  team_experience: string;
  key_hires_needed: string[];
  culture: string;
}

export interface Founder {
  name: string;
  role: string;
  background: string;
  linkedin?: string;
}

export interface FinancialHealth {
  revenue: string;
  burn_rate: string;
  runway: string;
  funding_history: FundingRound[];
  unit_economics: string;
}

export interface FundingRound {
  date: string;
  amount: string;
  investors: string[];
  round_type: string;
}

export interface CompetitiveAnalysis {
  direct_competitors: Competitor[];
  indirect_competitors: Competitor[];
  competitive_advantage: string[];
}

export interface Competitor {
  name: string;
  url?: string;
  strengths: string[];
  weaknesses: string[];
}

export interface FounderEvaluation {
  success_prediction: boolean;
  evaluation_criteria: FounderEvaluationCriteria;
  overall_assessment: string;
}

export interface FounderEvaluationCriteria {
  industry_fit: { score: number; assessment: string };
  innovation: { score: number; assessment: string };
  outcomes: { score: number; assessment: string };
  funding: { score: number; assessment: string };
  press_recognition: { score: number; assessment: string };
  product_vs_service: { score: number; assessment: string };
  market_traction: { score: number; assessment: string };
  location_advantage: { score: number; assessment: string };
  crisis_management: { score: number; assessment: string };
  roadmap: { score: number; assessment: string };
  skill_alignment: { score: number; assessment: string };
  role_tenure: { score: number; assessment: string };
  network_quality: { score: number; assessment: string };
  third_party_validation: { score: number; assessment: string };
  ecosystem_participation: { score: number; assessment: string };
  value_proposition: { score: number; assessment: string };
  tech_currency: { score: number; assessment: string };
  data_consistency: { score: number; assessment: string };
}

// Pagination interface for API responses
export interface PaginatedResponse<T> {
  items: T[];
  total: number;
  page: number;
  limit: number;
  total_pages: number;
}

// Search parameters interface
export interface SearchParams {
  query?: string;
  page?: number;
  limit?: number;
  sort_by?: string;
  sort_order?: 'asc' | 'desc';
}

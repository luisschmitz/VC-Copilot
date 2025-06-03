import type { NextApiRequest, NextApiResponse } from 'next';
import axios from 'axios';

type AnalyzeRequestBody = {
  url: string;
  data_sources?: string[];
  analysis_types?: string[];
};

// Mock data generator for development purposes
const generateMockAnalysis = (url: string, dataSources: string[], analysisTypes: string[]) => {
  // Extract domain name from URL for company name
  const domain = new URL(url.startsWith('http') ? url : `https://${url}`).hostname;
  const companyName = domain.split('.')[0].charAt(0).toUpperCase() + domain.split('.')[0].slice(1);
  
  // Generate mock data
  const result: any = {
    id: `mock-${Date.now()}`,
    company_name: companyName,
    url: url,
    description: `${companyName} is an innovative startup focused on delivering cutting-edge solutions in the technology space. They are known for their unique approach to solving industry challenges.`,
    industry: ['Technology', 'SaaS', 'AI', 'Fintech', 'Healthcare'][Math.floor(Math.random() * 5)],
    team_size: ['5-10', '11-50', '51-200', '201-500'][Math.floor(Math.random() * 4)],
    funding_stage: ['Pre-seed', 'Seed', 'Series A', 'Series B', 'Series C'][Math.floor(Math.random() * 5)],
    strengths: [
      `Strong technical team with expertise in ${['AI', 'blockchain', 'cloud computing', 'data science'][Math.floor(Math.random() * 4)]}`,
      'Innovative product with clear market differentiation',
      'Scalable business model with recurring revenue',
      'Strong intellectual property portfolio'
    ],
    weaknesses: [
      'Limited market presence and brand recognition',
      'Early stage with unproven track record',
      'Potential cash flow constraints',
      'Highly competitive market segment'
    ],
    opportunities: [
      'Expanding to international markets',
      'Strategic partnerships with established companies',
      'Growing market demand for innovative solutions',
      'Potential for acquisition by larger players'
    ],
    threats: [
      'Emerging competitors with similar offerings',
      'Regulatory changes affecting the industry',
      'Economic downturn impacting customer spending',
      'Rapid technological changes requiring constant adaptation'
    ],
    score: Math.floor(Math.random() * 4) + 6, // Random score between 6-10
    recommendation: `Based on our analysis, ${companyName} shows promising potential in the ${['short', 'medium', 'long'][Math.floor(Math.random() * 3)]}-term. We recommend ${['closely monitoring their progress', 'considering a small initial investment', 'engaging in partnership discussions'][Math.floor(Math.random() * 3)]}.`,
    data_sources: dataSources,
    analysis_types: analysisTypes,
    created_at: new Date().toISOString()
  };
  
  // Add founder evaluation data if requested
  if (analysisTypes.includes('founder_evaluation')) {
    const successPrediction = Math.random() > 0.3; // 70% chance of success
    result.founder_evaluation = {
      success_prediction: successPrediction,
      overall_assessment: successPrediction 
        ? `The founder of ${companyName} demonstrates strong potential for success based on our evaluation criteria. Their experience, market positioning, and execution strategy align well with successful founder patterns.` 
        : `While ${companyName} has some promising aspects, our evaluation indicates potential challenges for the founder based on our scientific criteria. There are several areas that require improvement to increase chances of success.`,
      evaluation_criteria: {
        industry_fit: {
          score: Math.floor(Math.random() * 4) + (successPrediction ? 6 : 3),
          assessment: successPrediction 
            ? `Strong alignment with scalable tech industry trends.` 
            : `Limited alignment with scalable technology models.`
        },
        innovation: {
          score: Math.floor(Math.random() * 4) + (successPrediction ? 6 : 3),
          assessment: successPrediction 
            ? `Evidence of defensible IP and innovation in core offerings.` 
            : `Limited evidence of patentable innovation or defensible IP.`
        },
        outcomes: {
          score: Math.floor(Math.random() * 4) + (successPrediction ? 6 : 3),
          assessment: successPrediction 
            ? `Demonstrated quantifiable outcomes and measurable progress.` 
            : `Limited verifiable outcomes or quantifiable results.`
        },
        funding: {
          score: Math.floor(Math.random() * 4) + (successPrediction ? 6 : 3),
          assessment: successPrediction 
            ? `Recent funding from credible investors signals market validation.` 
            : `Funding history shows potential gaps or stagnation.`
        },
        press_recognition: {
          score: Math.floor(Math.random() * 4) + (successPrediction ? 6 : 3),
          assessment: successPrediction 
            ? `Recent coverage in reputable industry publications.` 
            : `Limited recent press coverage from independent sources.`
        },
        product_vs_service: {
          score: Math.floor(Math.random() * 4) + (successPrediction ? 6 : 3),
          assessment: successPrediction 
            ? `Product-focused business with high margins and scalability.` 
            : `Service-heavy model with potential scaling limitations.`
        },
        market_traction: {
          score: Math.floor(Math.random() * 4) + (successPrediction ? 6 : 3),
          assessment: successPrediction 
            ? `Strong cohort data showing growth and retention metrics.` 
            : `Limited specific market traction data beyond anecdotal evidence.`
        },
        location_advantage: {
          score: Math.floor(Math.random() * 4) + (successPrediction ? 6 : 3),
          assessment: successPrediction 
            ? `Strategic presence in tech hub with active ecosystem participation.` 
            : `Location does not provide significant strategic advantage.`
        },
        crisis_management: {
          score: Math.floor(Math.random() * 4) + (successPrediction ? 6 : 3),
          assessment: successPrediction 
            ? `Evidence of successful pivots and adaptation to market challenges.` 
            : `Limited history of crisis management or successful pivots.`
        },
        roadmap: {
          score: Math.floor(Math.random() * 4) + (successPrediction ? 6 : 3),
          assessment: successPrediction 
            ? `Clear 3-5 year roadmap aligned with market trends and capital needs.` 
            : `Roadmap lacks specificity or alignment with market realities.`
        },
        skill_alignment: {
          score: Math.floor(Math.random() * 4) + (successPrediction ? 6 : 3),
          assessment: successPrediction 
            ? `Founder skills directly align with venture requirements.` 
            : `Some misalignment between founder skills and venture needs.`
        },
        role_tenure: {
          score: Math.floor(Math.random() * 4) + (successPrediction ? 6 : 3),
          assessment: successPrediction 
            ? `Consistent focus on core venture for 4+ years.` 
            : `Multiple simultaneous roles may dilute focus on this venture.`
        },
        network_quality: {
          score: Math.floor(Math.random() * 4) + (successPrediction ? 6 : 3),
          assessment: successPrediction 
            ? `Strong network of engaged industry experts and investors.` 
            : `Network connections appear limited in depth or relevance.`
        },
        third_party_validation: {
          score: Math.floor(Math.random() * 4) + (successPrediction ? 6 : 3),
          assessment: successPrediction 
            ? `Multiple credible third-party validations of claims and performance.` 
            : `Limited independent verification of key claims and metrics.`
        },
        ecosystem_participation: {
          score: Math.floor(Math.random() * 4) + (successPrediction ? 6 : 3),
          assessment: successPrediction 
            ? `Active participation in investment ecosystem showing deal flow.` 
            : `Limited evidence of ecosystem participation or contributions.`
        },
        value_proposition: {
          score: Math.floor(Math.random() * 4) + (successPrediction ? 6 : 3),
          assessment: successPrediction 
            ? `Clear, data-supported value proposition with defensibility.` 
            : `Value proposition lacks clarity or supporting evidence.`
        },
        tech_currency: {
          score: Math.floor(Math.random() * 4) + (successPrediction ? 6 : 3),
          assessment: successPrediction 
            ? `Current and relevant tech stack and go-to-market approach.` 
            : `Technology approach shows signs of being outdated.`
        },
        data_consistency: {
          score: Math.floor(Math.random() * 4) + (successPrediction ? 6 : 3),
          assessment: successPrediction 
            ? `Consistent data across platforms and public profiles.` 
            : `Some inconsistencies in data across different platforms.`
        }
      }
    };
  }
  
  return result;
};

export default async function handler(
  req: NextApiRequest,
  res: NextApiResponse
) {
  // Only allow POST requests
  if (req.method !== 'POST') {
    return res.status(405).json({ message: 'Method not allowed' });
  }

  try {
    const { url, data_sources = ['website'], analysis_types = ['swot'] } = req.body as AnalyzeRequestBody;

    // Validate required fields
    if (!url) {
      return res.status(400).json({ message: 'URL is required' });
    }

    // Check if we're in development mode or if MOCK_API is enabled
    const useMockData = process.env.NODE_ENV === 'development' || process.env.MOCK_API === 'true';
    
    if (useMockData) {
      // Add artificial delay to simulate API call
      await new Promise(resolve => setTimeout(resolve, 2000));
      
      // Return mock data
      return res.status(200).json(generateMockAnalysis(url, data_sources, analysis_types));
    }

    // Get backend URL from environment variables
    const backendUrl = process.env.BACKEND_URL || 'http://localhost:8000';

    // Forward the request to the backend API
    const response = await axios.post(`${backendUrl}/api/analyze`, {
      url,
      data_sources,
      analysis_types,
    }, {
      headers: {
        'Content-Type': 'application/json',
      },
      // Increase timeout for longer analyses
      timeout: 60000, // 60 seconds
    });

    // Return the analysis result
    return res.status(200).json(response.data);
  } catch (error) {
    console.error('Error analyzing startup:', error);
    
    // Handle different types of errors
    if (axios.isAxiosError(error)) {
      const status = error.response?.status || 500;
      const message = error.response?.data?.message || 'Failed to analyze startup';
      
      return res.status(status).json({ message });
    }
    
    return res.status(500).json({ message: 'Internal server error' });
  }
}

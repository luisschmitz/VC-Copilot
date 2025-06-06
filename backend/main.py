import os
import json
import uuid
from typing import Optional, Dict, Any, List, Union
from fastapi import FastAPI, HTTPException, BackgroundTasks, Query, Path, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, HttpUrl, Field
from sqlalchemy.orm import Session
import requests
from bs4 import BeautifulSoup
import asyncio
from dotenv import load_dotenv
import logging
from datetime import datetime
from openai import OpenAI
import re
import time
from urllib.parse import urlparse

# Load environment variables
load_dotenv()

# Set OpenAI API key
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")
if not OPENAI_API_KEY:
    print("Warning: OPENAI_API_KEY environment variable not set. Some features may not work.")

# Initialize OpenAI client
client = OpenAI(api_key=OPENAI_API_KEY)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler("app.log")
    ]
)
logger = logging.getLogger(__name__)

app = FastAPI(title="Startup Analyzer API")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",  # Local development
        "https://vc-copilot.vercel.app",  # Vercel deployment (update with your actual domain)
        "https://vc-copilot-frontend.vercel.app"  # Alternative Vercel domain format
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Models
class StartupAnalysisRequest(BaseModel):
    url: str
    data_sources: List[str] = Field(default=["website"])
    analysis_types: List[str] = Field(default=["swot", "deep_dive"])

class ScrapedData(BaseModel):
    company_name: str
    description: str
    team_info: Optional[List[Dict[str, str]]] = None
    technologies: Optional[List[str]] = None
    social_links: Optional[Dict[str, str]] = None
    funding_info: Optional[str] = None
    raw_text: Optional[str] = None
    data_sources: List[str] = Field(default=["website"])

class StartupAnalysis(BaseModel):
    id: str = Field(default_factory=lambda: f"analysis_{uuid.uuid4()}")
    company_name: str
    url: str
    description: str
    industry: str
    team_size: str
    funding_stage: str
    strengths: List[str]
    weaknesses: List[str]
    opportunities: List[str]
    threats: List[str]
    score: float
    recommendation: str
    data_sources: List[str]
    analysis_types: List[str]
    deep_dive: Optional[Dict[str, Any]] = None
    founder_evaluation: Optional[Dict[str, Any]] = None
    created_at: str = Field(default_factory=lambda: datetime.now().isoformat())

# Import database modules
from models import StartupAnalysis, get_db, create_tables
import database as db_ops

# Create database tables
create_tables()

# Pagination model
class PaginatedResponse(BaseModel):
    items: List[Any]
    total: int
    page: int
    page_size: int
    total_pages: int

@app.get("/")
async def root():
    return {"message": "Welcome to the Startup Analyzer API"}

@app.post("/api/analyze", response_model=StartupAnalysis)
async def analyze_startup(request: StartupAnalysisRequest):
    url = str(request.url)
    
    # Normalize URL for caching
    parsed_url = urlparse(url if url.startswith(('http://', 'https://')) else f"https://{url}")
    normalized_url = parsed_url.netloc + parsed_url.path.rstrip('/')
    
    # Check if we already have an analysis for this URL
    db = next(get_db())
    existing_analysis = db_ops.get_analysis_by_url(db, normalized_url)
    if existing_analysis:
        logger.info(f"Returning existing analysis for {normalized_url}")
        return existing_analysis
    
    try:
        # Step 1: Scrape the website
        scraped_data = await scrape_website(url)
        scraped_data.data_sources = request.data_sources
        
        # Step 2: Analyze the data
        analysis = await analyze_data(scraped_data, request.analysis_types)
        analysis.url = normalized_url
        
        # Store the result
        db = next(get_db())
        db_ops.create_analysis(db, analysis.dict())
        
        return analysis
    except Exception as e:
        logger.error(f"Error analyzing startup: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/analyses", response_model=PaginatedResponse)
async def get_analyses(page: int = Query(1, ge=1), page_size: int = Query(10, ge=1, le=100), db: Session = Depends(get_db)):
    """Get paginated list of analyses"""
    try:
        # Get analyses with pagination
        skip = (page - 1) * page_size
        analyses = db_ops.get_all_analyses(db, skip=skip, limit=page_size)
        
        # Get total count
        total = db.query(StartupAnalysis).count()
        total_pages = (total + page_size - 1) // page_size
        
        # Get items for current page
        items = analyses
        
        return {
            "items": items,
            "total": total,
            "page": page,
            "page_size": page_size,
            "total_pages": total_pages
        }
    except Exception as e:
        logger.error(f"Error getting analyses: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/analyses/{analysis_id}", response_model=StartupAnalysis)
async def get_analysis(analysis_id: str = Path(...), db: Session = Depends(get_db)):
    """Get a specific analysis by ID"""
    analysis = db_ops.get_analysis_by_id(db, analysis_id)
    if not analysis:
        raise HTTPException(status_code=404, detail="Analysis not found")
    
    return analysis

@app.get("/api/search", response_model=PaginatedResponse)
async def search_analyses(query: str = Query(...), page: int = Query(1, ge=1), page_size: int = Query(10, ge=1, le=100), db: Session = Depends(get_db)):
    """Search analyses by company name or URL"""
    try:
        # Search analyses
        filtered_analyses = db_ops.search_analyses(db, query, limit=page_size)
        
        # Get total count for the search
        total = len(filtered_analyses)  # This is simplified; in production you'd use a COUNT query
        total_pages = (total + page_size - 1) // page_size
        
        # Get items for current page
        items = filtered_analyses
        
        return {
            "items": items,
            "total": total,
            "page": page,
            "page_size": page_size,
            "total_pages": total_pages
        }
    except Exception as e:
        logger.error(f"Error searching analyses: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

async def scrape_website(url: str) -> ScrapedData:
    """Scrape website data using requests and BeautifulSoup"""
    logger.info(f"Scraping website: {url}")
    
    try:
        # Add protocol if missing
        if not url.startswith(('http://', 'https://')):
            url = f"https://{url}"
        
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Extract company name (usually in title or logo alt text)
        title = soup.title.text.strip() if soup.title else "Unknown Company"
        company_name = title.split('|')[0].strip() or title.split('-')[0].strip() or "Unknown Company"
        
        # Extract description (meta description or first paragraph)
        description = ""
        meta_desc = soup.find('meta', attrs={'name': 'description'})
        if meta_desc and meta_desc.get('content'):
            description = meta_desc['content']
        else:
            first_p = soup.find('p')
            if first_p:
                description = first_p.text.strip()
        
        # Extract social links
        social_links = {}
        social_patterns = ['facebook.com', 'twitter.com', 'linkedin.com', 'instagram.com', 'github.com']
        for link in soup.find_all('a', href=True):
            href = link['href']
            for pattern in social_patterns:
                if pattern in href:
                    platform = pattern.split('.')[0]
                    social_links[platform] = href
                    break
        
        # Extract all text for further analysis
        all_text = ' '.join([p.text for p in soup.find_all('p')])
        
        # For MVP, we'll return basic data
        # In a production app, we would extract more data
        return ScrapedData(
            company_name=company_name,
            description=description or "No description available",
            social_links=social_links,
            raw_text=all_text[:5000]  # Limit text size
        )
    except Exception as e:
        logger.error(f"Error scraping website: {str(e)}")
        raise Exception(f"Failed to scrape website: {str(e)}")

async def analyze_data(data: ScrapedData, analysis_types: List[str]) -> StartupAnalysis:
    """
    Analyze the scraped data using OpenAI API
    """
    logger.info(f"Analyzing data for {data.company_name}")
    
    # Prepare SWOT analysis prompt
    swot_prompt = f"""
    Company Name: {data.company_name}
    Description: {data.description}
    Social Links: {data.social_links if data.social_links else 'None'}
    Additional Text: {data.raw_text if data.raw_text else 'None'}
    
    Analyze this startup and provide:
    1. Industry
    2. Approximate team size
    3. Funding stage
    4. SWOT analysis (strengths, weaknesses, opportunities, threats)
    5. Overall score (0-10)
    6. Recommendation
    
    Format your response as JSON with the following structure:
    {{
        "industry": "string",
        "team_size": "string",
        "funding_stage": "string",
        "strengths": ["string"],
        "weaknesses": ["string"],
        "opportunities": ["string"],
        "threats": ["string"],
        "score": float,
        "recommendation": "string"
    }}
    """
    
    # Run SWOT analysis
    logger.info("Running SWOT analysis")
    try:
        swot_response = client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are a startup analyst specializing in SWOT analysis."},
                {"role": "user", "content": swot_prompt}
            ],
            temperature=0.7,
            response_format={"type": "json_object"}
        )
        
        # Parse the response
        swot_text = swot_response.choices[0].message.content
        swot_data = json.loads(swot_text)
        
        # Initialize analysis result
        analysis = StartupAnalysis(
            company_name=data.company_name,
            url="",  # Will be set by the calling function
            description=data.description,
            industry=swot_data.get("industry", "Technology"),
            team_size=swot_data.get("team_size", "Unknown"),
            funding_stage=swot_data.get("funding_stage", "Unknown"),
            strengths=swot_data.get("strengths", []),
            weaknesses=swot_data.get("weaknesses", []),
            opportunities=swot_data.get("opportunities", []),
            threats=swot_data.get("threats", []),
            score=swot_data.get("score", 5.0),
            recommendation=swot_data.get("recommendation", ""),
            data_sources=data.data_sources,
            analysis_types=analysis_types
        )
        
        # Run deep dive analysis if requested
        if "deep_dive" in analysis_types:
            logger.info("Running deep dive analysis")
            deep_dive_data = await run_deep_dive_analysis(data.company_name, data.description, data.raw_text)
            analysis.deep_dive = deep_dive_data
        
        # Run founder evaluation if requested
        if "founder_evaluation" in analysis_types:
            logger.info("Running founder evaluation")
            founder_data = await evaluate_founders(data.company_name, data.description, data.team_info, data.raw_text, deep_dive_data if "deep_dive" in analysis_types else None)
            analysis.founder_evaluation = founder_data
        
        return analysis
    except Exception as e:
        logger.error(f"Error in OpenAI API call: {str(e)}")
        raise Exception(f"Failed to analyze startup: {str(e)}")

async def run_deep_dive_analysis(company_name: str, description: str, raw_text: str) -> Dict[str, Any]:
    """
    Run a deep dive analysis on the company using OpenAI
    """
    # Deep dive prompt
    system_prompt = f"""
    Can you compile a deep dive on {company_name}?

    I'm interested in a report covering the background and history of the company, including how it got started, what was its initial product-market fit, and how it has expanded over time. What are its products? Who uses their products? What roles, verticals, industries, or functions does it target? What's their ICP? What's the average contract value? What's their business model? What's its go-to-market strategy?

    What are the company's opportunities? Where is it growing? What is it doing around AI? How are these opportunities meaningfully unique or different from competitors? What are the risks in its business? Where are there threats? How is it responding to them?

    What do users think of the company's products? Do they like it or do they not? Why is it sticky? What attracts customers to it?

    What competitors does the company have? Focus on close competitors, not everyone. Include comparative metrics if available. Who are its threats and who is it threatening?

    Does the company have traction? Can you surface any key metrics or KPIs? What can you tell me about the company's financials? Is it generating revenue? Can you ballpark how much? How many customers does it have? Are there notable customers that they reference? What's the company's ARR? The company is private, so whatever data is available, whether it's publicly available or rumors or estimates.

    What's the company's current headcount? How has that grown in the past few years? Where are the bulk of employees? Are they in office or remote? What can you tell me about the company's funding? How much has it raised? What Series funding are they at? When did they last raise money? Who did they raise money from? What valuation did they last raise at? What's the history of their valuations? What are their stated next plans, if any? Are they planning for an IPO?

    I'm also interested in knowing about the founders and their backgrounds, as well as information on the current senior leadership, particularly if the current CEO is not the founder.

    Ideally, there are some good profiles I can read about the company.

    Make the report structured with headings and sections. The structure could be something like follows:

    Executive Summary
    Key Insights
    Key Risks
    Team Info
    Problem & Market
    Solution & Product
    Competition
    Business Model
    Traction
    Funding and Investors
    Conclusion
    """
    
    user_prompt = f"""
    Company: {company_name}
    Description: {description}
    Additional Information: {raw_text if raw_text else 'None'}
    
    Please format your response as JSON with the following structure:
    {{
        "executive_summary": "string",
        "key_insights": ["string"],
        "key_risks": ["string"],
        "team_info": {{
            "founders": ["string"],
            "leadership": ["string"]
        }},
        "problem_and_market": "string",
        "solution_and_product": "string",
        "competition": ["string"],
        "business_model": "string",
        "traction": {{
            "metrics": ["string"],
            "notable_customers": ["string"]
        }},
        "funding": {{
            "total_raised": "string",
            "latest_round": "string",
            "investors": ["string"]
        }},
        "conclusion": "string"
    }}
    """
    
    try:
        # Call OpenAI API
        response = client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            temperature=0.7,
            response_format={"type": "json_object"}
        )
        
        # Parse the response
        deep_dive_text = response.choices[0].message.content
        deep_dive_data = json.loads(deep_dive_text)
        
        return deep_dive_data
    except Exception as e:
        logger.error(f"Error in deep dive analysis: {str(e)}")
        # Return a minimal structure if the API call fails
        return {
            "executive_summary": f"Failed to generate deep dive for {company_name}: {str(e)}",
            "key_insights": [],
            "key_risks": []
        }

async def evaluate_founders(company_name: str, description: str, team_info: Optional[List[Dict[str, str]]], raw_text: str, deep_dive_data: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """
    Evaluate startup founders using scientific criteria to predict success
    """
    logger.info(f"Evaluating founders for {company_name}")
    
    # Prepare all acquired data about the company and founders
    acquired_data = {
        "company_name": company_name,
        "description": description,
        "team_info": team_info if team_info else [],
        "raw_text": raw_text
    }
    
    # Include deep dive data if available
    if deep_dive_data:
        acquired_data["deep_dive"] = deep_dive_data
    
    # Convert acquired data to string format for the prompt
    data_str = json.dumps(acquired_data, indent=2)
    
    # Scientific prompt for founder evaluation
    system_prompt = """
    You are an expert in venture capital, specializing in evaluating startup founders. Your task is to distinguish successful founders from unsuccessful ones.
    
    Here is a policy to assist you:
    
    **Updated Policies for Distinguishing Successful Founders:**
    
    1. **Industry Fit & Scalability**: Prioritize founders building scalable tech, AI, or deep-tech products over service-heavy models.
    
    2. **Sector-Specific Innovation & Patent Verification**: Require defensible IP with issued or published patents validated through public databases.
    
    3. **Quantifiable Outcomes, Exits & (for Bio/Med) Regulatory Milestones**: Demand audited revenue, exits, or documented IND/clinical-phase progress—not just pre-clinical claims.
    
    4. **Funding & Investor Validation**: Look for credible, recent third-party capital or follow-on rounds; stale or absent fundraising signals stagnation.
    
    5. **Press & Recognition Depth**: Favor independent, reputable coverage within the last 24 months and cross-checked with filings; outdated or missing press is a red flag.
    
    6. **Product vs. Service Assessment**: Score higher for automated, high-margin SaaS, platform, or therapeutics with clear IP; pure services rank lower.
    
    7. **Market Traction Specificity**: Require cohort-level data on growth, retention, margins; name-dropping clients or "pilot" studies alone don't qualify.
    
    8. **Location Advantage with Proof**: Presence in a tech/biotech hub must align with active local partnerships, accelerators, or ecosystem leadership roles.
    
    9. **Crisis Management & Pivot History**: Validate data-backed pivots that preserved or grew value during downturns.
    
    10. **Sustainable 3–5-Year Roadmap**: Roadmap must tie to market trends, capital needs, and measurable milestones.
    
    11. **Skill Alignment & Visibility**: Match proven technical, operational, or sales expertise to venture stage; generic "entrepreneur" labels penalize.
    
    12. **Consistent Role Tenure & Title Concentration**: Favor ≥4-year focus in one core venture; multiple simultaneous C-suite/advisory titles or role inflation is a downgrade.
    
    13. **Network Quality & Engagement**: Measure depth and actual engagement of investor and domain-expert ties over raw connection counts.
    
    14. **Third-Party Validation & References**: Require testimonials, case studies, regulatory filings, or audits corroborating performance and scientific claims.
    
    15. **Investment Ecosystem Participation**: Credit active, recent angel or fund roles that demonstrate curated deal flow and learning loops.
    
    16. **Differentiated Value Proposition**: Demand a clear, data-supported statement of competitive advantage and defensibility.
    
    17. **Tech Currency & Relevance**: Ensure the founder's expertise, tech stack, and go-to-market playbook are current; legacy success alone is insufficient.
    
    18. **Data Consistency Across Platforms**: Cross-verify LinkedIn, Crunchbase, press, and regulatory filings; inconsistencies or absent data trigger deeper diligence or rejection.
    """
    
    user_prompt = f"""
    Given the founder's profile and company data:
    {data_str}
    
    Based on this information, provide a detailed evaluation of the founder(s) according to the 18 criteria. For each criterion, provide a score (0-10) and a brief assessment.
    
    Then determine if the founder will succeed. Answer with True or False, followed by an overall assessment.
    
    Format your response as JSON with the following structure:
    {{
        "success_prediction": boolean,
        "overall_assessment": "string",
        "evaluation_criteria": {{
            "industry_fit": {{ "score": number, "assessment": "string" }},
            "innovation": {{ "score": number, "assessment": "string" }},
            "outcomes": {{ "score": number, "assessment": "string" }},
            "funding": {{ "score": number, "assessment": "string" }},
            "press_recognition": {{ "score": number, "assessment": "string" }},
            "product_vs_service": {{ "score": number, "assessment": "string" }},
            "market_traction": {{ "score": number, "assessment": "string" }},
            "location_advantage": {{ "score": number, "assessment": "string" }},
            "crisis_management": {{ "score": number, "assessment": "string" }},
            "roadmap": {{ "score": number, "assessment": "string" }},
            "skill_alignment": {{ "score": number, "assessment": "string" }},
            "role_tenure": {{ "score": number, "assessment": "string" }},
            "network_quality": {{ "score": number, "assessment": "string" }},
            "third_party_validation": {{ "score": number, "assessment": "string" }},
            "ecosystem_participation": {{ "score": number, "assessment": "string" }},
            "value_proposition": {{ "score": number, "assessment": "string" }},
            "tech_currency": {{ "score": number, "assessment": "string" }},
            "data_consistency": {{ "score": number, "assessment": "string" }}
        }}
    }}
    """
    
    try:
        # Call OpenAI API
        response = client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            temperature=0.7,
            response_format={"type": "json_object"}
        )
        
        # Parse the response
        founder_eval_text = response.choices[0].message.content
        founder_eval_data = json.loads(founder_eval_text)
        
        return founder_eval_data
    except Exception as e:
        logger.error(f"Error in founder evaluation: {str(e)}")
        # Return a minimal structure if the API call fails
        return {
            "success_prediction": False,
            "overall_assessment": f"Failed to evaluate founders for {company_name}: {str(e)}",
            "evaluation_criteria": {
                "industry_fit": {"score": 0, "assessment": "Evaluation failed"}
            }
        }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)

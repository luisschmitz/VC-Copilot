import os
import logging
import json
from typing import Dict, List, Optional, Any
from enum import Enum
from datetime import datetime
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, HttpUrl

# Import local modules
from backend.scraping import scrape_website, ScrapedData
from backend.analysis import run_deep_dive_analysis, evaluate_founders
from backend.founder_info import fetch_founder_information, FounderResponse
from backend.funding_news import fetch_funding_news, FundingNewsResponse
from backend.utils import extract_company_name, DateTimeEncoder

class DataSource(str, Enum):
    """Available data sources for startup analysis"""
    WEBSITE = "website"
    FOUNDERS = "founders"
    FUNDING_NEWS = "funding_news"

class AnalysisType(str, Enum):
    """Available analysis types for startup evaluation"""
    DEEP_DIVE = "deep_dive"
    FOUNDER_EVALUATION = "founder_evaluation"

class StartupRequest(BaseModel):
    """Request model for startup analysis with modular data sourcing and analysis"""
    url: HttpUrl
    data_sources: List[DataSource] = []  # Data to fetch
    analysis_types: List[AnalysisType] = []  # Analysis to perform
    max_pages: Optional[int] = 5  # Maximum number of pages to scrape

    class Config:
        use_enum_values = True

class StartupResponse(BaseModel):
    """Response model containing requested data and analysis results"""
    company_name: str
    url: str
    # Data source results
    website_data: Optional[ScrapedData] = None
    founder_data: Optional[List[Dict[str, Any]]] = None
    founding_story: Optional[str] = None
    funding_data: Optional[FundingNewsResponse] = None
    # Analysis results
    deep_dive_sections: Optional[Dict[str, str]] = None
    founder_evaluation: Optional[Dict[str, Any]] = None

# Load environment variables and configure logging
load_dotenv()

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="VC Copilot API",
    version="2.0.0",
    description="Modular API for startup analysis with independent data sourcing and analysis"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    """Health check endpoint"""
    return {"message": "VC Copilot API is running", "version": "1.0.0"}

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "vc-copilot-api",
        "version": "2.0.0",
        "features": [
            "modular_analysis",
            "independent_data_sourcing",
            "conditional_evaluation"
        ]
    }

# Individual data source endpoints
@app.post("/scrape", response_model=ScrapedData)
async def scrape_startup(url: str, max_pages: int = 5):
    """
    Scrape a website without analysis
    
    Args:
        url: Website URL to scrape
        max_pages: Maximum number of pages to scrape (default: 5)
    
    Returns:
        ScrapedData with extracted website information
    """
    try:
        logger.info(f"Scraping URL: {url} with max_pages: {max_pages}")
        
        scraped_data = await scrape_website(
            url=url,
            max_pages=max_pages
        )
        
        logger.info(f"Successfully scraped {scraped_data.company_name}")
        return scraped_data
        
    except Exception as e:
        logger.error(f"Error scraping website: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error scraping website: {str(e)}")

@app.post("/founders", response_model=Dict[str, Any])
async def get_founder_info(url: str):
    """Get founder information"""
    try:
        founders, founding_story = await fetch_founder_information(url)
        return {
            "founders": founders,
            "founding_story": founding_story
        }
    except Exception as e:
        logger.error(f"Error fetching founder information: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/funding-news", response_model=FundingNewsResponse)
async def get_funding_news(url: str):
    """Get funding and news information"""
    try:
        funding_rounds, news_items, additional_info = await fetch_funding_news(url)
        
        # Extract company name from URL
        from urllib.parse import urlparse
        domain = urlparse(url).netloc
        company_name = domain.split('.')[0].capitalize()
        
        # Construct response
        response = FundingNewsResponse(
            company_name=company_name,
            url=url,
            funding_rounds=funding_rounds,
            latest_news=news_items,
            total_funding=additional_info.get('total_funding'),
            total_funding_usd=additional_info.get('total_funding_usd'),
            funding_status=additional_info.get('funding_status'),
            notable_investors=additional_info.get('notable_investors'),
            last_funding_date=additional_info.get('last_funding_date')
        )
        return response
        
    except Exception as e:
        logger.error(f"Error fetching funding and news: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# Main analysis endpoint
@app.post("/analyze", response_model=StartupResponse)
async def analyze_startup(request: StartupRequest, background_tasks: BackgroundTasks):
    """
    Analyze a startup with modular data sourcing and analysis.
    
    This endpoint provides a flexible way to analyze startups by:
    1. Independently sourcing data (website, founders, funding)
    2. Running optional deep dive analysis
    3. Conditionally evaluating founders based on analysis
    
    The response includes only the requested data and analysis components.
    """
    try:
        logger.info(f"Starting analysis for URL: {request.url}")
        url_str = str(request.url)
        
        # Initialize response
        company_name = None
        response_data = {}
        
        # PART 1: DATA SOURCING
        # Step 1: Website Scraping
        scraped_data = None
        if DataSource.WEBSITE in request.data_sources:
            logger.info(f"Scraping website: {url_str}")
            try:
                scraped_data = await scrape_website(
                    url=url_str,
                    max_pages=request.max_pages or 5
                )
                company_name = scraped_data.company_name
                response_data['website_data'] = scraped_data
                logger.info(f"Successfully scraped {company_name}")
            except Exception as e:
                logger.error(f"Error scraping website: {str(e)}")
        
        # Derive company name from URL if not scraped
        if not company_name:
            from urllib.parse import urlparse
            domain = urlparse(url_str).netloc
            company_name = domain.split('.')[0].capitalize()
        
        # Step 2: Founder Information
        if DataSource.FOUNDERS in request.data_sources:
            logger.info(f"Fetching founder information for {company_name}")
            try:
                founders, founding_story = await fetch_founder_information(url_str)
                response_data['founder_data'] = [founder.dict() for founder in founders]
                response_data['founding_story'] = founding_story
                logger.info("Successfully fetched founder information")
            except Exception as e:
                logger.error(f"Error fetching founder information: {str(e)}")
        
        # Step 3: Funding and News
        if DataSource.FUNDING_NEWS in request.data_sources:
            logger.info(f"Fetching funding and news information for {company_name}")
            try:
                funding_rounds, news_items, additional_info = await fetch_funding_news(url_str)
                response_data['funding_data'] = FundingNewsResponse(
                    company_name=company_name,
                    url=url_str,
                    funding_rounds=funding_rounds,
                    latest_news=news_items,
                    total_funding=additional_info.get('total_funding'),
                    total_funding_usd=additional_info.get('total_funding_usd'),
                    funding_status=additional_info.get('funding_status'),
                    notable_investors=additional_info.get('notable_investors'),
                    last_funding_date=additional_info.get('last_funding_date')
                )
                logger.info("Successfully fetched funding and news")
            except Exception as e:
                logger.error(f"Error fetching funding and news: {str(e)}")
        
        # PART 2: ANALYSIS
        # Step 4: Deep Dive Analysis
        if AnalysisType.DEEP_DIVE in request.analysis_types:
            if scraped_data:  # Need website data for analysis
                logger.info(f"Running deep dive analysis for {company_name}")
                try:
                    deep_dive_data = await run_deep_dive_analysis(
                        scraped_data={
                            'company_name': company_name,
                            'description': scraped_data.description,
                            'raw_text': scraped_data.raw_text
                        },
                        founder_data=response_data.get('founder_data'),
                        funding_data=response_data.get('funding_data')
                    )
                    response_data['deep_dive_sections'] = deep_dive_data.get('sections', {})
                    logger.info("Completed deep dive analysis")
                except Exception as e:
                    logger.error(f"Error in deep dive analysis: {str(e)}")
            else:
                logger.warning("Skipping deep dive analysis - no website data available")

        # Step 5: Founder Evaluation
        if AnalysisType.FOUNDER_EVALUATION in request.analysis_types:
            if scraped_data and response_data.get('founder_data'):
                logger.info("Evaluating founders...")
                try:
                    response_data["founder_evaluation"] = await evaluate_founders(
                        company_name=company_name,
                        description=scraped_data.description,
                        team_info=response_data.get('founder_data'),
                        raw_text=scraped_data.raw_text,
                        deep_dive_data=response_data.get('deep_dive_sections')
                    )
                    logger.info("Completed founder evaluation")
                except Exception as e:
                    logger.error(f"Error in founder evaluation: {str(e)}")
            else:
                logger.warning("Skipping founder evaluation - missing required data")

        response = StartupResponse(
            company_name=company_name,
            url=url_str,
            **response_data
        )

        # Log completion and response content
        logger.info(f"Analysis complete for {company_name}")
        response_dict = response.dict(exclude_none=True)
        logger.info(f"Response contains: {list(response_dict.keys())}")
        
        # Log data source and analysis coverage
        if request.data_sources:
            logger.info(f"Data sources fetched: {request.data_sources}")
        if request.analysis_types:
            logger.info(f"Analysis types completed: {request.analysis_types}")

        return response

    except HTTPException as he:
        # Re-raise HTTP exceptions as-is
        raise he
    except ValueError as ve:
        # Handle validation errors
        logger.error(f"Validation error during startup analysis: {str(ve)}")
        raise HTTPException(status_code=422, detail=str(ve))
    except Exception as e:
        # Handle unexpected errors
        logger.error(f"Unexpected error during startup analysis: {str(e)}")
        logger.exception(e)  # Log full traceback
        raise HTTPException(
            status_code=500,
            detail="An unexpected error occurred during analysis"
        )

@app.post("/scrape", response_model=ScrapedData)
async def scrape_only(url: str, max_pages: int = 5):
    """
    Scrape a website without analysis
    
    Args:
        url: Website URL to scrape
        max_pages: Maximum number of pages to scrape (default: 5)
    
    Returns:
        ScrapedData with extracted website information
    """
    try:
        logger.info(f"Scraping URL: {url} with max_pages: {max_pages}")
        
        scraped_data = await scrape_website(
            url=url,
            max_pages=max_pages
        )
        
        logger.info(f"Successfully scraped {scraped_data.company_name}")
        return scraped_data
        
    except Exception as e:
        logger.error(f"Error scraping website: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error scraping website: {str(e)}")

@app.post("/analyze-data")
async def analyze_scraped_data(scraped_data: ScrapedData, analysis_types: list = ["executive_summary", "success_prediction"]):
    """
    Analyze already scraped data
    
    Args:
        scraped_data: Previously scraped website data
        analysis_types: Types of analysis to perform
    
    Returns:
        Analysis results
    """
    try:
        logger.info(f"Analyzing scraped data for {scraped_data.company_name}")
        
        # Run deep dive analysis if requested
        deep_dive_data = {}
        if "executive_summary" in analysis_types:
            deep_dive_data = await run_deep_dive_analysis(
                company_name=scraped_data.company_name,
                description=scraped_data.description,
                raw_text=scraped_data.raw_text
            )
        
        # Evaluate founders if requested
        founder_evaluation = {}
        if "success_prediction" in analysis_types:
            founder_evaluation = await evaluate_founders(
                company_name=scraped_data.company_name,
                description=scraped_data.description,
                team_info=scraped_data.team_info,
                raw_text=scraped_data.raw_text,
                deep_dive_data=deep_dive_data
            )
        
        # Create response
        response = AnalysisResponse(
            company_name=scraped_data.company_name,
            executive_summary=deep_dive_data.get("executive_summary", ""),
            key_insights=deep_dive_data.get("key_insights", []),
            key_risks=deep_dive_data.get("key_risks", []),
            success_prediction=founder_evaluation.get("success_prediction", None),
            overall_assessment=founder_evaluation.get("overall_assessment", ""),
            evaluation_criteria=founder_evaluation.get("evaluation_criteria", {})
        )
        
        logger.info(f"Analysis complete for {scraped_data.company_name}")
        return response
        
    except Exception as e:
        logger.error(f"Error analyzing data: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error analyzing data: {str(e)}")

@app.post("/founder-info", response_model=FounderResponse)
async def get_founder_information(url: str):
    """
    Fetch detailed founder information for a startup
    
    Args:
        url: Website URL of the startup
    
    Returns:
        FounderResponse with structured founder information
    """
    try:
        logger.info(f"Fetching founder information for URL: {url}")
        
        # Step 1: Scrape the website to get company name (minimal scrape for efficiency)
        scraped_data = await scrape_website(url=url, scrape_depth="minimal")
        company_name = scraped_data.company_name
        
        # Step 2: Fetch founder information from Perplexity (separate from scraping)
        founders, founding_story = await fetch_founder_information(url)
        
        # Step 3: Create response
        response = FounderResponse(
            founders=founders,
            founding_story=founding_story,
            company_name=company_name,
            url=url
        )
        
        logger.info(f"Successfully fetched founder information for {company_name}")
        logger.info(f"Found {len(founders)} founders")
        
        return response
        
    except Exception as e:
        logger.error(f"Error fetching founder information: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error fetching founder information: {str(e)}")

@app.post("/funding-news")
async def get_funding_news(url: str):
    """
    Fetch funding history and recent news for a startup
    
    Args:
        url: Website URL of the startup
    
    Returns:
        FundingNewsResponse with structured funding and news information
    """
    try:
        logger.info(f"Fetching funding and news information for {url}")
        
        # Extract company name from URL for display purposes
        company_name = url.replace("https://", "").replace("http://", "").split(".")[0]
        company_name = company_name.replace("-", " ").title()
        
        # Fetch funding and news information
        funding_rounds, news_items, additional_info = await fetch_funding_news(url)
        
        # Create response
        response = FundingNewsResponse(
            company_name=company_name,
            url=url,
            funding_rounds=funding_rounds,
            latest_news=news_items,
            total_funding=additional_info.get("total_funding"),
            total_funding_usd=additional_info.get("total_funding_usd"),
            funding_status=additional_info.get("funding_status"),
            notable_investors=additional_info.get("notable_investors"),
            last_funding_date=additional_info.get("last_funding_date")
        )
        
        return response
    except Exception as e:
        logger.error(f"Error fetching funding and news information: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error fetching funding and news information: {str(e)}")

# Error handlers
@app.exception_handler(404)
async def not_found_handler(request, exc):
    return {"error": "Endpoint not found", "detail": "The requested endpoint does not exist"}

@app.exception_handler(500)
async def internal_error_handler(request, exc):
    return {"error": "Internal server error", "detail": "An unexpected error occurred"}

# Run the API server when the script is executed directly
if __name__ == "__main__":
    import uvicorn
    
    port = int(os.environ.get("PORT", 8000))
    host = os.environ.get("HOST", "0.0.0.0")
    debug = os.environ.get("DEBUG", "False").lower() == "true"
    
    logger.info(f"Starting VC Copilot API on {host}:{port}")
    uvicorn.run(
        "main:app", 
        host=host, 
        port=port, 
        reload=debug,
        log_level="info"
    )
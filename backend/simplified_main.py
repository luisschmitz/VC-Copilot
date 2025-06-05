import os
import json
import logging
from typing import Optional
from datetime import datetime
from uuid import uuid4

from fastapi import FastAPI, HTTPException, Request, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from dotenv import load_dotenv

# Custom JSON encoder to handle datetime objects
class DateTimeEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, datetime):
            return obj.isoformat()
        return super(DateTimeEncoder, self).default(obj)

# Import from our modules using relative imports
from .scraping import scrape_website, ScrapedData
from .analysis import run_deep_dive_analysis, evaluate_founders, AnalysisRequest, AnalysisResponse

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="VC Copilot API",
    version="1.0.0",
    description="API for analyzing startups and evaluating founders"
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
    return {"status": "healthy", "service": "vc-copilot-api"}

@app.post("/analyze", response_model=AnalysisResponse)
async def analyze_startup(request: AnalysisRequest, background_tasks: BackgroundTasks):
    """
    Analyze a startup based on its website URL
    
    Args:
        request: AnalysisRequest containing URL and analysis parameters
        background_tasks: FastAPI background tasks for async processing
    
    Returns:
        AnalysisResponse with comprehensive startup analysis
    """
    try:
        logger.info(f"Starting analysis for URL: {request.url}")
        
        # Step 1: Scrape the website
        url_str = str(request.url)
        scraped_data = await scrape_website(
            url=url_str,
            scrape_depth=request.scrape_depth,
            scrape_pages=request.scrape_pages,
            additional_sources=request.additional_sources
        )
        
        logger.info(f"Successfully scraped {scraped_data.company_name}")
        
        # Step 2: Run deep dive analysis if requested
        deep_dive_data = {}
        if "executive_summary" in request.analysis_types:
            deep_dive_data = await run_deep_dive_analysis(
                company_name=scraped_data.company_name,
                description=scraped_data.description,
                raw_text=scraped_data.raw_text
            )
            logger.info(f"Completed deep dive analysis for {scraped_data.company_name}")
        
        # Step 3: Evaluate founders if requested
        founder_evaluation = {}
        if "success_prediction" in request.analysis_types:
            founder_evaluation = await evaluate_founders(
                company_name=scraped_data.company_name,
                description=scraped_data.description,
                team_info=scraped_data.team_info,
                raw_text=scraped_data.raw_text,
                deep_dive_data=deep_dive_data
            )
            logger.info(f"Completed founder evaluation for {scraped_data.company_name}")
        
        # Step 4: Create response
        response = AnalysisResponse(
            company_name=scraped_data.company_name,
            url=str(request.url),  # Include the URL in the response
            sections=deep_dive_data.get("sections", {}),  # Parsed markdown sections
            success_prediction=founder_evaluation.get("success_prediction", None),
            overall_assessment=founder_evaluation.get("overall_assessment", ""),
            evaluation_criteria=founder_evaluation.get("evaluation_criteria", {}),
            raw_llm_response=deep_dive_data.get("raw_llm_response", "")  # Raw LLM response for debugging
        )
        
        # Debug output to show what data is being transmitted
        logger.info(f"Analysis complete for {scraped_data.company_name}")
        logger.info(f"API Response - Sections: {list(response.sections.keys()) if response.sections else 'None'}")
        logger.info(f"API Response - Success Prediction: {response.success_prediction}")
        logger.info(f"API Response - Raw LLM Response Length: {len(response.raw_llm_response) if response.raw_llm_response else 0} chars")
        
        # Convert to dict for more detailed logging
        response_dict = response.dict()
        # Use the custom DateTimeEncoder for JSON serialization
        logger.info(f"Full API Response Structure: {json.dumps({k: (v if k != 'raw_llm_response' else f'[{len(v)} chars]') for k, v in response_dict.items()}, indent=2, cls=DateTimeEncoder)}")
        
        
        return response
        
    except Exception as e:
        logger.error(f"Error analyzing startup: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error analyzing startup: {str(e)}")

@app.post("/scrape", response_model=ScrapedData)
async def scrape_only(url: str, scrape_depth: str = "standard"):
    """
    Scrape a website without analysis
    
    Args:
        url: Website URL to scrape
        scrape_depth: Depth of scraping ("standard", "deep", or "custom")
    
    Returns:
        ScrapedData with extracted website information
    """
    try:
        logger.info(f"Scraping URL: {url}")
        
        scraped_data = await scrape_website(
            url=url,
            scrape_depth=scrape_depth
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
        "simplified_main:app", 
        host=host, 
        port=port, 
        reload=debug,
        log_level="info"
    )
import logging
import os
import re
import json
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime
from pydantic import BaseModel, Field
from dotenv import load_dotenv

# Configure logging
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

class FundingRound(BaseModel):
    """Model for a single funding round"""
    date: Optional[str] = None
    round_type: Optional[str] = None  # e.g., Seed, Series A, Series B
    amount: Optional[str] = None  # e.g., $5M, $10M
    amount_usd: Optional[float] = None  # Normalized amount in USD
    lead_investors: Optional[List[str]] = None
    other_investors: Optional[List[str]] = None
    valuation: Optional[str] = None  # e.g., $100M post-money
    valuation_usd: Optional[float] = None  # Normalized valuation in USD
    source_url: Optional[str] = None

class NewsItem(BaseModel):
    """Model for a news item about the company"""
    date: Optional[str] = None
    title: str
    summary: str
    source: Optional[str] = None
    url: Optional[str] = None
    category: Optional[str] = None  # e.g., Product Launch, Partnership, Acquisition

class FundingNewsResponse(BaseModel):
    """Response model for funding and news information API"""
    company_name: str
    url: str
    total_funding: Optional[str] = None
    total_funding_usd: Optional[float] = None
    funding_rounds: List[FundingRound] = []
    latest_news: List[NewsItem] = []
    funding_status: Optional[str] = None  # e.g., Bootstrapped, Seed-funded, Series A
    notable_investors: Optional[List[str]] = None
    last_funding_date: Optional[str] = None

async def fetch_funding_news(url: str) -> Tuple[List[FundingRound], List[NewsItem], Dict[str, Any]]:
    """
    Fetch detailed funding history and recent news using Perplexity
    
    Args:
        url: The website URL of the startup
        
    Returns:
        Tuple containing a list of FundingRound objects, a list of NewsItem objects,
        and a dictionary with additional funding information
    """
    logger.info(f"💰 Fetching funding and news for {url}")
    try:
        import httpx
        
        # Get Perplexity API key
        perplexity_api_key = os.environ.get("PERPLEXITY_API_KEY")
        if not perplexity_api_key:
            logger.warning("PERPLEXITY_API_KEY not found in environment variables")
            return [], [], {}
        
        # Format the prompt for Perplexity
        prompt = f"""Find comprehensive funding history and recent news for the startup at {url}. Provide:

1. Complete funding history:
   - Date of each round
   - Round type (Pre-seed, Seed, Series A, etc.)
   - Amount raised in each round
   - Lead investors for each round
   - Other participating investors
   - Valuation at time of funding (if available)
   - Source of funding information

2. Recent news and developments:
   - Latest product launches
   - Partnerships or collaborations
   - Major milestones or achievements
   - Recent press coverage
   - Any significant company changes or pivots

3. Summary information:
   - Total funding raised to date
   - Current funding status
   - Most notable investors
   - Date of last funding round

Please search for information from Crunchbase, PitchBook, company press releases, tech news sites, and investor announcements.

Format your response as a JSON object with the following structure:
{{
    "funding_rounds": [
        {{
            "date": "YYYY-MM-DD or Month Year",
            "round_type": "e.g., Seed, Series A",
            "amount": "e.g., $5M",
            "amount_usd": 5000000,
            "lead_investors": ["Lead Investor Name"],
            "other_investors": ["Investor 1", "Investor 2"],
            "valuation": "e.g., $100M post-money",
            "valuation_usd": 100000000,
            "source_url": "URL of source"
        }}
    ],
    "latest_news": [
        {{
            "date": "YYYY-MM-DD or Month Year",
            "title": "News headline",
            "summary": "Brief summary of the news",
            "source": "Source name",
            "url": "URL to news article",
            "category": "e.g., Product Launch, Partnership"
        }}
    ],
    "total_funding": "e.g., $15M",
    "total_funding_usd": 15000000,
    "funding_status": "e.g., Seed-funded, Series A",
    "notable_investors": ["Notable Investor 1", "Notable Investor 2"],
    "last_funding_date": "YYYY-MM-DD or Month Year"
}}
"""
        
        # Call Perplexity API
        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.post(
                "https://api.perplexity.ai/chat/completions",
                headers={
                    "Authorization": f"Bearer {perplexity_api_key}",
                    "Content-Type": "application/json"
                },
                json={
                    "model": "sonar",
                    "messages": [
                        {"role": "user", "content": prompt}
                    ],
                    "temperature": 0.2,
                    "max_tokens": 4000
                }
            )
            
            if response.status_code != 200:
                logger.error(f"Perplexity API error: {response.status_code} - {response.text}")
                return [], [], {}
            
            result = response.json()
            
            # Only print in debug mode
            if os.environ.get("DEBUG", "").lower() == "true":
                print("\n==== PERPLEXITY API RESPONSE (FUNDING & NEWS) ====")
                print(f"Status Code: {response.status_code}")
                print(json.dumps(result, indent=2))
                print("=================================================\n")
            
            logger.info(f"Perplexity API response received for funding & news. Status: {response.status_code}")
            
            content = result.get("choices", [{}])[0].get("message", {}).get("content", "")
            
            # Log the content for debugging
            logger.info(f"Content length: {len(content)}")
            
            # First try to parse the entire response as JSON
            try:
                # Some responses might be directly formatted as JSON
                data = json.loads(content)
                if "funding_rounds" in data or "latest_news" in data:
                    logger.info("Found direct JSON response with funding and news data")
                    
                    # Process funding rounds
                    funding_rounds = []
                    for round_data in data.get("funding_rounds", []):
                        try:
                            funding_rounds.append(FundingRound(**round_data))
                        except Exception as e:
                            logger.error(f"Error parsing funding round data: {str(e)}")
                    
                    # Process news items
                    news_items = []
                    for news_data in data.get("latest_news", []):
                        try:
                            news_items.append(NewsItem(**news_data))
                        except Exception as e:
                            logger.error(f"Error parsing news item data: {str(e)}")
                    
                    # Extract additional funding information
                    additional_info = {
                        "total_funding": data.get("total_funding"),
                        "total_funding_usd": data.get("total_funding_usd"),
                        "funding_status": data.get("funding_status"),
                        "notable_investors": data.get("notable_investors"),
                        "last_funding_date": data.get("last_funding_date")
                    }
                    
                    return funding_rounds, news_items, additional_info
            except json.JSONDecodeError:
                # If it's not direct JSON, try to extract JSON from the text
                logger.info("Content is not direct JSON, trying to extract JSON from text")
                pass
            
            # Try to extract JSON from the response text
            json_patterns = [
                r'\{\s*"funding_rounds".*\}\s*\}',
                r'\{\s*"latest_news".*\}\s*\}',
                r'\{[\s\S]*funding_rounds[\s\S]*\}',
                r'\{[\s\S]*latest_news[\s\S]*\}'
            ]
            
            for pattern in json_patterns:
                json_match = re.search(pattern, content, re.DOTALL)
                if json_match:
                    json_str = json_match.group(0)
                    logger.info(f"Found JSON match with pattern for funding & news")
                    try:
                        data = json.loads(json_str)
                        
                        # Process funding rounds
                        funding_rounds = []
                        for round_data in data.get("funding_rounds", []):
                            try:
                                funding_rounds.append(FundingRound(**round_data))
                            except Exception as e:
                                logger.error(f"Error parsing funding round data: {str(e)}")
                        
                        # Process news items
                        news_items = []
                        for news_data in data.get("latest_news", []):
                            try:
                                news_items.append(NewsItem(**news_data))
                            except Exception as e:
                                logger.error(f"Error parsing news item data: {str(e)}")
                        
                        # Extract additional funding information
                        additional_info = {
                            "total_funding": data.get("total_funding"),
                            "total_funding_usd": data.get("total_funding_usd"),
                            "funding_status": data.get("funding_status"),
                            "notable_investors": data.get("notable_investors"),
                            "last_funding_date": data.get("last_funding_date")
                        }
                        
                        # Log found data
                        logger.info(f"Found {len(funding_rounds)} funding rounds and {len(news_items)} news items")
                        if funding_rounds:
                            logger.info("Preview of latest funding round:")
                            preview = {k: v for k, v in funding_rounds[0].dict().items() if v is not None}
                            logger.info(json.dumps(preview, indent=2))
                        if additional_info:
                            logger.info(f"Additional funding info: {json.dumps(additional_info, indent=2)}")
                        
                        return funding_rounds, news_items, additional_info
                    except json.JSONDecodeError as e:
                        logger.error(f"Error decoding JSON from match: {str(e)}")
            
            # If we get here, we couldn't find valid JSON
            logger.error("Could not find valid JSON in Perplexity response for funding & news")
            
            return [], [], {}
    except Exception as e:
        logger.error(f"Error fetching funding and news information: {e}")
        return [], [], {}

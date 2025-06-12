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
    lead_investors: Optional[List[str]] = None
    other_investors: Optional[List[str]] = None
    valuation: Optional[str] = None  # e.g., $100M post-money
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
        prompt = f"""Find comprehensive funding history and recent news for the startup at {url}. 

IMPORTANT: You must return your response as a valid JSON object with the exact structure specified below. For any missing information, use "Not Available" as the value. Do not include any text before or after the JSON.

Search for information from Crunchbase, PitchBook, company press releases, tech news sites, and investor announcements.

Return ONLY a JSON object with this exact structure:

{{
    "funding_rounds": [
        {{
            "date": "YYYY-MM-DD or Month Year format, or 'Not Available'",
            "round_type": "Pre-seed/Seed/Series A/Series B/etc, or 'Not Available'",
            "amount": "$X.XM format, or 'Not Available'",
            "lead_investors": ["Lead Investor Name"] or ["Not Available"],
            "other_investors": ["Investor 1", "Investor 2"] or ["Not Available"],
            "valuation": "$X.XM pre-money/post-money format, or 'Not Available'",
            "source_url": "URL of source or 'Not Available'"
        }}
    ],
    "latest_news": [
        {{
            "date": "YYYY-MM-DD or Month Year format, or 'Not Available'",
            "title": "News headline or 'Not Available'",
            "summary": "Brief summary of the news or 'Not Available'",
            "source": "Source name or 'Not Available'",
            "url": "URL to news article or 'Not Available'",
            "category": "Product Launch/Partnership/Acquisition/Funding/etc or 'Not Available'"
        }}
    ],
    "total_funding": "$X.XM format or 'Not Available'",
    "funding_status": "Bootstrapped/Pre-seed/Seed-funded/Series A/Series B/etc or 'Not Available'",
    "notable_investors": ["Notable Investor 1", "Notable Investor 2"] or ["Not Available"],
    "last_funding_date": "YYYY-MM-DD or Month Year format, or 'Not Available'"
}}

Rules:
1. Always include all fields even if no data is found
2. Use "Not Available" for string fields when no information is found
4. For arrays, use ["Not Available"] when no data is found
5. Include at least the most recent 3-5 news items if available
6. Include all known funding rounds
7. Ensure the JSON is valid and properly formatted
8. Do not include any explanatory text outside the JSON

Search thoroughly for this company's funding and news information."""
        
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
                    "temperature": 0.1,  # Lower temperature for more consistent JSON output
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
            
            # Clean the content to extract JSON
            content = content.strip()
            
            # Remove any markdown code blocks if present
            if content.startswith("```json"):
                content = content[7:]
            if content.startswith("```"):
                content = content[3:]
            if content.endswith("```"):
                content = content[:-3]
            
            content = content.strip()
            
            # First try to parse the entire response as JSON
            try:
                data = json.loads(content)
                logger.info("Successfully parsed direct JSON response")
                
                # Validate and ensure all required fields are present
                data = ensure_complete_structure(data)
                
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
                    "funding_status": data.get("funding_status"),
                    "notable_investors": data.get("notable_investors"),
                    "last_funding_date": data.get("last_funding_date")
                }
                
                logger.info(f"Found {len(funding_rounds)} funding rounds and {len(news_items)} news items")
                return funding_rounds, news_items, additional_info
                
            except json.JSONDecodeError as e:
                logger.error(f"Error decoding direct JSON: {str(e)}")
                
                # Try to extract JSON from the response text using regex patterns
                json_patterns = [
                    r'\{[\s\S]*?"funding_rounds"[\s\S]*?\}(?=\s*$)',
                    r'\{[\s\S]*?"latest_news"[\s\S]*?\}(?=\s*$)',
                    r'\{[\s\S]*?"total_funding"[\s\S]*?\}(?=\s*$)',
                    r'\{[\s\S]*\}',  # Last resort - any JSON-like structure
                ]
                
                for pattern in json_patterns:
                    json_match = re.search(pattern, content, re.DOTALL)
                    if json_match:
                        json_str = json_match.group(0)
                        logger.info(f"Found JSON match with pattern")
                        try:
                            data = json.loads(json_str)
                            
                            # Validate and ensure all required fields are present
                            data = ensure_complete_structure(data)
                            
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
                            
                            logger.info(f"Found {len(funding_rounds)} funding rounds and {len(news_items)} news items")
                            return funding_rounds, news_items, additional_info
                            
                        except json.JSONDecodeError as e:
                            logger.error(f"Error decoding JSON from match: {str(e)}")
                            continue
            
            # If we get here, we couldn't parse any JSON - return default structure
            logger.error("Could not find valid JSON in Perplexity response, returning default structure")
            return [], [], get_default_additional_info()
            
    except Exception as e:
        logger.error(f"Error fetching funding and news information: {e}")
        return [], [], get_default_additional_info()

def ensure_complete_structure(data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Ensure the data dictionary has all required fields with appropriate defaults
    """
    # Ensure funding_rounds exists and has proper structure
    if "funding_rounds" not in data:
        data["funding_rounds"] = []
    
    # Ensure latest_news exists and has proper structure
    if "latest_news" not in data:
        data["latest_news"] = []
    
    # Ensure all top-level fields exist
    required_fields = {
        "total_funding": "Not Available",
        "funding_status": "Not Available",
        "notable_investors": ["Not Available"],
        "last_funding_date": "Not Available"
    }
    
    for field, default_value in required_fields.items():
        if field not in data or data[field] is None:
            data[field] = default_value
    
    # Ensure each funding round has all required fields
    for round_data in data["funding_rounds"]:
        round_defaults = {
            "date": "Not Available",
            "round_type": "Not Available",
            "amount": "Not Available",
            "lead_investors": ["Not Available"],
            "other_investors": ["Not Available"],
            "valuation": "Not Available",
            "source_url": "Not Available"
        }
        
        for field, default_value in round_defaults.items():
            if field not in round_data or round_data[field] is None:
                round_data[field] = default_value
    
    # Ensure each news item has all required fields
    for news_data in data["latest_news"]:
        news_defaults = {
            "date": "Not Available",
            "title": "Not Available",
            "summary": "Not Available",
            "source": "Not Available",
            "url": "Not Available",
            "category": "Not Available"
        }
        
        for field, default_value in news_defaults.items():
            if field not in news_data or news_data[field] is None:
                news_data[field] = default_value
    
    return data

def get_default_additional_info() -> Dict[str, Any]:
    """
    Return default additional info structure when no data is available
    """
    return {
        "total_funding": "Not Available",
        "funding_status": "Not Available",
        "notable_investors": ["Not Available"],
        "last_funding_date": "Not Available"
    }
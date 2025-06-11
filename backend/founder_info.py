import logging
import os
import re
import json
from typing import List, Dict, Any, Optional, Tuple
from pydantic import BaseModel
from dotenv import load_dotenv

# Configure logging
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

class FounderInfo(BaseModel):
    """Model for structured founder information"""
    name: str
    title: Optional[str] = None
    education: Optional[List[Dict[str, str]]] = None
    work_experience: Optional[List[Dict[str, str]]] = None
    achievements: Optional[List[str]] = None
    previous_startups: Optional[List[Dict[str, str]]] = None
    expertise: Optional[List[str]] = None
    age: Optional[int] = None
    location: Optional[str] = None
    social_profiles: Optional[Dict[str, str]] = None

class FounderResponse(BaseModel):
    """Response model for founder information API"""
    founders: List[FounderInfo] = []
    founding_story: Optional[str] = None
    company_name: str
    url: str

async def fetch_founder_information(url: str) -> Tuple[List[FounderInfo], Optional[str]]:
    """
    Fetch detailed founder information using Perplexity
    
    Args:
        url: The website URL of the startup
        
    Returns:
        Tuple containing a list of FounderInfo objects and the founding story
    """
    try:
        import httpx
        
        # Get Perplexity API key
        perplexity_api_key = os.environ.get("PERPLEXITY_API_KEY")
        if not perplexity_api_key:
            logger.warning("PERPLEXITY_API_KEY not found in environment variables")
            return [], None
        
        # Format the prompt for Perplexity
        prompt = f"""Find comprehensive founder information for the startup at {url}. For each founder, provide:

1. Full name and current title/role
2. Educational background (universities, degrees, graduation years)
3. Previous work experience and companies (with dates and positions)
4. Notable achievements, awards, or recognitions
5. Previous startups founded or co-founded
6. Technical expertise or specializations
7. Age (if publicly available)
8. Location/based in
9. Social media profiles (LinkedIn, Twitter/X)

Also include:
- How the founders met or came together

Please search for LinkedIn profiles, company press releases, accelerator profiles, and any biographical information available online.

Format your response as a JSON object with the following structure:
{{
    "founders": [
        {{
            "name": "Full Name",
            "title": "Current Title/Role",
            "education": [
                {{
                    "institution": "University Name",
                    "degree": "Degree Name",
                    "year": "Graduation Year"
                }}
            ],
            "work_experience": [
                {{
                    "company": "Company Name",
                    "position": "Position Title",
                    "duration": "Start Year - End Year"
                }}
            ],
            "achievements": ["Achievement 1", "Achievement 2"],
            "previous_startups": [
                {{
                    "name": "Startup Name",
                    "role": "Role",
                    "outcome": "Outcome (e.g., Acquired, Failed)"
                }}
            ],
            "expertise": ["Area of Expertise 1", "Area of Expertise 2"],
            "age": "Age (if available)",
            "location": "City, Country",
            "social_profiles": {{
                "linkedin": "LinkedIn URL",
                "twitter": "Twitter/X URL"
            }}
        }}
    ],
    "founding_story": "A paragraph describing how the founders met and started the company"
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
                return [], None
            
            result = response.json()
            
            # Only print in debug mode
            if os.environ.get("DEBUG", "").lower() == "true":
                print("\n==== PERPLEXITY API RESPONSE ====")
                print(f"Status Code: {response.status_code}")
                print(json.dumps(result, indent=2))
                print("================================\n")
            
            logger.info(f"Perplexity API response received. Status: {response.status_code}")
            
            content = result.get("choices", [{}])[0].get("message", {}).get("content", "")
            
            # Log the content for debugging
            logger.info(f"Content length: {len(content)}")
            
            # First try to parse the entire response as JSON
            try:
                # Some responses might be directly formatted as JSON
                data = json.loads(content)
                if "founders" in data:
                    logger.info(f"Found direct JSON response with {len(data.get('founders', []))} founders")
                    # Process the data
                    founders = []
                    for founder_data in data.get("founders", []):
                        try:
                            # Map the fields to match our model
                            mapped_data = {
                                "name": founder_data.get("name", ""),
                                "title": founder_data.get("title"),
                                "education": founder_data.get("education"),
                                "work_experience": founder_data.get("work_experience"),
                                "achievements": founder_data.get("achievements"),
                                "previous_startups": founder_data.get("previous_startups"),
                                "expertise": founder_data.get("expertise"),
                                "location": founder_data.get("location"),
                                "social_profiles": founder_data.get("social_profiles")
                            }
                            
                            # Convert age to int if possible
                            age = founder_data.get("age")
                            if isinstance(age, str):
                                if age.isdigit():
                                    mapped_data["age"] = int(age)
                                else:
                                    mapped_data["age"] = None
                            elif isinstance(age, int):
                                mapped_data["age"] = age
                            else:
                                mapped_data["age"] = None
                                
                            founders.append(FounderInfo(**mapped_data))
                            logger.info(f"Successfully parsed founder: {mapped_data['name']}")
                        except Exception as e:
                            logger.error(f"Error parsing founder data: {str(e)}")
                            logger.debug(f"Problematic founder data: {founder_data}")
                    
                    founding_story = data.get("founding_story")
                    logger.info(f"Founding story found: {founding_story is not None}")
                    return founders, founding_story
            except json.JSONDecodeError:
                # If it's not direct JSON, try to extract JSON from the text
                logger.info("Content is not direct JSON, trying to extract JSON from text")
                pass
            
            # Try to extract JSON from the response text
            # Look for patterns like {"founders":[...]} or { "founders": [...] }
            json_patterns = [
                r'\{\s*"founders".*\}\s*\}',  # Standard JSON pattern
                r'\{[\s\S]*"founders"[\s\S]*\}',  # More flexible pattern
                r'\{[\s\S]*founders[\s\S]*\}'   # Even more flexible
            ]
            
            for pattern in json_patterns:
                json_match = re.search(pattern, content, re.DOTALL)
                if json_match:
                    json_str = json_match.group(0)
                    logger.info(f"Found JSON match with pattern: {pattern[:20]}...")
                    try:
                        data = json.loads(json_str)
                        if "founders" in data:
                            logger.info(f"Successfully parsed JSON with {len(data.get('founders', []))} founders")
                            
                            # Convert to FounderInfo objects
                            founders = []
                            for founder_data in data.get("founders", []):
                                try:
                                    # Map the fields to match our model
                                    mapped_data = {
                                        "name": founder_data.get("name", ""),
                                        "title": founder_data.get("title"),
                                        "education": founder_data.get("education"),
                                        "work_experience": founder_data.get("work_experience"),
                                        "achievements": founder_data.get("achievements"),
                                        "previous_startups": founder_data.get("previous_startups"),
                                        "expertise": founder_data.get("expertise"),
                                        "location": founder_data.get("location"),
                                        "social_profiles": founder_data.get("social_profiles")
                                    }
                                    
                                    # Convert age to int if possible
                                    age = founder_data.get("age")
                                    if isinstance(age, str):
                                        if age.isdigit():
                                            mapped_data["age"] = int(age)
                                        else:
                                            mapped_data["age"] = None
                                    elif isinstance(age, int):
                                        mapped_data["age"] = age
                                    else:
                                        mapped_data["age"] = None
                                        
                                    founders.append(FounderInfo(**mapped_data))
                                except Exception as e:
                                    logger.error(f"Error parsing founder data: {str(e)}")
                            
                            founding_story = data.get("founding_story")
                            return founders, founding_story
                    except json.JSONDecodeError as e:
                        logger.error(f"Error decoding JSON from match: {str(e)}")
            
            # If we get here, we couldn't find valid JSON
            logger.error("Could not find valid JSON in Perplexity response")
            
            return [], None
    except Exception as e:
        logger.error(f"Error fetching founder information: {e}")
        return [], None

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
    title: Optional[str] = "Not publicly listed"
    education: Optional[List[Dict[str, str]]] = None
    work_experience: Optional[List[Dict[str, str]]] = None
    achievements: Optional[List[str]] = None
    previous_startups: Optional[List[Dict[str, str]]] = None
    expertise: Optional[List[str]] = None
    age: Optional[str] = "Not publicly listed"
    location: Optional[str] = "Not publicly listed"
    social_profiles: Optional[Dict[str, str]] = None

class FounderResponse(BaseModel):
    """Response model for founder information API"""
    founders: List[FounderInfo] = []
    founding_story: Optional[str] = None
    company_name: str
    url: str

def clean_json_content(content: str) -> str:
    """Clean JSON content from markdown and comments"""
    # Extract content between ```json and ``` if present
    json_block_match = re.search(r'```json\s*([\s\S]*?)```', content)
    if json_block_match:
        content = json_block_match.group(1)
    else:
        # Remove any remaining markdown code blocks
        content = re.sub(r'```[^`]*```', '', content)
    
    # Remove comments
    content = re.sub(r'#[^\n]*', '', content)
    content = re.sub(r'//[^\n]*', '', content)
    
    # Remove trailing commas in objects and arrays
    content = re.sub(r',(\s*[}\]])', r'\1', content)
    
    # Clean up whitespace and special characters
    content = content.strip()
    content = content.replace('\\n', '\n')
    content = content.replace('\\"', '"')
    content = content.replace('\\\\', '\\')
    
    return content

def parse_response(content: str) -> Tuple[List[FounderInfo], Optional[str]]:
    """Parse the API response into structured data"""
    
    def try_parse_json(json_str: str, source: str = "unknown") -> Optional[Dict]:
        """Helper function to try parsing JSON with detailed logging"""
        try:
            data = json.loads(json_str)
            if isinstance(data, dict) and "founders" in data:
                logger.info(f"Successfully parsed JSON from {source} with {len(data.get('founders', []))} founders")
                return data
            else:
                logger.warning(f"Parsed JSON from {source} but missing 'founders' key or invalid structure")
        except json.JSONDecodeError as e:
            logger.info(f"JSON parsing failed from {source}: {str(e)}")
        except Exception as e:
            logger.error(f"Unexpected error parsing JSON from {source}: {str(e)}")
        return None
    
    # Try direct JSON parsing first
    if data := try_parse_json(content, "direct parsing"):
        return process_founders(data)
    
    # Clean and try again
    cleaned_content = clean_json_content(content)
    if data := try_parse_json(cleaned_content, "cleaned content"):
        return process_founders(data)
    
    # Try to extract JSON from text using more specific pattern
    json_patterns = [
        r'\{[\s\S]*?"founders"[\s\S]*?\}(?=\s*$)',  # Matches JSON object ending at the end of string
        r'\{[\s\S]*?"founders"[\s\S]*?\}(?=\s*[^\}])',  # Matches JSON object followed by non-brace
        r'\{(?:[^{}]|\{[^{}]*\})*\}'  # Matches balanced braces
    ]
    
    for i, pattern in enumerate(json_patterns):
        match = re.search(pattern, cleaned_content)
        if match:
            json_str = clean_json_content(match.group(0))
            if data := try_parse_json(json_str, f"pattern {i + 1}"):
                return process_founders(data)
    
    # Last resort: try to parse each line as JSON
    for line in content.split('\n'):
        line = line.strip()
        if line and line[0] == '{' and line[-1] == '}':
            if data := try_parse_json(line, "line-by-line"):
                return process_founders(data)
    
    logger.error("Could not parse JSON from response after all attempts")
    logger.info("Raw content:")
    logger.info(content)
    return [], None

def process_founders(data: Dict[str, Any]) -> Tuple[List[FounderInfo], Optional[str]]:
    """Process founder data into FounderInfo objects"""
    founders = []
    
    for founder_data in data.get("founders", []):
        try:
            # Create FounderInfo object
            founder = FounderInfo(
                name=founder_data.get("name", "/"),
                title=founder_data.get("title", "/"),
                education=founder_data.get("education", "/"),
                work_experience=founder_data.get("work_experience", "/"),
                achievements=founder_data.get("achievements", "/"),
                previous_startups=founder_data.get("previous_startups", "/"),
                expertise=founder_data.get("expertise", "/"),
                age=founder_data.get("age", "/"),
                location=founder_data.get("location", "/"),
                social_profiles=founder_data.get("social_profiles")
            )
            founders.append(founder)
            logger.info(f"Processed founder: {founder.name}")
            
        except Exception as e:
            logger.error(f"Error processing founder: {str(e)}")
            continue
    
    founding_story = data.get("founding_story")
    return founders, founding_story

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
        
        # Updated prompt based on working version
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

IMPORTANT:
- For any information that is not publicly available or cannot be found, use "/" as the value. Do not leave fields empty or null.
- Format all numeric values as strings (e.g., age should be "35" not 35).
- For durations and years, always use string format (e.g., "2020-2023", "2019").

Format your response as a valid JSON object with the following structure:
{{
    "founders": [
        {{
            "name": "Full Name",
            "title": "Current Title/Role",
            "education": [
                {{
                    "institution": "University Name",
                    "degree": "Degree Type",
                    "year": "Graduation Year (as string)"
                }}
            ],
            "work_experience": [
                {{
                    "company": "Company Name",
                    "position": "Position Title",
                    "duration": "Duration (e.g., 2020-2023)"
                }}
            ],
            "achievements": ["Achievement 1", "Achievement 2"],
            "previous_startups": [
                {{
                    "name": "Startup Name",
                    "role": "Role",
                    "duration": "Duration"
                }}
            ],
            "expertise": ["Area 1", "Area 2"],
            "age": "Age or Not publicly listed",
            "location": "City, Country",
            "social_profiles": {{
                "linkedin": "LinkedIn URL",
                "twitter": "Twitter URL"
            }}
        }}
    ],
    "founding_story": "Story of how founders met and started the company"
}}

Return only the JSON object, no markdown formatting or explanations."""
        
        # Call Perplexity API with updated parameters
        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.post(
                "https://api.perplexity.ai/chat/completions",
                headers={
                    "Authorization": f"Bearer {perplexity_api_key}",
                    "Content-Type": "application/json"
                },
                json={
                    "model": "llama-3.1-sonar-small-128k-online",  # Updated model name
                    "messages": [
                        {
                            "role": "system",
                            "content": "You are a research assistant. Return only valid JSON responses with no additional formatting or markdown."
                        },
                        {
                            "role": "user", 
                            "content": prompt
                        }
                    ],
                    "temperature": 0.1,  # Lower temperature for more consistent output
                    "max_tokens": 4000
                }
            )
            
            if response.status_code != 200:
                logger.error(f"Perplexity API error: {response.status_code} - {response.text}")
                return [], None
            
            result = response.json()
            

            print("\n==== PERPLEXITY API RESPONSE ====")
            print(f"Status Code: {response.status_code}")
            print(json.dumps(result, indent=2))
            print("================================\n")
            
            logger.info(f"Perplexity API response received. Status: {response.status_code}")
            
            content = result.get("choices", [{}])[0].get("message", {}).get("content", "")
            
            logger.info(f"Content length: {len(content)}")
            logger.info(f"Response received - Content length: {len(content)}")
            
            # Parse the response using the improved parsing logic
            founders, founding_story = parse_response(content)
            
            # Log summary
            logger.info(f"Found {len(founders)} founders")
            for founder in founders:
                logger.info(f"Founder: {founder.name} - {founder.title}")
            
            if founding_story:
                logger.info(f"Found founding story ({len(founding_story)} chars)")
            
            return founders, founding_story
            
    except Exception as e:
        logger.error(f"Error fetching founder information: {e}")
        return [], None
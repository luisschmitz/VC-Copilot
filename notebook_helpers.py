"""
Helper functions for the simplified test notebook
that directly use the OpenAI API key from the backend/.env file
"""

import os
import re
import json
import logging
import requests
from bs4 import BeautifulSoup
from openai import OpenAI
from dotenv import load_dotenv

# Load environment variables from backend/.env file
backend_env_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'backend', '.env')
load_dotenv(backend_env_path)

# Get OpenAI API key
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")
if not OPENAI_API_KEY:
    print("Warning: OPENAI_API_KEY environment variable not set. Using fallback method.")
    # Try to read directly from the file
    try:
        with open(backend_env_path, 'r') as f:
            for line in f:
                if line.startswith('OPENAI_API_KEY='):
                    OPENAI_API_KEY = line.split('=', 1)[1].strip().strip("'").strip('"')
                    break
    except Exception as e:
        print(f"Error reading .env file: {e}")

# Initialize OpenAI client with explicit API key
client = OpenAI(api_key=OPENAI_API_KEY)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Helper functions for text extraction
def extract_sections(text, section_markers):
    """Extract sections from text based on section markers."""
    sections = {}
    current_section = None
    current_content = []
    
    lines = text.split('\n')
    for line in lines:
        matched = False
        for marker, section_name in section_markers.items():
            if re.match(f'^{marker}', line):
                if current_section:
                    sections[current_section] = '\n'.join(current_content).strip()
                current_section = section_name
                current_content = []
                matched = True
                break
        
        if not matched and current_section:
            current_content.append(line)
    
    if current_section and current_content:
        sections[current_section] = '\n'.join(current_content).strip()
    
    return sections

def extract_list_items(text):
    """Extract list items from text."""
    items = []
    for line in text.split('\n'):
        line = line.strip()
        if line.startswith('- ') or line.startswith('* '):
            items.append(line[2:].strip())
        elif re.match(r'^\d+\.\s+', line):
            items.append(re.sub(r'^\d+\.\s+', '', line).strip())
    return items

# Core functions from backend/main.py
async def scrape_website(url):
    """Scrape website content for analysis."""
    logger.info(f"Scraping website: {url}")
    
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Extract title
        title = soup.title.string if soup.title else "No title found"
        
        # Extract meta description
        meta_desc = ""
        meta_tag = soup.find('meta', attrs={'name': 'description'})
        if meta_tag and 'content' in meta_tag.attrs:
            meta_desc = meta_tag['content']
        
        # Extract main content
        main_content = ""
        for tag in soup.find_all(['p', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'li']):
            if tag.text.strip():
                main_content += tag.text.strip() + "\n\n"
        
        # Extract company name from title or URL
        company_name = title.split('-')[0].strip() if '-' in title else title.strip()
        if len(company_name) > 30:  # If title is too long, try to extract from URL
            domain = url.split('//')[-1].split('/')[0]
            if domain.startswith('www.'):
                domain = domain[4:]
            company_name = domain.split('.')[0].capitalize()
        
        return {
            "url": url,
            "company_name": company_name,
            "title": title,
            "meta_description": meta_desc,
            "content": main_content[:5000]  # Limit content to 5000 chars
        }
    
    except Exception as e:
        logger.error(f"Error scraping website: {e}")
        return {
            "url": url,
            "error": str(e),
            "company_name": url.split('//')[-1].split('/')[0].replace('www.', '').split('.')[0].capitalize(),
            "title": "Error retrieving data",
            "meta_description": "",
            "content": ""
        }

async def run_deep_dive_analysis(scraped_data):
    """Generate a deep dive analysis of the startup."""
    logger.info(f"Running deep dive analysis for: {scraped_data['company_name']}")
    
    # Prepare prompts
    system_prompt = """You are an expert venture capital analyst specializing in startup evaluation.
Your task is to analyze the provided startup information and create a comprehensive executive summary.
Focus on extracting key insights about the business model, market opportunity, competitive advantage, and potential risks.
Structure your response in JSON format with the following sections:
1. executive_summary: A concise overview of the startup
2. key_insights: List of important observations about the startup's potential
3. key_risks: List of potential challenges or red flags
"""

    user_prompt = f"""
Company Name: {scraped_data['company_name']}
Website Title: {scraped_data['title']}
Meta Description: {scraped_data['meta_description']}
Website Content:
{scraped_data['content']}

Based on this information, provide a deep dive analysis of this startup.
"""

    try:
        # Try with response_format parameter
        try:
            response = client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.7,
                response_format={"type": "json_object"}
            )
            
            # Parse JSON response
            result = json.loads(response.choices[0].message.content)
            
        except Exception as format_error:
            # If response_format is not supported, try without it
            if "response_format" in str(format_error):
                logger.info("Model does not support response_format, trying without it")
                response = client.chat.completions.create(
                    model="gpt-4",
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": user_prompt}
                    ],
                    temperature=0.7
                )
                
                # Try to parse JSON from text response
                try:
                    result = json.loads(response.choices[0].message.content)
                except json.JSONDecodeError:
                    # If JSON parsing fails, extract sections from text
                    text = response.choices[0].message.content
                    
                    # Define section markers
                    section_markers = {
                        "Executive Summary:": "executive_summary",
                        "Key Insights:": "key_insights",
                        "Key Risks:": "key_risks"
                    }
                    
                    # Extract sections
                    sections = extract_sections(text, section_markers)
                    
                    # Create result dictionary
                    result = {
                        "executive_summary": sections.get("executive_summary", ""),
                        "key_insights": extract_list_items(sections.get("key_insights", "")),
                        "key_risks": extract_list_items(sections.get("key_risks", ""))
                    }
            else:
                raise
        
        return result
    
    except Exception as e:
        logger.error(f"Error in deep dive analysis: {e}")
        return {
            "executive_summary": f"Error generating analysis: {str(e)}",
            "key_insights": ["Analysis failed due to an error"],
            "key_risks": ["Unable to evaluate risks due to analysis failure"]
        }

async def evaluate_founders(scraped_data, deep_dive_result=None):
    """Evaluate the founders based on scientific criteria."""
    logger.info(f"Evaluating founders for: {scraped_data['company_name']}")
    
    # Prepare prompts
    system_prompt = """You are an expert in founder evaluation using scientific criteria from entrepreneurship research.
Analyze the provided information and evaluate the founding team's potential for success.
Your evaluation should be based on established research on founder success factors.
Structure your response in JSON format with the following sections:
1. success_prediction: Boolean (true/false) indicating if the founders are likely to succeed
2. overall_assessment: A paragraph explaining your overall assessment
3. evaluation_criteria: Object containing specific criteria scores (0-10) and assessments
   - industry_fit
   - innovation
   - market_traction
   - team_quality
"""

    # Combine scraped data with deep dive insights if available
    deep_dive_text = ""
    if deep_dive_result:
        # Handle the executive_summary which might be a string or a dictionary
        exec_summary = deep_dive_result.get('executive_summary', '')
        if isinstance(exec_summary, dict):
            # If it's a dictionary, format it nicely
            exec_summary_text = '\n'.join([f"{k}: {v}" for k, v in exec_summary.items()])
        else:
            # If it's already a string, use it directly
            exec_summary_text = exec_summary
            
        # Handle key_insights which might contain dictionaries
        insights = deep_dive_result.get('key_insights', [])
        insights_text = []
        for insight in insights:
            if isinstance(insight, dict):
                # If insight is a dictionary, extract the first value
                insights_text.append(next(iter(insight.values()), ''))
            else:
                insights_text.append(insight)
                
        # Handle key_risks
        risks = deep_dive_result.get('key_risks', [])
        risks_text = []
        for risk in risks:
            if isinstance(risk, dict):
                risks_text.append(next(iter(risk.values()), ''))
            else:
                risks_text.append(risk)
                
        deep_dive_text = f"""
Executive Summary: {exec_summary_text}
Key Insights: {', '.join(insights_text)}
Key Risks: {', '.join(risks_text)}
"""

    user_prompt = f"""
Company Name: {scraped_data['company_name']}
Website Title: {scraped_data['title']}
Meta Description: {scraped_data['meta_description']}
Website Content:
{scraped_data['content']}

Additional Analysis:
{deep_dive_text}

Based on this information, evaluate the founding team's potential for success.
"""

    try:
        # Try with response_format parameter
        try:
            response = client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.7,
                response_format={"type": "json_object"}
            )
            
            # Parse JSON response
            result = json.loads(response.choices[0].message.content)
            
        except Exception as format_error:
            # If response_format is not supported, try without it
            if "response_format" in str(format_error):
                logger.info("Model does not support response_format, trying without it")
                response = client.chat.completions.create(
                    model="gpt-4",
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": user_prompt}
                    ],
                    temperature=0.7
                )
                
                # Try to parse JSON from text response
                try:
                    result = json.loads(response.choices[0].message.content)
                except json.JSONDecodeError:
                    # If JSON parsing fails, extract sections from text
                    text = response.choices[0].message.content
                    
                    # Define section markers
                    section_markers = {
                        "Success Prediction:": "success_prediction",
                        "Overall Assessment:": "overall_assessment",
                        "Evaluation Criteria:": "evaluation_criteria"
                    }
                    
                    # Extract sections
                    sections = extract_sections(text, section_markers)
                    
                    # Parse success prediction
                    success_text = sections.get("success_prediction", "").lower()
                    success_prediction = "true" in success_text or "yes" in success_text or "likely" in success_text
                    
                    # Parse evaluation criteria
                    criteria_text = sections.get("evaluation_criteria", "")
                    criteria_sections = {
                        "Industry Fit:": "industry_fit",
                        "Innovation:": "innovation",
                        "Market Traction:": "market_traction",
                        "Team Quality:": "team_quality"
                    }
                    
                    criteria = extract_sections(criteria_text, criteria_sections)
                    evaluation_criteria = {}
                    
                    for key, value in criteria.items():
                        # Extract score from text (e.g., "Score: 7/10")
                        score_match = re.search(r'(\d+)(?:/10)?', value)
                        score = int(score_match.group(1)) if score_match else 5
                        
                        # Remove score from assessment
                        assessment = re.sub(r'Score:?\s*\d+(?:/10)?', '', value).strip()
                        
                        evaluation_criteria[key] = {
                            "score": score,
                            "assessment": assessment
                        }
                    
                    # Create result dictionary
                    result = {
                        "success_prediction": success_prediction,
                        "overall_assessment": sections.get("overall_assessment", ""),
                        "evaluation_criteria": evaluation_criteria
                    }
            else:
                raise
        
        return result
    
    except Exception as e:
        logger.error(f"Error in founder evaluation: {e}")
        return {
            "success_prediction": False,
            "overall_assessment": f"Error evaluating founders: {str(e)}",
            "evaluation_criteria": {
                "industry_fit": {"score": 0, "assessment": "Evaluation failed"},
                "innovation": {"score": 0, "assessment": "Evaluation failed"},
                "market_traction": {"score": 0, "assessment": "Evaluation failed"},
                "team_quality": {"score": 0, "assessment": "Evaluation failed"}
            }
        }

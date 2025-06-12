import logging
import json
import re
import os
from typing import Optional, Dict, Any, List
from pydantic import BaseModel, Field
from datetime import datetime
from openai import OpenAI
import uuid
from dotenv import load_dotenv
from .founder_info import FounderInfo

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

# Set OpenAI API key
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")
if not OPENAI_API_KEY:
    logger.warning("Warning: OPENAI_API_KEY environment variable not set. Some features may not work.")

client = OpenAI(api_key=OPENAI_API_KEY)

class AnalysisRequest(BaseModel):
    url: str  # Changed from HttpUrl to str to avoid import issues
    analysis_types: List[str] = ["executive_summary", "success_prediction"]
    max_pages: int = 5  # Default to 5 pages
    scrape_pages: Optional[List[str]] = None
    additional_sources: Optional[List[str]] = None

# FounderInfo is imported at the top of the file

class AnalysisResponse(BaseModel):
    company_name: str
    url: Optional[str] = None
    sections: Optional[Dict[str, str]] = None  # Parsed markdown sections
    success_prediction: Optional[bool] = None
    overall_assessment: Optional[str] = None
    evaluation_criteria: Optional[Dict[str, Dict[str, Any]]] = None
    founder_info: Optional[List[FounderInfo]] = None  # Structured founder information
    founding_story: Optional[str] = None  # How the founders met
    raw_llm_response: Optional[str] = None  # Raw LLM response for debugging
    timestamp: datetime = Field(default_factory=datetime.now)
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))

def extract_section(text, section_name, next_section=None):
    """Extract a specific section from structured text"""
    if not text or not section_name:
        return ""
    
    # Create regex pattern for section header
    section_pattern = rf"(?:^|\n)\s*{re.escape(section_name)}\s*(?:\n|$)"
    section_match = re.search(section_pattern, text, re.IGNORECASE | re.MULTILINE)
    
    if not section_match:
        return ""
    
    start_pos = section_match.end()
    
    if next_section:
        # Find the next section
        next_pattern = rf"(?:^|\n)\s*{re.escape(next_section)}\s*(?:\n|$)"
        next_match = re.search(next_pattern, text[start_pos:], re.IGNORECASE | re.MULTILINE)
        if next_match:
            end_pos = start_pos + next_match.start()
            return text[start_pos:end_pos].strip()
    
    return text[start_pos:].strip()

def extract_list_items(text, section_name, next_section=None):
    """Extract list items from a specific section"""
    section_text = extract_section(text, section_name, next_section)
    if not section_text:
        return []
    
    # Try to find bullet points or numbered lists
    items = re.findall(r'[-*•]\s*(.+?)(?=\n[-*•]|$)', section_text, re.DOTALL)
    if not items:
        items = re.findall(r'\d+\.\s*(.+?)(?=\n\d+\.|$)', section_text, re.DOTALL)
    if not items:
        # If no structured list found, return the whole section as a single item
        return [section_text.strip()]
    
    return [item.strip() for item in items]

def clean_analysis_text(text: str) -> str:
    """Clean and format analysis text for consistent output"""
    if not text:
        return ""
    
    try:
        # Convert common AI output patterns to proper markdown
        cleaned = text
        # Handle section headers
        cleaned = re.sub(r'^([A-Za-z\s&]+):\s*$', r'## \1', cleaned, flags=re.MULTILINE)
        cleaned = re.sub(r'^\*\*([^*]+)\*\*:?\s*$', r'## \1', cleaned, flags=re.MULTILINE)
        
        # Handle lists
        cleaned = re.sub(r'^[-•●]\s+', '- ', cleaned, flags=re.MULTILINE)
        cleaned = re.sub(r'^(\d+)\.\s+', r'\1. ', cleaned, flags=re.MULTILINE)
        
        # Fix spacing
        cleaned = re.sub(r'\n{3,}', '\n\n', cleaned)
        cleaned = re.sub(r'([^\n])\n([A-Z])', r'\1\n\n\2', cleaned)
        
        # Clean up markdown
        cleaned = re.sub(r'\*\*\s*([^*]+?)\s*\*\*', r'**\1**', cleaned)
        cleaned = re.sub(r'_\s*([^_]+?)\s*_', r'_\1_', cleaned)
        
        return cleaned.strip()
    except Exception as e:
        logger.error(f"Error cleaning analysis text: {str(e)}")
        return text

def parse_all_markdown_sections(text: str) -> Dict[str, str]:
    """
    Parse all markdown sections from text into a dictionary
    
    Args:
        text: Markdown text with section headers (supports both ## Section and **Section** formats)
        
    Returns:
        Dictionary with section names as keys and content as values
    """
    logger.info("Starting markdown section parsing")
    logger.info(f"Input text length: {len(text)} characters")
    
    # Check for bold headers first
    bold_pattern = re.compile(r'^\*\*([^*]+)\*\*:?\s*$', re.MULTILINE)
    bold_matches = list(bold_pattern.finditer(text))
    logger.info(f"Found {len(bold_matches)} bold headers in the text")
    
    # Check for markdown headers
    md_pattern = re.compile(r'^##\s+([^\n]+)', re.MULTILINE)
    md_matches = list(md_pattern.finditer(text))
    logger.info(f"Found {len(md_matches)} markdown headers in the text")
    
    # Convert **Section Name** to ## Section Name for consistency
    cleaned_text = re.sub(r'^\*\*([^*]+)\*\*:?\s*$', r'## \1', text, flags=re.MULTILINE)
    logger.info("Converted bold headers to markdown headers for consistency")
    
    # Find all ## headers and extract sections
    section_pattern = re.compile(r'^##\s+([^\n]+)', re.MULTILINE)
    section_matches = list(section_pattern.finditer(cleaned_text))
    logger.info(f"Found {len(section_matches)} total section headers after normalization")
    
    # Extract content between headers into dictionary
    sections = {}
    
    # If no section headers found, log warning and return empty dict
    if not section_matches:
        logger.warning("No section headers found in text")
        # Log the first 100 chars of text for debugging
        logger.warning(f"Text starts with: {text[:100]}...")
        return {}
    
    # Extract content for each section
    for i, match in enumerate(section_matches):
        section_name = match.group(1).strip()
        start_pos = match.end()
        
        # If this is the last section, content goes to the end
        if i == len(section_matches) - 1:
            section_content = cleaned_text[start_pos:].strip()
        else:
            # Otherwise, content goes until the next section header
            end_pos = section_matches[i + 1].start()
            section_content = cleaned_text[start_pos:end_pos].strip()
        
        # Clean up the section content
        clean_content = section_content.strip()
        
        # Add to sections dictionary
        sections[section_name] = clean_content
    
    # Log the parsed sections for debugging
    logger.info(f"Parsed {len(sections)} sections: {list(sections.keys())}")
    
    return sections

async def run_deep_dive_analysis(scraped_data: dict, founder_data: dict = None, funding_data: dict = None) -> Dict[str, Any]:
    """
    Generate a deep dive analysis of the startup based on scraped website data and additional information
    
    Args:
        scraped_data: Dictionary containing scraped website data (company_name, description, raw_text)
        founder_data: Optional dictionary with founder information
        funding_data: Optional dictionary with funding and news information
    """
    company_name = scraped_data.get('company_name', '')
    description = scraped_data.get('description', '')
    logger.info(f"Running deep dive analysis for: {company_name}")
    
    # Debug logging for input data
    logger.info(f"Deep dive input - Company: {company_name}")
    logger.info(f"Deep dive input - Description length: {len(description) if description else 0}")
    logger.info(f"Deep dive input - Has founder data: {bool(founder_data)}")
    logger.info(f"Deep dive input - Has funding data: {bool(funding_data)}")
    
    system_prompt = (
        "You are an expert startup analyst. Analyze the startup data provided in JSON format and generate a comprehensive analysis. "
        "Format your response with bold section headers (e.g. '**Executive Summary**') and provide detailed analysis in each section."
    )
    
    # Prepare data in a token-efficient JSON format
    analysis_data = {
        "company": company_name,
        "desc": description,
        "founders": founder_data,
        "funding": funding_data.model_dump() if funding_data else {}
    }
    
    # Debug logging for processed data
    logger.info(f"Analysis data prepared - Founders count: {len(analysis_data['founders'])}")
    logger.info(f"Analysis data prepared - Has funding info: {bool(analysis_data['funding'])}")
    
    # Build the user prompt with the JSON data

    user_prompt = (
        f"Can you compile a deep dive analysis on this startup based primarily on their website content? "
        f"I'm providing both scraped website data (which should be treated as the primary source of truth) "
        f"and supplementary external data for context.\n\n"
        
        f"PRIMARY ANALYSIS FOCUS:\n"
        f"Base your analysis primarily on the raw website content provided, as this represents the company's "
        f"own messaging, positioning, and current state. Use the external data points only to supplement "
        f"or validate findings from the website.\n\n"
        
        f"CRITICAL FORMATTING REQUIREMENTS:\n"
        f"• Use EXACTLY this header format for each section: **Section Name**\n"
        f"• Each section header must be on its own line\n"
        f"• Leave a blank line after each header before the content\n"
        f"• If insufficient information exists for any section, write: 'Not enough information provided to analyze this area thoroughly.'\n"
        f"• Do NOT skip sections - include all 11 sections even if information is limited\n\n"
        
        f"REQUIRED REPORT STRUCTURE:\n"
        f"You must include EXACTLY these 11 sections in this order. Do not add, remove, or rename any sections:\n\n"
        
        f"**Executive Summary**\n"
        f"High-level overview and key takeaways. Company background, history, how it got started, initial product-market fit, and evolution. If limited information, provide what you can determine.\n\n"
        
        f"**Key Insights**\n"
        f"Most important discoveries and strategic observations. Focus on unique differentiators, AI integration, expansion plans, and strategic positioning. Include any unique aspects you can identify.\n\n"
        
        f"**Key Risks**\n"
        f"Primary threats and challenges they face and how they're addressing them. Include both obvious market risks and subtle operational/competitive risks you can identify.\n\n"
        
        f"**Team Info**\n"
        f"Founder backgrounds, current leadership structure, and organizational insights. Include how founders met, their experience, and team composition. If founder info is limited, state this clearly.\n\n"
        
        f"**Problem & Market**\n"
        f"Market opportunity and problem being solved. Target roles, verticals, industries, functions they serve, and their Ideal Customer Profile (ICP). Extract from company messaging if available.\n\n"
        
        f"**Solution & Product**\n"
        f"What they offer, product offerings, value proposition, and who their target users are. Focus on what the company says about their solution and how it addresses customer needs.\n\n"
        
        f"**Competition**\n"
        f"Main competitors, competitive positioning, and differentiation. Analyze how they compare in the competitive landscape and position against competitors.\n\n"
        
        f"**Business Model**\n"
        f"How they make money, revenue model, go-to-market strategy, pricing, customer acquisition details, and any insights on contract values or monetization approach.\n\n"
        
        f"**Traction**\n"
        f"Growth metrics, customer counts, notable clients, revenue indicators, KPIs, user retention, engagement metrics, and market validation. Include any traction data or customer mentions.\n\n"
        
        f"**Funding and Investors**\n"
        f"Financial backing, investment history, funding rounds, headcount growth, expansion plans, and IPO prospects. Include any funding announcements or investor mentions.\n\n"
        
        f"**Conclusion**\n"
        f"Future outlook, final assessment, and user sentiment. What customers think, what makes the product sticky, and synthesize your overall view of the company's prospects.\n\n"
        
        f"CONTENT GUIDELINES:\n"
        f"• If you cannot find adequate information for a section, write concisely: 'Not enough information provided.'\n"
        f"• Be purely objective, do not include any personal opinions or biases and rather report only the facts.\n"
        f"• Be specific and cite details from the website when possible\n"
        f"• Each section should provide all the facts when information is available\n\n"
        
        f"DATA SOURCES (prioritize in this order):\n"
        f"1. Raw Website Content (PRIMARY SOURCE): {scraped_data.get('raw_text', '')[:3000]}\n\n"
        f"2. External Data Context (SUPPLEMENTARY): {json.dumps(analysis_data, default=str)}\n\n"
        
        f"Remember: Use the exact header format **Section Name** and include all 11 sections even if some lack sufficient information."
    )

    # Debug logging for API call
    logger.info("Preparing to call OpenAI API for deep dive analysis")
    
    try:
        response = client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            temperature=0.5
        )
        
        deep_dive_text = response.choices[0].message.content
        
        # Debug output of raw LLM response
        logger.info(f"Raw LLM Response (first 200 chars): {deep_dive_text[:200]}...")
        
        # Parse all markdown sections
        sections = parse_all_markdown_sections(deep_dive_text)
        
        # Log the parsed sections for debugging
        logger.info(f"Parsed {len(sections)} sections from LLM response")
        logger.info(f"Section names: {list(sections.keys())}")
        
        # Debug output for each section
        for section_name, content in sections.items():
            logger.info(f"Section '{section_name}' length: {len(content)} chars")
            logger.info(f"Section '{section_name}' preview: {content[:50]}...")
            
        # If no sections were parsed, log the entire response for debugging
        if not sections:
            logger.warning("No sections were parsed from the LLM response!")
            logger.warning(f"Full LLM response: {deep_dive_text}")
        
        # Create a complete response with sections
        result = {
            "sections": sections,
            "raw_llm_response": deep_dive_text  # Include the raw LLM response
        }
        
        return result
    except Exception as e:
        logger.error(f"Error in deep dive analysis: {str(e)}")
        return {
            "sections": {},
            "raw_llm_response": ""  # Empty string for raw response in case of error
        }

async def evaluate_founders(company_name: str, description: str, team_info: Optional[List[Dict[str, str]]], raw_text: str, deep_dive_data: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """
    Evaluate startup founders using scientific criteria to predict success
    """
    logger.info(f"Evaluating founders for {company_name}")
    
    # Debug logging for input data
    logger.info(f"Founder eval input - Company: {company_name}")
    logger.info(f"Founder eval input - Description length: {len(description) if description else 0}")
    logger.info(f"Founder eval input - Team info count: {len(team_info) if team_info else 0}")
    logger.info(f"Founder eval input - Has deep dive data: {bool(deep_dive_data)}")
    
    acquired_data = {
        "company_name": company_name,
        "description": description,
        "team_info": team_info if team_info else []
    }
    
    if deep_dive_data and isinstance(deep_dive_data, dict):
        exec_summary = deep_dive_data.get('Executive Summary', '')
        if isinstance(exec_summary, dict):
            exec_summary_text = '\n'.join([f"{k}: {v}" for k, v in exec_summary.items()])
        else:
            exec_summary_text = str(exec_summary)
        acquired_data["deep_dive"] = exec_summary_text
    
    # Debug logging for processed data
    logger.info(f"Founder eval data prepared - Team info processed: {bool(acquired_data['team_info'])}")
    logger.info(f"Founder eval data prepared - Has deep dive: {bool(acquired_data.get('deep_dive'))}")
    
    data_str = json.dumps(acquired_data, indent=2)
    
    system_prompt = (
        "You are an expert in venture capital, specializing in evaluating startup founders. "
        "Your task is to distinguish successful founders from unsuccessful ones.\n\n"
        "Here is a policy to assist you:\n\n"
        "**Updated Policies for Distinguishing Successful Founders:**\n\n"
        "1. **Industry Fit & Scalability**: Prioritize founders building scalable tech, AI, or deep-tech products over service-heavy models.\n\n"
        "2. **Sector-Specific Innovation & Patent Verification**: Require defensible IP with issued or published patents validated through public databases.\n\n"
        "3. **Quantifiable Outcomes, Exits & (for Bio/Med) Regulatory Milestones**: Demand audited revenue, exits, or documented IND/clinical-phase progress—not just pre-clinical claims.\n\n"
        "4. **Funding Validation**: Verify that reputable VCs have invested, not just accelerators or angels, and confirm the funding amount.\n\n"
        "5. **Press Recognition**: Assess quality of press mentions, distinguishing between paid content and earned media from reputable sources.\n\n"
        "6. **Product vs. Service Orientation**: Favor high-margin, scalable products with IP protection over service-based models.\n\n"
        "7. **Market Traction Metrics**: Require evidence of growth, user retention, and engagement metrics, not just download numbers.\n\n"
        "8. **Location Advantage**: Consider whether the founder has leveraged local partnerships, ecosystem leadership, or geographic advantages.\n\n"
        "9. **Crisis Management & Pivot History**: Evaluate how founders have navigated setbacks, with preference for those who've successfully pivoted.\n\n"
        "10. **Roadmap Realism**: Assess whether growth projections and milestone timelines are realistic given the industry and resources.\n\n"
        "11. **Skill Alignment**: Verify that the founder's skills match the venture's needs, especially technical expertise for deep-tech startups.\n\n"
        "12. **Role Tenure**: Prioritize founders with significant experience in relevant roles, not just brief stints.\n\n"
        "13. **Network Quality**: Evaluate the founder's professional network quality and engagement, not just size.\n\n"
        "14. **Third-Party Validation**: Verify customer testimonials and partnerships through independent sources.\n\n"
        "15. **Ecosystem Participation**: Assess the founder's participation in the investment ecosystem through speaking engagements, mentorship, etc.\n\n"
        "16. **Value Proposition Clarity**: Evaluate whether the founder can articulate a clear, differentiated value proposition.\n\n"
        "17. **Tech Currency**: Assess whether the founder keeps current with relevant technologies and industry trends.\n\n"
        "18. **Data Consistency**: Cross-verify founder claims across platforms (LinkedIn, company website, etc.) for consistency."
    )
    
    user_prompt = f"""
    Please evaluate the founder(s) of {company_name} based on the scientific criteria in the policy.
    Here's all the information we have about the company and its founders:
    {data_str}
    Based on this information, please:
    1. Determine if the founder(s) are likely to be successful (true/false)
    2. Provide a comprehensive overall assessment that includes your evaluation against the policy criteria
    Format your response as JSON with the following structure:
    {{
        "success_prediction": boolean,
        "overall_assessment": "A comprehensive assessment that includes your evaluation of the founder against all policy criteria. Explain how the founder performs against each criterion from the policy and why this leads to your success prediction. Keep this as a single cohesive analysis rather than splitting it into separate sections."
    }}
    """
    
    try:
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
        except Exception as format_error:
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
            else:
                raise
        
        founder_eval_text = response.choices[0].message.content
        
        try:
            founder_evaluation = json.loads(founder_eval_text)
            simplified_evaluation = {
                "success_prediction": founder_evaluation.get("success_prediction", False),
                "overall_assessment": founder_evaluation.get("overall_assessment", "")
            }
            return simplified_evaluation
        except json.JSONDecodeError:
            logger.info("Response is not valid JSON, extracting structured information")
            
            success_prediction = False
            if "true" in founder_eval_text.lower() and "success_prediction" in founder_eval_text.lower():
                success_prediction = True
            
            overall_match = re.search(r'overall[\s_]assessment[":\s]+(.*?)(?:"success_prediction"|"}|$)', 
                                     founder_eval_text, re.IGNORECASE | re.DOTALL)
            overall_assessment = overall_match.group(1).strip() if overall_match else ""
            overall_assessment = overall_assessment.strip('"\n\r\t ,:')
            
            simplified_evaluation = {
                "success_prediction": success_prediction,
                "overall_assessment": overall_assessment
            }
            return simplified_evaluation
    except Exception as e:
        logger.error(f"Error in founder evaluation: {str(e)}")
        return {
            "success_prediction": False,
            "overall_assessment": f"Failed to evaluate founders for {company_name}: {str(e)}"
        }
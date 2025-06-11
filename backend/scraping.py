import re
import requests
import logging
from bs4 import BeautifulSoup
from urllib.parse import urlparse, urljoin, urlunparse
from typing import Optional, Dict, Any, List, Set, Tuple
from pydantic import BaseModel
import time
from collections import defaultdict, deque

logger = logging.getLogger(__name__)

class ScrapedData(BaseModel):
    company_name: str
    description: str
    raw_text: str
    team_info: Optional[List[Dict[str, str]]] = None
    social_links: Optional[Dict[str, str]] = None
    about_page: Optional[str] = None
    contact_info: Optional[Dict[str, str]] = None
    products_services: Optional[List[Dict[str, str]]] = None
    news_data: Optional[List[Dict[str, str]]] = None
    pages_scraped: Optional[List[Dict[str, Any]]] = None
    total_pages_found: Optional[int] = None

class SmartPageClassifier:
    """Classifies pages based on URL patterns, content, and link text"""
    
    def __init__(self):
        self.page_keywords = {
            'about': {
                'url_patterns': [
                    r'/about', r'/about-us', r'/about-company', r'/our-story', 
                    r'/who-we-are', r'/mission', r'/vision', r'/values', 
                    r'/company', r'/overview', r'/history'
                ],
                'link_text': [
                    'about', 'about us', 'about company', 'our story', 
                    'who we are', 'mission', 'vision', 'company', 'overview'
                ],
                'content_indicators': [
                    'founded', 'established', 'our mission', 'our vision', 
                    'company history', 'who we are', 'what we do'
                ]
            },
            'products': {
                'url_patterns': [
                    r'/products', r'/services', r'/solutions', r'/offerings', 
                    r'/platform', r'/technology', r'/features', r'/what-we-do',
                    r'/portfolio', r'/catalog'
                ],
                'link_text': [
                    'products', 'services', 'solutions', 'offerings', 
                    'platform', 'technology', 'features', 'what we do',
                    'portfolio', 'catalog'
                ],
                'content_indicators': [
                    'our products', 'our services', 'what we offer', 
                    'solutions', 'features', 'capabilities'
                ]
            },
            'team': {
                'url_patterns': [
                    r'/team', r'/our-team', r'/leadership', r'/management', 
                    r'/founders', r'/people', r'/board', r'/executives',
                    r'/staff', r'/directors'
                ],
                'link_text': [
                    'team', 'our team', 'leadership', 'management', 
                    'founders', 'people', 'board', 'executives', 'staff'
                ],
                'content_indicators': [
                    'our team', 'leadership team', 'founders', 'executives',
                    'management', 'board of directors'
                ]
            },
            'contact': {
                'url_patterns': [
                    r'/contact', r'/contact-us', r'/get-in-touch', r'/reach-us', 
                    r'/locations', r'/offices', r'/support', r'/help'
                ],
                'link_text': [
                    'contact', 'contact us', 'get in touch', 'reach us', 
                    'locations', 'offices', 'support', 'help'
                ],
                'content_indicators': [
                    'contact us', 'get in touch', 'phone', 'email', 
                    'address', 'location', 'office'
                ]
            },
            'news': {
                'url_patterns': [
                    r'/news', r'/blog', r'/press', r'/media', r'/updates', 
                    r'/insights', r'/resources', r'/articles', r'/announcements'
                ],
                'link_text': [
                    'news', 'blog', 'press', 'media', 'updates', 
                    'insights', 'resources', 'articles'
                ],
                'content_indicators': [
                    'latest news', 'blog posts', 'press releases', 
                    'media coverage', 'announcements'
                ]
            },
            'careers': {
                'url_patterns': [
                    r'/careers', r'/jobs', r'/join-us', r'/work-with-us', 
                    r'/opportunities', r'/positions', r'/hiring'
                ],
                'link_text': [
                    'careers', 'jobs', 'join us', 'work with us', 
                    'opportunities', 'hiring'
                ],
                'content_indicators': [
                    'join our team', 'career opportunities', 'job openings',
                    'work with us', 'we are hiring'
                ]
            }
        }
    
    def classify_page(self, url: str, link_text: str = "", content: str = "") -> List[str]:
        """Classify a page based on URL, link text, and content"""
        classifications = []
        url_lower = url.lower()
        link_text_lower = link_text.lower()
        content_lower = content.lower()
        
        for page_type, keywords in self.page_keywords.items():
            score = 0
            
            # Check URL patterns
            for pattern in keywords['url_patterns']:
                if re.search(pattern, url_lower):
                    score += 3
                    break
            
            # Check link text
            for text in keywords['link_text']:
                if text in link_text_lower:
                    score += 2
                    break
            
            # Check content indicators (if content provided)
            if content:
                for indicator in keywords['content_indicators']:
                    if indicator in content_lower:
                        score += 1
                        break
            
            if score >= 2:  # Threshold for classification
                classifications.append(page_type)
        
        return classifications

def normalize_url(url: str, base_url: str) -> str:
    """Normalize and resolve URLs"""
    if not url:
        return ""
    
    # Remove fragments and normalize
    url = url.split('#')[0].strip()
    
    # Handle relative URLs
    if url.startswith('/'):
        normalized = urljoin(base_url, url)
    elif not url.startswith(('http://', 'https://')):
        normalized = urljoin(base_url, url)
    else:
        normalized = url
    
    # Remove trailing slash for consistency (except for root)
    if normalized.endswith('/') and len(normalized.split('/')) > 3:
        normalized = normalized[:-1]
    
    return normalized

def is_same_domain(url1: str, url2: str) -> bool:
    """Check if two URLs are from the same domain"""
    return urlparse(url1).netloc == urlparse(url2).netloc

def should_skip_url(url: str) -> bool:
    """Determine if a URL should be skipped"""
    url_lower = url.lower()
    
    # Skip non-content file extensions
    skip_extensions = ('.pdf', '.doc', '.docx', '.xls', '.xlsx', '.zip', 
                      '.png', '.jpg', '.jpeg', '.gif', '.svg', '.ico',
                      '.css', '.js', '.xml', '.json', '.rss')
    
    # Skip common non-content paths
    skip_paths = ('/login', '/signin', '/signup', '/register', '/cart', 
                 '/checkout', '/privacy', '/terms', '/cookie', '/legal',
                 '/wp-admin', '/admin', '/dashboard', '/account')
    
    # Skip external links to common domains
    skip_domains = ('facebook.com', 'twitter.com', 'linkedin.com', 
                   'instagram.com', 'youtube.com', 'google.com')
    
    return (any(ext in url_lower for ext in skip_extensions) or
            any(path in url_lower for path in skip_paths) or
            any(domain in url_lower for domain in skip_domains))

def extract_links_with_context(soup: BeautifulSoup, base_url: str) -> List[Tuple[str, str]]:
    """Extract links with their anchor text context"""
    links_with_context = []
    seen_urls = set()
    
    for link in soup.find_all('a', href=True):
        href = link.get('href', '').strip()
        if not href or href.startswith(('mailto:', 'tel:', 'javascript:')):
            continue
        
        normalized_url = normalize_url(href, base_url)
        if not normalized_url or should_skip_url(normalized_url):
            continue
        
        # Skip if we've already seen this URL
        if normalized_url in seen_urls:
            continue
        
        # Skip if it's just the base URL or homepage variations
        base_domain = base_url.rstrip('/')
        if normalized_url in [base_domain, base_domain + '/', base_domain + '/index.html', base_domain + '/home']:
            continue
        
        seen_urls.add(normalized_url)
        
        # Get link text and context
        link_text = link.get_text(strip=True)
        
        # Skip empty link text or very short generic text
        if not link_text or len(link_text) < 2 or link_text.lower() in ['home', 'here', 'click', 'more']:
            continue
        
        # Also check parent elements for additional context
        parent_text = ""
        parent = link.parent
        while parent and not parent_text and parent.name != 'body':
            parent_text = parent.get_text(strip=True)[:100]
            parent = parent.parent
        
        context = f"{link_text} {parent_text}".strip()
        links_with_context.append((normalized_url, context))
    
    return links_with_context

def extract_contact_info(soup, text):
    """Extract contact information from the page"""
    contact_info = {}
    
    # Email extraction (improved pattern)
    email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
    emails = re.findall(email_pattern, text)
    if emails:
        # Filter out common false positives
        valid_emails = [email for email in emails if not any(skip in email.lower() 
                       for skip in ['@example.com', '@domain.com', '@yoursite.com'])]
        if valid_emails:
            contact_info['emails'] = list(set(valid_emails))
    
    # Phone extraction (improved patterns)
    phone_patterns = [
        r'(\+?1?[-.\s]?\(?[0-9]{3}\)?[-.\s]?[0-9]{3}[-.\s]?[0-9]{4})',
        r'(\+?[0-9]{1,3}[-.\s]?[0-9]{1,4}[-.\s]?[0-9]{1,4}[-.\s]?[0-9]{1,9})'
    ]
    
    phones = []
    for pattern in phone_patterns:
        phones.extend(re.findall(pattern, text))
    
    if phones:
        contact_info['phones'] = list(set(phones))
    
    # Address extraction (improved)
    address_patterns = [
        r'(?i)address[:\s]+([^.]*(?:street|st|avenue|ave|road|rd|drive|dr|boulevard|blvd|lane|ln)[^.]*)',
        r'(?i)(?:located at|headquarters|office)[:\s]+([^.]*(?:street|st|avenue|ave|road|rd)[^.]*)',
        r'([0-9]+\s+[A-Za-z\s]+(?:street|st|avenue|ave|road|rd|drive|dr|boulevard|blvd|lane|ln)[^.]*)'
    ]
    
    addresses = []
    for pattern in address_patterns:
        matches = re.findall(pattern, text)
        addresses.extend(matches)
    
    if addresses:
        contact_info['addresses'] = list(set(addresses))
    
    return contact_info

def extract_team_info(soup):
    """Extract team information from the page"""
    team_info = []
    
    # Look for team member sections with various selectors
    team_selectors = [
        {'class': re.compile(r'team|member|founder|leadership|staff|employee', re.I)},
        {'id': re.compile(r'team|member|founder|leadership|staff', re.I)},
        {'data-team': True}
    ]
    
    team_sections = []
    for selector in team_selectors:
        team_sections.extend(soup.find_all(['div', 'section', 'article'], selector))
    
    # Also look for structured data
    for section in team_sections:
        # Method 1: Look for name-title pairs
        names = section.find_all(['h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'strong', 'b'])
        for name_elem in names:
            name_text = name_elem.get_text().strip()
            
            # Basic validation for person names
            if (2 <= len(name_text.split()) <= 4 and 
                len(name_text) < 50 and 
                not any(skip in name_text.lower() for skip in ['team', 'leadership', 'about', 'contact'])):
                
                # Look for title/role nearby
                title = ""
                
                # Check next sibling elements
                for sibling in name_elem.find_next_siblings(['p', 'div', 'span', 'h6'])[:3]:
                    sibling_text = sibling.get_text().strip()
                    if sibling_text and len(sibling_text) < 100:
                        title = sibling_text
                        break
                
                # Check parent container
                if not title:
                    parent = name_elem.parent
                    if parent:
                        title_elem = parent.find(['p', 'span', 'div'])
                        if title_elem:
                            title = title_elem.get_text().strip()[:100]
                
                team_info.append({
                    'name': name_text,
                    'title': title
                })
    
    # Remove duplicates based on name
    seen_names = set()
    unique_team_info = []
    for member in team_info:
        if member['name'] not in seen_names:
            seen_names.add(member['name'])
            unique_team_info.append(member)
    
    return unique_team_info

def extract_products_services(soup):
    """Extract products and services information"""
    products_services = []
    
    # Look for product/service sections
    product_selectors = [
        {'class': re.compile(r'product|service|offering|solution|feature', re.I)},
        {'id': re.compile(r'product|service|offering|solution', re.I)}
    ]
    
    sections = []
    for selector in product_selectors:
        sections.extend(soup.find_all(['div', 'section', 'article'], selector))
    
    for section in sections:
        title_elem = section.find(['h1', 'h2', 'h3', 'h4', 'h5', 'h6'])
        if title_elem:
            title = title_elem.get_text().strip()
            
            # Find description
            description = ""
            desc_elem = section.find(['p', 'div'])
            if desc_elem:
                description = desc_elem.get_text().strip()
            
            # Get any additional info like pricing, features
            features = []
            feature_lists = section.find_all(['ul', 'ol'])
            for feature_list in feature_lists:
                features.extend([li.get_text().strip() for li in feature_list.find_all('li')])
            
            if title and len(title) > 3:  # Basic validation
                product_info = {
                    'title': title[:200],
                    'description': description[:1000]
                }
                if features:
                    product_info['features'] = features[:10]  # Limit features
                
                products_services.append(product_info)
    
    return products_services

def extract_news_posts(soup):
    """Extract news/blog posts"""
    news_data = []
    
    # Look for news/blog sections
    news_selectors = [
        {'class': re.compile(r'news|blog|post|article|press|update', re.I)},
        {'id': re.compile(r'news|blog|post|article|press', re.I)}
    ]
    
    sections = []
    for selector in news_selectors:
        sections.extend(soup.find_all(['div', 'article', 'section'], selector))
    
    for section in sections:
        title_elem = section.find(['h1', 'h2', 'h3', 'h4', 'h5', 'h6'])
        if title_elem:
            title = title_elem.get_text().strip()
            
            # Extract date
            date = ""
            date_patterns = [
                {'class': re.compile(r'date|time|published', re.I)},
                {'datetime': True},
                {'time': True}
            ]
            
            for pattern in date_patterns:
                date_elem = section.find(['time', 'span', 'div'], pattern)
                if date_elem:
                    date = date_elem.get_text().strip()
                    break
            
            # Extract content
            content = ""
            content_elem = section.find(['p', 'div'])
            if content_elem:
                content = content_elem.get_text().strip()
            
            if title and len(title) > 5:  # Basic validation
                news_data.append({
                    'title': title[:300],
                    'date': date[:50],
                    'content': content[:800]
                })
    
    return news_data

async def fetch_news_data(company_name: str) -> List[Dict[str, str]]:
    """Fetch external news data about the company"""
    # This is a placeholder for future implementation
    # In a real implementation, this would call a news API or web search
    return []

# This function has been moved to founder_info.py

def clean_text(text):
    """Clean and normalize text content"""
    if not text:
        return ""
    
    # Remove excessive whitespace
    text = re.sub(r'\s+', ' ', text)
    
    # Remove common navigation and UI text
    ui_patterns = [
        r'(menu|navigation|search|close|open|toggle|submit|cancel|accept cookies)\b',
        r'(follow us on|share on|like us on|connect with us on)\b.*',
        r'(skip to content|skip navigation|accessibility)',
        r'(cookie policy|privacy policy|terms of service)\b'
    ]
    
    for pattern in ui_patterns:
        text = re.sub(pattern, '', text, flags=re.IGNORECASE)
    
    return text.strip()

def extract_company_name(soup: BeautifulSoup, url: str) -> str:
    """
    Extract company name with fallback to domain if title/meta content looks like marketing copy
    """
    
    # Marketing/tagline indicators - if we see these, it's probably not a company name
    marketing_keywords = [
        # Action words
        'get', 'start', 'try', 'buy', 'learn', 'discover', 'create', 'build', 'make', 
        'grow', 'boost', 'increase', 'improve', 'transform', 'convert', 'deliver',
        'drive', 'scale', 'automate', 'connect', 'helps', 'help',
        
        # Descriptive words  
        'best', 'top', 'leading', 'ultimate', 'perfect', 'easy', 'simple', 'fast',
        'smart', 'powerful', 'advanced', 'revolutionary', 'cutting-edge',
        
        # Common tagline patterns
        'that', 'which', 'for your', 'your business', 'solution', 'platform',
        'software', 'service', 'tool', 'system', 'technology'
    ]
    
    def looks_like_marketing(text: str) -> bool:
        """Check if text looks like marketing copy rather than a company name"""
        if not text or len(text) > 60:  # Too long for typical company name
            return True
            
        text_lower = text.lower()
        
        # Count marketing keywords
        marketing_count = sum(1 for keyword in marketing_keywords if keyword in text_lower)
        
        # If multiple marketing words or specific patterns, likely marketing copy
        if marketing_count >= 2:
            return True
            
        # Check for specific tagline patterns
        tagline_patterns = [
            r'\bthat\s+\w+',     # "AI that converts"
            r'\bfor\s+\w+',      # "Software for teams" 
            r'\bto\s+\w+',       # "Tools to grow"
            r'\byour\s+\w+',     # "Your business partner"
            r'\bhelps?\s+\w+',   # "Helps you grow"
        ]
        
        for pattern in tagline_patterns:
            if re.search(pattern, text_lower):
                return True
                
        return False
    
    def extract_from_domain(url: str) -> str:
        """Extract clean company name from domain"""
        parsed_url = urlparse(url)
        domain = parsed_url.netloc
        
        # Remove www prefix
        if domain.startswith('www.'):
            domain = domain[4:]
        
        # Get main domain part (before first dot)
        domain_name = domain.split('.')[0]
        
        # Convert to readable format
        company_name = domain_name.replace('-', ' ').replace('_', ' ')
        
        # Capitalize properly
        return ' '.join(word.capitalize() for word in company_name.split())
    
    # Try to extract from common sources, but validate each
    candidates = []
    
    # 1. Try page title
    if soup.title:
        title = soup.title.string.strip()
        
        # Split by common separators and check each part
        for separator in ['|', '-', '–', ':', '•']:
            if separator in title:
                parts = [part.strip() for part in title.split(separator)]
                for part in parts:
                    if part and not looks_like_marketing(part):
                        candidates.append(part)
                break
        
        # If no separator, check whole title
        if not candidates and not looks_like_marketing(title):
            candidates.append(title)
    
    # 2. Try Open Graph site name
    og_site_name = soup.find('meta', property='og:site_name')
    if og_site_name and og_site_name.get('content'):
        site_name = og_site_name['content'].strip()
        if not looks_like_marketing(site_name):
            candidates.append(site_name)
    
    # 3. Try meta application name
    app_name = soup.find('meta', {'name': 'application-name'})
    if app_name and app_name.get('content'):
        app_name_content = app_name['content'].strip()
        if not looks_like_marketing(app_name_content):
            candidates.append(app_name_content)
    
    # Return first valid candidate or fall back to domain
    if candidates:
        return candidates[0]
    else:
        return extract_from_domain(url)

async def scrape_website(url: str, max_pages: int = 5) -> ScrapedData:
    """
    Enhanced website scraping with smart page discovery and classification.
    
    Args:
        url (str): The URL of the startup's website to scrape
        max_pages (int, optional): Maximum number of pages to scrape. Defaults to 5.
        
    Returns:
        ScrapedData: Structured data extracted from the website
    """
    """
    Enhanced website scraping with smart page discovery and classification
    """
    logger.info(f"Starting enhanced scraping of {url} with max_pages: {max_pages}")
    
    classifier = SmartPageClassifier()
    pages_scraped = []
    all_discovered_links = set()
    classified_pages = defaultdict(list)
    pages_to_scrape = deque([(url, "")])  # (url, link_text) pairs
    
    # Initialize session with better configuration
    session = requests.Session()
    session.headers.update({
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    })
    
    retries = requests.adapters.Retry(
        total=3,
        backoff_factor=0.5,
        status_forcelist=[500, 502, 503, 504, 429],
        allowed_methods=["GET"]
    )
    session.mount('http://', requests.adapters.HTTPAdapter(max_retries=retries))
    session.mount('https://', requests.adapters.HTTPAdapter(max_retries=retries))
    
    try:
        # Step 1: Scrape main page
        logger.info("Scraping main page...")
        response = session.get(url, timeout=20)
        response.raise_for_status()
        
        main_soup = BeautifulSoup(response.text, 'html.parser')
        main_text = main_soup.get_text(separator='\n', strip=True)
        
        # Extract basic company info from main page
        company_name = extract_company_name(main_soup, url)
        description = extract_description(main_soup)
        social_links = extract_social_links(main_soup)
        
        # Initialize combined text with main page
        all_text = f"--- MAIN PAGE ---\n{clean_text(main_text)}"
        
        pages_scraped.append({
            'url': url,
            'type': 'main',
            'title': main_soup.title.string if main_soup.title else 'Main Page',
            'word_count': len(main_text.split())
        })
        
        # Step 2: Discover all internal links from main page
        base_url = f"{urlparse(url).scheme}://{urlparse(url).netloc}"
        links_with_context = extract_links_with_context(main_soup, base_url)
        
        # Step 3: Classify discovered links
        unique_links = {}  # Use dict to avoid duplicates while keeping context
        for link_url, context in links_with_context:
            if is_same_domain(link_url, url) and link_url != url:  # Exclude main page
                if link_url not in unique_links:
                    unique_links[link_url] = context
                    all_discovered_links.add((link_url, context))
                    classifications = classifier.classify_page(link_url, context)
                    for classification in classifications:
                        if not any(existing_url == link_url for existing_url, _ in classified_pages[classification]):
                            classified_pages[classification].append((link_url, context))
        
        logger.info(f"Discovered {len(all_discovered_links)} internal links")
        logger.info(f"Classified pages: {dict(classified_pages)}")
        
        # Step 4: Prioritize pages to scrape based on classification and max_pages
        priority_pages = []
        
        # Define key page types in order of importance
        key_page_types = ['about', 'team', 'products', 'contact', 'news']
        
        # First, add one page from each key type if available
        for page_type in key_page_types:
            if page_type in classified_pages and classified_pages[page_type]:
                link_url, context = classified_pages[page_type][0]
                if len(priority_pages) < max_pages - 1:  # -1 for main page
                    priority_pages.append((link_url, context, page_type))
        
        # Then fill remaining slots with other classified pages
        remaining_slots = max_pages - len(priority_pages) - 1  # -1 for main page
        if remaining_slots > 0:
            # Get remaining classified pages
            remaining_classified = [
                (url, ctx, ptype)
                for ptype in classified_pages
                for url, ctx in classified_pages[ptype]
                if not any(url == p[0] for p in priority_pages)
            ]
            
            # Sort by URL structure (shorter URLs often more important)
            remaining_classified.sort(key=lambda x: (len(x[0].split('/')), x[0]))
            
            # Add remaining classified pages
            priority_pages.extend(remaining_classified[:remaining_slots])
        
        # Step 5: Scrape prioritized pages
        scraped_data_parts = {
            'about_page': None,
            'contact_info': {},
            'team_info': [],
            'products_services': [],
            'news_data': []
        }
        
        logger.info(f"Scraping {len(priority_pages)} prioritized pages")
        for i, (page_url, context, page_type) in enumerate(priority_pages, 1):
            try:
                if page_url == url:  # Skip if same as main page
                    continue
                
                logger.info(f"Scraping page {i}/{len(priority_pages)}: {page_url} ({page_type})")
                
                # Add delay to be respectful
                if i > 0:
                    time.sleep(1)
                
                page_response = session.get(page_url, timeout=15)
                page_response.raise_for_status()
                
                # Verify content type
                content_type = page_response.headers.get('content-type', '')
                if not any(ct in content_type.lower() for ct in ['text/html', 'application/xhtml']):
                    logger.warning(f"Skipping {page_url}: Invalid content type {content_type}")
                    continue
                
                page_soup = BeautifulSoup(page_response.text, 'html.parser')
                page_text = page_soup.get_text(separator='\n', strip=True)
                cleaned_page_text = clean_text(page_text)
                
                # Add to combined text
                all_text += f"\n\n--- {page_type.upper()} PAGE: {page_url} ---\n{cleaned_page_text}"
                
                # Extract specific information based on page type
                if page_type == 'about':
                    scraped_data_parts['about_page'] = cleaned_page_text
                elif page_type == 'contact':
                    scraped_data_parts['contact_info'].update(extract_contact_info(page_soup, cleaned_page_text))
                elif page_type == 'team':
                    scraped_data_parts['team_info'].extend(extract_team_info(page_soup))
                elif page_type == 'products':
                    scraped_data_parts['products_services'].extend(extract_products_services(page_soup))
                elif page_type == 'news':
                    scraped_data_parts['news_data'].extend(extract_news_posts(page_soup))
                
                # Track scraped page
                pages_scraped.append({
                    'url': page_url,
                    'type': page_type,
                    'title': page_soup.title.string if page_soup.title else f'{page_type.title()} Page',
                    'word_count': len(page_text.split())
                })
                
            except Exception as e:
                logger.warning(f"Error scraping {page_url}: {str(e)}")
                continue
        
        # Step 6: Create final ScrapedData object
        scraped_data = ScrapedData(
            company_name=company_name,
            description=description,
            raw_text=all_text,
            team_info=scraped_data_parts['team_info'] if scraped_data_parts['team_info'] else None,
            social_links=social_links if social_links else None,
            about_page=scraped_data_parts['about_page'],
            contact_info=scraped_data_parts['contact_info'] if scraped_data_parts['contact_info'] else None,
            products_services=scraped_data_parts['products_services'] if scraped_data_parts['products_services'] else None,
            news_data=scraped_data_parts['news_data'] if scraped_data_parts['news_data'] else None,
            pages_scraped=pages_scraped,
            total_pages_found=len(all_discovered_links)
        )
        
        logger.info(f"Scraping completed. Scraped {len(pages_scraped)} pages out of {len(all_discovered_links)} discovered")
        return scraped_data
        
    except Exception as e:
        logger.error(f"Error during website scraping: {str(e)}")
        raise Exception(f"Failed to scrape website: {str(e)}")

def extract_description(soup: BeautifulSoup) -> str:
    """Extract site description from various sources"""
    # Try meta description
    meta_desc = soup.find('meta', {'name': 'description'})
    if meta_desc and meta_desc.get('content'):
        return meta_desc['content'].strip()
    
    # Try Open Graph description
    og_desc = soup.find('meta', property='og:description')
    if og_desc and og_desc.get('content'):
        return og_desc['content'].strip()
    
    # Try first paragraph
    first_p = soup.find('p')
    if first_p:
        text = first_p.get_text().strip()
        if len(text) > 50:  # Ensure it's substantial
            return text[:300]  # Limit length
    
    # Try h1 + following paragraph
    h1 = soup.find('h1')
    if h1:
        next_elem = h1.find_next('p')
        if next_elem:
            return next_elem.get_text().strip()[:300]
    
    return ""

def extract_social_links(soup: BeautifulSoup) -> Dict[str, str]:
    """Extract social media links"""
    social_links = {}
    social_platforms = {
        'twitter': ['twitter.com', 'x.com'],
        'linkedin': ['linkedin.com'],
        'facebook': ['facebook.com'],
        'instagram': ['instagram.com'],
        'github': ['github.com'],
        'youtube': ['youtube.com'],
        'tiktok': ['tiktok.com'],
        'discord': ['discord.com', 'discord.gg']
    }
    
    for link in soup.find_all('a', href=True):
        href = link['href'].lower()
        for platform, domains in social_platforms.items():
            if any(domain in href for domain in domains):
                # Clean up the URL
                if href.startswith('//'):
                    href = 'https:' + href
                elif not href.startswith('http'):
                    continue
                social_links[platform] = href
                break
    
    return social_links
import re
import requests
import logging
from bs4 import BeautifulSoup, Comment
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
    contact_info: Optional[Dict[str, List[str]]] = None
    products_services: Optional[List[Dict[str, str]]] = None
    news_data: Optional[List[Dict[str, str]]] = None
    pages_scraped: Optional[List[Dict[str, Any]]] = None
    total_pages_found: Optional[int] = None

class EnhancedTextExtractor:
    """Enhanced text extraction with comprehensive noise removal"""
    
    def __init__(self):
        logger.debug("Initializing EnhancedTextExtractor")
        
        # Expanded noise patterns for better cleaning
        self.noise_patterns = {
            'navigation': [
                r'(menu|nav|navigation|breadcrumb|sidebar|footer|header)\s*:?\s*',
                r'(skip to|jump to|go to)\s+(content|main|navigation)',
                r'(toggle|open|close|show|hide)\s+(menu|navigation)',
                r'(home|back to top|scroll to top)',
                r'(previous|next|page \d+|\d+ of \d+)',
                r'(sort by|filter by|view all|show more|load more)',
                r'(search|submit|reset|cancel|ok|yes|no)\s*(button)?'
            ],
            'privacy': [
                r'(cookie|privacy|gdpr|ccpa)\s*(policy|notice|consent|banner)',
                r'(accept|decline|manage|customize)\s*(cookies|privacy|preferences)',
                r'(we use cookies|this site uses|by continuing)',
                r'(privacy policy|terms of service|legal notice)',
                r'(your privacy|data protection|cookie settings)'
            ],
            'social': [
                r'(follow us|connect with us|find us)\s*on',
                r'(share|like|tweet|post)\s*(this|on|via)',
                r'(facebook|twitter|linkedin|instagram|youtube|tiktok)\s*(page|profile)?',
                r'(social media|social networks)',
                r'(subscribe|newsletter|email updates)'
            ],
            'ads': [
                r'(advertisement|sponsored|promoted|ad\s)',
                r'(buy now|shop now|order now|get started|sign up)',
                r'(free trial|limited time|special offer|discount)',
                r'(click here|learn more|read more|find out)',
                r'(call now|contact today|get quote)',
                r'(\$\d+|\d+% off|save \$)',
                r'(testimonial|review|rating|stars)'
            ],
            'forms': [
                r'(enter|type|select|choose|pick)\s*(your|a|an)',
                r'(required|optional|please|must)\s*(field|enter|provide)',
                r'(email|password|username|phone|address)\s*(field)?',
                r'(checkbox|radio|dropdown|select|input)',
                r'(validation|error|success|warning)\s*(message)?'
            ],
            'technical': [
                r'(loading|please wait|processing)',
                r'(javascript|css|browser|compatibility)',
                r'(404|error|not found|page not found)',
                r'(copyright|all rights reserved|\(c\)\s*\d{4})',
                r'(version|update|upgrade|download)',
                r'(api|sdk|documentation|docs)'
            ]
        }
        
        # Elements to completely remove
        self.remove_selectors = [
            'nav', 'navbar', '.navbar', '#navbar', '.nav', '#nav',
            '.navigation', '#navigation', '.menu', '#menu',
            '.breadcrumb', '.breadcrumbs', '.sidebar', '.aside',
            'header', 'footer', '.header', '.footer', '#header', '#footer',
            '.site-header', '.site-footer', '.page-header', '.page-footer',
            '.ad', '.ads', '.advertisement', '.banner', '.promo',
            '.marketing', '.cta', '.call-to-action', '.popup', '.modal',
            '.overlay', '.lightbox', '[class*="ad-"]', '[id*="ad-"]',
            '.social', '.share', '.sharing', '.follow', '.subscribe',
            '.newsletter', '.social-media', '.social-links',
            '.comments', '.comment', '.review', '.reviews', '.rating',
            '.testimonial', '.testimonials', '.feedback',
            '.search', '.search-form', '#search', '.login', '.signup',
            '.registration', '.newsletter-signup',
            'script', 'style', 'noscript', '.hidden', '.invisible',
            '[style*="display:none"]', '[style*="visibility:hidden"]',
            '.cookie', '.privacy', '.gdpr', '.consent', '.notice',
            '.meta', '.metadata', '.tags', '.categories', '.author-info',
            '.publish-date', '.last-updated'
        ]
        
        # Content-rich elements to prioritize
        self.content_selectors = [
            'main', '[role="main"]', '.main', '#main',
            '.content', '#content', '.page-content', '.main-content',
            'article', '.article', '.post', '.entry',
            '.description', '.summary', '.intro', '.overview',
            '.about', '.company-info', '.product-info'
        ]

    def remove_noise_elements(self, soup: BeautifulSoup) -> BeautifulSoup:
        """Remove noise elements from the soup"""
        logger.debug("Removing noise elements from HTML")
        
        # Remove comments
        comments_removed = 0
        for comment in soup.find_all(string=lambda text: isinstance(text, Comment)):
            comment.extract()
            comments_removed += 1
        logger.debug(f"Removed {comments_removed} HTML comments")
        
        # Remove script, style, meta, link tags
        technical_tags_removed = 0
        for tag in soup(['script', 'style', 'meta', 'link']):
            tag.decompose()
            technical_tags_removed += 1
        logger.debug(f"Removed {technical_tags_removed} technical tags")
        
        # Remove elements by selector
        elements_removed = 0
        for selector in self.remove_selectors:
            try:
                for element in soup.select(selector):
                    element.decompose()
                    elements_removed += 1
            except Exception as e:
                logger.warning(f"Error removing selector {selector}: {str(e)}")
                continue
        logger.debug(f"Removed {elements_removed} noise elements by selector")
        
        # Remove elements with noise-indicating attributes
        attr_elements_removed = 0
        noise_attributes = [
            ('class', ['ad', 'ads', 'advertisement', 'banner', 'popup', 'modal',
                      'cookie', 'privacy', 'gdpr', 'social', 'share', 'nav',
                      'menu', 'header', 'footer', 'sidebar']),
            ('id', ['ad', 'ads', 'banner', 'popup', 'cookie', 'privacy',
                   'nav', 'menu', 'header', 'footer']),
            ('role', ['banner', 'navigation', 'contentinfo', 'complementary'])
        ]
        
        for attr, keywords in noise_attributes:
            try:
                elements_to_remove = []
                for element in soup.find_all(attrs={attr: True}):
                    try:
                        if element is None:
                            continue
                            
                        attr_value = element.get(attr, '')
                        if attr_value is None:
                            continue
                            
                        if isinstance(attr_value, list):
                            attr_value = ' '.join(str(v) for v in attr_value if v is not None)
                        
                        attr_value = str(attr_value).lower()
                        
                        if any(keyword in attr_value for keyword in keywords):
                            elements_to_remove.append(element)
                            
                    except Exception as e:
                        logger.debug(f"Error processing individual element for {attr}: {str(e)}")
                        continue
                
                # Remove elements outside the iteration
                for element in elements_to_remove:
                    try:
                        element.decompose()
                        attr_elements_removed += 1
                    except Exception as e:
                        logger.debug(f"Error removing element: {str(e)}")
                        continue
                        
            except Exception as e:
                logger.warning(f"Error processing attribute {attr}: {str(e)}")
                continue
        
        logger.debug(f"Removed {attr_elements_removed} elements by noise attributes")
        return soup

    def extract_main_content(self, soup: BeautifulSoup) -> str:
        """Extract main content with priority to content-rich elements"""
        logger.debug("Extracting main content from cleaned HTML")
        
        content_texts = []
        main_content = None
        
        # Try to find main content area first
        for selector in self.content_selectors:
            try:
                main_content = soup.select_one(selector)
                if main_content:
                    logger.debug(f"Found main content using selector: {selector}")
                    break
            except Exception as e:
                logger.warning(f"Error with content selector {selector}: {str(e)}")
                continue
        
        if main_content:
            content_texts.append(self.extract_clean_text(main_content))
        else:
            logger.debug("No main content area found, extracting from body")
            body = soup.find('body')
            if body:
                content_texts.append(self.extract_clean_text(body))
            else:
                logger.debug("No body found, extracting from entire soup")
                content_texts.append(self.extract_clean_text(soup))
        
        final_text = '\n\n'.join(filter(None, content_texts))
        logger.debug(f"Extracted {len(final_text)} characters of main content")
        return final_text

    def extract_clean_text(self, element) -> str:
        """Extract and clean text from an element"""
        if not element:
            return ""
        
        text = element.get_text(separator='\n', strip=True)
        return self.clean_text_content(text)

    def clean_text_content(self, text: str) -> str:
        """Clean text content by removing noise patterns"""
        if not text:
            return ""
        
        original_length = len(text)
        
        # Normalize whitespace
        text = re.sub(r'\s+', ' ', text)
        text = re.sub(r'\n\s*\n', '\n\n', text)
        
        # Remove noise patterns
        patterns_removed = 0
        for category, patterns in self.noise_patterns.items():
            for pattern in patterns:
                before_length = len(text)
                text = re.sub(pattern, '', text, flags=re.IGNORECASE)
                if len(text) < before_length:
                    patterns_removed += 1
        
        # Remove common UI text patterns
        ui_removals = [
            r'^(home|menu|navigation|search|close|open)\s*$',
            r'^(skip to|jump to)\s+\w+\s*$',
            r'^(page \d+ of \d+|previous|next)\s*$',
            r'^(loading|please wait)\s*\.{0,3}\s*$',
            r'^(required field|please enter|must be)\s*\.{0,3}\s*$',
            r'^[\*\+\-\•]\s*$',
            r'^\d+\s*$',
            r'^[^\w\s]*$',
        ]
        
        lines = text.split('\n')
        cleaned_lines = []
        lines_removed = 0
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            skip_line = False
            for pattern in ui_removals:
                if re.match(pattern, line, re.IGNORECASE):
                    skip_line = True
                    lines_removed += 1
                    break
            
            if not skip_line and len(line) > 2:
                cleaned_lines.append(line)
        
        # Join lines and normalize spacing
        text = '\n'.join(cleaned_lines)
        text = re.sub(r'\n{3,}', '\n\n', text)
        text = re.sub(r'[ \t]+', ' ', text)
        
        final_length = len(text)
        logger.debug(f"Text cleaning: {original_length} -> {final_length} chars, "
                    f"removed {patterns_removed} noise patterns, {lines_removed} UI lines")
        
        return text.strip()

class SmartPageClassifier:
    """Enhanced page classifier with better patterns"""
    
    def __init__(self):
        logger.debug("Initializing SmartPageClassifier")
        
        self.page_keywords = {
            'about': {
                'url_patterns': [
                    r'/about', r'/about-us', r'/about-company', r'/our-story', 
                    r'/who-we-are', r'/mission', r'/vision', r'/values', 
                    r'/company', r'/overview', r'/history', r'/story',
                    r'/why-us', r'/our-mission', r'/our-vision'
                ],
                'link_text': [
                    'about', 'about us', 'about company', 'our story', 
                    'who we are', 'mission', 'vision', 'company', 'overview',
                    'story', 'history', 'background', 'why us', 'our mission'
                ],
                'content_indicators': [
                    'founded', 'established', 'our mission', 'our vision', 
                    'company history', 'who we are', 'what we do', 'our story',
                    'why we exist', 'our purpose'
                ]
            },
            'products': {
                'url_patterns': [
                    r'/products', r'/product', r'/services', r'/service', r'/solutions', r'/solution',
                    r'/offerings', r'/platform', r'/technology', r'/features', r'/what-we-do',
                    r'/portfolio', r'/catalog', r'/tools', r'/capabilities', r'/how-it-works',
                    r'/pricing', r'/plans'
                ],
                'link_text': [
                    'products', 'product', 'services', 'service', 'solutions', 'solution',
                    'offerings', 'platform', 'technology', 'features', 'what we do',
                    'portfolio', 'catalog', 'tools', 'capabilities', 'how it works',
                    'pricing', 'plans', 'get started'
                ],
                'content_indicators': [
                    'our products', 'our services', 'what we offer', 
                    'solutions', 'features', 'capabilities', 'platform',
                    'how it works', 'pricing', 'plans'
                ]
            },
            'team': {
                'url_patterns': [
                    r'/team', r'/our-team', r'/leadership', r'/management', 
                    r'/founders', r'/people', r'/board', r'/executives',
                    r'/staff', r'/directors', r'/advisors', r'/meet-the-team',
                    r'/our-people', r'/who-we-are'
                ],
                'link_text': [
                    'team', 'our team', 'leadership', 'management', 
                    'founders', 'people', 'board', 'executives', 'staff',
                    'advisors', 'directors', 'meet the team', 'our people',
                    'who we are'
                ],
                'content_indicators': [
                    'our team', 'leadership team', 'founders', 'executives',
                    'management', 'board of directors', 'meet the team',
                    'our people', 'who we are'
                ]
            },
            'contact': {
                'url_patterns': [
                    r'/contact', r'/contact-us', r'/get-in-touch', r'/reach-us', 
                    r'/locations', r'/offices', r'/support', r'/help', r'/reach-out',
                    r'/talk-to-us', r'/schedule', r'/demo', r'/book'
                ],
                'link_text': [
                    'contact', 'contact us', 'get in touch', 'reach us', 
                    'locations', 'offices', 'support', 'help', 'reach out',
                    'talk to us', 'schedule', 'demo', 'book', 'get started'
                ],
                'content_indicators': [
                    'contact us', 'get in touch', 'phone', 'email', 
                    'address', 'location', 'office', 'reach out',
                    'schedule', 'demo', 'book'
                ]
            },
            'news': {
                'url_patterns': [
                    r'/news', r'/blog', r'/press', r'/media', r'/updates', 
                    r'/insights', r'/resources', r'/articles', r'/announcements',
                    r'/content', r'/knowledge', r'/learn'
                ],
                'link_text': [
                    'news', 'blog', 'press', 'media', 'updates', 
                    'insights', 'resources', 'articles', 'announcements',
                    'content', 'knowledge', 'learn', 'latest'
                ],
                'content_indicators': [
                    'latest news', 'blog posts', 'press releases', 
                    'media coverage', 'announcements', 'insights',
                    'resources', 'knowledge'
                ]
            },
            'careers': {
                'url_patterns': [
                    r'/careers', r'/jobs', r'/join-us', r'/work-with-us', 
                    r'/opportunities', r'/positions', r'/hiring', r'/openings',
                    r'/jobs-board', r'/employment'
                ],
                'link_text': [
                    'careers', 'jobs', 'join us', 'work with us', 
                    'opportunities', 'hiring', 'openings', 'employment',
                    'job board', 'work here'
                ],
                'content_indicators': [
                    'join our team', 'career opportunities', 'job openings',
                    'work with us', 'we are hiring', 'employment'
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
            
            # Check URL patterns (highest weight)
            for pattern in keywords['url_patterns']:
                if re.search(pattern, url_lower):
                    score += 4
                    break
            
            # Check link text (medium weight)
            for text in keywords['link_text']:
                if text in link_text_lower:
                    score += 2
                    break
            
            # Check content indicators (lower weight)
            if content:
                for indicator in keywords['content_indicators']:
                    if indicator in content_lower:
                        score += 1
                        break
            
            if score >= 2:
                classifications.append(page_type)
        
        logger.debug(f"Classified URL {url} as: {classifications}")
        return classifications

def normalize_url(url: str, base_url: str) -> str:
    """Normalize and resolve URLs with better deduplication"""
    if not url:
        return ""
    
    url = url.split('#')[0].strip()
    
    if url.startswith('/'):
        normalized = urljoin(base_url, url)
    elif not url.startswith(('http://', 'https://')):
        normalized = urljoin(base_url, url)
    else:
        normalized = url
    
    # More aggressive trailing slash normalization
    # Always remove trailing slash except for root domain
    parsed = urlparse(normalized)
    if parsed.path and parsed.path != '/' and parsed.path.endswith('/'):
        normalized = normalized.rstrip('/')
    
    return normalized

def urls_are_equivalent(url1: str, url2: str) -> bool:
    """Check if two URLs are equivalent (same content)"""
    # Normalize both URLs
    parsed1 = urlparse(url1.rstrip('/'))
    parsed2 = urlparse(url2.rstrip('/'))
    
    # Same if domain and path are the same
    return (parsed1.netloc == parsed2.netloc and 
            parsed1.path.rstrip('/') == parsed2.path.rstrip('/'))

def deduplicate_urls(urls_with_context: List[Tuple[str, str]]) -> List[Tuple[str, str]]:
    """Remove duplicate URLs that point to the same content"""
    seen_urls = set()
    deduplicated = []
    
    for url, context in urls_with_context:
        # Create a canonical version for comparison
        parsed = urlparse(url.rstrip('/'))
        canonical = f"{parsed.netloc}{parsed.path.rstrip('/')}"
        
        if canonical not in seen_urls:
            seen_urls.add(canonical)
            # Use the cleaner URL (without trailing slash)
            clean_url = f"{parsed.scheme}://{parsed.netloc}{parsed.path.rstrip('/')}"
            if clean_url.endswith('://'):  # Handle edge case for root domain
                clean_url += parsed.netloc
            deduplicated.append((clean_url, context))
        else:
            logger.debug(f"Skipping duplicate URL: {url}")
    
    return deduplicated

def is_same_domain(url1: str, url2: str) -> bool:
    """Check if two URLs are from the same domain"""
    return urlparse(url1).netloc == urlparse(url2).netloc

def should_skip_url(url: str) -> bool:
    """Determine if a URL should be skipped"""
    url_lower = url.lower()
    
    skip_extensions = ('.pdf', '.doc', '.docx', '.xls', '.xlsx', '.zip', 
                      '.png', '.jpg', '.jpeg', '.gif', '.svg', '.ico',
                      '.css', '.js', '.xml', '.json', '.rss', '.txt')
    
    skip_paths = ('/login', '/signin', '/signup', '/register', '/cart', 
                 '/checkout', '/privacy', '/terms', '/cookie', '/legal',
                 '/wp-admin', '/admin', '/dashboard', '/account', '/user',
                 '/auth', '/oauth', '/api', '/download')
    
    skip_domains = ('facebook.com', 'twitter.com', 'linkedin.com', 
                   'instagram.com', 'youtube.com', 'google.com',
                   'github.com', 'medium.com', 'reddit.com')
    
    should_skip = (any(ext in url_lower for ext in skip_extensions) or
                   any(path in url_lower for path in skip_paths) or
                   any(domain in url_lower for domain in skip_domains))
    
    if should_skip:
        logger.debug(f"Skipping URL: {url}")
    
    return should_skip

def extract_links_with_context(soup: BeautifulSoup, base_url: str) -> List[Tuple[str, str]]:
    """Extract links with their anchor text context - enhanced for modern websites"""
    logger.debug("Extracting links with context")
    
    links_with_context = []
    seen_urls = set()
    
    # Method 1: Traditional <a> tags
    for link in soup.find_all('a', href=True):
        href = link.get('href', '').strip()
        if not href or href.startswith(('mailto:', 'tel:', 'javascript:')):
            continue
        
        normalized_url = normalize_url(href, base_url)
        if not normalized_url or should_skip_url(normalized_url):
            continue
        
        if normalized_url in seen_urls:
            continue
        
        base_domain = base_url.rstrip('/')
        if normalized_url in [base_domain, base_domain + '/', base_domain + '/index.html', base_domain + '/home']:
            continue
        
        seen_urls.add(normalized_url)
        
        link_text = link.get_text(strip=True)
        if not link_text or len(link_text) < 2 or link_text.lower() in ['home', 'here', 'click', 'more', '»', '›']:
            continue
        
        parent_text = ""
        parent = link.parent
        while parent and not parent_text and parent.name != 'body':
            parent_text = parent.get_text(strip=True)[:100]
            parent = parent.parent
        
        context = f"{link_text} {parent_text}".strip()
        links_with_context.append((normalized_url, context))
    
    # Method 2: Look for data attributes that might contain URLs (for SPAs)
    for element in soup.find_all(attrs={"data-href": True}):
        href = element.get('data-href', '').strip()
        if href:
            normalized_url = normalize_url(href, base_url)
            if normalized_url and not should_skip_url(normalized_url) and normalized_url not in seen_urls:
                seen_urls.add(normalized_url)
                text = element.get_text(strip=True)
                links_with_context.append((normalized_url, text))
    
    # Method 3: Common navigation patterns and text-based discovery
    common_pages = [
        ('about', ['about', 'about-us', 'about-company', 'our-story', 'company', 'who-we-are']),
        ('products', ['products', 'product', 'solutions', 'services', 'platform', 'features']),
        ('team', ['team', 'our-team', 'leadership', 'founders', 'people', 'management']),
        ('contact', ['contact', 'contact-us', 'get-in-touch', 'reach-us', 'support']),
        ('news', ['news', 'blog', 'press', 'media', 'updates', 'insights', 'resources']),
        ('careers', ['careers', 'jobs', 'join-us', 'work-with-us', 'opportunities'])
    ]
    
    # Method 4: Look for text that suggests navigation but might not be linked properly
    all_text = soup.get_text().lower()
    parsed_url = urlparse(base_url)
    domain = parsed_url.netloc
    
    for page_type, variations in common_pages:
        for variation in variations:
            # Check if the text appears on the page (suggesting the section exists)
            if variation in all_text:
                # Try common URL patterns
                potential_urls = [
                    f"{base_url}/{variation}",
                    f"{base_url}/{variation}/",
                    f"https://{domain}/{variation}",
                    f"https://www.{domain}/{variation}" if not domain.startswith('www.') else f"https://{domain[4:]}/{variation}"
                ]
                
                for potential_url in potential_urls:
                    if potential_url not in seen_urls and not should_skip_url(potential_url):
                        seen_urls.add(potential_url)
                        links_with_context.append((potential_url, f"{variation} (discovered from content)"))
                        logger.debug(f"Discovered potential page: {potential_url}")
                        break  # Only add one variation per page type
    
    # Method 5: Look for navigation menus and buttons that might not be proper links
    nav_selectors = [
        'nav', '.nav', '.navigation', '.navbar', '.menu', 
        '[role="navigation"]', '.header-nav', '.main-nav'
    ]
    
    for selector in nav_selectors:
        try:
            nav_elements = soup.select(selector)
            for nav in nav_elements:
                # Look for clickable elements within navigation
                for element in nav.find_all(['button', 'div', 'span', 'li']):
                    text = element.get_text(strip=True).lower()
                    if text and len(text) > 2:
                        for page_type, variations in common_pages:
                            if text in variations:
                                potential_url = f"{base_url}/{text}"
                                if potential_url not in seen_urls and not should_skip_url(potential_url):
                                    seen_urls.add(potential_url)
                                    links_with_context.append((potential_url, f"{text} (from navigation)"))
                                    logger.debug(f"Discovered nav page: {potential_url}")
        except Exception as e:
            logger.warning(f"Error processing nav selector {selector}: {str(e)}")
            continue
    
    logger.debug(f"Found {len(links_with_context)} valid internal links")
    return links_with_context

def extract_contact_info(soup, text):
    """Extract contact information from the page"""
    logger.debug("Extracting contact information")
    contact_info = {}
    
    try:
        # Email extraction
        email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        emails = re.findall(email_pattern, text)
        if emails:
            valid_emails = [email for email in emails if not any(skip in email.lower() 
                           for skip in ['@example.com', '@domain.com', '@yoursite.com', '@test.com'])]
            if valid_emails:
                contact_info['emails'] = list(set(valid_emails))[:5]
                logger.debug(f"Found {len(contact_info['emails'])} valid emails")
    except Exception as e:
        logger.warning(f"Error extracting emails: {str(e)}")
    
    try:
        # Phone extraction
        phone_patterns = [
            r'(\+?1?[-.\s]?\(?[0-9]{3}\)?[-.\s]?[0-9]{3}[-.\s]?[0-9]{4})',
            r'(\+?[0-9]{1,3}[-.\s]?[0-9]{1,4}[-.\s]?[0-9]{1,4}[-.\s]?[0-9]{1,9})'
        ]
        
        phones = []
        for pattern in phone_patterns:
            phones.extend(re.findall(pattern, text))
        
        if phones:
            contact_info['phones'] = list(set(phones))[:3]
            logger.debug(f"Found {len(contact_info['phones'])} phone numbers")
    except Exception as e:
        logger.warning(f"Error extracting phones: {str(e)}")
    
    try:
        # Address extraction
        address_patterns = [
            r'(?i)address[:\s]+([^.]*(?:street|st|avenue|ave|road|rd|drive|dr|boulevard|blvd|lane|ln)[^.]*)',
            r'([0-9]+\s+[A-Za-z\s]+(?:street|st|avenue|ave|road|rd|drive|dr|boulevard|blvd|lane|ln)[^.]*)'
        ]
        
        addresses = []
        for pattern in address_patterns:
            matches = re.findall(pattern, text)
            addresses.extend(matches)
        
        if addresses:
            contact_info['addresses'] = list(set(addresses))[:3]
            logger.debug(f"Found {len(contact_info['addresses'])} addresses")
    except Exception as e:
        logger.warning(f"Error extracting addresses: {str(e)}")
    
    return contact_info

def extract_team_info(soup):
    """Extract team information from the page"""
    logger.debug("Extracting team information")
    team_info = []
    
    try:
        team_selectors = [
            {'class': re.compile(r'team|member|founder|leadership|staff|employee', re.I)},
            {'id': re.compile(r'team|member|founder|leadership|staff', re.I)}
        ]
        
        team_sections = []
        for selector in team_selectors:
            try:
                team_sections.extend(soup.find_all(['div', 'section', 'article'], selector))
            except Exception as e:
                logger.warning(f"Error with team selector: {str(e)}")
                continue
        
        logger.debug(f"Found {len(team_sections)} potential team sections")
        
        for section in team_sections:
            try:
                names = section.find_all(['h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'strong', 'b'])
                for name_elem in names:
                    name_text = name_elem.get_text().strip()
                    
                    if (2 <= len(name_text.split()) <= 4 and 
                        len(name_text) < 50 and 
                        not any(skip in name_text.lower() for skip in ['team', 'leadership', 'about', 'contact'])):
                        
                        title = ""
                        
                        for sibling in name_elem.find_next_siblings(['p', 'div', 'span', 'h6'])[:3]:
                            sibling_text = sibling.get_text().strip()
                            if sibling_text and len(sibling_text) < 100:
                                title = sibling_text
                                break
                        
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
            except Exception as e:
                logger.warning(f"Error processing team section: {str(e)}")
                continue
        
        # Remove duplicates
        seen_names = set()
        unique_team_info = []
        for member in team_info:
            if member['name'] not in seen_names:
                seen_names.add(member['name'])
                unique_team_info.append(member)
        
        logger.debug(f"Extracted {len(unique_team_info)} unique team members")
        return unique_team_info[:10]
        
    except Exception as e:
        logger.warning(f"Error extracting team info: {str(e)}")
        return []

def extract_products_services(soup):
    """Extract products and services information"""
    logger.debug("Extracting products and services")
    products_services = []
    
    try:
        product_selectors = [
            {'class': re.compile(r'product|service|offering|solution|feature', re.I)},
            {'id': re.compile(r'product|service|offering|solution', re.I)}
        ]
        
        sections = []
        for selector in product_selectors:
            try:
                sections.extend(soup.find_all(['div', 'section', 'article'], selector))
            except Exception as e:
                logger.warning(f"Error with product selector: {str(e)}")
                continue
        
        logger.debug(f"Found {len(sections)} potential product/service sections")
        
        for section in sections:
            try:
                title_elem = section.find(['h1', 'h2', 'h3', 'h4', 'h5', 'h6'])
                if title_elem:
                    title = title_elem.get_text().strip()
                    
                    description = ""
                    desc_elem = section.find(['p', 'div'])
                    if desc_elem:
                        description = desc_elem.get_text().strip()
                    
                    if title and len(title) > 3:
                        product_info = {
                            'title': title[:200],
                            'description': description[:1000]
                        }
                        products_services.append(product_info)
            except Exception as e:
                logger.warning(f"Error processing product section: {str(e)}")
                continue
        
        logger.debug(f"Extracted {len(products_services)} products/services")
        return products_services[:10]
        
    except Exception as e:
        logger.warning(f"Error extracting products/services: {str(e)}")
        return []

def extract_news_posts(soup):
    """Extract news/blog posts"""
    logger.debug("Extracting news/blog posts")
    news_data = []
    
    try:
        news_selectors = [
            {'class': re.compile(r'news|blog|post|article|press|update', re.I)},
            {'id': re.compile(r'news|blog|post|article|press', re.I)}
        ]
        
        sections = []
        for selector in news_selectors:
            try:
                sections.extend(soup.find_all(['div', 'article', 'section'], selector))
            except Exception as e:
                logger.warning(f"Error with news selector: {str(e)}")
                continue
        
        logger.debug(f"Found {len(sections)} potential news sections")
        
        for section in sections:
            try:
                title_elem = section.find(['h1', 'h2', 'h3', 'h4', 'h5', 'h6'])
                if title_elem:
                    title = title_elem.get_text().strip()
                    
                    date = ""
                    date_patterns = [
                        {'class': re.compile(r'date|time|published', re.I)},
                        {'datetime': True}
                    ]
                    
                    for pattern in date_patterns:
                        try:
                            date_elem = section.find(['time', 'span', 'div'], pattern)
                            if date_elem:
                                date = date_elem.get_text().strip()
                                break
                        except Exception:
                            continue
                    
                    content = ""
                    try:
                        content_elem = section.find(['p', 'div'])
                        if content_elem:
                            content = content_elem.get_text().strip()
                    except Exception:
                        pass
                    
                    if title and len(title) > 5:
                        news_data.append({
                            'title': title[:300],
                            'date': date[:50],
                            'content': content[:800]
                        })
            except Exception as e:
                logger.warning(f"Error processing news section: {str(e)}")
                continue
        
        logger.debug(f"Extracted {len(news_data)} news items")
        return news_data[:10]
        
    except Exception as e:
        logger.warning(f"Error extracting news posts: {str(e)}")
        return []

def extract_company_name(soup: BeautifulSoup, url: str) -> str:
    """Extract company name with better fallbacks and logging"""
    logger.debug("Extracting company name")
    
    marketing_keywords = [
        'get', 'start', 'try', 'buy', 'learn', 'discover', 'create', 'build', 
        'best', 'top', 'leading', 'ultimate', 'perfect', 'easy', 'simple',
        'that', 'which', 'for your', 'solution', 'platform', 'software'
    ]
    
    def looks_like_marketing(text: str) -> bool:
        if not text or len(text) > 60:
            return True
        text_lower = text.lower()
        marketing_count = sum(1 for keyword in marketing_keywords if keyword in text_lower)
        return marketing_count >= 2
    
    def extract_from_domain(url: str) -> str:
        parsed_url = urlparse(url)
        domain = parsed_url.netloc
        if domain.startswith('www.'):
            domain = domain[4:]
        domain_name = domain.split('.')[0]
        company_name = domain_name.replace('-', ' ').replace('_', ' ')
        return ' '.join(word.capitalize() for word in company_name.split())
    
    candidates = []
    
    # Try multiple sources
    try:
        if soup.title:
            title = soup.title.string.strip()
            logger.debug(f"Found page title: {title}")
            
            for separator in ['|', '-', '–', ':', '•']:
                if separator in title:
                    parts = [part.strip() for part in title.split(separator)]
                    for part in parts:
                        if part and not looks_like_marketing(part):
                            candidates.append(part)
                            logger.debug(f"Added title candidate: {part}")
                    break
            if not candidates and not looks_like_marketing(title):
                candidates.append(title)
                logger.debug(f"Added full title as candidate: {title}")
    except Exception as e:
        logger.warning(f"Error extracting from title: {str(e)}")
    
    try:
        og_site_name = soup.find('meta', property='og:site_name')
        if og_site_name and og_site_name.get('content'):
            site_name = og_site_name['content'].strip()
            logger.debug(f"Found OG site name: {site_name}")
            if not looks_like_marketing(site_name):
                candidates.append(site_name)
                logger.debug(f"Added OG site name as candidate: {site_name}")
    except Exception as e:
        logger.warning(f"Error extracting OG site name: {str(e)}")
    
    final_name = candidates[0] if candidates else extract_from_domain(url)
    logger.info(f"Extracted company name: {final_name}")
    return final_name

def extract_description(soup: BeautifulSoup) -> str:
    """Extract site description with logging"""
    logger.debug("Extracting site description")
    
    try:
        meta_desc = soup.find('meta', {'name': 'description'})
        if meta_desc and meta_desc.get('content'):
            desc = meta_desc['content'].strip()
            logger.debug(f"Found meta description: {desc[:100]}...")
            return desc
    except Exception as e:
        logger.warning(f"Error extracting meta description: {str(e)}")
    
    try:
        og_desc = soup.find('meta', property='og:description')
        if og_desc and og_desc.get('content'):
            desc = og_desc['content'].strip()
            logger.debug(f"Found OG description: {desc[:100]}...")
            return desc
    except Exception as e:
        logger.warning(f"Error extracting OG description: {str(e)}")
    
    try:
        first_p = soup.find('p')
        if first_p:
            text = first_p.get_text().strip()
            if len(text) > 50:
                desc = text[:300]
                logger.debug(f"Found first paragraph description: {desc[:100]}...")
                return desc
    except Exception as e:
        logger.warning(f"Error extracting first paragraph: {str(e)}")
    
    logger.debug("No description found")
    return ""

def extract_social_links(soup: BeautifulSoup) -> Dict[str, str]:
    """Extract social media links with logging"""
    logger.debug("Extracting social media links")
    social_links = {}
    
    try:
        social_platforms = {
            'twitter': ['twitter.com', 'x.com'],
            'linkedin': ['linkedin.com'],
            'facebook': ['facebook.com'],
            'instagram': ['instagram.com'],
            'github': ['github.com'],
            'youtube': ['youtube.com']
        }
        
        for link in soup.find_all('a', href=True):
            try:
                href = link['href'].lower()
                for platform, domains in social_platforms.items():
                    if any(domain in href for domain in domains):
                        if href.startswith('//'):
                            href = 'https:' + href
                        elif not href.startswith('http'):
                            continue
                        social_links[platform] = href
                        logger.debug(f"Found {platform} link: {href}")
                        break
            except Exception as e:
                logger.warning(f"Error processing social link: {str(e)}")
                continue
    except Exception as e:
        logger.warning(f"Error extracting social links: {str(e)}")
    
    logger.debug(f"Found {len(social_links)} social media links")
    return social_links

def clean_text(text):
    """Clean and normalize text content with logging"""
    if not text:
        return ""
    
    original_length = len(text)
    
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
    
    final_length = len(text)
    if original_length != final_length:
        logger.debug(f"Text cleaning: {original_length} -> {final_length} characters")
    
    return text.strip()

async def scrape_website(url: str, max_pages: int = 5) -> ScrapedData:
    """
    Enhanced website scraping with smart page discovery and classification.
    Continues scraping even if individual sections encounter errors.
    
    Args:
        url (str): The URL of the startup's website to scrape
        max_pages (int, optional): Maximum number of pages to scrape. Defaults to 5.
        
    Returns:
        ScrapedData: Structured data extracted from the website
    """
    logger.info(f"Starting enhanced scraping of {url} with max_pages: {max_pages}")
    
    text_extractor = EnhancedTextExtractor()
    classifier = SmartPageClassifier()
    pages_scraped = []
    all_discovered_links = set()
    classified_pages = defaultdict(list)
    pages_to_scrape = deque([(url, "")])
    
    # Initialize session with better configuration
    session = requests.Session()
    session.headers.update({
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
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
        logger.info("Step 1: Scraping main page...")
        try:
            logger.debug(f"Fetching URL: {url}")
            response = session.get(url, timeout=20)
            response.raise_for_status()
            logger.debug(f"Successfully fetched main page, status: {response.status_code}")
            
            main_soup = BeautifulSoup(response.text, 'html.parser')
            logger.debug("Successfully parsed HTML with BeautifulSoup")
            
            # Remove noise elements and extract clean text
            cleaned_soup = text_extractor.remove_noise_elements(main_soup)
            main_text = text_extractor.extract_main_content(cleaned_soup)
            
        except requests.RequestException as e:
            error_msg = f"Failed to fetch website {url}: {str(e)}"
            logger.error(error_msg)
            return ScrapedData(
                company_name=urlparse(url).netloc,
                description=f"Error fetching website: {str(e)}",
                raw_text=""
            )
        except Exception as e:
            error_msg = f"Error parsing website {url}: {str(e)}"
            logger.error(error_msg)
            return ScrapedData(
                company_name=urlparse(url).netloc,
                description=f"Error parsing website: {str(e)}",
                raw_text=""
            )
        
        # Extract basic company info from main page
        logger.info("Step 2: Extracting basic company information...")
        try:
            company_name = extract_company_name(main_soup, url)
        except Exception as e:
            logger.warning(f"Error extracting company name: {str(e)}")
            company_name = urlparse(url).netloc
        
        try:
            description = extract_description(main_soup)
        except Exception as e:
            logger.warning(f"Error extracting description: {str(e)}")
            description = ""
        
        try:
            social_links = extract_social_links(main_soup)
        except Exception as e:
            logger.warning(f"Error extracting social links: {str(e)}")
            social_links = {}
        
        # Initialize combined text with main page
        all_text = f"--- MAIN PAGE ---\n{main_text}"
        logger.debug(f"Main page text length: {len(main_text)} characters")
        
        pages_scraped.append({
            'url': url,
            'type': 'main',
            'title': main_soup.title.string if main_soup.title else 'Main Page',
            'word_count': len(main_text.split())
        })
        
        # Step 3: Discover all internal links from main page
        logger.info("Step 3: Discovering internal links...")
        base_url = f"{urlparse(url).scheme}://{urlparse(url).netloc}"
        links_with_context = extract_links_with_context(main_soup, base_url)
        
        # Deduplicate URLs before processing
        links_with_context = deduplicate_urls(links_with_context)
        logger.debug(f"After deduplication: {len(links_with_context)} unique links")
        
        # Step 4: Classify discovered links and verify they exist
        logger.info("Step 4: Classifying and verifying discovered links...")
        unique_links = {}
        verified_links = []
        scraped_urls = set()  # Track URLs we've already scraped
        
        for link_url, context in links_with_context:
            if is_same_domain(link_url, url) and link_url != url:
                if link_url not in unique_links:
                    unique_links[link_url] = context
                    
                    # Verify the URL exists before adding to discovered links
                    try:
                        # Quick HEAD request to check if URL exists
                        head_response = session.head(link_url, timeout=5, allow_redirects=True)
                        if head_response.status_code < 400:
                            all_discovered_links.add((link_url, context))
                            verified_links.append((link_url, context))
                            logger.debug(f"Verified URL exists: {link_url}")
                        else:
                            logger.debug(f"URL returned {head_response.status_code}: {link_url}")
                    except Exception as e:
                        # If HEAD fails, try GET as some servers don't support HEAD
                        try:
                            get_response = session.get(link_url, timeout=5, allow_redirects=True)
                            if get_response.status_code < 400:
                                all_discovered_links.add((link_url, context))
                                verified_links.append((link_url, context))
                                logger.debug(f"Verified URL exists (GET): {link_url}")
                            else:
                                logger.debug(f"URL not accessible: {link_url} - {str(e)}")
                        except Exception as e2:
                            logger.debug(f"URL verification failed: {link_url} - {str(e2)}")
                            continue
        
        # Classify verified links with deduplication
        for link_url, context in verified_links:
            classifications = classifier.classify_page(link_url, context)
            for classification in classifications:
                # Only add if we haven't already classified this URL for this type
                existing_urls = [existing_url for existing_url, _ in classified_pages[classification]]
                if not any(urls_are_equivalent(link_url, existing_url) for existing_url in existing_urls):
                    classified_pages[classification].append((link_url, context))
        
        logger.info(f"Discovered {len(all_discovered_links)} verified internal links")
        logger.info(f"Classified pages: {dict(classified_pages)}")
        
        # If we didn't find many pages, try some additional discovery methods
        if len(all_discovered_links) < 3:
            logger.info("Few pages discovered, trying additional discovery methods...")
            
            # Method: Check common page patterns directly
            common_paths = [
                'about', 'about-us', 'company', 'our-story', 'who-we-are',
                'products', 'product', 'services', 'solutions', 'platform', 'features',
                'team', 'our-team', 'leadership', 'founders', 'people',
                'contact', 'contact-us', 'get-in-touch', 'support',
                'news', 'blog', 'press', 'media', 'updates', 'insights'
            ]
            
            additional_found = 0
            for path in common_paths:
                test_url = f"{base_url}/{path}"
                
                # Check if we already have an equivalent URL
                if any(urls_are_equivalent(test_url, existing_url) for existing_url, _ in all_discovered_links):
                    continue
                
                try:
                    test_response = session.head(test_url, timeout=3, allow_redirects=True)
                    if test_response.status_code < 400:
                        all_discovered_links.add((test_url, f"{path} (direct discovery)"))
                        classifications = classifier.classify_page(test_url, path)
                        for classification in classifications:
                            # Check for equivalent URLs in this classification
                            existing_urls = [existing_url for existing_url, _ in classified_pages[classification]]
                            if not any(urls_are_equivalent(test_url, existing_url) for existing_url in existing_urls):
                                classified_pages[classification].append((test_url, f"{path} (direct discovery)"))
                        additional_found += 1
                        logger.debug(f"Direct discovery found: {test_url}")
                        
                        if additional_found >= 5:  # Limit additional discoveries
                            break
                except Exception:
                    continue
            
            if additional_found > 0:
                logger.info(f"Additional discovery found {additional_found} more pages")
        
        
        # Step 5: Prioritize pages to scrape based on classification and max_pages
        logger.info("Step 5: Prioritizing pages to scrape...")
        priority_pages = []
        
        # Define key page types in order of importance
        key_page_types = ['about', 'team', 'products', 'contact', 'news']
        
        # First, add one page from each key type if available
        for page_type in key_page_types:
            if page_type in classified_pages and classified_pages[page_type]:
                link_url, context = classified_pages[page_type][0]
                if len(priority_pages) < max_pages - 1:  # -1 for main page
                    priority_pages.append((link_url, context, page_type))
                    logger.debug(f"Added {page_type} page to priority: {link_url}")
        
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
            logger.debug(f"Added {len(remaining_classified[:remaining_slots])} additional pages")
        
        # Step 6: Scrape prioritized pages with deduplication
        logger.info(f"Step 6: Scraping {len(priority_pages)} prioritized pages...")
        scraped_data_parts = {
            'about_page': None,
            'contact_info': {},
            'team_info': [],
            'products_services': [],
            'news_data': []
        }
        
        scraped_urls = set()  # Track URLs we've actually scraped content from
        
        for i, (page_url, context, page_type) in enumerate(priority_pages, 1):
            try:
                # Skip if we've already scraped an equivalent URL
                if any(urls_are_equivalent(page_url, scraped_url) for scraped_url in scraped_urls):
                    logger.debug(f"Skipping duplicate URL: {page_url}")
                    continue
                
                if page_url == url:  # Skip if same as main page
                    continue
                
                logger.info(f"Scraping page {i}/{len(priority_pages)}: {page_url} ({page_type})")
                
                # Add delay to be respectful
                if i > 0:
                    time.sleep(1)
                
                page_response = session.get(page_url, timeout=15)
                page_response.raise_for_status()
                logger.debug(f"Successfully fetched {page_url}, status: {page_response.status_code}")
                
                # Verify content type
                content_type = page_response.headers.get('content-type', '')
                if not any(ct in content_type.lower() for ct in ['text/html', 'application/xhtml']):
                    logger.warning(f"Skipping {page_url}: Invalid content type {content_type}")
                    continue
                
                page_soup = BeautifulSoup(page_response.text, 'html.parser')
                
                # Clean and extract text
                try:
                    cleaned_page_soup = text_extractor.remove_noise_elements(page_soup)
                    cleaned_page_text = text_extractor.extract_main_content(cleaned_page_soup)
                    logger.debug(f"Extracted {len(cleaned_page_text)} characters from {page_type} page")
                    
                    # Add to combined text only if we haven't scraped this URL before
                    all_text += f"\n\n--- {page_type.upper()} PAGE: {page_url} ---\n{cleaned_page_text}"
                    scraped_urls.add(page_url)  # Mark this URL as scraped
                    
                except Exception as e:
                    logger.warning(f"Error cleaning text for {page_url}: {str(e)}")
                    # Fallback to basic text extraction
                    try:
                        fallback_text = page_soup.get_text(separator='\n', strip=True)
                        cleaned_page_text = clean_text(fallback_text)
                        all_text += f"\n\n--- {page_type.upper()} PAGE: {page_url} ---\n{cleaned_page_text}"
                        scraped_urls.add(page_url)  # Mark this URL as scraped
                        logger.debug(f"Used fallback text extraction for {page_url}")
                    except Exception:
                        logger.error(f"Failed to extract any text from {page_url}")
                        continue
                
                # Extract specific information based on page type
                if page_type == 'about' and scraped_data_parts['about_page'] is None:
                    try:
                        scraped_data_parts['about_page'] = cleaned_page_text
                        logger.debug("Successfully extracted about page content")
                    except Exception as e:
                        logger.warning(f"Error extracting about page: {str(e)}")
                
                elif page_type == 'contact':
                    try:
                        contact_info = extract_contact_info(page_soup, cleaned_page_text)
                        if contact_info:
                            # Merge contact info, handling list concatenation
                            for key, value in contact_info.items():
                                if key in scraped_data_parts['contact_info']:
                                    # Extend existing lists and remove duplicates
                                    scraped_data_parts['contact_info'][key].extend(value)
                                    scraped_data_parts['contact_info'][key] = list(dict.fromkeys(
                                        scraped_data_parts['contact_info'][key]))
                                else:
                                    scraped_data_parts['contact_info'][key] = value
                            logger.debug(f"Successfully extracted contact info: {list(contact_info.keys())}")
                    except Exception as e:
                        logger.warning(f"Error extracting contact info: {str(e)}")
                
                elif page_type == 'team':
                    try:
                        team_info = extract_team_info(page_soup)
                        if team_info:
                            # Add team members, avoiding duplicates by name
                            existing_names = {member['name'] for member in scraped_data_parts['team_info']}
                            new_members = [member for member in team_info if member['name'] not in existing_names]
                            scraped_data_parts['team_info'].extend(new_members)
                            logger.debug(f"Successfully extracted {len(new_members)} new team members")
                    except Exception as e:
                        logger.warning(f"Error extracting team info: {str(e)}")
                
                elif page_type == 'products':
                    try:
                        products = extract_products_services(page_soup)
                        if products:
                            # Add products, avoiding duplicates by title
                            existing_titles = {product['title'] for product in scraped_data_parts['products_services']}
                            new_products = [product for product in products if product['title'] not in existing_titles]
                            scraped_data_parts['products_services'].extend(new_products)
                            logger.debug(f"Successfully extracted {len(new_products)} new products/services")
                    except Exception as e:
                        logger.warning(f"Error extracting products/services: {str(e)}")
                
                elif page_type == 'news':
                    try:
                        news = extract_news_posts(page_soup)
                        if news:
                            # Add news items, avoiding duplicates by title
                            existing_titles = {item['title'] for item in scraped_data_parts['news_data']}
                            new_news = [item for item in news if item['title'] not in existing_titles]
                            scraped_data_parts['news_data'].extend(new_news)
                            logger.debug(f"Successfully extracted {len(new_news)} new news items")
                    except Exception as e:
                        logger.warning(f"Error extracting news data: {str(e)}")
                
                # Track scraped page (only for unique URLs)
                pages_scraped.append({
                    'url': page_url,
                    'type': page_type,
                    'title': page_soup.title.string if page_soup.title else f'{page_type.title()} Page',
                    'word_count': len(cleaned_page_text.split()) if 'cleaned_page_text' in locals() else 0
                })
                
            except Exception as e:
                logger.warning(f"Error scraping {page_url}: {str(e)}")
                continue
        
        # Step 7: Create final ScrapedData object
        logger.info("Step 7: Creating final scraped data object...")
        
        # Remove duplicates from team info
        if scraped_data_parts['team_info']:
            seen_names = set()
            unique_team = []
            for member in scraped_data_parts['team_info']:
                if member['name'] not in seen_names:
                    seen_names.add(member['name'])
                    unique_team.append(member)
            scraped_data_parts['team_info'] = unique_team
        
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
        
        logger.info(f"Scraping completed successfully!")
        logger.info(f"- Scraped {len(pages_scraped)} pages out of {len(all_discovered_links)} discovered")
        logger.info(f"- Total text length: {len(all_text)} characters")
        logger.info(f"- Company: {company_name}")
        logger.info(f"- Team members found: {len(scraped_data_parts['team_info']) if scraped_data_parts['team_info'] else 0}")
        logger.info(f"- Products/services found: {len(scraped_data_parts['products_services']) if scraped_data_parts['products_services'] else 0}")
        logger.info(f"- Contact info types: {list(scraped_data_parts['contact_info'].keys()) if scraped_data_parts['contact_info'] else []}")
        
        return scraped_data
        
    except Exception as e:
        error_msg = f"Error during website scraping: {str(e)}"
        logger.error(error_msg)
        raise Exception(f"Failed to scrape website: {str(e)}")
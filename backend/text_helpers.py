import re

def extract_section(text, section_name, next_section=None):
    """Extract a section from text between section_name and next_section"""
    # Escape special regex characters in section names
    section_name_escaped = re.escape(section_name)
    next_section_escaped = re.escape(next_section) if next_section else None
    
    # Create pattern to match the section
    if next_section:
        pattern = rf"{section_name_escaped}.*?\n(.*?)(?={next_section_escaped}|$)"
    else:
        pattern = rf"{section_name_escaped}.*?\n(.*?)$"
    
    match = re.search(pattern, text, re.DOTALL)
    if match:
        return match.group(1).strip()
    return ""

def extract_list_items(text, section_name, next_section=None):
    """Extract list items from a section"""
    section_text = extract_section(text, section_name, next_section)
    if not section_text:
        return []
    
    # Look for bullet points or numbered lists
    items = re.findall(r'[-*•]\\s*(.+?)(?=\\n[-*•]|$)', section_text, re.DOTALL)
    if not items:
        # Try numbered lists
        items = re.findall(r'\\d+\\.\\s*(.+?)(?=\\n\\d+\\.|$)', section_text, re.DOTALL)
    if not items:
        # If no list format is found, just return the whole section as one item
        return [section_text.strip()]
    
    return [item.strip() for item in items]

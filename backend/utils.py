"""Utility functions and classes for VC Copilot"""

import json
from datetime import datetime
from urllib.parse import urlparse

class DateTimeEncoder(json.JSONEncoder):
    """JSON encoder that handles datetime objects"""
    def default(self, obj):
        if isinstance(obj, datetime):
            return obj.isoformat()
        return super().default(obj)

def extract_company_name(url: str) -> str:
    """Extract company name from URL"""
    domain = urlparse(url).netloc
    return domain.split('.')[0].capitalize()

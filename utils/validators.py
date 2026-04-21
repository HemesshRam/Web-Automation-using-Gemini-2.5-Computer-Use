"""
Input Validators
Validate user inputs and data
"""

import re
from typing import Tuple
from urllib.parse import urlparse


def validate_url(url: str) -> Tuple[bool, str]:
    """Validate URL format"""
    url_pattern = re.compile(
        r'^https?://'
        r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+[A-Z]{2,6}\.?|'
        r'localhost|'
        r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'
        r'(?::\d+)?'
        r'(?:/?|[/?]\S+)$', re.IGNORECASE)
    
    if url_pattern.match(url):
        return True, "Valid URL"
    else:
        return False, "Invalid URL format"


def validate_email(email: str) -> Tuple[bool, str]:
    """Validate email format"""
    email_pattern = re.compile(
        r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    )
    
    if email_pattern.match(email):
        return True, "Valid email"
    else:
        return False, "Invalid email format"


def validate_phone(phone: str) -> Tuple[bool, str]:
    """Validate phone number"""
    phone_pattern = re.compile(r'^\d{10,15}$')
    
    if phone_pattern.match(phone.replace('-', '').replace(' ', '')):
        return True, "Valid phone number"
    else:
        return False, "Invalid phone number format"


def validate_selector(selector: str) -> Tuple[bool, str]:
    """Validate CSS/XPath selector"""
    if not selector or len(selector.strip()) == 0:
        return False, "Selector cannot be empty"
    
    return True, "Valid selector"
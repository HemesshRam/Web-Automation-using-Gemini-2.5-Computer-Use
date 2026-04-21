"""
Helper Functions
Utility functions for common tasks
"""

import random
import string
import re
from typing import List
from datetime import datetime, timedelta


def generate_random_email() -> str:
    """Generate random email"""
    username = ''.join(random.choices(string.ascii_lowercase + string.digits, k=10))
    domain = random.choice(['gmail.com', 'yahoo.com', 'outlook.com', 'test.com'])
    return f"{username}@{domain}"


def generate_random_phone() -> str:
    """Generate random phone number"""
    return ''.join(random.choices(string.digits, k=10))


def generate_random_name() -> tuple:
    """Generate random first and last name"""
    first_names = ['John', 'Jane', 'Michael', 'Sarah', 'David', 'Emily', 'James', 'Jessica']
    last_names = ['Smith', 'Johnson', 'Williams', 'Brown', 'Jones', 'Garcia', 'Miller', 'Davis']
    
    return random.choice(first_names), random.choice(last_names)


def generate_random_address() -> str:
    """Generate random address"""
    street_num = random.randint(1, 999)
    street_names = ['Main', 'Oak', 'Elm', 'Pine', 'Maple', 'Broadway', 'Park']
    city_names = ['Springfield', 'Shelbyville', 'Capital City', 'Sunnyville']
    
    street = random.choice(street_names)
    city = random.choice(city_names)
    state = random.choice(['CA', 'NY', 'TX', 'FL', 'IL', 'PA'])
    zipcode = random.randint(10000, 99999)
    
    return f"{street_num} {street} Street, {city}, {state} {zipcode}"


def generate_random_dob() -> str:
    """Generate random date of birth"""
    year = random.randint(1950, 2005)
    month = random.randint(1, 12)
    day = random.randint(1, 28)
    
    return f"{month:02d}/{day:02d}/{year}"


def format_date(date_obj: datetime, format_str: str = "%Y-%m-%d") -> str:
    """Format datetime object"""
    return date_obj.strftime(format_str)


def get_random_delay(min_val: float = 1.0, max_val: float = 5.0) -> float:
    """Get random delay"""
    return random.uniform(min_val, max_val)
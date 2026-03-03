import re

def validate_email(email):
    if not email:
        return False
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None

def validate_password(password):
    return password and len(password) >= 8

def validate_rating(rating):
    return isinstance(rating, int) and 1 <= rating <= 5

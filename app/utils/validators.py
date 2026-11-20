import re
from datetime import datetime

EMAIL_REGEX = r"^[\w\.-]+@[\w\.-]+\.\w+$"

def validate_email_format(email: str) -> bool:
    if not email or len(email) > 160:
        return False
    return bool(re.match(EMAIL_REGEX, email.strip()))

def validate_password_strength(password: str) -> tuple[bool, str]:
    if not password or len(password) < 6:
        return False, "Password must be at least 6 characters long."
    return True, ""

def validate_marks_entry(obtained: float, maximum: float) -> tuple[bool, str]:
    try:
        obt = float(obtained)
        max_m = float(maximum)
    except (ValueError, TypeError):
        return False, "Marks must be numeric values."
    
    if max_m <= 0:
        return False, "Maximum marks must be greater than zero."
    if obt < 0:
        return False, "Marks obtained cannot be negative."
    if obt > max_m:
        return False, f"Marks obtained ({obt}) cannot exceed maximum marks ({max_m})."
    
    return True, ""

def validate_roll_number(roll_no: str) -> bool:
    if not roll_no or len(roll_no.strip()) < 2 or len(roll_no) > 40:
        return False
    return True

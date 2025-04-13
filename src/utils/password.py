import bcrypt
import re
from typing import Tuple, Optional
from src.config.security import security_settings

def hash_password(password: str) -> str:
    """Hash a password using bcrypt"""
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')

def verify_password(password: str, hashed_password: str) -> bool:
    """Verify a password against its hash"""
    return bcrypt.checkpw(password.encode('utf-8'), hashed_password.encode('utf-8'))

def validate_password_strength(password: str) -> Tuple[bool, Optional[str]]:
    """Validate password strength according to security settings"""
    if len(password) < security_settings.PASSWORD_MIN_LENGTH:
        return False, f"Password must be at least {security_settings.PASSWORD_MIN_LENGTH} characters long"
    
    if security_settings.PASSWORD_REQUIRE_UPPER and not re.search(r'[A-Z]', password):
        return False, "Password must contain at least one uppercase letter"
    
    if security_settings.PASSWORD_REQUIRE_LOWER and not re.search(r'[a-z]', password):
        return False, "Password must contain at least one lowercase letter"
    
    if security_settings.PASSWORD_REQUIRE_NUMBERS and not re.search(r'[0-9]', password):
        return False, "Password must contain at least one number"
    
    if security_settings.PASSWORD_REQUIRE_SPECIAL and not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
        return False, "Password must contain at least one special character"
    
    return True, None

def generate_password_reset_token() -> str:
    """Generate a secure password reset token"""
    import secrets
    return secrets.token_urlsafe(32)

def is_common_password(password: str) -> bool:
    """Check if the password is in a list of common passwords"""
    # This is a simplified version - in production, you would use a more comprehensive list
    common_passwords = [
        "password", "123456", "qwerty", "admin", "letmein", 
        "welcome", "monkey", "dragon", "baseball", "football"
    ]
    return password.lower() in common_passwords 
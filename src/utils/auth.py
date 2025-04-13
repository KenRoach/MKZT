from datetime import datetime, timedelta
from typing import Optional, Dict, Any
import jwt
from fastapi import HTTPException, status, Depends
from fastapi.security import OAuth2PasswordBearer
from src.config.security import security_settings
from src.utils.supabase_client import supabase

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

def create_access_token(data: Dict[str, Any], expires_delta: Optional[timedelta] = None) -> str:
    """Create a JWT access token"""
    to_encode = data.copy()
    
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=security_settings.JWT_EXPIRATION_MINUTES)
    
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(
        to_encode, 
        security_settings.JWT_SECRET.get_secret_value(), 
        algorithm=security_settings.JWT_ALGORITHM
    )
    
    return encoded_jwt

def verify_token(token: str) -> Dict[str, Any]:
    """Verify a JWT token"""
    try:
        payload = jwt.decode(
            token, 
            security_settings.JWT_SECRET.get_secret_value(), 
            algorithms=[security_settings.JWT_ALGORITHM]
        )
        return payload
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has expired",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except jwt.JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

def create_refresh_token(data: Dict[str, Any]) -> str:
    """Create a refresh token with longer expiration"""
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(days=30)  # 30 days
    to_encode.update({"exp": expire, "refresh": True})
    encoded_jwt = jwt.encode(
        to_encode, 
        security_settings.JWT_SECRET.get_secret_value(), 
        algorithm=security_settings.JWT_ALGORITHM
    )
    return encoded_jwt

def is_token_expired(token: str) -> bool:
    """Check if a token is expired without raising an exception"""
    try:
        jwt.decode(
            token, 
            security_settings.JWT_SECRET.get_secret_value(), 
            algorithms=[security_settings.JWT_ALGORITHM]
        )
        return False
    except jwt.ExpiredSignatureError:
        return True
    except jwt.JWTError:
        return True

        return True 
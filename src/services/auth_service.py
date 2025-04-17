from datetime import datetime, timedelta
from typing import Optional, Dict, Any
import jwt
from uuid import uuid4
import logging
from fastapi import HTTPException, status, Depends
from fastapi.security import OAuth2PasswordBearer
from src.config.security import security_settings
from src.services.redis_service import redis_client
from src.utils.password import PasswordService

logger = logging.getLogger(__name__)

class AuthService:
    def __init__(self):
        self.oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")
        self.password_service = PasswordService()
        
    async def authenticate_user(self, username: str, password: str) -> Dict[str, Any]:
        """Authenticate a user with rate limiting and security measures"""
        try:
            # Check rate limiting for login attempts
            ip_key = f"login_ip:{request.client.host}"
            if await redis_client.get(ip_key) and int(await redis_client.get(ip_key)) > 10:
                logger.warning(f"Too many login attempts from IP: {request.client.host}")
                raise HTTPException(
                    status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                    detail="Too many login attempts. Please try again later."
                )

            # Get user from database
            user = await self.get_user_by_username(username)
            if not user:
                await redis_client.incr(ip_key)
                await redis_client.expire(ip_key, 300)  # 5 minutes
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid credentials"
                )

            # Verify password
            if not await self.password_service.verify_password(password, user["password_hash"], str(user["id"])):
                await redis_client.incr(ip_key)
                await redis_client.expire(ip_key, 300)  # 5 minutes
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid credentials"
                )

            # Clear rate limiting on successful login
            await redis_client.delete(ip_key)

            # Create session
            session_id = str(uuid4())
            await self.create_session(user["id"], session_id)

            return {
                "user": self.sanitize_user(user),
                "access_token": await self.create_access_token({"sub": str(user["id"]), "session": session_id}),
                "refresh_token": await self.create_refresh_token({"sub": str(user["id"]), "session": session_id})
            }

        except Exception as e:
            logger.error(f"Authentication error: {str(e)}")
            raise
        
    async def create_access_token(self, data: Dict[str, Any], expires_delta: Optional[timedelta] = None) -> str:
        """Create a JWT access token with enhanced security"""
        try:
            to_encode = data.copy()
            
            expire = datetime.utcnow() + (expires_delta or timedelta(minutes=security_settings.JWT_EXPIRATION_MINUTES))
            jti = str(uuid4())
            
            to_encode.update({
                "exp": expire,
                "iat": datetime.utcnow(),
                "jti": jti,
                "iss": "mkzt-auth",
                "aud": ["mkzt-api"],
                "type": "access"
            })
            
            # Store JTI in Redis for token tracking
            await redis_client.setex(
                f"token:{jti}",
                security_settings.JWT_EXPIRATION_MINUTES * 60,
                "valid"
            )
            
            token = jwt.encode(
                to_encode,
                security_settings.JWT_SECRET.get_secret_value(),
                algorithm=security_settings.JWT_ALGORITHM
            )

            logger.info(f"Created access token for user {data.get('sub')}")
            return token

        except Exception as e:
            logger.error(f"Error creating access token: {str(e)}")
            raise
    
    async def create_refresh_token(self, data: Dict[str, Any]) -> str:
        """Create a refresh token with longer expiration"""
        try:
            to_encode = data.copy()
            jti = str(uuid4())
            
            expire = datetime.utcnow() + timedelta(days=security_settings.JWT_REFRESH_TOKEN_EXPIRE_DAYS)
            to_encode.update({
                "exp": expire,
                "iat": datetime.utcnow(),
                "jti": jti,
                "iss": "mkzt-auth",
                "aud": ["mkzt-api"],
                "type": "refresh"
            })
            
            # Store refresh token JTI
            await redis_client.setex(
                f"refresh_token:{jti}",
                security_settings.JWT_REFRESH_TOKEN_EXPIRE_DAYS * 24 * 60 * 60,
                "valid"
            )
            
            token = jwt.encode(
                to_encode,
                security_settings.JWT_SECRET.get_secret_value(),
                algorithm=security_settings.JWT_ALGORITHM
            )

            logger.info(f"Created refresh token for user {data.get('sub')}")
            return token

        except Exception as e:
            logger.error(f"Error creating refresh token: {str(e)}")
            raise
            
    async def verify_token(self, token: str) -> Dict[str, Any]:
        """Verify JWT token with enhanced security checks"""
        try:
            payload = jwt.decode(
                token,
                security_settings.JWT_SECRET.get_secret_value(),
                algorithms=[security_settings.JWT_ALGORITHM],
                audience=["mkzt-api"]
            )
            
            # Check token type
            token_type = payload.get("type")
            if not token_type:
                raise jwt.InvalidTokenError("Token type not specified")

            # Check if token is blacklisted
            jti = payload.get("jti")
            if not jti:
                raise jwt.InvalidTokenError("Token has no ID")

            token_key = f"{'refresh_token' if token_type == 'refresh' else 'token'}:{jti}"
            if not await redis_client.get(token_key):
                raise jwt.InvalidTokenError("Token has been revoked")

            # Verify session is still valid
            session_id = payload.get("session")
            if not session_id or not await self.verify_session(payload.get("sub"), session_id):
                raise jwt.InvalidTokenError("Invalid session")
                
            return payload
            
        except jwt.ExpiredSignatureError:
            logger.warning(f"Expired token attempt: {token[:20]}...")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token has expired"
            )
        except jwt.JWTError as e:
            logger.warning(f"Invalid token attempt: {token[:20]}... - {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=f"Invalid token: {str(e)}"
            )
            
    async def get_current_user(self, token: str = Depends(OAuth2PasswordBearer(tokenUrl="token"))) -> Dict[str, Any]:
        """Get current user with role-based access control"""
        try:
            payload = await self.verify_token(token)
            user_id = payload.get("sub")
            
            if not user_id:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid user identifier"
                )
                
            # Get user from database with roles
            user = await self.get_user_with_roles(user_id)
            if not user:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="User not found"
                )
                
            # Update last activity
            await self.update_user_activity(user_id)
                
            return self.sanitize_user(user)

        except Exception as e:
            logger.error(f"Error getting current user: {str(e)}")
            raise

    async def create_session(self, user_id: str, session_id: str):
        """Create a new session for a user"""
        try:
            await redis_client.setex(
                f"session:{session_id}",
                security_settings.SESSION_LIFETIME,
                user_id
            )
            logger.info(f"Created session {session_id} for user {user_id}")
        except Exception as e:
            logger.error(f"Error creating session: {str(e)}")
            raise

    async def verify_session(self, user_id: str, session_id: str) -> bool:
        """Verify if a session is valid"""
        try:
            stored_user_id = await redis_client.get(f"session:{session_id}")
            return stored_user_id == user_id
        except Exception as e:
            logger.error(f"Error verifying session: {str(e)}")
            return False

    async def revoke_token(self, token: str):
        """Revoke a token"""
        try:
            payload = jwt.decode(
                token,
                security_settings.JWT_SECRET.get_secret_value(),
                algorithms=[security_settings.JWT_ALGORITHM],
                audience=["mkzt-api"]
            )
            
            jti = payload.get("jti")
            if jti:
                token_key = f"{'refresh_token' if payload.get('type') == 'refresh' else 'token'}:{jti}"
                await redis_client.delete(token_key)
                logger.info(f"Revoked token {jti}")
        except Exception as e:
            logger.error(f"Error revoking token: {str(e)}")
            raise

    def sanitize_user(self, user: Dict[str, Any]) -> Dict[str, Any]:
        """Remove sensitive information from user data"""
        sanitized = user.copy()
        sensitive_fields = {"password_hash", "security_question_answer", "recovery_codes"}
        for field in sensitive_fields:
            sanitized.pop(field, None)
        return sanitized

# Create singleton instance
auth_service = AuthService() 
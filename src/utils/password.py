import bcrypt
import re
import logging
from typing import Tuple, Optional, List
from datetime import datetime, timedelta
from src.config.security import security_settings
from src.services.redis_service import redis_client
import zxcvbn  # For password strength estimation

logger = logging.getLogger(__name__)

class PasswordService:
    def __init__(self):
        self.bcrypt_rounds = 12  # Recommended rounds for security/performance balance
        self.max_login_attempts = security_settings.PASSWORD_MAX_ATTEMPTS
        self.lockout_duration = security_settings.PASSWORD_LOCKOUT_DURATION
        self.password_history_size = security_settings.PASSWORD_HISTORY_SIZE
        
    async def hash_password(self, password: str) -> str:
        """Hash password with bcrypt using optimal work factor"""
        try:
            salt = bcrypt.gensalt(rounds=self.bcrypt_rounds)
            return bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')
        except Exception as e:
            logger.error(f"Error hashing password: {str(e)}")
            raise
        
    async def verify_password(self, password: str, hashed_password: str, user_id: str) -> bool:
        """Verify password with rate limiting and account lockout"""
        try:
            # Check if account is locked
            if await self.is_account_locked(user_id):
                logger.warning(f"Attempted login to locked account: {user_id}")
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Account is locked. Please try again later or reset your password."
                )
                
            # Verify password
            is_valid = bcrypt.checkpw(
                password.encode('utf-8'),
                hashed_password.encode('utf-8')
            )
            
            if not is_valid:
                await self.record_failed_attempt(user_id)
                logger.warning(f"Failed password verification for user: {user_id}")
            else:
                await self.reset_failed_attempts(user_id)
                logger.info(f"Successful password verification for user: {user_id}")
                
            return is_valid
            
        except Exception as e:
            logger.error(f"Error verifying password: {str(e)}")
            raise
        
    async def validate_password_strength(self, password: str, user_info: dict = None) -> Tuple[bool, Optional[str]]:
        """Enhanced password validation with zxcvbn"""
        try:
            # Basic length check
            if len(password) < security_settings.PASSWORD_MIN_LENGTH:
                return False, f"Password must be at least {security_settings.PASSWORD_MIN_LENGTH} characters"
                
            # Use zxcvbn for comprehensive password strength check
            user_inputs = []
            if user_info:
                user_inputs.extend([
                    user_info.get('username', ''),
                    user_info.get('email', ''),
                    user_info.get('first_name', ''),
                    user_info.get('last_name', '')
                ])
                
            strength_result = zxcvbn.zxcvbn(password, user_inputs=user_inputs)
            
            # Check password strength score (0-4)
            if strength_result['score'] < 3:
                suggestions = strength_result.get('feedback', {}).get('suggestions', [])
                return False, f"Password is too weak. {' '.join(suggestions)}"
                
            # Check for common patterns
            if strength_result['sequence']:
                return False, "Password contains common patterns or sequences"
                
            # Additional complexity requirements
            if not all([
                re.search(r'[A-Z]', password),  # uppercase
                re.search(r'[a-z]', password),  # lowercase
                re.search(r'[0-9]', password),  # numbers
                re.search(r'[!@#$%^&*(),.?":{}|<>]', password)  # special chars
            ]):
                return False, "Password must contain uppercase, lowercase, numbers, and special characters"
                
            return True, None
            
        except Exception as e:
            logger.error(f"Error validating password strength: {str(e)}")
            raise
        
    async def is_account_locked(self, user_id: str) -> bool:
        """Check if account is locked due to failed attempts"""
        try:
            attempts_key = f"login_attempts:{user_id}"
            attempts = await redis_client.get(attempts_key)
            
            if attempts and int(attempts) >= self.max_login_attempts:
                # Check if lockout period has expired
                ttl = await redis_client.ttl(attempts_key)
                if ttl > 0:
                    return True
                    
                # If lockout period expired, reset attempts
                await self.reset_failed_attempts(user_id)
                
            return False
            
        except Exception as e:
            logger.error(f"Error checking account lock: {str(e)}")
            return False
        
    async def record_failed_attempt(self, user_id: str):
        """Record failed login attempt with exponential backoff"""
        try:
            key = f"login_attempts:{user_id}"
            attempts = await redis_client.incr(key)
            
            if attempts == 1:
                # First failure: set initial lockout time
                await redis_client.expire(key, 300)  # 5 minutes
            elif attempts >= self.max_login_attempts:
                # Subsequent failures: increase lockout time exponentially
                lockout_time = min(self.lockout_duration * (2 ** (attempts - self.max_login_attempts)), 86400)  # Max 24 hours
                await redis_client.expire(key, lockout_time)
                
            logger.warning(f"Failed login attempt {attempts} for user {user_id}")
            
        except Exception as e:
            logger.error(f"Error recording failed attempt: {str(e)}")
            raise
        
    async def reset_failed_attempts(self, user_id: str):
        """Reset failed login attempts after successful login"""
        try:
            await redis_client.delete(f"login_attempts:{user_id}")
            logger.info(f"Reset failed attempts for user {user_id}")
        except Exception as e:
            logger.error(f"Error resetting failed attempts: {str(e)}")
            raise
            
    async def add_to_password_history(self, user_id: str, password_hash: str):
        """Add password hash to user's password history"""
        try:
            key = f"password_history:{user_id}"
            await redis_client.lpush(key, password_hash)
            await redis_client.ltrim(key, 0, self.password_history_size - 1)
            logger.info(f"Added password to history for user {user_id}")
        except Exception as e:
            logger.error(f"Error adding password to history: {str(e)}")
            raise
            
    async def is_password_reused(self, user_id: str, password: str) -> bool:
        """Check if password exists in user's password history"""
        try:
            key = f"password_history:{user_id}"
            history = await redis_client.lrange(key, 0, -1)
            
            for old_hash in history:
                if bcrypt.checkpw(password.encode('utf-8'), old_hash.encode('utf-8')):
                    logger.warning(f"Password reuse detected for user {user_id}")
                    return True
                    
            return False
            
        except Exception as e:
            logger.error(f"Error checking password history: {str(e)}")
            return False
            
    async def generate_reset_token(self, user_id: str) -> str:
        """Generate a secure password reset token"""
        try:
            import secrets
            token = secrets.token_urlsafe(32)
            
            # Store token with expiration
            await redis_client.setex(
                f"reset_token:{token}",
                3600,  # 1 hour expiration
                user_id
            )
            
            logger.info(f"Generated password reset token for user {user_id}")
            return token
            
        except Exception as e:
            logger.error(f"Error generating reset token: {str(e)}")
            raise
            
    async def verify_reset_token(self, token: str) -> Optional[str]:
        """Verify a password reset token"""
        try:
            user_id = await redis_client.get(f"reset_token:{token}")
            if user_id:
                # Delete token after use
                await redis_client.delete(f"reset_token:{token}")
                logger.info(f"Verified reset token for user {user_id}")
                return user_id
                
            logger.warning("Invalid or expired reset token")
            return None
            
        except Exception as e:
            logger.error(f"Error verifying reset token: {str(e)}")
            return None

# Create singleton instance
password_service = PasswordService() 
from typing import Dict, Any, Optional, List
import jwt
from datetime import datetime, timedelta
from passlib.hash import pbkdf2_sha256
from dataclasses import dataclass
import pyotp
import logging
from cryptography.fernet import Fernet
import bcrypt

@dataclass
class SecurityContext:
    user_id: str
    role: str
    permissions: List[str]
    session_id: str
    ip_address: str
    user_agent: str

class EnhancedSecurity:
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.active_sessions = {}
        self.blocked_ips = set()
        self.rate_limiters = {}
        self.suspicious_activities = []
        self.key = Fernet.generate_key()
        self.cipher_suite = Fernet(self.key)
        
    async def authenticate_user(self,
                              access_code: str,
                              context: Dict[str, Any]) -> Dict[str, Any]:
        """Authenticate user with enhanced security"""
        # Validate access code
        user_info = await self._validate_access_code(access_code)
        if not user_info:
            self._log_failed_attempt(context)
            return {"status": "error", "message": "Invalid access code"}
            
        # Check for suspicious activity
        if self._is_suspicious_activity(context):
            await self._trigger_security_alert(user_info, context)
            return {"status": "error", "message": "Security check required"}
            
        # Generate session
        session = await self._create_secure_session(user_info, context)
        
        # Set up 2FA if needed
        if self._requires_2fa(user_info):
            await self._setup_2fa(user_info)
            
        return {
            "status": "success",
            "session": session,
            "requires_2fa": self._requires_2fa(user_info)
        }
        
    async def validate_request(self,
                             token: str,
                             context: Dict[str, Any]) -> SecurityContext:
        """Validate request with comprehensive security checks"""
        # Decode and validate token
        payload = self._decode_token(token)
        if not payload:
            raise SecurityException("Invalid token")
            
        # Check rate limits
        if not self._check_rate_limit(payload["user_id"]):
            raise SecurityException("Rate limit exceeded")
            
        # Validate permissions
        security_context = await self._build_security_context(payload, context)
        if not self._validate_permissions(security_context):
            raise SecurityException("Insufficient permissions")
            
        # Log access
        await self._log_access(security_context)
        
        return security_context 

    async def secure_request(self, 
                           request: Dict[str, Any]) -> Dict[str, Any]:
        """Process request with enhanced security"""
        try:
            # Validate request
            if not await self._validate_request(request):
                raise SecurityException("Invalid request")
                
            # Check rate limits
            if not await self._check_rate_limit(request):
                raise SecurityException("Rate limit exceeded")
                
            # Validate authentication
            security_context = await self._authenticate_request(request)
            if not security_context:
                raise SecurityException("Authentication failed")
                
            # Check permissions
            if not await self._check_permissions(security_context):
                raise SecurityException("Insufficient permissions")
                
            # Process request
            response = await self._process_secure_request(request, security_context)
            
            # Audit logging
            await self._audit_log(request, response, security_context)
            
            return response
            
        except Exception as e:
            await self._handle_security_exception(e, request)
            raise
            
    async def _validate_request(self, request: Dict[str, Any]) -> bool:
        """Validate request parameters"""
        try:
            # Check required fields
            required_fields = ['token', 'timestamp', 'data']
            if not all(field in request for field in required_fields):
                return False
                
            # Validate timestamp
            request_time = datetime.fromtimestamp(request['timestamp'])
            if datetime.now() - request_time > timedelta(minutes=5):
                return False
                
            # Validate token format
            if not self._is_valid_token_format(request['token']):
                return False
                
            # Validate data structure
            if not self._is_valid_data_structure(request['data']):
                return False
                
            return True
            
        except Exception as e:
            logging.error(f"Request validation error: {str(e)}")
            return False
            
    async def _check_rate_limit(self, request: Dict[str, Any]) -> bool:
        """Check rate limits for request"""
        try:
            identifier = self._get_rate_limit_identifier(request)
            
            # Get or create limiter
            limiter = self.rate_limiters.get(identifier)
            if not limiter:
                limiter = RateLimiter(
                    max_requests=100,
                    window_seconds=60
                )
                self.rate_limiters[identifier] = limiter
                
            # Check limit
            return await limiter.check_limit()
            
        except Exception as e:
            logging.error(f"Rate limit check error: {str(e)}")
            return False
            
    async def _authenticate_request(self, 
                                  request: Dict[str, Any]) -> Optional[SecurityContext]:
        """Authenticate request and create security context"""
        try:
            # Decode token
            token_data = jwt.decode(
                request['token'],
                self.key,
                algorithms=['HS256']
            )
            
            # Validate token data
            if not self._is_valid_token_data(token_data):
                return None
                
            # Create security context
            return SecurityContext(
                user_id=token_data['user_id'],
                role=token_data['role'],
                permissions=token_data['permissions'],
                ip_address=request.get('ip_address'),
                user_agent=request.get('user_agent'),
                session_id=token_data['session_id']
            )
            
        except Exception as e:
            logging.error(f"Authentication error: {str(e)}")
            return None
            
    async def _check_permissions(self, context: SecurityContext) -> bool:
        """Check if security context has required permissions"""
        try:
            # Get required permissions
            required_permissions = self._get_required_permissions(context.role)
            
            # Check permissions
            return all(
                perm in context.permissions
                for perm in required_permissions
            )
            
        except Exception as e:
            logging.error(f"Permission check error: {str(e)}")
            return False 
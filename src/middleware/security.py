from fastapi import Request, HTTPException
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import os
from typing import Optional, List
import logging
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response
import ipaddress
from src.config.security import security_settings
from src.services.redis_service import redis_client
import time
import re

logger = logging.getLogger(__name__)

class APIKeyMiddleware:
    def __init__(self):
        self.api_key = os.getenv("API_KEY")
        self.excluded_paths = ["/docs", "/redoc", "/openapi.json"]

    async def __call__(self, request: Request, call_next):
        # Skip API key check for excluded paths
        if any(request.url.path.startswith(path) for path in self.excluded_paths):
            return await call_next(request)

        # Get API key from header
        api_key = request.headers.get("X-API-Key")
        
        if not api_key:
            return JSONResponse(
                status_code=401,
                content={"error": "API key is required"}
            )
            
        if api_key != self.api_key:
            return JSONResponse(
                status_code=403,
                content={"error": "Invalid API key"}
            )
            
        return await call_next(request)

def setup_cors(app):
    origins = os.getenv("CORS_ORIGINS", "*").split(",")
    
    app.add_middleware(
        CORSMiddleware,
        allow_origins=origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    ) 

class SecurityMiddleware(BaseHTTPMiddleware):
    def __init__(
        self,
        app,
        trusted_ips: Optional[List[str]] = None,
        rate_limit: Optional[int] = None,
        rate_window: Optional[int] = None
    ):
        super().__init__(app)
        self.trusted_ips = [ipaddress.ip_network(ip) for ip in (trusted_ips or [])]
        self.rate_limit = rate_limit or security_settings.RATE_LIMIT_REQUESTS
        self.rate_window = rate_window or security_settings.RATE_LIMIT_WINDOW
        self.ip_blacklist = set()
        self.suspicious_patterns = [
            r"(?i)(?:union.*select|' *or *'|exec.*\(|drop.*table)",  # SQL injection
            r"(?i)<script.*?>",  # XSS
            r"(?i)(?:/etc/passwd|/etc/shadow)",  # Path traversal
            r"(?i)(?:\.\./|\.\./\./)",  # Directory traversal
        ]
        
    async def dispatch(self, request: Request, call_next) -> Response:
        """Process request with security checks"""
        try:
            start_time = time.time()
            client_ip = ipaddress.ip_address(request.client.host)
            
            # Security checks
            await self._check_ip_security(client_ip)
            await self._check_rate_limit(client_ip, request.url.path)
            await self._check_request_security(request)
            
            # Process request
            response = await call_next(request)
            
            # Add security headers
            response.headers.update(security_settings.SECURITY_HEADERS)
            
            # Add CSP header
            response.headers["Content-Security-Policy"] = self._build_csp_header()
            
            # Log request details
            self._log_request(request, response, start_time)
            
            return response
            
        except HTTPException as e:
            logger.warning(
                "Security check failed",
                extra={
                    "ip": str(client_ip),
                    "path": request.url.path,
                    "error": str(e)
                }
            )
            raise
        except Exception as e:
            logger.error(
                "Security middleware error",
                extra={
                    "ip": str(client_ip),
                    "path": request.url.path,
                    "error": str(e)
                }
            )
            raise HTTPException(status_code=500, detail="Internal server error")
            
    async def _check_ip_security(self, client_ip: ipaddress.IPv4Address):
        """Check IP-based security rules"""
        # Check if IP is blacklisted
        if str(client_ip) in self.ip_blacklist:
            raise HTTPException(status_code=403, detail="IP address blocked")
            
        # Check if IP is trusted for sensitive operations
        if not any(client_ip in network for network in self.trusted_ips):
            # Additional checks for untrusted IPs
            suspicious_count = await redis_client.get(f"suspicious_ip:{client_ip}")
            if suspicious_count and int(suspicious_count) > 10:
                self.ip_blacklist.add(str(client_ip))
                raise HTTPException(status_code=403, detail="IP address blocked due to suspicious activity")
                
    async def _check_rate_limit(self, client_ip: ipaddress.IPv4Address, path: str):
        """Check rate limiting rules"""
        key = f"rate_limit:{client_ip}:{path}"
        
        # Get current request count
        requests = await redis_client.incr(key)
        if requests == 1:
            await redis_client.expire(key, self.rate_window)
            
        # Check if rate limit exceeded
        if requests > self.rate_limit:
            await redis_client.incr(f"suspicious_ip:{client_ip}")
            raise HTTPException(status_code=429, detail="Too many requests")
            
    async def _check_request_security(self, request: Request):
        """Check request content for security issues"""
        # Get request body (if any)
        body = await request.body()
        body_str = body.decode() if body else ""
        
        # Check for suspicious patterns
        for pattern in self.suspicious_patterns:
            if re.search(pattern, body_str) or re.search(pattern, str(request.query_params)):
                client_ip = request.client.host
                await redis_client.incr(f"suspicious_ip:{client_ip}")
                raise HTTPException(status_code=400, detail="Invalid request content")
                
        # Check content type for file uploads
        content_type = request.headers.get("content-type", "")
        if "multipart/form-data" in content_type:
            await self._validate_file_upload(request)
            
    async def _validate_file_upload(self, request: Request):
        """Validate file uploads for security"""
        form = await request.form()
        for field in form:
            if hasattr(form[field], "filename"):
                # Check file size
                if len(await form[field].read()) > security_settings.MAX_UPLOAD_SIZE:
                    raise HTTPException(status_code=400, detail="File too large")
                    
                # Check file type
                if not any(form[field].filename.lower().endswith(ext) for ext in security_settings.ALLOWED_EXTENSIONS):
                    raise HTTPException(status_code=400, detail="File type not allowed")
                    
    def _build_csp_header(self) -> str:
        """Build Content Security Policy header"""
        return "; ".join(
            f"{key} {' '.join(values)}"
            for key, values in security_settings.CSP_DIRECTIVES.items()
        )
        
    def _log_request(self, request: Request, response: Response, start_time: float):
        """Log request details for security monitoring"""
        duration = time.time() - start_time
        logger.info(
            "Request processed",
            extra={
                "ip": request.client.host,
                "method": request.method,
                "path": request.url.path,
                "status_code": response.status_code,
                "duration": duration,
                "user_agent": request.headers.get("user-agent"),
                "referer": request.headers.get("referer")
            }
        ) 
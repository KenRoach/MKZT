from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response
from src.config.security import security_settings
import re

class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        response = await call_next(request)
        
        # Add security headers
        for header, value in security_settings.SECURITY_HEADERS.items():
            response.headers[header] = value
        
        # Add Content Security Policy
        csp_directives = []
        for directive, sources in security_settings.CSP_DIRECTIVES.items():
            csp_directives.append(f"{directive} {' '.join(sources)}")
        
        response.headers["Content-Security-Policy"] = "; ".join(csp_directives)
        
        # Add Strict-Transport-Security header for HTTPS
        response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
        
        # Remove server header
        if "Server" in response.headers:
            del response.headers["Server"]
        
        return response

class InputSanitizationMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        # Sanitize query parameters
        if request.query_params:
            sanitized_params = {}
            for key, value in request.query_params.items():
                sanitized_params[key] = self._sanitize_input(value)
            request._query_params = sanitized_params
        
        # Sanitize path parameters
        if request.path_params:
            sanitized_params = {}
            for key, value in request.path_params.items():
                sanitized_params[key] = self._sanitize_input(value)
            request._path_params = sanitized_params
        
        # Sanitize headers
        if request.headers:
            sanitized_headers = {}
            for key, value in request.headers.items():
                sanitized_headers[key] = self._sanitize_input(value)
            request._headers = sanitized_headers
        
        response = await call_next(request)
        return response
    
    def _sanitize_input(self, value: str) -> str:
        """Sanitize input to prevent XSS and injection attacks"""
        if not isinstance(value, str):
            return value
        
        # Remove HTML tags
        value = re.sub(r'<[^>]*>', '', value)
        
        # Escape special characters
        value = value.replace('&', '&amp;')
        value = value.replace('<', '&lt;')
        value = value.replace('>', '&gt;')
        value = value.replace('"', '&quot;')
        value = value.replace("'", '&#x27;')
        
        return value 
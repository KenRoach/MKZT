from fastapi import Request, HTTPException
from starlette.middleware.base import BaseHTTPMiddleware
from src.config.security import security_settings
from src.data.crm_repository import CRMRepository
from typing import Optional

class APIKeyMiddleware(BaseHTTPMiddleware):
    def __init__(self, app):
        super().__init__(app)
        self.crm_repository = CRMRepository()
        self.settings = security_settings

    async def dispatch(self, request: Request, call_next):
        # Skip API key validation for certain paths
        if self._should_skip_validation(request.url.path):
            return await call_next(request)

        api_key = self._extract_api_key(request)
        if not api_key:
            raise HTTPException(
                status_code=401,
                detail="API key is required"
            )

        # Validate API key
        if not await self._validate_api_key(api_key):
            raise HTTPException(
                status_code=403,
                detail="Invalid API key"
            )

        return await call_next(request)

    def _should_skip_validation(self, path: str) -> bool:
        """Check if the path should skip API key validation."""
        skip_paths = [
            "/docs",
            "/redoc",
            "/openapi.json",
            "/health",
            "/metrics"
        ]
        return any(path.startswith(p) for p in skip_paths)

    def _extract_api_key(self, request: Request) -> Optional[str]:
        """Extract API key from request headers."""
        return request.headers.get(self.settings.api_key_header)

    async def _validate_api_key(self, api_key: str) -> bool:
        """Validate the API key against the database."""
        try:
            # Check if API key exists and is active
            # This is a placeholder - implement actual validation logic
            return True
        except Exception as e:
            return False 
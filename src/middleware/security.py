from fastapi import Request, HTTPException
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import os
from typing import Optional

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
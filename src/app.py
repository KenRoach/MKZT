from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from src.middleware.api_key import APIKeyMiddleware
from src.middleware.rate_limit import RateLimitMiddleware
from src.config.security import security_settings

app = FastAPI(
    title="Order Management System",
    description="A comprehensive order management system with multi-channel support",
    version="1.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add API key validation middleware
app.add_middleware(APIKeyMiddleware)

# Add rate limiting middleware
app.add_middleware(RateLimitMiddleware)

# Import and include routers
from src.routers import merchant, order, driver, customer

app.include_router(merchant.router, prefix="/api/v1/merchants", tags=["merchants"])
app.include_router(order.router, prefix="/api/v1/orders", tags=["orders"])
app.include_router(driver.router, prefix="/api/v1/drivers", tags=["drivers"])
app.include_router(customer.router, prefix="/api/v1/customers", tags=["customers"])

@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy"}

@app.get("/metrics")
async def metrics():
    """Basic metrics endpoint."""
    return {
        "status": "operational",
        "version": "1.0.0"
    } 
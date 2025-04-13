import pytest
import requests
import time
import os
from src.config.security import security_settings

# Base URL for the API
BASE_URL = "http://localhost:8000"

# Test API key
TEST_API_KEY = "test_api_key_123"

@pytest.mark.e2e
def test_health_check():
    """Test the health check endpoint."""
    response = requests.get(f"{BASE_URL}/health")
    assert response.status_code == 200
    assert response.json() == {"status": "healthy"}

@pytest.mark.e2e
def test_metrics():
    """Test the metrics endpoint."""
    response = requests.get(f"{BASE_URL}/metrics")
    assert response.status_code == 200
    data = response.json()
    assert "status" in data
    assert "version" in data

@pytest.mark.e2e
def test_api_key_required():
    """Test that API key is required for protected endpoints."""
    # Try to access a protected endpoint without an API key
    response = requests.get(f"{BASE_URL}/api/v1/merchants")
    assert response.status_code == 401
    assert "API key is required" in response.json()["detail"]

@pytest.mark.e2e
def test_api_key_validation():
    """Test API key validation."""
    # Try with an invalid API key
    headers = {security_settings.API_KEY_HEADER: "invalid_key"}
    response = requests.get(f"{BASE_URL}/api/v1/merchants", headers=headers)
    assert response.status_code == 403
    assert "Invalid API key" in response.json()["detail"]

@pytest.mark.e2e
def test_rate_limiting():
    """Test rate limiting."""
    headers = {security_settings.API_KEY_HEADER: TEST_API_KEY}
    
    # Make requests up to the limit
    for _ in range(security_settings.RATE_LIMIT_REQUESTS):
        response = requests.get(f"{BASE_URL}/api/v1/merchants", headers=headers)
        assert response.status_code == 200
    
    # The next request should be rate limited
    response = requests.get(f"{BASE_URL}/api/v1/merchants", headers=headers)
    assert response.status_code == 429
    assert "Too many requests" in response.json()["detail"]
    
    # Wait for the rate limit window to reset
    time.sleep(security_settings.RATE_LIMIT_WINDOW)
    
    # Should be able to make requests again
    response = requests.get(f"{BASE_URL}/api/v1/merchants", headers=headers)
    assert response.status_code == 200 
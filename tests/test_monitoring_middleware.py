import pytest
from fastapi import FastAPI, Request
from fastapi.testclient import TestClient
from starlette.testclient import TestClient as StarletteTestClient

from src.middleware.monitoring import MonitoringMiddleware
from src.utils.monitoring import metrics_tracker

# Create a test app
app = FastAPI()

@app.get("/test")
async def test_endpoint():
    return {"message": "test"}

@app.get("/error")
async def error_endpoint():
    raise Exception("Test error")

# Add the monitoring middleware
app.add_middleware(MonitoringMiddleware)

# Create a test client
client = TestClient(app)

@pytest.fixture(autouse=True)
def reset_metrics():
    """Reset metrics before each test"""
    metrics_tracker.reset_metrics()
    yield
    metrics_tracker.reset_metrics()

def test_middleware_tracks_request():
    """Test that the middleware tracks API requests"""
    # Make a request
    response = client.get("/test")
    
    # Verify response
    assert response.status_code == 200
    assert response.json() == {"message": "test"}
    
    # Get metrics
    metrics = metrics_tracker.get_metrics()
    
    # Verify request was tracked
    assert "GET:/test" in metrics["requests"]
    assert metrics["requests"]["GET:/test"]["count"] == 1
    assert metrics["requests"]["GET:/test"]["status_codes"][200] == 1
    assert metrics["requests"]["GET:/test"]["total_time"] > 0
    assert metrics["requests"]["GET:/test"]["avg_time"] > 0

def test_middleware_tracks_error():
    """Test that the middleware tracks API errors"""
    # Make a request that will raise an error
    with pytest.raises(Exception):
        client.get("/error")
    
    # Get metrics
    metrics = metrics_tracker.get_metrics()
    
    # Verify request was tracked
    assert "GET:/error" in metrics["requests"]
    assert metrics["requests"]["GET:/error"]["count"] == 1
    assert metrics["requests"]["GET:/error"]["status_codes"][500] == 1
    assert metrics["requests"]["GET:/error"]["total_time"] > 0
    assert metrics["requests"]["GET:/error"]["avg_time"] > 0

def test_middleware_tracks_multiple_requests():
    """Test that the middleware tracks multiple requests"""
    # Make multiple requests
    for _ in range(3):
        client.get("/test")
    
    # Get metrics
    metrics = metrics_tracker.get_metrics()
    
    # Verify requests were tracked
    assert "GET:/test" in metrics["requests"]
    assert metrics["requests"]["GET:/test"]["count"] == 3
    assert metrics["requests"]["GET:/test"]["status_codes"][200] == 3
    assert metrics["requests"]["GET:/test"]["total_time"] > 0
    assert metrics["requests"]["GET:/test"]["avg_time"] > 0

def test_middleware_tracks_different_methods():
    """Test that the middleware tracks different HTTP methods"""
    # Create a test app with POST endpoint
    test_app = FastAPI()
    
    @test_app.post("/test")
    async def test_post():
        return {"message": "test"}
    
    # Add the monitoring middleware
    test_app.add_middleware(MonitoringMiddleware)
    
    # Create a test client
    test_client = TestClient(test_app)
    
    # Make GET and POST requests
    client.get("/test")
    test_client.post("/test")
    
    # Get metrics
    metrics = metrics_tracker.get_metrics()
    
    # Verify requests were tracked
    assert "GET:/test" in metrics["requests"]
    assert "POST:/test" in metrics["requests"]
    assert metrics["requests"]["GET:/test"]["count"] == 1
    assert metrics["requests"]["POST:/test"]["count"] == 1
    assert metrics["requests"]["GET:/test"]["status_codes"][200] == 1
    assert metrics["requests"]["POST:/test"]["status_codes"][200] == 1 
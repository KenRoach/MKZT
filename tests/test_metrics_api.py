import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from src.api.metrics import router as metrics_router
from src.utils.monitoring import metrics_tracker

# Create a test app
app = FastAPI()
app.include_router(metrics_router)

# Create a test client
client = TestClient(app)

@pytest.fixture(autouse=True)
def reset_metrics():
    """Reset metrics before each test"""
    metrics_tracker.reset_metrics()
    yield
    metrics_tracker.reset_metrics()

def test_get_metrics():
    """Test getting all metrics"""
    # Track some metrics
    metrics_tracker.track_request("/test", "GET", 200, 0.1)
    metrics_tracker.track_error("TestError", "Test error")
    metrics_tracker.track_processing_time("test_op", 0.1)
    metrics_tracker.track_custom_metric("test_metric", 42)
    
    # Get metrics via API
    response = client.get("/metrics")
    
    # Verify response
    assert response.status_code == 200
    metrics = response.json()
    
    # Verify metrics
    assert "requests" in metrics
    assert "errors" in metrics
    assert "processing_times" in metrics
    assert "custom" in metrics
    assert "GET:/test" in metrics["requests"]
    assert "TestError" in metrics["errors"]
    assert "test_op" in metrics["processing_times"]
    assert "test_metric" in metrics["custom"]

def test_reset_metrics():
    """Test resetting metrics"""
    # Track some metrics
    metrics_tracker.track_request("/test", "GET", 200, 0.1)
    metrics_tracker.track_error("TestError", "Test error")
    metrics_tracker.track_processing_time("test_op", 0.1)
    metrics_tracker.track_custom_metric("test_metric", 42)
    
    # Verify metrics were tracked
    metrics = metrics_tracker.get_metrics()
    assert len(metrics["requests"]) > 0
    assert len(metrics["errors"]) > 0
    assert len(metrics["processing_times"]) > 0
    assert len(metrics["custom"]) > 0
    
    # Reset metrics via API
    response = client.post("/metrics/reset")
    
    # Verify response
    assert response.status_code == 200
    assert response.json() == {"status": "success", "message": "Metrics reset successfully"}
    
    # Verify metrics were reset
    metrics = metrics_tracker.get_metrics()
    assert len(metrics["requests"]) == 0
    assert len(metrics["errors"]) == 0
    assert len(metrics["processing_times"]) == 0
    assert len(metrics["custom"]) == 0 
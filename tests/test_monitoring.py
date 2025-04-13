import pytest
import time
from src.utils.monitoring import MetricsTracker, track_time

@pytest.fixture
def metrics_tracker():
    """Create a fresh metrics tracker for each test"""
    tracker = MetricsTracker()
    return tracker

def test_track_request(metrics_tracker):
    """Test tracking API requests"""
    # Track a request
    metrics_tracker.track_request(
        endpoint="/test",
        method="GET",
        status_code=200,
        processing_time=0.1
    )
    
    # Get metrics
    metrics = metrics_tracker.get_metrics()
    
    # Verify request was tracked
    assert "GET:/test" in metrics["requests"]
    assert metrics["requests"]["GET:/test"]["count"] == 1
    assert metrics["requests"]["GET:/test"]["total_time"] == 0.1
    assert metrics["requests"]["GET:/test"]["avg_time"] == 0.1
    assert metrics["requests"]["GET:/test"]["status_codes"][200] == 1
    
    # Track another request with different status code
    metrics_tracker.track_request(
        endpoint="/test",
        method="GET",
        status_code=404,
        processing_time=0.2
    )
    
    # Get updated metrics
    metrics = metrics_tracker.get_metrics()
    
    # Verify metrics were updated
    assert metrics["requests"]["GET:/test"]["count"] == 2
    assert metrics["requests"]["GET:/test"]["total_time"] == 0.3
    assert metrics["requests"]["GET:/test"]["avg_time"] == 0.15
    assert metrics["requests"]["GET:/test"]["status_codes"][200] == 1
    assert metrics["requests"]["GET:/test"]["status_codes"][404] == 1

def test_track_error(metrics_tracker):
    """Test tracking errors"""
    # Track an error
    metrics_tracker.track_error(
        error_type="ValueError",
        error_message="Invalid value",
        context={"operation": "test", "value": 123}
    )
    
    # Get metrics
    metrics = metrics_tracker.get_metrics()
    
    # Verify error was tracked
    assert "ValueError" in metrics["errors"]
    assert metrics["errors"]["ValueError"]["count"] == 1
    assert metrics["errors"]["ValueError"]["last_occurrence"] is not None
    assert len(metrics["errors"]["ValueError"]["contexts"]) == 1
    assert metrics["errors"]["ValueError"]["contexts"][0]["message"] == "Invalid value"
    assert metrics["errors"]["ValueError"]["contexts"][0]["context"] == {"operation": "test", "value": 123}

def test_track_processing_time(metrics_tracker):
    """Test tracking processing time"""
    # Track processing time
    metrics_tracker.track_processing_time("test_operation", 0.1)
    
    # Get metrics
    metrics = metrics_tracker.get_metrics()
    
    # Verify processing time was tracked
    assert "test_operation" in metrics["processing_times"]
    assert metrics["processing_times"]["test_operation"]["count"] == 1
    assert metrics["processing_times"]["test_operation"]["total_time"] == 0.1
    assert metrics["processing_times"]["test_operation"]["avg_time"] == 0.1
    assert metrics["processing_times"]["test_operation"]["min_time"] == 0.1
    assert metrics["processing_times"]["test_operation"]["max_time"] == 0.1
    
    # Track another processing time
    metrics_tracker.track_processing_time("test_operation", 0.3)
    
    # Get updated metrics
    metrics = metrics_tracker.get_metrics()
    
    # Verify metrics were updated
    assert metrics["processing_times"]["test_operation"]["count"] == 2
    assert metrics["processing_times"]["test_operation"]["total_time"] == 0.4
    assert metrics["processing_times"]["test_operation"]["avg_time"] == 0.2
    assert metrics["processing_times"]["test_operation"]["min_time"] == 0.1
    assert metrics["processing_times"]["test_operation"]["max_time"] == 0.3

def test_track_custom_metric(metrics_tracker):
    """Test tracking custom metrics"""
    # Track a custom metric
    metrics_tracker.track_custom_metric("test_metric", 42, {"tag1": "value1"})
    
    # Get metrics
    metrics = metrics_tracker.get_metrics()
    
    # Verify custom metric was tracked
    assert "test_metric" in metrics["custom"]
    assert len(metrics["custom"]["test_metric"]["values"]) == 1
    assert metrics["custom"]["test_metric"]["values"][0]["value"] == 42
    assert metrics["custom"]["test_metric"]["tags"] == {"tag1": "value1"}
    
    # Track another custom metric
    metrics_tracker.track_custom_metric("test_metric", 43, {"tag2": "value2"})
    
    # Get updated metrics
    metrics = metrics_tracker.get_metrics()
    
    # Verify metrics were updated
    assert len(metrics["custom"]["test_metric"]["values"]) == 2
    assert metrics["custom"]["test_metric"]["values"][1]["value"] == 43
    assert metrics["custom"]["test_metric"]["tags"] == {"tag1": "value1", "tag2": "value2"}

def test_reset_metrics(metrics_tracker):
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
    
    # Reset metrics
    metrics_tracker.reset_metrics()
    
    # Verify metrics were reset
    metrics = metrics_tracker.get_metrics()
    assert len(metrics["requests"]) == 0
    assert len(metrics["errors"]) == 0
    assert len(metrics["processing_times"]) == 0
    assert len(metrics["custom"]) == 0

def test_track_time_decorator():
    """Test the track_time decorator"""
    # Create a metrics tracker
    tracker = MetricsTracker()
    
    # Define a function to test
    @track_time("test_function")
    def test_function():
        time.sleep(0.1)
        return "test"
    
    # Call the function
    result = test_function()
    
    # Verify the function returned correctly
    assert result == "test"
    
    # Get metrics
    metrics = tracker.get_metrics()
    
    # Verify processing time was tracked
    assert "test_function" in metrics["processing_times"]
    assert metrics["processing_times"]["test_function"]["count"] == 1
    assert metrics["processing_times"]["test_function"]["total_time"] >= 0.1 
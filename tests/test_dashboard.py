import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from src.main import app

# Create a test client
client = TestClient(app)

def test_dashboard_endpoint():
    """Test that the dashboard endpoint returns the dashboard template"""
    # Make a request to the dashboard endpoint
    response = client.get("/dashboard")
    
    # Verify response
    assert response.status_code == 200
    assert "text/html" in response.headers["content-type"]
    assert "WhatsApp AI Ordering Bot - Dashboard" in response.text
    assert "chart.js" in response.text
    assert "bootstrap" in response.text 
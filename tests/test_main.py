import os
import pytest
from fastapi.testclient import TestClient
from dotenv import load_dotenv
from src.main import app

# Load environment variables
load_dotenv()

# Create a test client
client = TestClient(app)

def test_root():
    """Test the root endpoint"""
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "WhatsApp AI Ordering Bot is running"}

def test_verify_webhook():
    """Test the webhook verification endpoint"""
    # Get the verify token from environment
    verify_token = os.getenv("WHATSAPP_VERIFY_TOKEN")
    
    # Test with correct token
    response = client.get(f"/webhook/whatsapp?hub.mode=subscribe&hub.verify_token={verify_token}&hub.challenge=1234567890")
    assert response.status_code == 200
    assert response.json() == 1234567890
    
    # Test with incorrect token
    response = client.get("/webhook/whatsapp?hub.mode=subscribe&hub.verify_token=incorrect_token&hub.challenge=1234567890")
    assert response.status_code == 200
    assert response.json() == {"error": "Invalid verification token"}
    
    # Test with missing parameters
    response = client.get("/webhook/whatsapp")
    assert response.status_code == 200
    assert response.json() == {"error": "Missing parameters"}

def test_webhook():
    """Test the webhook endpoint"""
    # Sample webhook data
    webhook_data = {
        "entry": [
            {
                "changes": [
                    {
                        "value": {
                            "messages": [
                                {
                                    "id": "test_message_id",
                                    "from": "+1234567890",
                                    "text": {
                                        "body": "Hello, I want to order a product"
                                    }
                                }
                            ]
                        }
                    }
                ]
            }
        ]
    }
    
    # Send the webhook data
    response = client.post("/webhook/whatsapp", json=webhook_data)
    assert response.status_code == 200
    assert "status" in response.json()
    assert response.json()["status"] == "success"
    assert "message_id" in response.json()
    assert "response" in response.json() 
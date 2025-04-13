import os
import pytest
import json
from unittest.mock import patch, MagicMock
from dotenv import load_dotenv
from src.ai.handler import AIHandler

# Load environment variables
load_dotenv()

@pytest.fixture
def ai_handler():
    """Create an AI handler for testing"""
    return AIHandler()

@pytest.fixture
def test_message():
    """Sample message for testing"""
    return "I want to order 2 blue shirts and 1 red shirt"

@pytest.fixture
def test_order_message():
    """Sample order message for testing"""
    return "What's the status of my order #ORD-001?"

@pytest.mark.asyncio
async def test_analyze_intent_greeting(ai_handler):
    """Test intent analysis for greeting messages"""
    # Mock OpenAI API response
    with patch('openai.ChatCompletion.create') as mock_create:
        mock_create.return_value = MagicMock(
            choices=[
                MagicMock(
                    message=MagicMock(
                        content=json.dumps({
                            "intent": "greeting",
                            "confidence": 0.95
                        })
                    )
                )
            ]
        )
        
        # Analyze intent
        result = await ai_handler.analyze_intent("Hello!")
        
        # Check result
        assert result["intent"] == "greeting"
        assert result["confidence"] == 0.95
        
        # Verify OpenAI API was called correctly
        mock_create.assert_called_once()
        call_args = mock_create.call_args[1]
        assert "greeting" in call_args["messages"][0]["content"].lower()

@pytest.mark.asyncio
async def test_analyze_intent_order(ai_handler, test_message):
    """Test intent analysis for order messages"""
    # Mock OpenAI API response
    with patch('openai.ChatCompletion.create') as mock_create:
        mock_create.return_value = MagicMock(
            choices=[
                MagicMock(
                    message=MagicMock(
                        content=json.dumps({
                            "intent": "order",
                            "confidence": 0.98
                        })
                    )
                )
            ]
        )
        
        # Analyze intent
        result = await ai_handler.analyze_intent(test_message)
        
        # Check result
        assert result["intent"] == "order"
        assert result["confidence"] == 0.98
        
        # Verify OpenAI API was called correctly
        mock_create.assert_called_once()
        call_args = mock_create.call_args[1]
        assert "order" in call_args["messages"][0]["content"].lower()

@pytest.mark.asyncio
async def test_extract_order_details(ai_handler, test_message):
    """Test order details extraction from messages"""
    # Mock OpenAI API response
    with patch('openai.ChatCompletion.create') as mock_create:
        mock_create.return_value = MagicMock(
            choices=[
                MagicMock(
                    message=MagicMock(
                        content=json.dumps({
                            "items": [
                                {
                                    "product": "blue shirt",
                                    "quantity": 2,
                                    "price": 1000
                                },
                                {
                                    "product": "red shirt",
                                    "quantity": 1,
                                    "price": 1000
                                }
                            ],
                            "total_amount": 3000
                        })
                    )
                )
            ]
        )
        
        # Extract order details
        result = await ai_handler.extract_order_details(test_message)
        
        # Check result
        assert len(result["items"]) == 2
        assert result["items"][0]["product"] == "blue shirt"
        assert result["items"][0]["quantity"] == 2
        assert result["items"][1]["product"] == "red shirt"
        assert result["items"][1]["quantity"] == 1
        assert result["total_amount"] == 3000
        
        # Verify OpenAI API was called correctly
        mock_create.assert_called_once()
        call_args = mock_create.call_args[1]
        assert "extract" in call_args["messages"][0]["content"].lower()

@pytest.mark.asyncio
async def test_extract_order_number(ai_handler, test_order_message):
    """Test order number extraction from messages"""
    # Mock OpenAI API response
    with patch('openai.ChatCompletion.create') as mock_create:
        mock_create.return_value = MagicMock(
            choices=[
                MagicMock(
                    message=MagicMock(
                        content=json.dumps({
                            "order_number": "ORD-001"
                        })
                    )
                )
            ]
        )
        
        # Extract order number
        result = await ai_handler.extract_order_number(test_order_message)
        
        # Check result
        assert result == "ORD-001"
        
        # Verify OpenAI API was called correctly
        mock_create.assert_called_once()
        call_args = mock_create.call_args[1]
        assert "order number" in call_args["messages"][0]["content"].lower()

@pytest.mark.asyncio
async def test_error_handling(ai_handler):
    """Test error handling in AI operations"""
    # Mock OpenAI API to simulate an error
    with patch('openai.ChatCompletion.create') as mock_create:
        mock_create.side_effect = Exception("API Error")
        
        # Try to analyze intent
        result = await ai_handler.analyze_intent("Hello!")
        
        # Check error handling
        assert result["intent"] == "unknown"
        assert result["confidence"] == 0.0

@pytest.mark.asyncio
async def test_invalid_json_response(ai_handler):
    """Test handling of invalid JSON responses from OpenAI"""
    # Mock OpenAI API to return invalid JSON
    with patch('openai.ChatCompletion.create') as mock_create:
        mock_create.return_value = MagicMock(
            choices=[
                MagicMock(
                    message=MagicMock(
                        content="Invalid JSON"
                    )
                )
            ]
        )
        
        # Try to analyze intent
        result = await ai_handler.analyze_intent("Hello!")
        
        # Check error handling
        assert result["intent"] == "unknown"
        assert result["confidence"] == 0.0 
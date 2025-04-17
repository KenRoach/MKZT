import pytest
import asyncio
from datetime import datetime
from src.services.conversation_manager import conversation_manager
from src.handlers.conversation_handler import ActorType

@pytest.mark.asyncio
async def test_complex_order_scenarios():
    """Test more complex ordering scenarios"""
    order_id = f"TEST_COMPLEX_{int(datetime.now().timestamp())}"
    
    # Test multiple items with modifications
    response = await conversation_manager.handle_customer_message(
        order_id=order_id,
        customer_id="CUST123",
        message="Quiero un California Roll sin pepino, dos Rainbow Roll y una Coca Zero"
    )
    assert "California Roll" in response["content"]
    assert "sin pepino" in response["content"].lower()
    
    # Test special instructions
    response = await conversation_manager.handle_customer_message(
        order_id=order_id,
        customer_id="CUST123",
        message="¿Pueden agregar más wasabi y dividir los rolls en dos entregas?"
    )
    assert "instrucciones especiales" in response["content"].lower()

@pytest.mark.asyncio
async def test_error_recovery():
    """Test system's ability to recover from errors"""
    order_id = f"TEST_ERROR_{int(datetime.now().timestamp())}"
    
    # Test recovery from invalid input
    response = await conversation_manager.handle_customer_message(
        order_id=order_id,
        customer_id="CUST123",
        message="@#$%^"
    )
    assert "no pude entender" in response["content"].lower()
    
    # Test recovery with valid input
    response = await conversation_manager.handle_customer_message(
        order_id=order_id,
        customer_id="CUST123",
        message="Quiero un California Roll"
    )
    assert "California Roll" in response["content"]

@pytest.mark.asyncio
async def test_multi_language_support():
    """Test handling conversations in multiple languages"""
    order_id = f"TEST_LANG_{int(datetime.now().timestamp())}"
    
    # Test Spanish
    response = await conversation_manager.handle_customer_message(
        order_id=order_id,
        customer_id="CUST123",
        message="Quiero un California Roll"
    )
    assert "California Roll" in response["content"]
    
    # Test English
    response = await conversation_manager.handle_customer_message(
        order_id=order_id,
        customer_id="CUST124",
        message="I want a California Roll"
    )
    assert "California Roll" in response["content"]

@pytest.mark.asyncio
async def test_peak_load():
    """Test system under peak load conditions"""
    async def create_order(index: int):
        order_id = f"TEST_PEAK_{index}_{int(datetime.now().timestamp())}"
        return await conversation_manager.handle_customer_message(
            order_id=order_id,
            customer_id=f"CUST{index}",
            message="Quiero un California Roll"
        )
    
    # Create 50 concurrent orders
    tasks = [create_order(i) for i in range(50)]
    responses = await asyncio.gather(*tasks)
    
    # Verify all orders were processed
    assert len(responses) == 50
    assert all("California Roll" in r["content"] for r in responses) 
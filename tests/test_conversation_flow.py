# Add comprehensive conversation flow tests
import pytest
from src.services.conversation_manager import conversation_manager
from src.handlers.conversation_handler import ActorType

@pytest.mark.asyncio
async def test_complete_order_flow():
    """Test complete order flow from customer to delivery"""
    # Initialize conversation
    order_id = "TEST123"
    
    # Test customer order
    response = await conversation_manager.handle_customer_message(
        order_id=order_id,
        customer_id="CUST123",
        message="Hola, quiero un California Roll"
    )
    assert "Bienvenido" in response
    
    # Test kitchen acknowledgment
    response = await conversation_manager.handle_kitchen_message(
        order_id=order_id,
        staff_id="STAFF123",
        message="15 minutos"
    )
    assert "tiempo de preparación" in response.lower()
    
    # Test driver assignment
    response = await conversation_manager.handle_driver_message(
        order_id=order_id,
        driver_id="DRIVER123",
        message="Confirmo disponibilidad"
    )
    assert "confirmado" in response.lower() 
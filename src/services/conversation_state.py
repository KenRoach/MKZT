from enum import Enum
from typing import Dict, Any, Optional
from datetime import datetime
import json

class OrderState(Enum):
    INITIAL = "initial"
    MENU_BROWSING = "menu_browsing"
    ITEM_SELECTION = "item_selection"
    EXTRAS_OFFERING = "extras_offering"
    PAYMENT_SELECTION = "payment_selection"
    PAYMENT_PENDING = "payment_pending"
    ORDER_CONFIRMED = "order_confirmed"
    IN_PREPARATION = "in_preparation"
    IN_DELIVERY = "in_delivery"
    COMPLETED = "completed"
    FEEDBACK = "feedback"

class ConversationManager:
    def __init__(self):
        self.conversations: Dict[str, Dict[str, Any]] = {}
        
    async def get_or_create_conversation(self, user_id: str) -> Dict[str, Any]:
        """Get existing conversation or create new one"""
        if user_id not in self.conversations:
            self.conversations[user_id] = {
                "state": OrderState.INITIAL,
                "cart": [],
                "selected_restaurants": [],
                "current_order": None,
                "last_interaction": datetime.now(),
                "language": "es",  # Default to Spanish
                "context": {}
            }
        return self.conversations[user_id]
    
    async def update_state(self, user_id: str, new_state: OrderState, context: Dict[str, Any] = None):
        """Update conversation state"""
        if user_id in self.conversations:
            self.conversations[user_id]["state"] = new_state
            self.conversations[user_id]["last_interaction"] = datetime.now()
            if context:
                self.conversations[user_id]["context"].update(context)
    
    async def add_to_cart(self, user_id: str, item: Dict[str, Any]):
        """Add item to cart"""
        if user_id in self.conversations:
            self.conversations[user_id]["cart"].append(item)
    
    async def get_cart_total(self, user_id: str) -> float:
        """Calculate cart total"""
        if user_id not in self.conversations:
            return 0.0
        return sum(item["price"] * item["quantity"] for item in self.conversations[user_id]["cart"]) 
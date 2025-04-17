from typing import Dict, List, Optional
from datetime import datetime
from enum import Enum
from pydantic import BaseModel
from src.models.order import Order
from src.models.user import User
from src.utils.logger import logger
from src.config.settings import settings

class ActorType(str, Enum):
    CUSTOMER = "customer"
    KITCHEN = "kitchen"
    DRIVER = "driver"
    AI = "ai"

class ConversationState(str, Enum):
    INITIAL = "initial"
    MENU_BROWSING = "menu_browsing"
    ORDER_CONFIRMATION = "order_confirmation"
    PAYMENT_PENDING = "payment_pending"
    PAYMENT_CONFIRMED = "payment_confirmed"
    KITCHEN_ASSIGNED = "kitchen_assigned"
    PREPARING = "preparing"
    DRIVER_ASSIGNED = "driver_assigned"
    IN_DELIVERY = "in_delivery"
    DELIVERED = "delivered"
    COMPLETED = "completed"

class Message(BaseModel):
    actor_type: ActorType
    actor_id: str
    content: str
    timestamp: datetime
    metadata: Optional[Dict] = None

class ConversationHandler:
    def __init__(self):
        self.conversations: Dict[str, List[Message]] = {}
        self.states: Dict[str, ConversationState] = {}
        self.active_actors: Dict[str, Dict[ActorType, str]] = {}

    async def create_conversation(self, order_id: str) -> str:
        """Initialize a new conversation for an order"""
        self.conversations[order_id] = []
        self.states[order_id] = ConversationState.INITIAL
        self.active_actors[order_id] = {}
        return order_id

    async def add_message(self, order_id: str, message: Message):
        """Add a message to the conversation"""
        if order_id not in self.conversations:
            await self.create_conversation(order_id)
        
        self.conversations[order_id].append(message)
        await self._process_message(order_id, message)

    async def get_conversation_history(self, order_id: str) -> List[Message]:
        """Get the full conversation history"""
        return self.conversations.get(order_id, [])

    async def _process_message(self, order_id: str, message: Message):
        """Process incoming message and update conversation state"""
        current_state = self.states[order_id]
        
        if message.actor_type == ActorType.CUSTOMER:
            await self._handle_customer_message(order_id, message)
        elif message.actor_type == ActorType.KITCHEN:
            await self._handle_kitchen_message(order_id, message)
        elif message.actor_type == ActorType.DRIVER:
            await self._handle_driver_message(order_id, message)

    async def _handle_customer_message(self, order_id: str, message: Message):
        """Handle customer messages and generate appropriate responses"""
        current_state = self.states[order_id]
        
        if current_state == ConversationState.INITIAL:
            # Process initial order request
            await self._process_order_request(order_id, message)
        elif current_state == ConversationState.MENU_BROWSING:
            # Handle menu browsing interactions
            await self._handle_menu_interaction(order_id, message)
        elif current_state == ConversationState.PAYMENT_PENDING:
            # Process payment confirmation
            await self._process_payment(order_id, message)

    async def _handle_kitchen_message(self, order_id: str, message: Message):
        """Handle kitchen staff messages"""
        if "tiempo" in message.content.lower():
            # Update preparation time
            await self._update_preparation_time(order_id, message)
        elif "listo" in message.content.lower():
            # Mark order as ready for pickup
            await self._mark_order_ready(order_id)

    async def _handle_driver_message(self, order_id: str, message: Message):
        """Handle driver messages"""
        if "confirmo" in message.content.lower():
            await self._confirm_driver_assignment(order_id, message)
        elif "entregado" in message.content.lower():
            await self._mark_order_delivered(order_id)

    async def generate_ai_response(self, order_id: str, context: Dict) -> Message:
        """Generate appropriate AI response based on context"""
        current_state = self.states[order_id]
        
        if current_state == ConversationState.INITIAL:
            return await self._generate_welcome_message(context)
        elif current_state == ConversationState.MENU_BROWSING:
            return await self._generate_menu_response(context)
        elif current_state == ConversationState.PAYMENT_PENDING:
            return await self._generate_payment_instructions(context)
        # Add more response generators for different states

    async def notify_all_parties(self, order_id: str, message: str):
        """Send notifications to all relevant parties"""
        actors = self.active_actors[order_id]
        
        for actor_type, actor_id in actors.items():
            await self._send_notification(actor_type, actor_id, message)

    async def _send_notification(self, actor_type: ActorType, actor_id: str, message: str):
        """Send notification to specific actor"""
        if actor_type == ActorType.CUSTOMER:
            await self._send_whatsapp_message(actor_id, message)
        elif actor_type == ActorType.KITCHEN:
            await self._send_kitchen_notification(actor_id, message)
        elif actor_type == ActorType.DRIVER:
            await self._send_driver_notification(actor_id, message)

conversation_handler = ConversationHandler() 
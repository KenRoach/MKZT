from typing import Dict, Optional
from datetime import datetime
from src.handlers.conversation_handler import conversation_handler, ActorType, Message
from src.templates.conversation_templates import message_templates
from src.models.order import Order
from src.utils.logger import logger

class ConversationManager:
    def __init__(self):
        self.conversation_handler = conversation_handler
        self.templates = message_templates

    async def handle_customer_message(self, order_id: str, customer_id: str, message: str):
        """Handle incoming customer message"""
        msg = Message(
            actor_type=ActorType.CUSTOMER,
            actor_id=customer_id,
            content=message,
            timestamp=datetime.utcnow()
        )
        
        await self.conversation_handler.add_message(order_id, msg)
        return await self._generate_response(order_id)

    async def handle_kitchen_message(self, order_id: str, staff_id: str, message: str):
        """Handle incoming kitchen staff message"""
        msg = Message(
            actor_type=ActorType.KITCHEN,
            actor_id=staff_id,
            content=message,
            timestamp=datetime.utcnow()
        )
        
        await self.conversation_handler.add_message(order_id, msg)
        return await self._notify_relevant_parties(order_id, msg)

    async def handle_driver_message(self, order_id: str, driver_id: str, message: str):
        """Handle incoming driver message"""
        msg = Message(
            actor_type=ActorType.DRIVER,
            actor_id=driver_id,
            content=message,
            timestamp=datetime.utcnow()
        )
        
        await self.conversation_handler.add_message(order_id, msg)
        return await self._notify_relevant_parties(order_id, msg)

    async def _generate_response(self, order_id: str) -> str:
        """Generate appropriate AI response"""
        context = await self._get_conversation_context(order_id)
        return await self.conversation_handler.generate_ai_response(order_id, context)

    async def _notify_relevant_parties(self, order_id: str, message: Message):
        """Notify relevant parties based on message context"""
        context = await self._get_conversation_context(order_id)
        notifications = await self._generate_notifications(message, context)
        
        for actor_type, notification in notifications.items():
            await self.conversation_handler.notify_all_parties(order_id, notification)

    async def _get_conversation_context(self, order_id: str) -> Dict:
        """Get current conversation context"""
        history = await self.conversation_handler.get_conversation_history(order_id)
        state = self.conversation_handler.states[order_id]
        
        return {
            "history": history,
            "state": state,
            "order_id": order_id
        }

    async def _generate_notifications(self, message: Message, context: Dict) -> Dict[ActorType, str]:
        """Generate notifications for different actors based on message context"""
        notifications = {}
        
        if message.actor_type == ActorType.KITCHEN:
            if "tiempo" in message.content.lower():
                notifications[ActorType.CUSTOMER] = self.templates.DELIVERY_UPDATE.substitute(
                    driver_name="",
                    estimated_time=message.content
                )
                notifications[ActorType.DRIVER] = f"Tiempo de preparación: {message.content}"
                
        elif message.actor_type == ActorType.DRIVER:
            if "entregado" in message.content.lower():
                notifications[ActorType.CUSTOMER] = self.templates.ORDER_COMPLETE.substitute(
                    restaurant_name=context.get("restaurant_name", "")
                )
                notifications[ActorType.KITCHEN] = "Pedido entregado exitosamente"
                
        return notifications

conversation_manager = ConversationManager() 
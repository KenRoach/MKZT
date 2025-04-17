from typing import Dict, Any, List
from datetime import datetime
import asyncio
from enum import Enum
from translate import Translator

class OrderStatus(Enum):
    RECEIVED = "received"
    CONFIRMED = "confirmed"
    IN_PREPARATION = "in_preparation"
    READY_FOR_PICKUP = "ready_for_pickup"
    IN_DELIVERY = "in_delivery"
    DELIVERED = "delivered"
    CLOSED = "closed"

class MultilingualOrderHandler:
    def __init__(self):
        self.translator = Translator(to_lang="es")
        self.order_statuses = {}
        self.delivery_assignments = {}
        
    async def process_order(self, order_data: Dict[str, Any], 
                          language: str = "es") -> Dict[str, Any]:
        """Process a new order with multilingual support"""
        try:
            order_id = order_data["order_id"]
            self.order_statuses[order_id] = OrderStatus.RECEIVED
            
            # Generate multilingual order notification
            notification = await self._generate_order_notification(order_data, language)
            
            return {
                "status": "success",
                "order_id": order_id,
                "notification": notification,
                "next_steps": await self._get_next_steps(order_id, language)
            }
        except Exception as e:
            logger.error(f"Error processing order: {str(e)}")
            return {"status": "error", "message": str(e)}

    async def _generate_order_notification(self, order_data: Dict[str, Any], 
                                         language: str) -> str:
        """Generate multilingual order notification"""
        templates = {
            "es": {
                "greeting": "¡Hola {restaurant}! Nuevo pedido recibido.",
                "order_header": "🧾 Pedido #{order_id}:",
                "payment": "💰 Pago recibido vía {payment_method}",
                "delivery": "📍 Entrega: {address}",
                "prep_time": "¿Puedes confirmar el tiempo estimado de preparación?"
            },
            "en": {
                "greeting": "Hello {restaurant}! New order received.",
                "order_header": "🧾 Order #{order_id}:",
                "payment": "💰 Payment received via {payment_method}",
                "delivery": "📍 Delivery to: {address}",
                "prep_time": "Can you confirm the estimated preparation time?"
            }
        }
        
        template = templates.get(language, templates["en"])
        
        items_text = "\n".join([
            f"• {item['quantity']}x {item['name']} ({item['restaurant']})"
            for item in order_data["items"]
        ])
        
        notification = (
            f"{template['greeting']}\n\n"
            f"{template['order_header']}\n"
            f"{items_text}\n"
            f"{template['payment']}\n"
            f"{template['delivery']}\n\n"
            f"{template['prep_time']}"
        ).format(
            restaurant=order_data["restaurant"],
            order_id=order_data["order_id"],
            payment_method=order_data["payment_method"],
            address=order_data["delivery_address"]
        )
        
        return notification

    async def confirm_preparation_time(self, order_id: str, prep_time: int, 
                                     language: str = "es") -> Dict[str, Any]:
        """Handle preparation time confirmation"""
        templates = {
            "es": {
                "confirmed": "✅ Tiempo confirmado: {prep_time} minutos.",
                "coordinating": "Coordinando motorizado para la recolección.",
                "notification": "Te notificaremos cuando llegue al punto de retiro."
            },
            "en": {
                "confirmed": "✅ Time confirmed: {prep_time} minutes.",
                "coordinating": "Coordinating driver for pickup.",
                "notification": "We'll notify you when they arrive for pickup."
            }
        }
        
        template = templates.get(language, templates["en"])
        
        self.order_statuses[order_id] = OrderStatus.CONFIRMED
        
        response = (
            f"{template['confirmed']}\n"
            f"{template['coordinating']}\n"
            f"{template['notification']}"
        ).format(prep_time=prep_time)
        
        return {
            "status": "success",
            "message": response,
            "order_status": self.order_statuses[order_id].value
        }

    async def assign_driver(self, order_id: str, driver_data: Dict[str, Any], 
                          language: str = "es") -> Dict[str, Any]:
        """Assign driver to order"""
        templates = {
            "es": {
                "assigned": "🚴‍♂️ El motorizado {driver} ha sido asignado al pedido #{order_id}.",
                "en_route": "Está en camino a {restaurant} para la recogida.",
                "track": "📍 Ver ubicación en tiempo real: {tracking_url}"
            },
            "en": {
                "assigned": "🚴‍♂️ Driver {driver} has been assigned to order #{order_id}.",
                "en_route": "They're on their way to {restaurant} for pickup.",
                "track": "📍 Track real-time location: {tracking_url}"
            }
        }
        
        template = templates.get(language, templates["en"])
        
        self.delivery_assignments[order_id] = driver_data
        self.order_statuses[order_id] = OrderStatus.IN_DELIVERY
        
        tracking_url = f"mealkitz.io/ubicacion/{driver_data['id']}-ruta"
        
        notification = (
            f"{template['assigned']}\n"
            f"{template['en_route']}\n\n"
            f"{template['track']}"
        ).format(
            driver=driver_data["name"],
            order_id=order_id,
            restaurant=driver_data["pickup_location"],
            tracking_url=tracking_url
        )
        
        return {
            "status": "success",
            "message": notification,
            "tracking_url": tracking_url
        }

    async def confirm_delivery(self, order_id: str, 
                             language: str = "es") -> Dict[str, Any]:
        """Confirm order delivery"""
        templates = {
            "es": {
                "delivered": "📬 {driver} confirmó la entrega del pedido #{order_id}.",
                "congrats": "🎉 ¡Buen trabajo!",
                "dashboard": "📊 Puedes revisar los detalles en tu dashboard:",
                "close_prompt": "¿Deseas dejar una nota o marcar el pedido como finalizado?"
            },
            "en": {
                "delivered": "📬 {driver} confirmed delivery of order #{order_id}.",
                "congrats": "🎉 Great job!",
                "dashboard": "📊 You can review the details in your dashboard:",
                "close_prompt": "Would you like to leave a note or mark the order as closed?"
            }
        }
        
        template = templates.get(language, templates["en"])
        driver_data = self.delivery_assignments.get(order_id, {})
        
        notification = (
            f"{template['delivered']}\n"
            f"{template['congrats']}\n"
            f"{template['dashboard']}\n"
            f"mealkitz.io/dashboard\n\n"
            f"{template['close_prompt']}"
        ).format(
            driver=driver_data.get("name", "Driver"),
            order_id=order_id
        )
        
        self.order_statuses[order_id] = OrderStatus.DELIVERED
        
        return {
            "status": "success",
            "message": notification,
            "order_status": self.order_statuses[order_id].value
        }

    async def close_order(self, order_id: str, 
                         language: str = "es") -> Dict[str, Any]:
        """Close the order"""
        templates = {
            "es": {
                "closed": "✅ Pedido cerrado oficialmente.",
                "thanks": "Gracias por ser parte de Mealkitz.",
                "next": "Te notificaremos en cuanto llegue un nuevo pedido 🙌"
            },
            "en": {
                "closed": "✅ Order officially closed.",
                "thanks": "Thank you for being part of Mealkitz.",
                "next": "We'll notify you when a new order arrives 🙌"
            }
        }
        
        template = templates.get(language, templates["en"])
        
        self.order_statuses[order_id] = OrderStatus.CLOSED
        
        notification = (
            f"{template['closed']}\n"
            f"{template['thanks']}\n"
            f"{template['next']}"
        )
        
        return {
            "status": "success",
            "message": notification,
            "order_status": self.order_statuses[order_id].value
        } 
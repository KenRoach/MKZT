from typing import Dict, Any, List
from datetime import datetime
from enum import Enum
from src.utils.logger import logger

class OrderStatus(Enum):
    RECEIVED = "received"
    CONFIRMED = "confirmed"
    IN_PREPARATION = "in_preparation"
    READY = "ready"
    PICKED_UP = "picked_up"
    DELIVERED = "delivered"
    CLOSED = "closed"

class RestaurantDashboardHandler:
    def __init__(self):
        self.active_orders: Dict[str, Dict[str, Any]] = {}
        self.order_history: List[Dict[str, Any]] = []
        
    async def process_message(self, restaurant_id: str, message: str) -> Dict[str, Any]:
        """Process incoming message from restaurant"""
        try:
            # Get restaurant context
            context = await self._get_restaurant_context(restaurant_id)
            
            # Process based on message intent
            if "tiempo" in message.lower() or "minutos" in message.lower():
                return await self._handle_preparation_time(restaurant_id, message)
            elif "listo" in message.lower() or "completado" in message.lower():
                return await self._handle_order_ready(restaurant_id, message)
            elif "cerrado" in message.lower():
                return await self._handle_order_closure(restaurant_id, message)
            
            return {
                "status": "error",
                "message": "No se pudo determinar la acción a realizar"
            }
            
        except Exception as e:
            logger.error(f"Error processing restaurant message: {str(e)}")
            return {"status": "error", "message": str(e)}
    
    async def notify_new_order(self, order: Dict[str, Any]) -> Dict[str, Any]:
        """Send new order notification to restaurant"""
        try:
            # Format order items for this restaurant
            restaurant_items = [
                item for item in order["items"] 
                if item["restaurant_id"] == order["restaurant_id"]
            ]
            
            message = (
                f"📢 ¡Hola {order['restaurant_name']}!\n"
                f"Acabamos de recibir un nuevo pedido.\n\n"
                f"🧾 Pedido #{order['order_id']}:\n"
            )
            
            for item in restaurant_items:
                message += f"• {item['quantity']}x {item['name']}\n"
            
            message += f"\n💰 Pago confirmado por {order['payment_method']}\n"
            message += f"📍 Entrega: {order['delivery_address']}\n"
            message += "¿Puedes confirmar el tiempo estimado de preparación?"
            
            return {
                "status": "success",
                "message": message,
                "quick_replies": ["15 minutos", "20 minutos", "30 minutos"]
            }
            
        except Exception as e:
            logger.error(f"Error notifying new order: {str(e)}")
            return {"status": "error", "message": str(e)}
    
    async def notify_driver_assignment(self, order_id: str, driver: Dict[str, Any]) -> Dict[str, Any]:
        """Notify restaurant about driver assignment"""
        try:
            message = (
                f"📦 El motorizado {driver['name']} ha sido asignado para este pedido.\n"
                f"🚴‍♂️ Se dirige a tu local para el retiro.\n\n"
                f"📍 Ver ubicación: mealkitz.io/ubicacion/{driver['route_id']}"
            )
            
            return {
                "status": "success",
                "message": message
            }
            
        except Exception as e:
            logger.error(f"Error notifying driver assignment: {str(e)}")
            return {"status": "error", "message": str(e)}
    
    async def notify_order_delivered(self, order_id: str) -> Dict[str, Any]:
        """Notify restaurant about successful delivery"""
        try:
            order = self.active_orders.get(order_id)
            if not order:
                return {"status": "error", "message": "Orden no encontrada"}
            
            message = (
                f"📬 Entrega exitosa del pedido #{order_id}.\n"
                f"🎉 ¡Buen trabajo!\n"
                f"Puedes revisar el detalle en tu dashboard:\n"
                f"📊 mealkitz.io/{order['restaurant_slug']}/dashboard\n\n"
                f"¿Deseas dejar alguna nota interna o marcar el pedido como cerrado?"
            )
            
            return {
                "status": "success",
                "message": message,
                "quick_replies": ["Cerrar pedido", "Agregar nota", "Ver detalles"]
            }
            
        except Exception as e:
            logger.error(f"Error notifying delivery: {str(e)}")
            return {"status": "error", "message": str(e)}
    
    async def _handle_preparation_time(self, restaurant_id: str, message: str) -> Dict[str, Any]:
        """Handle preparation time confirmation"""
        try:
            # Extract time from message
            time_minutes = self._extract_time(message)
            
            if not time_minutes:
                return {
                    "status": "error",
                    "message": "No se pudo determinar el tiempo de preparación"
                }
            
            message = (
                f"✅ Confirmado: {time_minutes} minutos.\n"
                f"Coordinaremos con otros restaurantes para alinear los tiempos.\n"
                f"Te avisaremos cuando el motorizado llegue al punto de retiro."
            )
            
            return {
                "status": "success",
                "message": message,
                "preparation_time": time_minutes
            }
            
        except Exception as e:
            logger.error(f"Error handling preparation time: {str(e)}")
            return {"status": "error", "message": str(e)}
    
    async def _handle_order_ready(self, restaurant_id: str, message: str) -> Dict[str, Any]:
        """Handle order ready notification"""
        try:
            message = (
                f"✅ Pedido marcado como listo.\n"
                f"El motorizado ha sido notificado."
            )
            
            return {
                "status": "success",
                "message": message
            }
            
        except Exception as e:
            logger.error(f"Error handling order ready: {str(e)}")
            return {"status": "error", "message": str(e)}
    
    async def _handle_order_closure(self, restaurant_id: str, message: str) -> Dict[str, Any]:
        """Handle order closure"""
        try:
            message = (
                f"✅ Pedido cerrado oficialmente.\n"
                f"¡Gracias por ser parte de Mealkitz!\n"
                f"Te notificaremos cuando entre un nuevo pedido 🙌"
            )
            
            return {
                "status": "success",
                "message": message
            }
            
        except Exception as e:
            logger.error(f"Error handling order closure: {str(e)}")
            return {"status": "error", "message": str(e)}
    
    def _extract_time(self, message: str) -> int:
        """Extract time in minutes from message"""
        try:
            # Simple time extraction - can be enhanced with NLP
            words = message.lower().split()
            for i, word in enumerate(words):
                if word.isdigit():
                    return int(word)
                if i < len(words) - 1 and word + words[i+1] == "quince minutos":
                    return 15
                if i < len(words) - 1 and word + words[i+1] == "veinte minutos":
                    return 20
                if i < len(words) - 1 and word + words[i+1] == "treinta minutos":
                    return 30
            return None
        except Exception:
            return None 
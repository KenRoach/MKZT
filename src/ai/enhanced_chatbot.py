from typing import Dict, Any, List
from src.services.conversation_state import ConversationManager, OrderState
from src.services.restaurant_service import RestaurantService
from src.services.nlp_service import NLPService
from src.utils.logger import logger

class EnhancedChatbot:
    def __init__(self):
        self.conversation_manager = ConversationManager()
        self.restaurant_service = RestaurantService()
        self.nlp_service = NLPService()
        
    async def process_message(self, user_id: str, message: str) -> Dict[str, Any]:
        """Process incoming message and generate response"""
        try:
            # Get or create conversation
            conversation = await self.conversation_manager.get_or_create_conversation(user_id)
            
            # Analyze intent
            intent = await self.nlp_service.analyze_intent(message)
            
            # Process based on current state
            if conversation["state"] == OrderState.INITIAL:
                return await self._handle_initial_state(user_id, message, intent)
            elif conversation["state"] == OrderState.MENU_BROWSING:
                return await self._handle_menu_browsing(user_id, message, intent)
            elif conversation["state"] == OrderState.ITEM_SELECTION:
                return await self._handle_item_selection(user_id, message, intent)
            elif conversation["state"] == OrderState.EXTRAS_OFFERING:
                return await self._handle_extras_offering(user_id, message, intent)
            elif conversation["state"] == OrderState.PAYMENT_SELECTION:
                return await self._handle_payment_selection(user_id, message, intent)
            
        except Exception as e:
            logger.error(f"Error processing message: {str(e)}")
            return self._generate_error_response()
    
    async def _handle_initial_state(self, user_id: str, message: str, intent: Dict) -> Dict[str, Any]:
        """Handle initial greeting and food type selection"""
        if "greeting" in intent["intents"]:
            return {
                "response": "🍱🍔 ¡Hola! Gracias por escribirle a Mealkitz AI.\n¿Te gustaría ver opciones de sushi, hamburguesas, o ambos?",
                "quick_replies": ["Sushi", "Hamburguesas", "Ambos"]
            }
        
        # Search for restaurants based on food type
        restaurants = await self.restaurant_service.search_restaurants(message)
        if restaurants:
            await self.conversation_manager.update_state(
                user_id,
                OrderState.MENU_BROWSING,
                {"available_restaurants": restaurants}
            )
            return self._format_restaurant_options(restaurants)
    
    async def _handle_menu_browsing(self, user_id: str, message: str, intent: Dict) -> Dict[str, Any]:
        """Handle menu browsing and item selection"""
        conversation = await self.conversation_manager.get_or_create_conversation(user_id)
        
        if "select_item" in intent["intents"]:
            # Extract item and quantity from message
            items = await self._extract_order_items(message, conversation["context"]["available_restaurants"])
            
            # Add items to cart
            for item in items:
                await self.conversation_manager.add_to_cart(user_id, item)
            
            # Generate cart summary
            cart_summary = await self._generate_cart_summary(user_id)
            
            # Move to extras offering
            await self.conversation_manager.update_state(user_id, OrderState.EXTRAS_OFFERING)
            
            return {
                "response": f"{cart_summary}\n\n¿Te gustaría agregar una bebida o postre? 🍹🍰\n• Té Frío – $1.50\n• Brownie con Helado – $3.00\n• Mousse de Maracuyá – $2.50",
                "quick_replies": ["Agregar bebida", "Agregar postre", "Continuar al pago"]
            }
    
    async def _handle_extras_offering(self, user_id: str, message: str, intent: Dict) -> Dict[str, Any]:
        """Handle extras selection"""
        if "add_item" in intent["intents"]:
            # Extract and add extra item
            extra_item = await self._extract_extra_item(message)
            if extra_item:
                await self.conversation_manager.add_to_cart(user_id, extra_item)
            
            # Move to payment selection
            await self.conversation_manager.update_state(user_id, OrderState.PAYMENT_SELECTION)
            
            return {
                "response": f"✅ Agregado.\nNuevo total: ${await self.conversation_manager.get_cart_total(user_id):.2f}\n\n¿Cómo deseas pagar?\n💳 En línea\n💵 Yappy\n💸 Efectivo al entregar",
                "quick_replies": ["En línea", "Yappy", "Efectivo"]
            }
    
    async def _handle_payment_selection(self, user_id: str, message: str, intent: Dict) -> Dict[str, Any]:
        """Handle payment method selection"""
        if "select_payment" in intent["intents"]:
            payment_method = self._extract_payment_method(message)
            
            # Update state to payment pending
            await self.conversation_manager.update_state(
                user_id,
                OrderState.PAYMENT_PENDING,
                {"payment_method": payment_method}
            )
            
            if payment_method == "yappy":
                return {
                    "response": "💚 ¡Gracias por elegir Mealkitz!\n👉 Realiza tu pago aquí: mealkitz.io/pago\nUna vez confirmado, empezaremos a preparar tu pedido."
                }
    
    def _format_restaurant_options(self, restaurants: List[Dict]) -> Dict[str, Any]:
        """Format restaurant options message"""
        response = "Perfecto. Aquí te presento opciones de dos de nuestros emprendedores:\n\n"
        
        for restaurant in restaurants:
            response += f"🍣 {restaurant['name']}\n"
            for item in restaurant['popular_items']:
                response += f"• {item['name']} – ${item['price']:.2f}\n"
            response += f"🖼️ Menú completo: mealkitz.io/restaurantes/{restaurant['slug']}\n\n"
        
        response += "¿Qué deseas agregar al pedido?"
        
        return {
            "response": response,
            "quick_replies": ["Ver más opciones", "Ayuda con el pedido"]
        }
    
    async def _generate_cart_summary(self, user_id: str) -> str:
        """Generate cart summary message"""
        conversation = await self.conversation_manager.get_or_create_conversation(user_id)
        
        summary = "✅ Pedido actual:\n"
        for item in conversation["cart"]:
            summary += f"• {item['quantity']}x {item['name']} – ${item['price']:.2f}\n"
        summary += f"Subtotal: ${await self.conversation_manager.get_cart_total(user_id):.2f}"
        
        return summary
    
    def _generate_error_response(self) -> Dict[str, Any]:
        """Generate error response"""
        return {
            "response": "Lo siento, hubo un error procesando tu mensaje. ¿Podrías intentarlo de nuevo?",
            "quick_replies": ["Comenzar de nuevo", "Ayuda"]
        } 
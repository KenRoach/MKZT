from typing import Dict, List, Optional
from datetime import datetime
from src.services.nlp_processor import nlp_processor
from src.templates.enhanced_templates import template_manager
from src.models.conversation_state import state_manager
from src.utils.logger import logger

class ConversationEnhancer:
    def __init__(self):
        self.nlp_processor = nlp_processor
        self.template_manager = template_manager
        self.state_manager = state_manager

    async def process_message(self, message: str, context: Dict) -> Dict:
        """Process message with enhanced features"""
        # Analyze message
        analysis = await self.nlp_processor.analyze_message(message)
        
        # Update context with analysis
        context.update({
            "intent": analysis["intent"],
            "sentiment": analysis["sentiment"],
            "entities": analysis["entities"],
            "urgency": analysis["urgency"],
            "formality": analysis["formality"]
        })
        
        # Get next state
        next_state = await self.state_manager.get_next_state(
            context["current_state"],
            context
        )
        
        # Handle state
        context = await self.state_manager.handle_state(next_state, context)
        
        # Generate response
        response = await self._generate_enhanced_response(context)
        
        return {
            "response": response,
            "context": context,
            "next_state": next_state
        }

    async def _generate_enhanced_response(self, context: Dict) -> str:
        """Generate enhanced response based on context"""
        # Select appropriate template based on state and context
        template_name = self._select_template(context)
        
        # Add dynamic content
        context = await self._add_dynamic_content(context)
        
        # Render template
        return self.template_manager.render_template(template_name, context)

    def _select_template(self, context: Dict) -> str:
        """Select appropriate template based on context"""
        state = context["current_state"]
        intent = context.get("intent", {})
        sentiment = context.get("sentiment", 0)
        
        if state == "greeting":
            return "WELCOME"
        elif state == "menu_browsing":
            return "MENU_SUGGESTION"
        elif state == "payment_confirmed":
            return "PAYMENT_CONFIRMATION"
        elif "status" in intent:
            return "ORDER_STATUS"
        
        return "DEFAULT"

    async def _add_dynamic_content(self, context: Dict) -> Dict:
        """Add dynamic content to context"""
        enhanced_context = context.copy()
        
        # Add personalization
        if context.get("customer_history"):
            enhanced_context["is_returning_customer"] = True
            enhanced_context["custom_greeting"] = self._generate_personal_greeting(context)
            
        # Add promotions
        if context.get("current_state") == "menu_browsing":
            enhanced_context["promotion_text"] = await self._get_relevant_promotions(context)
            
        # Add recommendations
        if context.get("order_items"):
            enhanced_context["recommendations"] = await self._generate_recommendations(context)
            
        return enhanced_context

    def _generate_personal_greeting(self, context: Dict) -> str:
        """Generate personalized greeting"""
        customer_name = context.get("customer_name", "")
        last_visit = context.get("last_visit")
        favorite_items = context.get("favorite_items", [])
        
        if last_visit and favorite_items:
            days_since = (datetime.now() - last_visit).days
            return f"¡Qué gusto verte de nuevo, {customer_name}! ¿Te gustaría repetir tu {favorite_items[0]}?"
            
        return f"¡Bienvenido de nuevo, {customer_name}!"

    async def _get_relevant_promotions(self, context: Dict) -> str:
        """Get relevant promotions based on context"""
        time_of_day = datetime.now().hour
        day_of_week = datetime.now().weekday()
        
        promotions = []
        if 11 <= time_of_day <= 15:
            promotions.append("🌟 ¡Promoción de almuerzo! 15% de descuento")
        if day_of_week in [5, 6]:  # Weekend
            promotions.append("🎉 ¡Especial de fin de semana! Postre gratis en pedidos +$20")
            
        return "\n".join(promotions) if promotions else ""

    async def _generate_recommendations(self, context: Dict) -> List[Dict]:
        """Generate personalized recommendations"""
        current_items = context.get("order_items", [])
        customer_history = context.get("customer_history", [])
        
        # Implement recommendation logic
        recommendations = []
        # Add recommendation logic here
        
        return recommendations

conversation_enhancer = ConversationEnhancer() 
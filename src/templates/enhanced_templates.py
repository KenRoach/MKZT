from typing import Dict, List, Optional
from string import Template
from datetime import datetime
import json
from src.utils.emoji_manager import get_emoji
from src.config.settings import settings

class EnhancedTemplate:
    def __init__(self, template: str, conditions: Dict = None):
        self.template = template
        self.conditions = conditions or {}
        
    def render(self, context: Dict) -> str:
        # Apply conditions
        template_to_use = self._apply_conditions(context)
        # Replace variables
        return Template(template_to_use).safe_substitute(context)
        
    def _apply_conditions(self, context: Dict) -> str:
        template_parts = []
        current_template = self.template
        
        for condition, sub_template in self.conditions.items():
            if eval(condition, {"context": context}):
                current_template = sub_template
                break
                
        return current_template

class EnhancedTemplateManager:
    def __init__(self):
        self.templates = self._load_templates()
        self.emoji_manager = get_emoji()

    def _load_templates(self) -> Dict[str, EnhancedTemplate]:
        return {
            "WELCOME": EnhancedTemplate(
                template="""
${emoji_restaurant} Bienvenido a ${restaurant_name}
${emoji_receipt} Pedido:
${order_items}
Total: $${total}
${custom_greeting}
                """.strip(),
                conditions={
                    "context.get('is_returning_customer')": """
${emoji_restaurant} ¡Bienvenido de nuevo a ${restaurant_name}!
${emoji_star} Nos alegra verte otra vez.
${emoji_receipt} Tu pedido:
${order_items}
Total: $${total}
${custom_greeting}
                    """.strip()
                }
            ),
            
            "MENU_SUGGESTION": EnhancedTemplate(
                template="""
${emoji_menu} Sugerencias basadas en tus preferencias:
${menu_items}
${promotion_text}
                """.strip(),
                conditions={
                    "context.get('has_dietary_restrictions')": """
${emoji_menu} Opciones que se ajustan a tus preferencias dietéticas:
${menu_items}
${promotion_text}
                    """.strip()
                }
            ),
            
            "ORDER_STATUS": EnhancedTemplate(
                template="""
${emoji_status} Estado de tu pedido: ${status}
${emoji_time} Tiempo estimado: ${estimated_time} minutos
${tracking_info}
                """.strip(),
                conditions={
                    "context.get('status') == 'delayed'": """
${emoji_status} Estado de tu pedido: ${status}
${emoji_time} Nuevo tiempo estimado: ${estimated_time} minutos
${emoji_sorry} Disculpa el retraso.
${compensation_offer}
                    """.strip()
                }
            ),
            
            "PAYMENT_CONFIRMATION": EnhancedTemplate(
                template="""
${emoji_check} Pago confirmado: $${amount}
${emoji_cooking} ¡Comenzamos a preparar tu pedido!
${order_details}
                """.strip(),
                conditions={
                    "float(context.get('amount', 0)) > 50": """
${emoji_check} Pago confirmado: $${amount}
${emoji_gift} ¡Regalo especial por tu compra!
${emoji_cooking} ¡Comenzamos a preparar tu pedido!
${order_details}
                    """.strip()
                }
            )
        }

    def render_template(self, template_name: str, context: Dict) -> str:
        """Render a template with given context"""
        if template_name not in self.templates:
            raise ValueError(f"Template {template_name} not found")
            
        # Add emojis to context
        context.update({
            f"emoji_{name}": self.emoji_manager.get(name)
            for name in ["restaurant", "receipt", "menu", "status", "time", 
                        "check", "cooking", "gift", "sorry"]
        })
        
        # Add custom formatting
        context = self._enhance_context(context)
        
        return self.templates[template_name].render(context)

    def _enhance_context(self, context: Dict) -> Dict:
        """Enhance context with formatted data"""
        enhanced = context.copy()
        
        # Format currency
        if "total" in enhanced:
            enhanced["total"] = f"{float(enhanced['total']):,.2f}"
            
        # Format timestamps
        if "timestamp" in enhanced:
            dt = datetime.fromisoformat(enhanced["timestamp"])
            enhanced["formatted_time"] = dt.strftime("%I:%M %p")
            enhanced["formatted_date"] = dt.strftime("%d/%m/%Y")
            
        # Format order items
        if "order_items" in enhanced and isinstance(enhanced["order_items"], list):
            enhanced["order_items"] = "\n".join(
                f"• {item['quantity']}x {item['name']} (${item['price']:,.2f})"
                for item in enhanced["order_items"]
            )
            
        return enhanced

template_manager = EnhancedTemplateManager() 
from typing import Dict, List
from string import Template

class MessageTemplates:
    WELCOME = Template("""
🍣 Bienvenido a $restaurant_name.
🧾 Pedido:
$order_items
Total: $$total
¿Deseas ver nuestro menú de postres?
    """.strip())

    DESSERT_MENU = Template("""
$dessert_items
¿Quieres ver una foto del $dessert_name?
    """.strip())

    PAYMENT_INSTRUCTIONS = Template("""
✅ Nuevo total: $$total
¿Cómo deseas pagar?
💳 En línea / 💵 Yappy
    """.strip())

    ORDER_CONFIRMATION = Template("""
✅ ¡Tu pedido ha sido aceptado por $restaurant_name!
Estamos preparando tu comida y hemos asignado a un motorizado para la entrega.
🛵 Te avisaremos cuando esté en camino.
    """.strip())

    KITCHEN_NOTIFICATION = Template("""
📢 Nuevo pedido recibido:
$order_items
💰 Pagado por $payment_method
📍 $delivery_address
¿Tiempo estimado de preparación?
    """.strip())

    DRIVER_ASSIGNMENT = Template("""
📦 Nuevo pedido asignado:
Pedido #$order_id – $restaurant_name
📍 Entrega: $delivery_address
¿Confirmas disponibilidad?
    """.strip())

    DELIVERY_UPDATE = Template("""
🚚 Tu pedido va en camino con $driver_name.
📍 Entrega estimada: $estimated_time minutos
    """.strip())

    ORDER_COMPLETE = Template("""
🙌 ¡Gracias por ordenar con $restaurant_name a través de Mealkitz!
¿Nos ayudas con una encuesta rápida?
👉 mealkitz.io/encuesta
    """.strip())

    def format_order_items(self, items: List[Dict]) -> str:
        return "\n".join([f"• {item['quantity']}x {item['name']}" for item in items])

message_templates = MessageTemplates() 
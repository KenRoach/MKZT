from typing import Dict, Any

class LanguageConfig:
    SUPPORTED_LANGUAGES = ["en", "es", "pt"]
    DEFAULT_LANGUAGE = "en"
    
    MESSAGES = {
        "en": {
            "order_confirmation": {
                "title": "Order Confirmation",
                "order_id": "Order ID",
                "items": "Items",
                "total_amount": "Total Amount",
                "delivery_address": "Delivery Address",
                "estimated_delivery": "Estimated Delivery",
                "thank_you": "Thank you for your order!"
            },
            "order_update": {
                "title": "Order Update",
                "order_id": "Order ID",
                "status": "Status",
                "details": "Details"
            },
            "tracking_update": {
                "title": "Order Tracking Update",
                "order_id": "Order ID",
                "status": "Status",
                "driver_location": "Driver Location",
                "estimated_delivery": "Estimated Delivery"
            }
        },
        "es": {
            "order_confirmation": {
                "title": "Confirmación de Pedido",
                "order_id": "ID del Pedido",
                "items": "Artículos",
                "total_amount": "Monto Total",
                "delivery_address": "Dirección de Entrega",
                "estimated_delivery": "Entrega Estimada",
                "thank_you": "¡Gracias por tu pedido!"
            },
            "order_update": {
                "title": "Actualización de Pedido",
                "order_id": "ID del Pedido",
                "status": "Estado",
                "details": "Detalles"
            },
            "tracking_update": {
                "title": "Actualización de Seguimiento",
                "order_id": "ID del Pedido",
                "status": "Estado",
                "driver_location": "Ubicación del Repartidor",
                "estimated_delivery": "Entrega Estimada"
            }
        },
        "pt": {
            "order_confirmation": {
                "title": "Confirmação do Pedido",
                "order_id": "ID do Pedido",
                "items": "Itens",
                "total_amount": "Valor Total",
                "delivery_address": "Endereço de Entrega",
                "estimated_delivery": "Entrega Estimada",
                "thank_you": "Obrigado pelo seu pedido!"
            },
            "order_update": {
                "title": "Atualização do Pedido",
                "order_id": "ID do Pedido",
                "status": "Status",
                "details": "Detalhes"
            },
            "tracking_update": {
                "title": "Atualização de Rastreamento",
                "order_id": "ID do Pedido",
                "status": "Status",
                "driver_location": "Localização do Entregador",
                "estimated_delivery": "Entrega Estimada"
            }
        }
    }
    
    @classmethod
    def get_message(cls, language: str, message_type: str, key: str) -> str:
        """Get localized message"""
        if language not in cls.SUPPORTED_LANGUAGES:
            language = cls.DEFAULT_LANGUAGE
        
        return cls.MESSAGES[language][message_type][key]
    
    @classmethod
    def format_currency(cls, amount: float, language: str) -> str:
        """Format currency based on language"""
        if language == "en":
            return f"${amount:.2f}"
        elif language == "es":
            return f"${amount:.2f} MXN"
        elif language == "pt":
            return f"R${amount:.2f}"
        else:
            return f"${amount:.2f}" 
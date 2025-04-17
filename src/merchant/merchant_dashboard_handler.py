from typing import Dict, Any, List
from datetime import datetime, timedelta
import asyncio
from enum import Enum
from decimal import Decimal
import json

class MerchantSession:
    def __init__(self, merchant_id: str, restaurant_name: str):
        self.merchant_id = merchant_id
        self.restaurant_name = restaurant_name
        self.last_activity = datetime.now()
        self.current_view = "main_menu"
        self.language = "es"

class SalesChannel(Enum):
    WHATSAPP = "whatsapp"
    INSTAGRAM = "instagram"
    WEBSITE = "website"
    MANUAL = "manual"

class MerchantDashboardHandler:
    def __init__(self):
        self.active_sessions = {}
        self.load_templates()
        
    def load_templates(self):
        """Load merchant dashboard templates"""
        with open('src/templates/merchant_templates.json', 'r', encoding='utf-8') as f:
            self.templates = json.load(f)

    async def authenticate_merchant(self, 
                                  credentials: str) -> Dict[str, Any]:
        """Authenticate merchant and create session"""
        try:
            # In real implementation, verify credentials against database
            merchant_data = await self._verify_credentials(credentials)
            
            if merchant_data:
                session = MerchantSession(
                    merchant_data["merchant_id"],
                    merchant_data["restaurant_name"]
                )
                self.active_sessions[merchant_data["merchant_id"]] = session
                
                return await self._generate_welcome_message(session)
            else:
                return {
                    "status": "error",
                    "message": "Credenciales inválidas. Por favor intenta nuevamente."
                }
        except Exception as e:
            logger.error(f"Authentication error: {str(e)}")
            return {"status": "error", "message": str(e)}

    async def process_merchant_input(self, 
                                   merchant_id: str, 
                                   input_text: str) -> Dict[str, Any]:
        """Process merchant input and generate response"""
        try:
            session = self.active_sessions.get(merchant_id)
            if not session:
                return {"status": "error", "message": "Sesión no encontrada"}
                
            # Update session activity
            session.last_activity = datetime.now()
            
            # Process input based on current view
            if session.current_view == "main_menu":
                return await self._process_main_menu_input(session, input_text)
            elif session.current_view == "sales_summary":
                return await self._process_sales_input(session, input_text)
            elif session.current_view == "inventory":
                return await self._process_inventory_input(session, input_text)
            else:
                return await self._generate_main_menu(session)
                
        except Exception as e:
            logger.error(f"Error processing merchant input: {str(e)}")
            return {"status": "error", "message": str(e)}

    async def _process_main_menu_input(self, 
                                     session: MerchantSession, 
                                     input_text: str) -> Dict[str, Any]:
        """Process main menu selections"""
        menu_options = {
            "1": "sales",
            "ventas": "sales",
            "2": "inventory",
            "inventario": "inventory",
            "3": "menu",
            "menú": "menu",
            "4": "orders",
            "pedidos": "orders",
            "5": "promotions",
            "promociones": "promotions",
            "6": "customers",
            "clientes": "customers",
            "7": "schedule",
            "horario": "schedule",
            "8": "support",
            "soporte": "support",
            "9": "logout",
            "cerrar": "logout"
        }
        
        action = menu_options.get(input_text.lower())
        
        if action == "sales":
            session.current_view = "sales_summary"
            return await self._generate_sales_summary(session)
        elif action == "inventory":
            session.current_view = "inventory"
            return await self._generate_inventory_summary(session)
        elif action == "logout":
            return await self._handle_logout(session)
        else:
            return {
                "status": "error",
                "message": "Opción no válida. Por favor selecciona una opción del menú."
            }

    async def _generate_sales_summary(self, 
                                    session: MerchantSession) -> Dict[str, Any]:
        """Generate sales summary for merchant"""
        sales_data = await self._fetch_sales_data(session.merchant_id)
        
        summary = {
            "total_sales": Decimal("128.50"),
            "total_orders": 14,
            "average_ticket": Decimal("9.18"),
            "channels": {
                "whatsapp": {
                    "sales": Decimal("52.00"),
                    "orders": 6,
                    "average": Decimal("8.67")
                },
                "instagram": {
                    "sales": Decimal("22.50"),
                    "orders": 3,
                    "average": Decimal("7.50")
                },
                "website": {
                    "sales": Decimal("41.00"),
                    "orders": 4,
                    "average": Decimal("10.25")
                },
                "manual": {
                    "sales": Decimal("13.00"),
                    "orders": 1,
                    "average": Decimal("13.00")
                }
            }
        }
        
        template = self.templates[session.language]["sales_summary"]
        
        message = template["summary"].format(
            total=summary["total_sales"],
            orders=summary["total_orders"],
            average=summary["average_ticket"]
        )
        
        return {
            "status": "success",
            "message": message,
            "data": summary,
            "prompt": template["prompt"]
        }

    async def _process_sales_input(self, 
                                 session: MerchantSession, 
                                 input_text: str) -> Dict[str, Any]:
        """Process sales view inputs"""
        if input_text.lower() in ["si", "sí", "yes", "s", "y"]:
            sales_data = await self._fetch_sales_data(session.merchant_id)
            template = self.templates[session.language]["sales_channels"]
            
            channels_summary = template["header"] + "\n\n"
            
            for channel, data in sales_data["channels"].items():
                channels_summary += template["channel_format"].format(
                    icon=template["channel_icons"][channel],
                    sales=data["sales"],
                    orders=data["orders"],
                    average=data["average"]
                ) + "\n"
                
            channels_summary += "\n" + template["options"]
            
            return {
                "status": "success",
                "message": channels_summary,
                "data": sales_data
            }
        else:
            session.current_view = "main_menu"
            return await self._generate_main_menu(session)

    async def _generate_welcome_message(self, 
                                      session: MerchantSession) -> Dict[str, Any]:
        """Generate welcome message and main menu"""
        template = self.templates[session.language]["welcome"]
        
        message = template["greeting"].format(
            merchant_name="Jonathan",
            restaurant_name=session.restaurant_name
        )
        
        message += "\n\n" + template["menu_header"] + "\n"
        for option in template["menu_options"]:
            message += option + "\n"
        
        message += "\n" + template["menu_footer"]
        
        return {
            "status": "success",
            "message": message,
            "session_id": session.merchant_id
        }

    async def _fetch_sales_data(self, merchant_id: str) -> Dict[str, Any]:
        """Fetch merchant's sales data"""
        # In real implementation, fetch from database
        return {
            "total_sales": Decimal("128.50"),
            "total_orders": 14,
            "average_ticket": Decimal("9.18"),
            "channels": {
                "whatsapp": {
                    "sales": Decimal("52.00"),
                    "orders": 6,
                    "average": Decimal("8.67")
                },
                "instagram": {
                    "sales": Decimal("22.50"),
                    "orders": 3,
                    "average": Decimal("7.50")
                },
                "website": {
                    "sales": Decimal("41.00"),
                    "orders": 4,
                    "average": Decimal("10.25")
                },
                "manual": {
                    "sales": Decimal("13.00"),
                    "orders": 1,
                    "average": Decimal("13.00")
                }
            }
        } 
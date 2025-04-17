from typing import Dict, Any, List
from datetime import datetime, timedelta
from enum import Enum
from decimal import Decimal
import asyncio

class SalesChannel(Enum):
    WHATSAPP = "whatsapp"
    INSTAGRAM = "instagram"
    WEBSITE = "website"
    PHONE = "phone"

class ProductStatus(Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    LOW_STOCK = "low_stock"
    OUT_OF_STOCK = "out_of_stock"

class AdvancedMerchantSystem:
    def __init__(self):
        self.load_templates()
        self.active_merchants = {}
        self.sales_data = {}
        self.inventory_data = {}
        self.customer_data = {}
        self.promotion_data = {}
        
    async def process_merchant_command(self, 
                                     merchant_id: str, 
                                     command: str) -> Dict[str, Any]:
        """Process natural language commands from merchant"""
        try:
            command = command.lower()
            
            if "vendí" in command or "ventas" in command:
                return await self.get_sales_summary(merchant_id)
            elif "menú" in command or "actualizar" in command:
                return await self.get_menu_management(merchant_id)
            elif "pedidos" in command or "activos" in command:
                return await self.get_active_orders(merchant_id)
            elif "inventario" in command:
                return await self.get_inventory_status(merchant_id)
            elif "clientes" in command:
                return await self.get_customer_insights(merchant_id)
            elif "promoción" in command or "combo" in command:
                return await self.manage_promotions(merchant_id)
            elif "reseñas" in command:
                return await self.get_recent_reviews(merchant_id)
                
            return {
                "status": "error",
                "message": "Comando no reconocido. Por favor intenta de nuevo."
            }
        except Exception as e:
            logger.error(f"Merchant command error: {str(e)}")
            return {"status": "error", "message": str(e)}

    async def get_sales_performance(self, 
                                  merchant_id: str, 
                                  period: str = "today") -> Dict[str, Any]:
        """Get comprehensive sales and performance data"""
        try:
            return {
                "sales_summary": await self._calculate_sales_summary(
                    merchant_id,
                    period
                ),
                "active_orders": await self._get_active_orders(merchant_id),
                "average_metrics": await self._calculate_average_metrics(
                    merchant_id,
                    period
                ),
                "channel_breakdown": await self._get_channel_breakdown(
                    merchant_id,
                    period
                ),
                "cancelled_orders": await self._analyze_cancelled_orders(
                    merchant_id,
                    period
                ),
                "performance_comparison": await self._compare_performance(
                    merchant_id,
                    period
                )
            }
        except Exception as e:
            logger.error(f"Sales performance error: {str(e)}")
            return {"status": "error", "message": str(e)}

    async def manage_menu_products(self, 
                                 merchant_id: str, 
                                 action: str,
                                 product_data: Dict[str, Any] = None) -> Dict[str, Any]:
        """Manage menu and products"""
        try:
            if action == "add_product":
                return await self._add_new_product(merchant_id, product_data)
            elif action == "edit_product":
                return await self._edit_product(merchant_id, product_data)
            elif action == "update_status":
                return await self._update_product_status(
                    merchant_id,
                    product_data["product_id"],
                    product_data["status"]
                )
            elif action == "update_image":
                return await self._update_product_image(
                    merchant_id,
                    product_data["product_id"],
                    product_data["image_data"]
                )
            elif action == "organize_categories":
                return await self._organize_product_categories(
                    merchant_id,
                    product_data["categories"]
                )
                
            return {
                "status": "error",
                "message": "Acción no válida"
            }
        except Exception as e:
            logger.error(f"Menu management error: {str(e)}")
            return {"status": "error", "message": str(e)}

    async def manage_inventory(self, 
                             merchant_id: str, 
                             action: str,
                             inventory_data: Dict[str, Any] = None) -> Dict[str, Any]:
        """Manage inventory and stock"""
        try:
            if action == "check_status":
                return await self._get_inventory_status(merchant_id)
            elif action == "add_stock":
                return await self._add_new_stock(merchant_id, inventory_data)
            elif action == "view_history":
                return await self._get_consumption_history(merchant_id)
            elif action == "production_cost":
                return await self._calculate_production_cost(merchant_id)
            elif action == "low_stock_alerts":
                return await self._generate_stock_alerts(merchant_id)
                
            return {
                "status": "error",
                "message": "Acción de inventario no válida"
            }
        except Exception as e:
            logger.error(f"Inventory management error: {str(e)}")
            return {"status": "error", "message": str(e)}

    async def manage_customer_relations(self, 
                                      merchant_id: str, 
                                      action: str,
                                      customer_data: Dict[str, Any] = None) -> Dict[str, Any]:
        """Manage customer relations and communications"""
        try:
            if action == "frequent_customers":
                return await self._get_frequent_customers(merchant_id)
            elif action == "recent_reviews":
                return await self._get_recent_reviews(merchant_id)
            elif action == "send_promotion":
                return await self._send_personalized_promotion(
                    merchant_id,
                    customer_data
                )
            elif action == "smart_recommendations":
                return await self._generate_smart_recommendations(merchant_id)
            elif action == "export_database":
                return await self._export_customer_database(merchant_id)
                
            return {
                "status": "error",
                "message": "Acción de cliente no válida"
            }
        except Exception as e:
            logger.error(f"Customer relations error: {str(e)}")
            return {"status": "error", "message": str(e)}

    async def manage_promotions(self, 
                              merchant_id: str, 
                              action: str,
                              promotion_data: Dict[str, Any] = None) -> Dict[str, Any]:
        """Manage promotions and loyalty programs"""
        try:
            if action == "create_combo":
                return await self._create_combo_promotion(
                    merchant_id,
                    promotion_data
                )
            elif action == "schedule_discount":
                return await self._schedule_discount(
                    merchant_id,
                    promotion_data
                )
            elif action == "create_promo_code":
                return await self._create_promo_code(
                    merchant_id,
                    promotion_data
                )
            elif action == "publish_promotion":
                return await self._publish_promotion(
                    merchant_id,
                    promotion_data
                )
            elif action == "track_usage":
                return await self._track_promotion_usage(merchant_id)
                
            return {
                "status": "error",
                "message": "Acción de promoción no válida"
            }
        except Exception as e:
            logger.error(f"Promotion management error: {str(e)}")
            return {"status": "error", "message": str(e)}

    async def manage_daily_operations(self, 
                                    merchant_id: str, 
                                    action: str) -> Dict[str, Any]:
        """Manage daily operations and coordination"""
        try:
            if action == "ready_orders":
                return await self._get_ready_orders(merchant_id)
            elif action == "preparation_times":
                return await self._get_preparation_times(merchant_id)
            elif action == "kitchen_delays":
                return await self._check_kitchen_delays(merchant_id)
            elif action == "coordinate_delivery":
                return await self._coordinate_with_drivers(merchant_id)
            elif action == "daily_report":
                return await self._generate_operations_report(merchant_id)
                
            return {
                "status": "error",
                "message": "Acción de operaciones no válida"
            }
        except Exception as e:
            logger.error(f"Daily operations error: {str(e)}")
            return {"status": "error", "message": str(e)}

    async def get_business_analytics(self, 
                                   merchant_id: str, 
                                   analysis_type: str) -> Dict[str, Any]:
        """Get business analytics and insights"""
        try:
            if analysis_type == "sales_evolution":
                return await self._analyze_sales_evolution(merchant_id)
            elif analysis_type == "product_analysis":
                return await self._analyze_product_performance(merchant_id)
            elif analysis_type == "demand_zones":
                return await self._analyze_demand_zones(merchant_id)
            elif analysis_type == "growth_tips":
                return await self._generate_growth_recommendations(merchant_id)
                
            return {
                "status": "error",
                "message": "Tipo de análisis no válido"
            }
        except Exception as e:
            logger.error(f"Business analytics error: {str(e)}")
            return {"status": "error", "message": str(e)}

    async def _calculate_sales_summary(self, 
                                     merchant_id: str, 
                                     period: str) -> Dict[str, Any]:
        """Calculate detailed sales summary"""
        sales_data = self.sales_data.get(merchant_id, {})
        
        if period == "today":
            start_date = datetime.now().date()
        elif period == "week":
            start_date = datetime.now().date() - timedelta(days=7)
        elif period == "month":
            start_date = datetime.now().date() - timedelta(days=30)
            
        relevant_sales = [
            sale for sale in sales_data.get("sales", [])
            if datetime.fromisoformat(sale["date"]).date() >= start_date
        ]
        
        return {
            "total_sales": sum(s["amount"] for s in relevant_sales),
            "order_count": len(relevant_sales),
            "average_ticket": (sum(s["amount"] for s in relevant_sales) / 
                             len(relevant_sales)) if relevant_sales else 0,
            "period_summary": {
                "start_date": start_date.isoformat(),
                "end_date": datetime.now().date().isoformat(),
                "best_selling_items": await self._get_best_sellers(relevant_sales),
                "peak_hours": await self._analyze_peak_hours(relevant_sales)
            }
        } 
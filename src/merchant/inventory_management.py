from typing import Dict, Any, List
from datetime import datetime, timedelta
from enum import Enum
from decimal import Decimal

class InventoryStatus(Enum):
    IN_STOCK = "in_stock"
    LOW_STOCK = "low_stock"
    OUT_OF_STOCK = "out_of_stock"
    EXPIRING_SOON = "expiring_soon"

class InventoryManager:
    def __init__(self):
        self.load_templates()
        
    async def get_inventory_summary(self, merchant_id: str) -> Dict[str, Any]:
        """Get inventory summary with alerts and status"""
        inventory_data = await self._fetch_inventory_data(merchant_id)
        
        return {
            "status": "success",
            "summary": {
                "total_items": len(inventory_data["items"]),
                "low_stock_items": len([i for i in inventory_data["items"] 
                                      if i["status"] == InventoryStatus.LOW_STOCK]),
                "out_of_stock": len([i for i in inventory_data["items"] 
                                   if i["status"] == InventoryStatus.OUT_OF_STOCK]),
                "expiring_soon": len([i for i in inventory_data["items"] 
                                    if i["status"] == InventoryStatus.EXPIRING_SOON])
            },
            "alerts": await self._generate_inventory_alerts(inventory_data),
            "items": inventory_data["items"]
        }

    async def update_inventory(self, merchant_id: str, 
                             updates: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Update inventory levels and generate alerts"""
        try:
            updated_items = []
            for update in updates:
                item = await self._update_item_inventory(
                    merchant_id,
                    update["item_id"],
                    update["quantity"],
                    update.get("expiry_date")
                )
                updated_items.append(item)
            
            return {
                "status": "success",
                "updated_items": updated_items,
                "alerts": await self._generate_inventory_alerts(
                    {"items": updated_items}
                )
            }
        except Exception as e:
            logger.error(f"Inventory update error: {str(e)}")
            return {"status": "error", "message": str(e)}

    async def _generate_inventory_alerts(self, 
                                       inventory_data: Dict[str, Any]) -> List[str]:
        """Generate inventory alerts based on status"""
        alerts = []
        for item in inventory_data["items"]:
            if item["status"] == InventoryStatus.LOW_STOCK:
                alerts.append(
                    f"⚠️ Stock bajo de {item['name']}: {item['quantity']} unidades"
                )
            elif item["status"] == InventoryStatus.OUT_OF_STOCK:
                alerts.append(f"🚫 {item['name']} agotado")
            elif item["status"] == InventoryStatus.EXPIRING_SOON:
                alerts.append(
                    f"⏰ {item['name']} vence en {item['days_until_expiry']} días"
                )
        return alerts

class PromotionManager:
    def __init__(self):
        self.load_templates()
        
    async def create_promotion(self, merchant_id: str, 
                             promotion_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create new promotion campaign"""
        try:
            promotion = {
                "id": str(uuid.uuid4()),
                "merchant_id": merchant_id,
                "name": promotion_data["name"],
                "type": promotion_data["type"],
                "discount": promotion_data["discount"],
                "start_date": promotion_data["start_date"],
                "end_date": promotion_data["end_date"],
                "conditions": promotion_data.get("conditions", {}),
                "target_audience": promotion_data.get("target_audience", "all"),
                "status": "active"
            }
            
            # Save promotion
            saved_promotion = await self._save_promotion(promotion)
            
            return {
                "status": "success",
                "promotion": saved_promotion,
                "message": f"Promoción '{promotion['name']}' creada exitosamente"
            }
        except Exception as e:
            logger.error(f"Error creating promotion: {str(e)}")
            return {"status": "error", "message": str(e)}

    async def get_active_promotions(self, merchant_id: str) -> Dict[str, Any]:
        """Get all active promotions"""
        promotions = await self._fetch_promotions(merchant_id)
        
        return {
            "status": "success",
            "active_count": len([p for p in promotions if p["status"] == "active"]),
            "promotions": promotions,
            "analytics": await self._get_promotion_analytics(merchant_id)
        }

    async def _get_promotion_analytics(self, 
                                     merchant_id: str) -> Dict[str, Any]:
        """Get promotion performance analytics"""
        return {
            "total_redemptions": 156,
            "revenue_impact": 450.75,
            "customer_acquisition": 23,
            "repeat_customers": 12
        }

class CustomerHistoryManager:
    def __init__(self):
        self.load_templates()
        
    async def get_customer_insights(self, merchant_id: str) -> Dict[str, Any]:
        """Get detailed customer insights and history"""
        customer_data = await self._fetch_customer_data(merchant_id)
        
        return {
            "status": "success",
            "summary": {
                "total_customers": len(customer_data["customers"]),
                "new_customers_30d": customer_data["new_customers_30d"],
                "repeat_customers": customer_data["repeat_customers"],
                "average_order_value": customer_data["average_order_value"]
            },
            "segments": await self._generate_customer_segments(customer_data),
            "trends": await self._analyze_customer_trends(customer_data)
        }

    async def get_customer_details(self, merchant_id: str, 
                                 customer_id: str) -> Dict[str, Any]:
        """Get detailed history for specific customer"""
        customer = await self._fetch_customer_details(merchant_id, customer_id)
        
        return {
            "status": "success",
            "customer": {
                "id": customer["id"],
                "name": customer["name"],
                "total_orders": customer["total_orders"],
                "total_spent": customer["total_spent"],
                "favorite_items": customer["favorite_items"],
                "last_visit": customer["last_visit"],
                "preferences": customer["preferences"]
            },
            "order_history": customer["orders"],
            "recommendations": await self._generate_recommendations(customer)
        } 
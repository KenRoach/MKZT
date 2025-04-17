from typing import Dict, Any, List
from datetime import datetime, timedelta
import numpy as np
from src.utils.logger import logger

class InventoryManagement:
    def __init__(self):
        self.low_stock_threshold = 0.2  # 20% of max stock
        self.reorder_threshold = 0.3    # 30% of max stock
        
    async def get_inventory_status(self, restaurant_id: str) -> Dict[str, Any]:
        """Get comprehensive inventory status"""
        try:
            current_stock = await self._get_current_stock(restaurant_id)
            usage_patterns = await self._analyze_usage_patterns(restaurant_id)
            predictions = await self._generate_stock_predictions(
                current_stock,
                usage_patterns
            )
            
            return {
                "status": "success",
                "current_stock": current_stock,
                "alerts": await self._generate_alerts(current_stock, predictions),
                "predictions": predictions,
                "recommendations": await self._generate_recommendations(
                    current_stock,
                    predictions
                )
            }
        except Exception as e:
            logger.error(f"Error getting inventory status: {str(e)}")
            return {"status": "error", "message": str(e)}

    async def update_inventory(self, restaurant_id: str, 
                             updates: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Update inventory levels"""
        try:
            results = []
            for update in updates:
                result = await self._process_inventory_update(
                    restaurant_id,
                    update
                )
                results.append(result)
            
            return {
                "status": "success",
                "updates": results,
                "alerts": await self._check_post_update_alerts(restaurant_id)
            }
        except Exception as e:
            logger.error(f"Error updating inventory: {str(e)}")
            return {"status": "error", "message": str(e)}

    async def _generate_alerts(self, current_stock: Dict[str, Any],
                             predictions: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate inventory alerts"""
        alerts = []
        
        # Check low stock items
        for item, details in current_stock.items():
            if details["current_level"] <= details["min_level"]:
                alerts.append({
                    "type": "low_stock",
                    "priority": "high",
                    "item": item,
                    "current_level": details["current_level"],
                    "min_level": details["min_level"],
                    "suggested_order": details["reorder_quantity"]
                })
        
        # Check expiring items
        for item, details in current_stock.items():
            if "expiry_date" in details and \
               (datetime.fromisoformat(details["expiry_date"]) - datetime.now()).days <= 7:
                alerts.append({
                    "type": "expiring_soon",
                    "priority": "medium",
                    "item": item,
                    "expiry_date": details["expiry_date"],
                    "current_level": details["current_level"]
                })
        
        # Check predicted stockouts
        for item, prediction in predictions.items():
            if prediction["days_until_stockout"] <= 3:
                alerts.append({
                    "type": "predicted_stockout",
                    "priority": "medium",
                    "item": item,
                    "days_remaining": prediction["days_until_stockout"],
                    "suggested_order": prediction["suggested_order_quantity"]
                })
        
        return alerts

    async def _generate_recommendations(self, current_stock: Dict[str, Any],
                                      predictions: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate inventory recommendations"""
        return [
            {
                "type": "reorder",
                "items": [
                    {
                        "name": "Salmon",
                        "quantity": "5kg",
                        "urgency": "high",
                        "reason": "Below reorder point"
                    }
                ]
            },
            {
                "type": "stock_optimization",
                "suggestions": [
                    {
                        "item": "Rice",
                        "current_stock": "25kg",
                        "optimal_stock": "20kg",
                        "action": "Reduce next order by 20%"
                    }
                ]
            },
            {
                "type": "waste_prevention",
                "items": [
                    {
                        "name": "Avocado",
                        "action": "Use within 2 days",
                        "quantity": "500g"
                    }
                ]
            }
        ] 
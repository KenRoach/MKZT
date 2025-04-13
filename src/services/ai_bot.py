import os
from typing import Dict, List, Any, Optional
import logging
from datetime import datetime, timedelta
from src.data.crm_repository import CRMRepository
from src.utils.openai_client import openai_client

logger = logging.getLogger(__name__)

class AIBot:
    """AI Bot service for inventory management"""
    
    def __init__(self):
        self.crm_repository = CRMRepository()
        self.openai_client = openai_client
        
    async def verify_merchant_inventory_access(self, merchant_id: str, inventory_item_id: str) -> bool:
        """Verify that the inventory item belongs to the merchant"""
        try:
            # Get the inventory item
            inventory_items = await self.crm_repository.get_inventory_items(merchant_id)
            
            # Check if the inventory item belongs to the merchant
            return any(item["id"] == inventory_item_id for item in inventory_items)
        except Exception as e:
            logger.error(f"Error verifying merchant inventory access: {str(e)}")
            return False
        
    async def process_inventory_query(self, merchant_id: str, query: str) -> Dict[str, Any]:
        """Process natural language queries about inventory"""
        try:
            # Get inventory context
            inventory_items = await self.crm_repository.get_inventory_items(merchant_id)
            inventory_alerts = await self.crm_repository.get_inventory_alerts(merchant_id)
            
            # Create context for the AI
            context = {
                "inventory_items": inventory_items,
                "alerts": inventory_alerts,
                "query": query
            }
            
            # Get AI response
            response = await self.openai_client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You are an inventory management assistant. Help users understand and manage their inventory."},
                    {"role": "user", "content": f"Context: {context}\nQuery: {query}"}
                ]
            )
            
            return {
                "response": response.choices[0].message.content,
                "context": context
            }
            
        except Exception as e:
            logger.error(f"Error processing inventory query: {str(e)}")
            raise
            
    async def check_inventory_levels(self, merchant_id: str) -> List[Dict[str, Any]]:
        """Check inventory levels and generate alerts"""
        try:
            inventory_items = await self.crm_repository.get_inventory_items(merchant_id)
            alerts = []
            
            for item in inventory_items:
                stock = await self.crm_repository.get_inventory_stock(item["id"])
                if stock and stock["quantity"] <= item["reorder_level"]:
                    alerts.append({
                        "item": item,
                        "current_stock": stock["quantity"],
                        "reorder_level": item["reorder_level"],
                        "message": f"Low stock alert for {item['name']}"
                    })
                    
            return alerts
            
        except Exception as e:
            logger.error(f"Error checking inventory levels: {str(e)}")
            raise
            
    async def suggest_reorder_quantities(self, merchant_id: str) -> List[Dict[str, Any]]:
        """Suggest reorder quantities based on historical data"""
        try:
            inventory_items = await self.crm_repository.get_inventory_items(merchant_id)
            suggestions = []
            
            for item in inventory_items:
                # Get recent transactions
                transactions = await self.crm_repository.get_inventory_transactions(
                    item["id"],
                    start_date=(datetime.now() - timedelta(days=30)).isoformat()
                )
                
                # Calculate average daily usage
                total_quantity = sum(t["quantity"] for t in transactions)
                avg_daily_usage = total_quantity / 30
                
                # Get current stock
                stock = await self.crm_repository.get_inventory_stock(item["id"])
                current_stock = stock["quantity"] if stock else 0
                
                # Calculate suggested reorder quantity
                days_until_reorder = item["reorder_level"] / avg_daily_usage if avg_daily_usage > 0 else float('inf')
                suggested_quantity = max(
                    item["reorder_quantity"],
                    int(avg_daily_usage * 7)  # 7 days worth of inventory
                )
                
                suggestions.append({
                    "item": item,
                    "current_stock": current_stock,
                    "avg_daily_usage": avg_daily_usage,
                    "days_until_reorder": days_until_reorder,
                    "suggested_quantity": suggested_quantity
                })
                
            return suggestions
            
        except Exception as e:
            logger.error(f"Error suggesting reorder quantities: {str(e)}")
            raise
            
    async def analyze_inventory_trends(self, merchant_id: str, days: int = 30) -> Dict[str, Any]:
        """Analyze inventory trends and patterns"""
        try:
            inventory_items = await self.crm_repository.get_inventory_items(merchant_id)
            trends = {}
            
            for item in inventory_items:
                # Get transactions for the period
                transactions = await self.crm_repository.get_inventory_transactions(
                    item["id"],
                    start_date=(datetime.now() - timedelta(days=days)).isoformat()
                )
                
                # Calculate trends
                daily_usage = {}
                for t in transactions:
                    date = t["created_at"].split("T")[0]
                    daily_usage[date] = daily_usage.get(date, 0) + t["quantity"]
                    
                trends[item["id"]] = {
                    "item": item,
                    "daily_usage": daily_usage,
                    "total_usage": sum(daily_usage.values()),
                    "avg_daily_usage": sum(daily_usage.values()) / len(daily_usage) if daily_usage else 0
                }
                
            return trends
            
        except Exception as e:
            logger.error(f"Error analyzing inventory trends: {str(e)}")
            raise
            
    async def generate_inventory_report(self, merchant_id: str) -> Dict[str, Any]:
        """Generate a comprehensive inventory report"""
        try:
            # Gather all necessary data
            inventory_items = await self.crm_repository.get_inventory_items(merchant_id)
            alerts = await self.crm_repository.get_inventory_alerts(merchant_id)
            trends = await self.analyze_inventory_trends(merchant_id)
            suggestions = await self.suggest_reorder_quantities(merchant_id)
            
            # Create report
            report = {
                "timestamp": datetime.now().isoformat(),
                "merchant_id": merchant_id,
                "total_items": len(inventory_items),
                "active_alerts": len([a for a in alerts if a["status"] == "pending"]),
                "low_stock_items": len(suggestions),
                "trends": trends,
                "suggestions": suggestions,
                "alerts": alerts
            }
            
            return report
            
        except Exception as e:
            logger.error(f"Error generating inventory report: {str(e)}")
            raise

# Create singleton instance
ai_bot = AIBot() 
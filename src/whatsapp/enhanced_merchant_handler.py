from typing import Dict, Any
from src.merchant.inventory_management import (
    InventoryManager,
    PromotionManager,
    CustomerHistoryManager
)
from twilio.rest import Client
import os

class EnhancedMerchantHandler:
    def __init__(self):
        self.inventory_manager = InventoryManager()
        self.promotion_manager = PromotionManager()
        self.customer_manager = CustomerHistoryManager()
        self.twilio_client = Client(
            os.getenv("TWILIO_ACCOUNT_SID"),
            os.getenv("TWILIO_AUTH_TOKEN")
        )
        self.whatsapp_number = os.getenv("TWILIO_WHATSAPP_NUMBER")
        
    async def process_merchant_request(self, 
                                     request_data: Dict[str, Any]) -> None:
        """Process merchant requests for inventory, promotions, or customers"""
        try:
            if request_data["type"] == "inventory":
                await self._handle_inventory_request(request_data)
            elif request_data["type"] == "promotions":
                await self._handle_promotion_request(request_data)
            elif request_data["type"] == "customers":
                await self._handle_customer_request(request_data)
        except Exception as e:
            logger.error(f"Error processing merchant request: {str(e)}")
            await self._send_error_message(request_data["phone_number"])

    async def _handle_inventory_request(self, data: Dict[str, Any]) -> None:
        """Handle inventory-related requests"""
        if data["action"] == "summary":
            summary = await self.inventory_manager.get_inventory_summary(
                data["merchant_id"]
            )
            
            message = self._format_inventory_message(summary)
            await self._send_message(data["phone_number"], message)
            
        elif data["action"] == "update":
            result = await self.inventory_manager.update_inventory(
                data["merchant_id"],
                data["updates"]
            )
            
            message = self._format_inventory_update_message(result)
            await self._send_message(data["phone_number"], message)

    async def _handle_promotion_request(self, data: Dict[str, Any]) -> None:
        """Handle promotion-related requests"""
        if data["action"] == "create":
            result = await self.promotion_manager.create_promotion(
                data["merchant_id"],
                data["promotion_data"]
            )
            
            message = self._format_promotion_message(result)
            await self._send_message(data["phone_number"], message)
            
        elif data["action"] == "list":
            promotions = await self.promotion_manager.get_active_promotions(
                data["merchant_id"]
            )
            
            message = self._format_promotions_list_message(promotions)
            await self._send_message(data["phone_number"], message)

    async def _handle_customer_request(self, data: Dict[str, Any]) -> None:
        """Handle customer-related requests"""
        if data["action"] == "insights":
            insights = await self.customer_manager.get_customer_insights(
                data["merchant_id"]
            )
            
            message = self._format_customer_insights_message(insights)
            await self._send_message(data["phone_number"], message)
            
        elif data["action"] == "details":
            details = await self.customer_manager.get_customer_details(
                data["merchant_id"],
                data["customer_id"]
            )
            
            message = self._format_customer_details_message(details)
            await self._send_message(data["phone_number"], message)

    def _format_inventory_message(self, summary: Dict[str, Any]) -> str:
        """Format inventory summary message"""
        template = self.templates["es"]["inventory"]
        
        message = template["summary"].format(
            total_items=summary["summary"]["total_items"],
            low_stock=summary["summary"]["low_stock_items"],
            out_of_stock=summary["summary"]["out_of_stock"],
            expiring_soon=summary["summary"]["expiring_soon"]
        )
        
        if summary["alerts"]:
            message += f"\n\n{template['alerts_header']}\n"
            message += "\n".join(summary["alerts"])
        else:
            message += f"\n\n{template['no_alerts']}"
            
        message += "\n\n" + "\n".join(template["options"])
        
        return message

    def _format_promotion_message(self, result: Dict[str, Any]) -> str:
        """Format promotion message"""
        template = self.templates["es"]["promotions"]
        
        if result["status"] == "success":
            message = f"✅ {result['message']}\n\n"
            message += template["summary"].format(
                active_count=result["promotion"]["active_count"],
                redemptions=result["promotion"]["total_redemptions"],
                revenue_impact=result["promotion"]["revenue_impact"]
            )
        else:
            message = f"❌ Error: {result['message']}"
            
        return message

    def _format_customer_insights_message(self, insights: Dict[str, Any]) -> str:
        """Format customer insights message"""
        template = self.templates["es"]["customers"]
        
        message = template["summary"].format(
            total=insights["summary"]["total_customers"],
            new_customers=insights["summary"]["new_customers_30d"],
            repeat_customers=insights["summary"]["repeat_customers"],
            average_order=insights["summary"]["average_order_value"]
        )
        
        message += f"\n\n{template['segments']}\n"
        for segment in insights["segments"]:
            message += template["segment_format"].format(
                segment_name=segment["name"],
                count=segment["count"],
                percentage=segment["percentage"]
            ) + "\n"
            
        message += "\n" + "\n".join(template["options"])
        
        return message 
import os
from typing import Dict, Any, Optional
from datetime import datetime, timedelta
import json
from src.services.nlp_service import NLPService
from src.data.crm_repository import CRMRepository
from src.utils.logger import logger

class AIChatbotHandler:
    """AI Chatbot handler for WhatsApp interactions"""
    
    def __init__(self):
        self.nlp_service = NLPService()
        self.crm_repository = CRMRepository()
        
        # Load prompts for different user types
        self.prompts = {
            "merchant": """You are a business analytics assistant helping merchants understand their:
                - Sales performance
                - Inventory levels
                - Customer trends
                - Financial metrics
                Provide concise, data-driven responses.""",
            
            "driver": """You are a driver performance assistant helping drivers understand their:
                - Delivery metrics
                - Earnings
                - Ratings
                - Schedule optimization
                Focus on actionable insights and performance metrics.""",
            
            "consumer": """You are a customer service assistant helping customers with:
                - Order history
                - Restaurant recommendations
                - Order status
                - Previous preferences
                Provide friendly, helpful responses with specific details."""
        }
    
    async def process_message(self, phone_number: str, message: str) -> Dict[str, Any]:
        """Process incoming message and generate response"""
        try:
            # Identify user
            user_info = await self.identify_user(phone_number)
            if not user_info:
                return {
                    "status": "error",
                    "message": "User not identified",
                    "response": "Please register to use this service."
                }
            
            # Analyze intent
            intent = await self.nlp_service.analyze_intent(message)
            
            # Get data based on user type and intent
            data = await self.get_data(user_info, intent, message)
            
            # Generate response
            response = await self.generate_response(user_info["user_type"], data, message)
            
            return {
                "status": "success",
                "response": response,
                "data": data
            }
            
        except Exception as e:
            logger.error(f"Error processing message: {str(e)}")
            return {
                "status": "error",
                "message": str(e),
                "response": "I apologize, but I encountered an error processing your request."
            }
    
    async def identify_user(self, phone_number: str) -> Optional[Dict[str, Any]]:
        """Identify user type and permissions"""
        try:
            # Check merchant
            merchant = await self.crm_repository.get_merchant_by_phone(phone_number)
            if merchant:
                return {
                    "user_type": "merchant",
                    "user_id": merchant["id"],
                    "permissions": ["view_sales", "view_inventory", "view_analytics"]
                }
            
            # Check driver
            driver = await self.crm_repository.get_driver_by_phone(phone_number)
            if driver:
                return {
                    "user_type": "driver",
                    "user_id": driver["id"],
                    "permissions": ["view_earnings", "view_metrics", "view_schedule"]
                }
            
            # Check consumer
            consumer = await self.crm_repository.get_customer_by_phone(phone_number)
            if consumer:
                return {
                    "user_type": "consumer",
                    "user_id": consumer["id"],
                    "permissions": ["view_orders", "view_recommendations"]
                }
            
            return None
            
        except Exception as e:
            logger.error(f"Error identifying user: {str(e)}")
            return None
    
    async def get_data(self, user_info: Dict[str, Any], intent: Dict[str, Any], message: str) -> Dict[str, Any]:
        """Get relevant data based on user type and intent"""
        try:
            if user_info["user_type"] == "merchant":
                return await self._get_merchant_data(user_info["user_id"], intent, message)
            elif user_info["user_type"] == "driver":
                return await self._get_driver_data(user_info["user_id"], intent, message)
            else:
                return await self._get_consumer_data(user_info["user_id"], intent, message)
                
        except Exception as e:
            logger.error(f"Error getting data: {str(e)}")
            raise
    
    async def _get_merchant_data(self, merchant_id: str, intent: Dict[str, Any], message: str) -> Dict[str, Any]:
        """Get merchant-specific data"""
        # Extract date range from message
        date_range = self._extract_date_range(message)
        
        if "sales" in intent["topics"]:
            return await self.crm_repository.get_merchant_analytics(
                merchant_id,
                date_range
            )
        elif "inventory" in intent["topics"]:
            return await self.crm_repository.get_inventory_status(
                merchant_id
            )
        elif "performance" in intent["topics"]:
            return await self.crm_repository.get_merchant_performance(
                merchant_id,
                date_range
            )
        else:
            return await self.crm_repository.get_merchant_summary(
                merchant_id
            )
    
    async def _get_driver_data(self, driver_id: str, intent: Dict[str, Any], message: str) -> Dict[str, Any]:
        """Get driver-specific data"""
        date_range = self._extract_date_range(message)
        
        if "earnings" in intent["topics"]:
            return await self.crm_repository.get_driver_earnings(
                driver_id,
                date_range
            )
        elif "performance" in intent["topics"]:
            return await self.crm_repository.get_driver_performance(
                driver_id,
                date_range
            )
        elif "schedule" in intent["topics"]:
            return await self.crm_repository.get_driver_schedule(
                driver_id
            )
        else:
            return await self.crm_repository.get_driver_summary(
                driver_id
            )
    
    async def _get_consumer_data(self, customer_id: str, intent: Dict[str, Any], message: str) -> Dict[str, Any]:
        """Get consumer-specific data"""
        if "order_status" in intent["topics"]:
            return await self.crm_repository.get_active_orders(
                customer_id
            )
        elif "order_history" in intent["topics"]:
            return await self.crm_repository.get_order_history(
                customer_id
            )
        elif "recommendations" in intent["topics"]:
            return await self.crm_repository.get_recommendations(
                customer_id
            )
        else:
            return await self.crm_repository.get_customer_summary(
                customer_id
            )
    
    async def generate_response(self, user_type: str, data: Dict[str, Any], original_message: str) -> str:
        """Generate natural language response"""
        try:
            # Create context for AI
            context = {
                "user_type": user_type,
                "data": data,
                "original_message": original_message,
                "timestamp": datetime.now().isoformat()
            }
            
            # Get appropriate prompt
            system_prompt = self.prompts[user_type]
            
            # Generate response using NLP service
            response = await self.nlp_service.generate_response(
                system_prompt=system_prompt,
                context=context
            )
            
            return response
            
        except Exception as e:
            logger.error(f"Error generating response: {str(e)}")
            return "I apologize, but I couldn't generate a proper response at the moment."
    
    def _extract_date_range(self, message: str) -> Dict[str, datetime]:
        """Extract date range from message"""
        # Default to last 7 days if not specified
        end_date = datetime.now()
        start_date = end_date - timedelta(days=7)
        
        # TODO: Implement more sophisticated date range extraction
        if "last month" in message.lower():
            start_date = end_date - timedelta(days=30)
        elif "last week" in message.lower():
            start_date = end_date - timedelta(days=7)
        elif "today" in message.lower():
            start_date = end_date - timedelta(days=1)
        
        return {
            "start_date": start_date,
            "end_date": end_date
        } 
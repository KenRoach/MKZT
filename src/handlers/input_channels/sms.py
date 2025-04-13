from typing import Dict, Any, Optional
import uuid
from datetime import datetime
from src.utils.logger import logger
from src.handlers.input_channels.base import BaseInputHandler
from src.services.web_scraper import WebScraperService, web_scraper
from src.services.nlp_service import nlp_service

class SMSInputHandler(BaseInputHandler):
    def __init__(self, api_key: str):
        """Initialize the SMS input handler"""
        super().__init__(api_key, "sms")
        self.web_scraper = WebScraperService()
    
    async def validate_input(self, data: Dict[str, Any]) -> bool:
        """
        Validate the incoming SMS data
        
        Args:
            data: The incoming SMS data
            
        Returns:
            bool: True if valid, False otherwise
        """
        required_fields = ["message_id", "customer_id", "message"]
        return all(field in data for field in required_fields)
    
    async def process_input(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process the incoming SMS data
        
        Args:
            data: The incoming SMS data
            
        Returns:
            Dict containing the processed order
        """
        try:
            # Extract order details using NLP
            order_details = await nlp_service.extract_order_details(data["message"])
            
            # Check if we need to scrape additional data
            if order_details.get("needs_scraping", False):
                # Define selectors for scraping
                selectors = {
                    "items": ".menu-item",
                    "prices": ".menu-item-price",
                    "descriptions": ".menu-item-description",
                    "total_amount": ".order-total"
                }
                
                # Scrape data from the source
                scraped_data = await web_scraper.scrape_data(
                    order_details["source"],
                    selectors
                )
                
                # Validate scraped data
                validation_rules = {
                    "items": {"required": True, "min_length": 1},
                    "prices": {"required": True, "pattern": r"^\$?\d+(\.\d{2})?$"},
                    "total_amount": {"required": True, "pattern": r"^\$?\d+(\.\d{2})?$"}
                }
                
                if await web_scraper.validate_scraped_data(scraped_data, validation_rules):
                    # Merge scraped data with order details
                    order_details = await web_scraper.merge_scraped_data(
                        order_details,
                        scraped_data
                    )
            
            # Enrich order details with additional information
            enriched_details = await nlp_service.enrich_order_details(order_details)
            
            # Create standardized order format
            order = {
                "id": str(uuid.uuid4()),
                "customer_id": data["customer_id"],
                "platform": "sms",
                "message_id": data["message_id"],
                "items": enriched_details["items"],
                "total_amount": enriched_details["total_amount"],
                "delivery_address": enriched_details["delivery_address"],
                "special_instructions": enriched_details["special_instructions"],
                "estimated_preparation_time": enriched_details.get("estimated_preparation_time"),
                "suggested_addons": enriched_details.get("suggested_addons", []),
                "dietary_restrictions": enriched_details.get("dietary_restrictions", []),
                "order_priority": enriched_details.get("order_priority", "medium"),
                "status": "pending",
                "created_at": datetime.utcnow().isoformat(),
                "updated_at": datetime.utcnow().isoformat()
            }
            
            return order
            
        except Exception as e:
            print(f"Error processing SMS input: {e}")
            return None
    
    async def enrich_customer_data(self, order: Dict[str, Any]) -> Dict[str, Any]:
        """
        Enrich the order with customer data
        
        Args:
            order: The order to enrich
            
        Returns:
            Dict containing the enriched order
        """
        try:
            # Get customer data from SMS API
            customer_data = await self._get_sms_customer_data(order["customer_id"])
            
            # Add customer data to order
            order["customer"] = customer_data
            
            return order
            
        except Exception as e:
            print(f"Error enriching customer data: {e}")
            return order
    
    async def _get_sms_customer_data(self, customer_id: str) -> Dict[str, Any]:
        """
        Get customer data from SMS API
        
        Args:
            customer_id: The customer ID
            
        Returns:
            Dict containing customer data
        """
        # TODO: Implement actual SMS API call
        return {
            "id": customer_id,
            "name": "John Doe",
            "phone": "+1234567890",
            "email": "john.doe@example.com",
            "preferences": {
                "language": "en",
                "notifications": ["sms", "email"]
            }
        } 
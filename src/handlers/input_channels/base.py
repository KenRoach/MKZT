from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
from datetime import datetime

class InputChannelHandler(ABC):
    """Base class for all input channel handlers"""
    
    @abstractmethod
    async def process_input(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Process input from the channel and convert to standard format"""
        pass
    
    @abstractmethod
    async def validate_input(self, data: Dict[str, Any]) -> bool:
        """Validate input data from the channel"""
        pass
    
    @abstractmethod
    async def enrich_customer_data(self, customer_id: str) -> Dict[str, Any]:
        """Enrich order with customer data from CRM"""
        pass
    
    def standardize_order_format(self, raw_order: Dict[str, Any]) -> Dict[str, Any]:
        """Convert channel-specific order format to standard format"""
        return {
            "order_id": raw_order.get("order_id"),
            "channel": self.__class__.__name__,
            "customer_id": raw_order.get("customer_id"),
            "items": raw_order.get("items", []),
            "total_amount": raw_order.get("total_amount"),
            "currency": raw_order.get("currency", "USD"),
            "status": raw_order.get("status", "pending"),
            "created_at": raw_order.get("created_at", datetime.utcnow().isoformat()),
            "metadata": {
                "channel_specific_data": raw_order.get("metadata", {}),
                "original_format": raw_order
            }
        } 
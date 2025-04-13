from typing import Dict, List, Any, Optional
from src.utils.supabase_client import supabase

class CRMRepository:
    """Repository for CRM data access"""
    
    # Customer methods
    def get_customers(self, limit: int = 100) -> List[Dict[str, Any]]:
        """Get all customers with pagination"""
        response = supabase.table("customers").select("*").limit(limit).execute()
        return response.data
    
    def get_customer_by_id(self, customer_id: str) -> Optional[Dict[str, Any]]:
        """Get a customer by ID"""
        response = supabase.table("customers").select("*").eq("id", customer_id).execute()
        return response.data[0] if response.data else None
    
    def create_customer(self, customer_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new customer"""
        response = supabase.table("customers").insert(customer_data).execute()
        return response.data[0]
    
    def update_customer(self, customer_id: str, customer_data: Dict[str, Any]) -> Dict[str, Any]:
        """Update a customer"""
        response = supabase.table("customers").update(customer_data).eq("id", customer_id).execute()
        return response.data[0]
    
    # Merchant methods
    def get_merchants(self, limit: int = 100) -> List[Dict[str, Any]]:
        """Get all merchants with pagination"""
        response = supabase.table("merchants").select("*").limit(limit).execute()
        return response.data
    
    def get_merchant_by_id(self, merchant_id: str) -> Optional[Dict[str, Any]]:
        """Get a merchant by ID"""
        response = supabase.table("merchants").select("*").eq("id", merchant_id).execute()
        return response.data[0] if response.data else None
    
    def create_merchant(self, merchant_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new merchant"""
        response = supabase.table("merchants").insert(merchant_data).execute()
        return response.data[0]
    
    def update_merchant(self, merchant_id: str, merchant_data: Dict[str, Any]) -> Dict[str, Any]:
        """Update a merchant"""
        response = supabase.table("merchants").update(merchant_data).eq("id", merchant_id).execute()
        return response.data[0]
    
    # Driver methods
    def get_drivers(self, limit: int = 100) -> List[Dict[str, Any]]:
        """Get all drivers with pagination"""
        response = supabase.table("drivers").select("*").limit(limit).execute()
        return response.data
    
    def get_driver_by_id(self, driver_id: str) -> Optional[Dict[str, Any]]:
        """Get a driver by ID"""
        response = supabase.table("drivers").select("*").eq("id", driver_id).execute()
        return response.data[0] if response.data else None
    
    def create_driver(self, driver_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new driver"""
        response = supabase.table("drivers").insert(driver_data).execute()
        return response.data[0]
    
    def update_driver(self, driver_id: str, driver_data: Dict[str, Any]) -> Dict[str, Any]:
        """Update a driver"""
        response = supabase.table("drivers").update(driver_data).eq("id", driver_id).execute()
        return response.data[0]
    
    def update_driver_location(self, driver_id: str, latitude: float, longitude: float) -> Dict[str, Any]:
        """Update a driver's location"""
        response = supabase.table("drivers").update({
            "current_location": f"({latitude},{longitude})"
        }).eq("id", driver_id).execute()
        return response.data[0]
    
    # Order methods
    def get_orders(self, limit: int = 100) -> List[Dict[str, Any]]:
        """Get all orders with pagination"""
        response = supabase.table("orders").select("*").limit(limit).execute()
        return response.data
    
    def get_order_by_id(self, order_id: str) -> Optional[Dict[str, Any]]:
        """Get an order by ID"""
        response = supabase.table("orders").select("*").eq("id", order_id).execute()
        return response.data[0] if response.data else None
    
    def get_orders_by_customer(self, customer_id: str) -> List[Dict[str, Any]]:
        """Get all orders for a customer"""
        response = supabase.table("orders").select("*").eq("customer_id", customer_id).execute()
        return response.data
    
    def get_orders_by_merchant(self, merchant_id: str) -> List[Dict[str, Any]]:
        """Get all orders for a merchant"""
        response = supabase.table("orders").select("*").eq("merchant_id", merchant_id).execute()
        return response.data
    
    def get_orders_by_driver(self, driver_id: str) -> List[Dict[str, Any]]:
        """Get all orders for a driver"""
        response = supabase.table("orders").select("*").eq("driver_id", driver_id).execute()
        return response.data
    
    def create_order(self, order_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new order"""
        response = supabase.table("orders").insert(order_data).execute()
        return response.data[0]
    
    def update_order(self, order_id: str, order_data: Dict[str, Any]) -> Dict[str, Any]:
        """Update an order"""
        response = supabase.table("orders").update(order_data).eq("id", order_id).execute()
        return response.data[0]
    
    def update_order_status(self, order_id: str, status: str) -> Dict[str, Any]:
        """Update an order's status"""
        response = supabase.table("orders").update({
            "status": status
        }).eq("id", order_id).execute()
        return response.data[0]
    
    # Order items methods
    def get_order_items(self, order_id: str) -> List[Dict[str, Any]]:
        """Get all items for an order"""
        response = supabase.table("order_items").select("*").eq("order_id", order_id).execute()
        return response.data
    
    def create_order_item(self, item_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new order item"""
        response = supabase.table("order_items").insert(item_data).execute()
        return response.data[0]
    
    # Notification methods
    def get_notifications(self, customer_id: Optional[str] = None, limit: int = 100) -> List[Dict[str, Any]]:
        """Get all notifications with optional filtering by customer"""
        query = supabase.table("notifications").select("*")
        
        if customer_id:
            query = query.eq("customer_id", customer_id)
        
        response = query.limit(limit).execute()
        return response.data
    
    def create_notification(self, notification_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new notification"""
        response = supabase.table("notifications").insert(notification_data).execute()
        return response.data[0]
    
    def update_notification_status(self, notification_id: str, status: str) -> Dict[str, Any]:
        """Update a notification's status"""
        response = supabase.table("notifications").update({
            "status": status,
            "sent_at": "now()" if status == "sent" else None
        }).eq("id", notification_id).execute()
        return response.data[0] 
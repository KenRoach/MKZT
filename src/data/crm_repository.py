from typing import Dict, List, Any, Optional
from src.utils.supabase_client import supabase
from datetime import datetime

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
    
    async def create_order_item(self, order_id: str, item_name: str, quantity: int, unit_price: float, 
                              product_id: str = None, variant_id: str = None, 
                              description: str = None, special_instructions: str = None) -> Dict[str, Any]:
        """Create a new order item"""
        try:
            data = {
                "order_id": order_id,
                "item_name": item_name,
                "quantity": quantity,
                "unit_price": unit_price,
                "product_id": product_id,
                "variant_id": variant_id,
                "description": description,
                "special_instructions": special_instructions
            }
            result = await supabase.table("order_items").insert(data).execute()
            return result.data[0]
        except Exception as e:
            logger.error(f"Error creating order item: {str(e)}")
            raise
    
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
    
    # Product methods
    async def get_products(self, merchant_id: str = None, category: str = None) -> List[Dict[str, Any]]:
        """Get all products with optional filtering"""
        try:
            query = supabase.table("products").select("*")
            if merchant_id:
                query = query.eq("merchant_id", merchant_id)
            if category:
                query = query.eq("category", category)
            result = await query.execute()
            return result.data
        except Exception as e:
            logger.error(f"Error getting products: {str(e)}")
            raise

    async def get_product_by_id(self, product_id: str) -> Dict[str, Any]:
        """Get a product by ID"""
        try:
            result = supabase.table("products").select("*").eq("id", product_id).execute()
            return result.data[0] if result.data else None
        except Exception as e:
            logger.error(f"Error getting product: {str(e)}")
            raise

    async def create_product(self, merchant_id: str, name: str, description: str, base_price: float, category: str = None) -> Dict[str, Any]:
        """Create a new product"""
        try:
            data = {
                "merchant_id": merchant_id,
                "name": name,
                "description": description,
                "base_price": base_price,
                "category": category
            }
            result = await supabase.table("products").insert(data).execute()
            return result.data[0]
        except Exception as e:
            logger.error(f"Error creating product: {str(e)}")
            raise

    async def update_product(self, product_id: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """Update a product"""
        try:
            result = supabase.table("products").update(data).eq("id", product_id).execute()
            return result.data[0]
        except Exception as e:
            logger.error(f"Error updating product: {str(e)}")
            raise

    # Product variant methods
    async def get_product_variants(self, product_id: str) -> List[Dict[str, Any]]:
        """Get all variants for a product"""
        try:
            result = supabase.table("product_variants").select("*").eq("product_id", product_id).execute()
            return result.data
        except Exception as e:
            logger.error(f"Error getting product variants: {str(e)}")
            raise

    async def create_product_variant(self, product_id: str, name: str, price: float) -> Dict[str, Any]:
        """Create a new product variant"""
        try:
            data = {
                "product_id": product_id,
                "name": name,
                "price": price
            }
            result = supabase.table("product_variants").insert(data).execute()
            return result.data[0]
        except Exception as e:
            logger.error(f"Error creating product variant: {str(e)}")
            raise

    async def update_product_variant(self, variant_id: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """Update a product variant"""
        try:
            result = supabase.table("product_variants").update(data).eq("id", variant_id).execute()
            return result.data[0]
        except Exception as e:
            logger.error(f"Error updating product variant: {str(e)}")
            raise

    # Customer preferences methods
    async def get_customer_preferences(self, customer_id: str) -> Dict[str, Any]:
        """Get customer preferences"""
        try:
            result = await supabase.table("customer_preferences").select("*").eq("customer_id", customer_id).execute()
            return result.data[0] if result.data else None
        except Exception as e:
            logger.error(f"Error getting customer preferences: {str(e)}")
            raise

    async def update_customer_preferences(self, customer_id: str, preferences: Dict[str, Any]) -> Dict[str, Any]:
        """Update customer preferences"""
        try:
            result = await supabase.table("customer_preferences").upsert({
                "customer_id": customer_id,
                **preferences
            }).execute()
            return result.data[0]
        except Exception as e:
            logger.error(f"Error updating customer preferences: {str(e)}")
            raise

    # Order preferences methods
    async def get_order_preferences(self, order_id: str) -> Dict[str, Any]:
        """Get order preferences"""
        try:
            raise 

    # Supplier methods
    async def get_suppliers(self, merchant_id: str) -> List[Dict[str, Any]]:
        """Get all suppliers for a merchant"""
        try:
            result = await supabase.table("suppliers").select("*").eq("merchant_id", merchant_id).execute()
            return result.data
        except Exception as e:
            logger.error(f"Error getting suppliers: {str(e)}")
            raise

    async def create_supplier(self, merchant_id: str, supplier_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new supplier"""
        try:
            data = {
                "merchant_id": merchant_id,
                **supplier_data
            }
            result = await supabase.table("suppliers").insert(data).execute()
            return result.data[0]
        except Exception as e:
            logger.error(f"Error creating supplier: {str(e)}")
            raise

    # Inventory item methods
    async def get_inventory_items(self, merchant_id: str, category: str = None) -> List[Dict[str, Any]]:
        """Get all inventory items for a merchant"""
        try:
            query = supabase.table("inventory_items").select("*").eq("merchant_id", merchant_id)
            if category:
                query = query.eq("category", category)
            result = await query.execute()
            return result.data
        except Exception as e:
            logger.error(f"Error getting inventory items: {str(e)}")
            raise

    async def create_inventory_item(self, merchant_id: str, item_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new inventory item"""
        try:
            data = {
                "merchant_id": merchant_id,
                **item_data
            }
            result = await supabase.table("inventory_items").insert(data).execute()
            return result.data[0]
        except Exception as e:
            logger.error(f"Error creating inventory item: {str(e)}")
            raise

    # Inventory stock methods
    async def get_inventory_stock(self, inventory_item_id: str) -> Dict[str, Any]:
        """Get current stock level for an inventory item"""
        try:
            result = await supabase.table("inventory_stock").select("*").eq("inventory_item_id", inventory_item_id).execute()
            return result.data[0] if result.data else None
        except Exception as e:
            logger.error(f"Error getting inventory stock: {str(e)}")
            raise

    async def update_inventory_stock(self, inventory_item_id: str, quantity: int, location: str = None, batch_number: str = None, expiry_date: str = None) -> Dict[str, Any]:
        """Update stock level for an inventory item"""
        try:
            data = {
                "inventory_item_id": inventory_item_id,
                "quantity": quantity
            }
            if location:
                data["location"] = location
            if batch_number:
                data["batch_number"] = batch_number
            if expiry_date:
                data["expiry_date"] = expiry_date

            result = await supabase.table("inventory_stock").upsert(data).execute()
            return result.data[0]
        except Exception as e:
            logger.error(f"Error updating inventory stock: {str(e)}")
            raise

    # Inventory transaction methods
    async def create_inventory_transaction(self, transaction_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new inventory transaction"""
        try:
            result = await supabase.table("inventory_transactions").insert(transaction_data).execute()
            return result.data[0]
        except Exception as e:
            logger.error(f"Error creating inventory transaction: {str(e)}")
            raise

    async def get_inventory_transactions(self, inventory_item_id: str, start_date: str = None, end_date: str = None) -> List[Dict[str, Any]]:
        """Get inventory transactions for an item"""
        try:
            query = supabase.table("inventory_transactions").select("*").eq("inventory_item_id", inventory_item_id)
            if start_date:
                query = query.gte("created_at", start_date)
            if end_date:
                query = query.lte("created_at", end_date)
            result = await query.execute()
            return result.data
        except Exception as e:
            logger.error(f"Error getting inventory transactions: {str(e)}")
            raise

    # Product inventory methods
    async def get_product_inventory(self, product_id: str) -> List[Dict[str, Any]]:
        """Get inventory items required for a product"""
        try:
            result = await supabase.table("product_inventory").select("*").eq("product_id", product_id).execute()
            return result.data
        except Exception as e:
            logger.error(f"Error getting product inventory: {str(e)}")
            raise

    async def update_product_inventory(self, product_id: str, inventory_items: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Update inventory items required for a product"""
        try:
            # First, delete existing inventory items
            await supabase.table("product_inventory").delete().eq("product_id", product_id).execute()
            
            # Then, insert new inventory items
            data = [{
                "product_id": product_id,
                "inventory_item_id": item["inventory_item_id"],
                "quantity_required": item["quantity_required"]
            } for item in inventory_items]
            
            result = await supabase.table("product_inventory").insert(data).execute()
            return result.data
        except Exception as e:
            logger.error(f"Error updating product inventory: {str(e)}")
            raise

    # Inventory alert methods
    async def get_inventory_alerts(self, merchant_id: str, status: str = None) -> List[Dict[str, Any]]:
        """Get inventory alerts for a merchant"""
        try:
            query = supabase.table("inventory_alerts").select("*").eq("merchant_id", merchant_id)
            if status:
                query = query.eq("status", status)
            result = await query.execute()
            return result.data
        except Exception as e:
            logger.error(f"Error getting inventory alerts: {str(e)}")
            raise

    async def update_inventory_alert(self, alert_id: str, status: str) -> Dict[str, Any]:
        """Update status of an inventory alert"""
        try:
            data = {
                "status": status,
                "resolved_at": datetime.utcnow().isoformat() if status == "resolved" else None
            }
            result = supabase.table("inventory_alerts").update(data).eq("id", alert_id).execute()
            return result.data[0]
        except Exception as e:
            logger.error(f"Error updating inventory alert: {str(e)}")
            raise 
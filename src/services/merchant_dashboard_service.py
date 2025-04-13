import os
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from src.utils.supabase_client import supabase
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class MerchantDashboardService:
    def __init__(self):
        """Initialize the merchant dashboard service"""
        self.supabase = supabase
    
    async def get_merchant_orders(self, merchant_id: str, status: Optional[str] = None, 
                                 start_date: Optional[datetime] = None, 
                                 end_date: Optional[datetime] = None) -> List[Dict[str, Any]]:
        """
        Get orders for a specific merchant
        
        Args:
            merchant_id: The merchant ID
            status: Filter by order status (optional)
            start_date: Filter by start date (optional)
            end_date: Filter by end date (optional)
            
        Returns:
            List of orders
        """
        try:
            # Build the query
            query = self.supabase.table("orders").select("*").eq("merchant_id", merchant_id)
            
            # Apply filters if provided
            if status:
                query = query.eq("status", status)
            
            if start_date:
                query = query.gte("created_at", start_date.isoformat())
            
            if end_date:
                query = query.lte("created_at", end_date.isoformat())
            
            # Execute the query
            response = await query.execute()
            
            # Process the response
            if response.data:
                return response.data
            else:
                return []
                
        except Exception as e:
            print(f"Error getting merchant orders: {e}")
            return []
    
    async def get_order_details(self, order_id: str) -> Dict[str, Any]:
        """
        Get detailed information about a specific order
        
        Args:
            order_id: The order ID
            
        Returns:
            Order details including items
        """
        try:
            # Get the order
            order_response = await self.supabase.table("orders").select("*").eq("id", order_id).execute()
            
            if not order_response.data:
                return {}
            
            order = order_response.data[0]
            
            # Get order items
            items_response = await self.supabase.table("order_items").select("*").eq("order_id", order_id).execute()
            
            if items_response.data:
                order["items"] = items_response.data
            else:
                order["items"] = []
            
            # Get customer information
            if order.get("customer_id"):
                customer_response = await self.supabase.table("customers").select("*").eq("id", order["customer_id"]).execute()
                
                if customer_response.data:
                    order["customer"] = customer_response.data[0]
            
            # Get driver information
            if order.get("driver_id"):
                driver_response = await self.supabase.table("drivers").select("*").eq("id", order["driver_id"]).execute()
                
                if driver_response.data:
                    order["driver"] = driver_response.data[0]
            
            return order
            
        except Exception as e:
            print(f"Error getting order details: {e}")
            return {}
    
    async def update_order_status(self, order_id: str, status: str, 
                                 notes: Optional[str] = None) -> Dict[str, Any]:
        """
        Update the status of an order
        
        Args:
            order_id: The order ID
            status: The new status
            notes: Optional notes about the status change
            
        Returns:
            Updated order
        """
        try:
            # Update the order
            update_data = {
                "status": status,
                "updated_at": datetime.utcnow().isoformat()
            }
            
            if notes:
                update_data["notes"] = notes
            
            response = await self.supabase.table("orders").update(update_data).eq("id", order_id).execute()
            
            if response.data:
                return response.data[0]
            else:
                return {}
                
        except Exception as e:
            print(f"Error updating order status: {e}")
            return {}
    
    async def get_merchant_metrics(self, merchant_id: str, 
                                  start_date: Optional[datetime] = None, 
                                  end_date: Optional[datetime] = None) -> Dict[str, Any]:
        """
        Get performance metrics for a merchant
        
        Args:
            merchant_id: The merchant ID
            start_date: Start date for metrics (optional)
            end_date: End date for metrics (optional)
            
        Returns:
            Dictionary of metrics
        """
        try:
            # Set default date range if not provided
            if not end_date:
                end_date = datetime.utcnow()
            
            if not start_date:
                start_date = end_date - timedelta(days=30)
            
            # Get orders for the date range
            orders = await self.get_merchant_orders(merchant_id, start_date=start_date, end_date=end_date)
            
            # Calculate metrics
            total_orders = len(orders)
            
            # Calculate revenue
            total_revenue = sum(order.get("total_amount", 0) for order in orders)
            
            # Calculate average order value
            avg_order_value = total_revenue / total_orders if total_orders > 0 else 0
            
            # Count orders by status
            status_counts = {}
            for order in orders:
                status = order.get("status", "unknown")
                status_counts[status] = status_counts.get(status, 0) + 1
            
            # Calculate completion rate
            completed_orders = status_counts.get("completed", 0) + status_counts.get("delivered", 0)
            completion_rate = (completed_orders / total_orders) * 100 if total_orders > 0 else 0
            
            # Calculate average preparation time
            prep_times = []
            for order in orders:
                if order.get("prepared_at") and order.get("created_at"):
                    created = datetime.fromisoformat(order["created_at"].replace("Z", "+00:00"))
                    prepared = datetime.fromisoformat(order["prepared_at"].replace("Z", "+00:00"))
                    prep_time = (prepared - created).total_seconds() / 60  # in minutes
                    prep_times.append(prep_time)
            
            avg_prep_time = sum(prep_times) / len(prep_times) if prep_times else 0
            
            # Return metrics
            return {
                "total_orders": total_orders,
                "total_revenue": total_revenue,
                "avg_order_value": avg_order_value,
                "status_counts": status_counts,
                "completion_rate": completion_rate,
                "avg_preparation_time": avg_prep_time,
                "period": {
                    "start": start_date.isoformat(),
                    "end": end_date.isoformat()
                }
            }
            
        except Exception as e:
            print(f"Error getting merchant metrics: {e}")
            return {}
    
    async def get_popular_items(self, merchant_id: str, 
                               limit: int = 10, 
                               start_date: Optional[datetime] = None, 
                               end_date: Optional[datetime] = None) -> List[Dict[str, Any]]:
        """
        Get popular items for a merchant
        
        Args:
            merchant_id: The merchant ID
            limit: Maximum number of items to return
            start_date: Start date for analysis (optional)
            end_date: End date for analysis (optional)
            
        Returns:
            List of popular items with counts
        """
        try:
            # Set default date range if not provided
            if not end_date:
                end_date = datetime.utcnow()
            
            if not start_date:
                start_date = end_date - timedelta(days=30)
            
            # Get orders for the date range
            orders = await self.get_merchant_orders(merchant_id, start_date=start_date, end_date=end_date)
            
            # Count items
            item_counts = {}
            for order in orders:
                # Get order items
                items_response = await self.supabase.table("order_items").select("*").eq("order_id", order["id"]).execute()
                
                if items_response.data:
                    for item in items_response.data:
                        item_name = item.get("item_name", "Unknown")
                        quantity = item.get("quantity", 1)
                        
                        if item_name in item_counts:
                            item_counts[item_name] += quantity
                        else:
                            item_counts[item_name] = quantity
            
            # Sort by count and get top items
            sorted_items = sorted(item_counts.items(), key=lambda x: x[1], reverse=True)
            top_items = [{"name": name, "count": count} for name, count in sorted_items[:limit]]
            
            return top_items
            
        except Exception as e:
            print(f"Error getting popular items: {e}")
            return []

# Create a singleton instance
merchant_dashboard = MerchantDashboardService() 
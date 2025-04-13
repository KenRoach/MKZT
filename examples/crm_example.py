import os
import sys
from pathlib import Path
from dotenv import load_dotenv
from src.data.crm_repository import CRMRepository

# Add the project root to the Python path
project_root = Path(__file__).parent.parent
sys.path.append(str(project_root))

# Load environment variables
load_dotenv()

def main():
    """Example usage of the CRM repository"""
    # Create a repository instance
    repo = CRMRepository()
    
    # Example 1: Get all customers
    print("\n=== Example 1: Get all customers ===")
    customers = repo.get_customers(limit=5)
    print(f"Found {len(customers)} customers:")
    for customer in customers:
        print(f"- {customer['name']} ({customer['email']})")
    
    # Example 2: Get all merchants
    print("\n=== Example 2: Get all merchants ===")
    merchants = repo.get_merchants(limit=5)
    print(f"Found {len(merchants)} merchants:")
    for merchant in merchants:
        print(f"- {merchant['name']} ({merchant['business_type']})")
    
    # Example 3: Get all drivers
    print("\n=== Example 3: Get all drivers ===")
    drivers = repo.get_drivers(limit=5)
    print(f"Found {len(drivers)} drivers:")
    for driver in drivers:
        print(f"- {driver['name']} (Status: {driver['status']})")
    
    # Example 4: Get all orders
    print("\n=== Example 4: Get all orders ===")
    orders = repo.get_orders(limit=5)
    print(f"Found {len(orders)} orders:")
    for order in orders:
        print(f"- Order {order['id'][:8]}... (Status: {order['status']}, Amount: ${order['total_amount']})")
    
    # Example 5: Get order items for the first order
    if orders:
        print("\n=== Example 5: Get order items for the first order ===")
        order_items = repo.get_order_items(orders[0]['id'])
        print(f"Found {len(order_items)} items for order {orders[0]['id'][:8]}...:")
        for item in order_items:
            print(f"- {item['quantity']}x {item['item_name']} (${item['unit_price']} each)")
    
    # Example 6: Get notifications
    print("\n=== Example 6: Get notifications ===")
    notifications = repo.get_notifications(limit=5)
    print(f"Found {len(notifications)} notifications:")
    for notification in notifications:
        print(f"- {notification['type']} via {notification['channel']} (Status: {notification['status']})")
    
    # Example 7: Create a new customer
    print("\n=== Example 7: Create a new customer ===")
    new_customer = repo.create_customer({
        "name": "John Smith",
        "email": "john.smith@example.com",
        "phone": "+1234567890",
        "address": "123 Main St, Anytown, USA"
    })
    print(f"Created new customer: {new_customer['name']} (ID: {new_customer['id']})")
    
    # Example 8: Create a new order
    print("\n=== Example 8: Create a new order ===")
    if customers and merchants and drivers:
        new_order = repo.create_order({
            "customer_id": customers[0]['id'],
            "merchant_id": merchants[0]['id'],
            "driver_id": drivers[0]['id'],
            "status": "pending",
            "total_amount": 45.99,
            "payment_status": "pending",
            "delivery_address": "456 Oak Ave, Somewhere, USA",
            "estimated_delivery_time": "2023-12-31T12:00:00Z"
        })
        print(f"Created new order: {new_order['id']} (Status: {new_order['status']})")
        
        # Example 9: Add items to the order
        print("\n=== Example 9: Add items to the order ===")
        items = [
            {"item_name": "Pizza", "quantity": 2, "unit_price": 12.99},
            {"item_name": "Salad", "quantity": 1, "unit_price": 8.99},
            {"item_name": "Drink", "quantity": 2, "unit_price": 2.99}
        ]
        
        for item in items:
            item["order_id"] = new_order["id"]
            new_item = repo.create_order_item(item)
            print(f"Added item: {new_item['quantity']}x {new_item['item_name']}")
        
        # Example 10: Update order status
        print("\n=== Example 10: Update order status ===")
        updated_order = repo.update_order_status(new_order["id"], "confirmed")
        print(f"Updated order status to: {updated_order['status']}")
        
        # Example 11: Create a notification
        print("\n=== Example 11: Create a notification ===")
        new_notification = repo.create_notification({
            "customer_id": customers[0]['id'],
            "type": "order_confirmation",
            "message": f"Your order {new_order['id']} has been confirmed!",
            "channel": "email",
            "status": "pending"
        })
        print(f"Created notification: {new_notification['type']} (Status: {new_notification['status']})")
        
        # Example 12: Update notification status
        print("\n=== Example 12: Update notification status ===")
        updated_notification = repo.update_notification_status(new_notification["id"], "sent")
        print(f"Updated notification status to: {updated_notification['status']}")

if __name__ == "__main__":
    main() 
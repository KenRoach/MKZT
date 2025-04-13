import os
import json
import requests
from typing import Dict, Any, Optional
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class CRMHandler:
    def __init__(self):
        self.api_key = os.getenv("CRM_API_KEY")
        self.api_url = os.getenv("CRM_BASE_URL")
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
    
    async def create_customer(self, customer_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a customer in the CRM"""
        try:
            url = f"{self.api_url}/customers"
            
            response = requests.post(url, headers=self.headers, json=customer_data)
            response.raise_for_status()
            
            return {
                "status": "success",
                "customer_id": response.json().get("id"),
                "message": "Customer created in CRM"
            }
            
        except Exception as e:
            print(f"Error creating customer in CRM: {str(e)}")
            return {
                "status": "error",
                "message": str(e)
            }
    
    async def update_customer(self, customer_id: str, customer_data: Dict[str, Any]) -> Dict[str, Any]:
        """Update a customer in the CRM"""
        try:
            url = f"{self.api_url}/customers/{customer_id}"
            
            response = requests.put(url, headers=self.headers, json=customer_data)
            response.raise_for_status()
            
            return {
                "status": "success",
                "message": "Customer updated in CRM"
            }
            
        except Exception as e:
            print(f"Error updating customer in CRM: {str(e)}")
            return {
                "status": "error",
                "message": str(e)
            }
    
    async def create_order(self, customer_id: str, order_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create an order in the CRM"""
        try:
            url = f"{self.api_url}/customers/{customer_id}/orders"
            
            response = requests.post(url, headers=self.headers, json=order_data)
            response.raise_for_status()
            
            return {
                "status": "success",
                "order_id": response.json().get("id"),
                "message": "Order created in CRM"
            }
            
        except Exception as e:
            print(f"Error creating order in CRM: {str(e)}")
            return {
                "status": "error",
                "message": str(e)
            }
    
    async def update_order_status(self, order_number: str, status: str) -> Dict[str, Any]:
        """Update order status in the CRM"""
        try:
            url = f"{self.api_url}/orders/{order_number}/status"
            
            response = requests.put(url, headers=self.headers, json={"status": status})
            response.raise_for_status()
            
            return {
                "status": "success",
                "message": "Order status updated in CRM"
            }
            
        except Exception as e:
            print(f"Error updating order status in CRM: {str(e)}")
            return {
                "status": "error",
                "message": str(e)
            }
    
    async def get_customer_orders(self, customer_id: str) -> Dict[str, Any]:
        """Get all orders for a customer from the CRM"""
        try:
            url = f"{self.api_url}/customers/{customer_id}/orders"
            
            response = requests.get(url, headers=self.headers)
            response.raise_for_status()
            
            return {
                "status": "success",
                "orders": response.json().get("orders", [])
            }
            
        except Exception as e:
            print(f"Error getting customer orders from CRM: {str(e)}")
            return {
                "status": "error",
                "message": str(e),
                "orders": []
            }
    
    async def get_customer_info(self, customer_id: str) -> Dict[str, Any]:
        """Get customer information from CRM"""
        try:
            url = f"{self.api_url}/customers/{customer_id}"
            
            response = requests.get(url, headers=self.headers)
            response.raise_for_status()
            
            return {
                "status": "success",
                "customer": response.json()
            }
            
        except Exception as e:
            print(f"Error getting customer info from CRM: {str(e)}")
            return {
                "status": "error",
                "message": str(e)
            }
    
    async def get_order_history(self, customer_id: str) -> Dict[str, Any]:
        """Get customer's order history from CRM"""
        try:
            url = f"{self.api_url}/customers/{customer_id}/orders"
            
            response = requests.get(url, headers=self.headers)
            response.raise_for_status()
            
            return {
                "status": "success",
                "orders": response.json().get("orders", [])
            }
            
        except Exception as e:
            print(f"Error getting order history from CRM: {str(e)}")
            return {
                "status": "error",
                "message": str(e),
                "orders": []
            }
    
    async def search_customers(self, query: str) -> Dict[str, Any]:
        """Search customers in CRM"""
        try:
            url = f"{self.api_url}/customers/search"
            
            response = requests.get(url, headers=self.headers, params={"q": query})
            response.raise_for_status()
            
            return {
                "status": "success",
                "customers": response.json().get("customers", [])
            }
            
        except Exception as e:
            print(f"Error searching customers in CRM: {str(e)}")
            return {
                "status": "error",
                "message": str(e),
                "customers": []
            } 
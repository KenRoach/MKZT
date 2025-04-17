import os
import json
import requests
from typing import Dict, Any, Optional
from dotenv import load_dotenv
from src.utils.logger import logger, RequestContext, log_execution_time

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
        self.logger = logger
    
    @log_execution_time(logger)
    async def create_customer(self, customer_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a customer in the CRM"""
        try:
            url = f"{self.api_url}/customers"
            
            self.logger.info(
                "Creating customer in CRM",
                customer_email=customer_data.get("email"),
                customer_name=customer_data.get("name")
            )
            
            response = requests.post(url, headers=self.headers, json=customer_data)
            response.raise_for_status()
            
            customer_id = response.json().get("id")
            self.logger.info(
                "Customer created successfully in CRM",
                customer_id=customer_id
            )
            
            return {
                "status": "success",
                "customer_id": customer_id,
                "message": "Customer created in CRM"
            }
            
        except Exception as e:
            self.logger.exception(
                "Error creating customer in CRM",
                error=str(e),
                customer_email=customer_data.get("email")
            )
            return {
                "status": "error",
                "message": str(e)
            }
    
    @log_execution_time(logger)
    async def update_customer(self, customer_id: str, customer_data: Dict[str, Any]) -> Dict[str, Any]:
        """Update a customer in the CRM"""
        try:
            url = f"{self.api_url}/customers/{customer_id}"
            
            self.logger.info(
                "Updating customer in CRM",
                customer_id=customer_id
            )
            
            response = requests.put(url, headers=self.headers, json=customer_data)
            response.raise_for_status()
            
            self.logger.info(
                "Customer updated successfully in CRM",
                customer_id=customer_id
            )
            
            return {
                "status": "success",
                "message": "Customer updated in CRM"
            }
            
        except Exception as e:
            self.logger.exception(
                "Error updating customer in CRM",
                error=str(e),
                customer_id=customer_id
            )
            return {
                "status": "error",
                "message": str(e)
            }
    
    @log_execution_time(logger)
    async def create_order(self, customer_id: str, order_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create an order in the CRM"""
        try:
            url = f"{self.api_url}/customers/{customer_id}/orders"
            
            self.logger.info(
                "Creating order in CRM",
                customer_id=customer_id,
                order_total=order_data.get("total_amount")
            )
            
            response = requests.post(url, headers=self.headers, json=order_data)
            response.raise_for_status()
            
            order_id = response.json().get("id")
            self.logger.info(
                "Order created successfully in CRM",
                order_id=order_id,
                customer_id=customer_id
            )
            
            return {
                "status": "success",
                "order_id": order_id,
                "message": "Order created in CRM"
            }
            
        except Exception as e:
            self.logger.exception(
                "Error creating order in CRM",
                error=str(e),
                customer_id=customer_id
            )
            return {
                "status": "error",
                "message": str(e)
            }
    
    @log_execution_time(logger)
    async def update_order_status(self, order_number: str, status: str) -> Dict[str, Any]:
        """Update order status in the CRM"""
        try:
            url = f"{self.api_url}/orders/{order_number}/status"
            
            self.logger.info(
                "Updating order status in CRM",
                order_number=order_number,
                new_status=status
            )
            
            response = requests.put(url, headers=self.headers, json={"status": status})
            response.raise_for_status()
            
            self.logger.info(
                "Order status updated successfully in CRM",
                order_number=order_number,
                status=status
            )
            
            return {
                "status": "success",
                "message": "Order status updated in CRM"
            }
            
        except Exception as e:
            self.logger.exception(
                "Error updating order status in CRM",
                error=str(e),
                order_number=order_number,
                status=status
            )
            return {
                "status": "error",
                "message": str(e)
            }
    
    @log_execution_time(logger)
    async def get_customer_orders(self, customer_id: str) -> Dict[str, Any]:
        """Get all orders for a customer from the CRM"""
        try:
            url = f"{self.api_url}/customers/{customer_id}/orders"
            
            self.logger.info(
                "Fetching customer orders from CRM",
                customer_id=customer_id
            )
            
            response = requests.get(url, headers=self.headers)
            response.raise_for_status()
            
            orders = response.json().get("orders", [])
            self.logger.info(
                "Customer orders fetched successfully from CRM",
                customer_id=customer_id,
                order_count=len(orders)
            )
            
            return {
                "status": "success",
                "orders": orders
            }
            
        except Exception as e:
            self.logger.exception(
                "Error getting customer orders from CRM",
                error=str(e),
                customer_id=customer_id
            )
            return {
                "status": "error",
                "message": str(e),
                "orders": []
            }
    
    @log_execution_time(logger)
    async def get_customer_info(self, customer_id: str) -> Dict[str, Any]:
        """Get customer information from CRM"""
        try:
            url = f"{self.api_url}/customers/{customer_id}"
            
            self.logger.info(
                "Fetching customer information from CRM",
                customer_id=customer_id
            )
            
            response = requests.get(url, headers=self.headers)
            response.raise_for_status()
            
            customer = response.json()
            self.logger.info(
                "Customer information fetched successfully from CRM",
                customer_id=customer_id
            )
            
            return {
                "status": "success",
                "customer": customer
            }
            
        except Exception as e:
            self.logger.exception(
                "Error getting customer info from CRM",
                error=str(e),
                customer_id=customer_id
            )
            return {
                "status": "error",
                "message": str(e)
            }
    
    @log_execution_time(logger)
    async def get_order_history(self, customer_id: str) -> Dict[str, Any]:
        """Get customer's order history from CRM"""
        try:
            url = f"{self.api_url}/customers/{customer_id}/orders"
            
            self.logger.info(
                "Fetching customer order history from CRM",
                customer_id=customer_id
            )
            
            response = requests.get(url, headers=self.headers)
            response.raise_for_status()
            
            orders = response.json().get("orders", [])
            self.logger.info(
                "Customer order history fetched successfully from CRM",
                customer_id=customer_id,
                order_count=len(orders)
            )
            
            return {
                "status": "success",
                "orders": orders
            }
            
        except Exception as e:
            self.logger.exception(
                "Error getting order history from CRM",
                error=str(e),
                customer_id=customer_id
            )
            return {
                "status": "error",
                "message": str(e),
                "orders": []
            }
    
    @log_execution_time(logger)
    async def search_customers(self, query: str) -> Dict[str, Any]:
        """Search customers in CRM"""
        try:
            url = f"{self.api_url}/customers/search"
            
            self.logger.info(
                "Searching customers in CRM",
                query=query
            )
            
            response = requests.get(url, headers=self.headers, params={"q": query})
            response.raise_for_status()
            
            customers = response.json().get("customers", [])
            self.logger.info(
                "Customer search completed successfully in CRM",
                query=query,
                result_count=len(customers)
            )
            
            return {
                "status": "success",
                "customers": customers
            }
            
        except Exception as e:
            self.logger.exception(
                "Error searching customers in CRM",
                error=str(e),
                query=query
            )
            return {
                "status": "error",
                "message": str(e),
                "customers": []
            } 
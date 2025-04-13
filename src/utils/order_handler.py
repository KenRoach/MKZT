from typing import Dict, Any, List, Optional
import json
import uuid
from datetime import datetime
from src.utils.database import SessionLocal, Customer, Order
from src.crm.handler import CRMHandler
from src.ai.handler import AIHandler

class OrderHandler:
    def __init__(self):
        self.crm_handler = CRMHandler()

    async def create_order(self, customer_id: int, items: List[Dict[str, Any]], shipping_address: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new order in the database and CRM"""
        try:
            db = SessionLocal()
            
            # Get customer
            customer = db.query(Customer).filter(Customer.id == customer_id).first()
            if not customer:
                return {"status": "error", "message": "Customer not found"}
            
            # Generate order number
            order_number = f"ORD-{uuid.uuid4().hex[:8].upper()}"
            
            # Calculate total amount (in cents)
            total_amount = sum(item.get("price", 0) * item.get("quantity", 1) for item in items)
            
            # Create order in database
            order = Order(
                customer_id=customer_id,
                order_number=order_number,
                status="pending",
                items=items,
                total_amount=total_amount,
                shipping_address=shipping_address
            )
            
            db.add(order)
            db.commit()
            db.refresh(order)
            
            # Create order in CRM
            crm_result = await self.crm_handler.create_order(str(customer_id), {
                "order_number": order_number,
                "items": items,
                "total_amount": total_amount,
                "shipping_address": shipping_address
            })
            
            if crm_result.get("status") == "error":
                # Update order status to indicate CRM error
                order.status = "crm_error"
                db.commit()
                return {"status": "error", "message": "Error creating order in CRM", "order_id": order.id}
            
            return {
                "status": "success",
                "order_id": order.id,
                "order_number": order_number,
                "total_amount": total_amount
            }
            
        except Exception as e:
            return {"status": "error", "message": str(e)}
        finally:
            db.close()

    async def get_order(self, order_id: int) -> Dict[str, Any]:
        """Get order details from database"""
        try:
            db = SessionLocal()
            
            # Get order
            order = db.query(Order).filter(Order.id == order_id).first()
            if not order:
                return {"status": "error", "message": "Order not found"}
            
            # Get customer
            customer = db.query(Customer).filter(Customer.id == order.customer_id).first()
            
            return {
                "status": "success",
                "order": {
                    "id": order.id,
                    "order_number": order.order_number,
                    "status": order.status,
                    "items": order.items,
                    "total_amount": order.total_amount,
                    "shipping_address": order.shipping_address,
                    "created_at": order.created_at.isoformat(),
                    "updated_at": order.updated_at.isoformat(),
                    "customer": {
                        "id": customer.id,
                        "name": customer.name,
                        "phone_number": customer.phone_number,
                        "email": customer.email
                    } if customer else None
                }
            }
            
        except Exception as e:
            return {"status": "error", "message": str(e)}
        finally:
            db.close()

    async def update_order_status(self, order_id: int, status: str) -> Dict[str, Any]:
        """Update order status in database and CRM"""
        try:
            db = SessionLocal()
            
            # Get order
            order = db.query(Order).filter(Order.id == order_id).first()
            if not order:
                return {"status": "error", "message": "Order not found"}
            
            # Update status
            order.status = status
            db.commit()
            
            # Update status in CRM
            crm_result = await self.crm_handler.update_order_status(order.order_number, status)
            
            if crm_result.get("status") == "error":
                return {"status": "error", "message": "Error updating order status in CRM"}
            
            return {
                "status": "success",
                "order_id": order.id,
                "order_number": order.order_number,
                "status": order.status
            }
            
        except Exception as e:
            return {"status": "error", "message": str(e)}
        finally:
            db.close()

    async def get_customer_orders(self, customer_id: int) -> Dict[str, Any]:
        """Get all orders for a customer"""
        try:
            db = SessionLocal()
            
            # Get orders
            orders = db.query(Order).filter(Order.customer_id == customer_id).order_by(Order.created_at.desc()).all()
            
            return {
                "status": "success",
                "orders": [
                    {
                        "id": order.id,
                        "order_number": order.order_number,
                        "status": order.status,
                        "total_amount": order.total_amount,
                        "created_at": order.created_at.isoformat()
                    }
                    for order in orders
                ]
            }
            
        except Exception as e:
            return {"status": "error", "message": str(e)}
        finally:
            db.close()

    async def extract_order_from_message(self, message: str) -> Dict[str, Any]:
        """Extract order information from a message using AI"""
        try:
            # Use AI handler to extract order details
            ai_handler = AIHandler()
            
            # Create a prompt for the AI
            prompt = f"""
            Extract order information from the following message. 
            Return a JSON object with 'items' (list of products with product_id, quantity, and price) 
            and 'shipping_address' (dictionary with street, city, state, zip, country).
            If shipping address is not provided, use default values.
            If product details are unclear, use best guess based on context.
            
            Message: {message}
            """
            
            # Get AI response
            response = await ai_handler.get_completion(prompt)
            
            # Parse the response
            try:
                # Extract JSON from response
                json_str = response.strip()
                if json_str.startswith("```json"):
                    json_str = json_str[7:-3]  # Remove ```json and ``` markers
                
                order_data = json.loads(json_str)
                
                # Validate the structure
                if "items" not in order_data or "shipping_address" not in order_data:
                    raise ValueError("Missing required fields in AI response")
                
                # Ensure shipping address has all required fields
                required_address_fields = ["street", "city", "state", "zip", "country"]
                for field in required_address_fields:
                    if field not in order_data["shipping_address"]:
                        order_data["shipping_address"][field] = "Not provided"
                
                return order_data
                
            except json.JSONDecodeError:
                # If AI response is not valid JSON, use a default structure
                return {
                    "items": [
                        {"product_id": 1, "quantity": 1, "price": 1000}  # $10.00
                    ],
                    "shipping_address": {
                        "street": "Not provided",
                        "city": "Not provided",
                        "state": "Not provided",
                        "zip": "Not provided",
                        "country": "Not provided"
                    }
                }
                
        except Exception as e:
            # Log the error and return a default structure
            print(f"Error extracting order from message: {str(e)}")
            return {
                "items": [
                    {"product_id": 1, "quantity": 1, "price": 1000}  # $10.00
                ],
                "shipping_address": {
                    "street": "Not provided",
                    "city": "Not provided",
                    "state": "Not provided",
                    "zip": "Not provided",
                    "country": "Not provided"
                }
            } 
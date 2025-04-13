from typing import Dict, Any, Optional
import json
from src.utils.database import SessionLocal, Customer
from src.crm.handler import CRMHandler

class CustomerHandler:
    def __init__(self):
        self.crm_handler = CRMHandler()
    
    async def get_or_create_customer(self, phone_number: str) -> Dict[str, Any]:
        """Get existing customer or create a new one"""
        try:
            db = SessionLocal()
            
            # Check if customer exists
            customer = db.query(Customer).filter(Customer.phone_number == phone_number).first()
            
            if customer:
                return {
                    "status": "success",
                    "customer_id": customer.id,
                    "message": "Customer found"
                }
            
            # Create new customer
            customer = Customer(
                phone_number=phone_number,
                name="",  # Will be updated when provided
                email=""  # Will be updated when provided
            )
            
            db.add(customer)
            db.commit()
            db.refresh(customer)
            
            # Create customer in CRM
            crm_result = await self.crm_handler.create_customer({
                "phone_number": phone_number,
                "name": "",
                "email": ""
            })
            
            if crm_result.get("status") == "error":
                return {
                    "status": "error",
                    "message": "Error creating customer in CRM",
                    "customer_id": customer.id
                }
            
            return {
                "status": "success",
                "customer_id": customer.id,
                "message": "Customer created"
            }
            
        except Exception as e:
            return {"status": "error", "message": str(e)}
        finally:
            db.close()
    
    async def get_customer_by_phone(self, phone_number: str) -> Dict[str, Any]:
        """Get customer by phone number"""
        try:
            db = SessionLocal()
            
            customer = db.query(Customer).filter(Customer.phone_number == phone_number).first()
            
            if not customer:
                return {"status": "error", "message": "Customer not found"}
            
            return {
                "status": "success",
                "customer": {
                    "id": customer.id,
                    "phone_number": customer.phone_number,
                    "name": customer.name,
                    "email": customer.email,
                    "created_at": customer.created_at.isoformat(),
                    "updated_at": customer.updated_at.isoformat()
                }
            }
            
        except Exception as e:
            return {"status": "error", "message": str(e)}
        finally:
            db.close()
    
    async def update_customer(self, customer_id: int, data: Dict[str, Any]) -> Dict[str, Any]:
        """Update customer information"""
        try:
            db = SessionLocal()
            
            customer = db.query(Customer).filter(Customer.id == customer_id).first()
            
            if not customer:
                return {"status": "error", "message": "Customer not found"}
            
            # Update fields
            if "name" in data:
                customer.name = data["name"]
            if "email" in data:
                customer.email = data["email"]
            
            db.commit()
            
            # Update customer in CRM
            crm_result = await self.crm_handler.update_customer(str(customer_id), {
                "name": customer.name,
                "email": customer.email
            })
            
            if crm_result.get("status") == "error":
                return {
                    "status": "error",
                    "message": "Error updating customer in CRM"
                }
            
            return {
                "status": "success",
                "message": "Customer updated successfully"
            }
            
        except Exception as e:
            return {"status": "error", "message": str(e)}
        finally:
            db.close()
    
    async def extract_customer_info(self, message: str) -> Dict[str, Any]:
        """Extract customer information from a message"""
        # This is a placeholder for AI-based customer info extraction
        # In a real implementation, you would use the AI handler to extract customer details
        return {
            "name": "",
            "email": ""
        } 
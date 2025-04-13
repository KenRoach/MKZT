from typing import Dict, Any, List, Optional
import json
import re
from src.utils.order_handler import OrderHandler
from src.utils.customer_handler import CustomerHandler
from src.ai.handler import AIHandler
from src.utils.database import SessionLocal, Customer, Message

class MessageHandler:
    def __init__(self):
        self.order_handler = OrderHandler()
        self.customer_handler = CustomerHandler()
        self.ai_handler = AIHandler()
    
    async def process_message(self, message_data: Dict[str, Any]) -> Dict[str, Any]:
        """Process an incoming WhatsApp message"""
        try:
            # Extract message details
            phone_number = message_data.get("from")
            message_text = message_data.get("text", {}).get("body", "")
            message_id = message_data.get("id")
            
            if not phone_number or not message_text:
                return {"status": "error", "message": "Invalid message format"}
            
            # Get or create customer
            customer_result = await self.customer_handler.get_or_create_customer(phone_number)
            if customer_result["status"] != "success":
                return customer_result
            
            customer_id = customer_result["customer_id"]
            
            # Save message to database
            db = SessionLocal()
            try:
                message = Message(
                    customer_id=customer_id,
                    message_id=message_id,
                    content=message_text,
                    direction="incoming"
                )
                db.add(message)
                db.commit()
            except Exception as e:
                db.rollback()
                print(f"Error saving message: {str(e)}")
            finally:
                db.close()
            
            # Use AI to understand message intent
            intent_result = await self.ai_handler.analyze_intent(message_text)
            
            if intent_result["status"] != "success":
                return {
                    "status": "error",
                    "message": "Could not understand message intent",
                    "response": "I'm sorry, I couldn't understand your message. Could you please rephrase it?"
                }
            
            intent = intent_result["intent"]
            
            # Process based on intent
            if intent == "order":
                return await self._handle_order_intent(customer_id, message_text)
            elif intent == "order_status":
                return await self._handle_order_status_intent(customer_id)
            elif intent == "help":
                return await self._handle_help_intent()
            elif intent == "greeting":
                return await self._handle_greeting_intent(customer_id)
            else:
                return {
                    "status": "success",
                    "response": "I'm not sure how to help with that. You can ask me about placing an order, checking order status, or type 'help' for more information."
                }
                
        except Exception as e:
            print(f"Error processing message: {str(e)}")
            return {
                "status": "error",
                "message": str(e),
                "response": "I'm sorry, there was an error processing your message. Please try again later."
            }
    
    async def _handle_order_intent(self, customer_id: int, message_text: str) -> Dict[str, Any]:
        """Handle order-related intents"""
        # Extract order details from message
        order_data = await self.order_handler.extract_order_from_message(message_text)
        
        # Check if shipping address is complete
        if any(value == "Not provided" for value in order_data["shipping_address"].values()):
            return {
                "status": "success",
                "response": "I need your shipping address to complete the order. Please provide your full address including street, city, state, zip code, and country.",
                "needs_shipping_address": True,
                "extracted_items": order_data["items"]
            }
        
        # Create the order
        result = await self.order_handler.create_order(
            customer_id=customer_id,
            items=order_data["items"],
            shipping_address=order_data["shipping_address"]
        )
        
        if result["status"] == "success":
            return {
                "status": "success",
                "response": f"Great! I've created your order #{result['order_number']}. The total amount is ${result['total_amount']/100:.2f}. You'll receive a confirmation email shortly.",
                "order_id": result["order_id"],
                "order_number": result["order_number"]
            }
        else:
            return {
                "status": "error",
                "message": result.get("message", "Unknown error"),
                "response": "I'm sorry, there was an error creating your order. Please try again or contact support."
            }
    
    async def _handle_order_status_intent(self, customer_id: int) -> Dict[str, Any]:
        """Handle order status check intents"""
        result = await self.order_handler.get_customer_orders(customer_id)
        
        if result["status"] != "success" or not result["orders"]:
            return {
                "status": "success",
                "response": "You don't have any orders yet."
            }
        
        # Format orders for response
        orders_text = ""
        for order in result["orders"]:
            orders_text += f"Order #{order['order_number']}: {order['status']} (${order['total_amount']/100:.2f})\n"
        
        return {
            "status": "success",
            "response": f"Here are your orders:\n{orders_text}"
        }
    
    async def _handle_help_intent(self) -> Dict[str, Any]:
        """Handle help requests"""
        help_text = """
        I can help you with the following:
        - Place an order: Just tell me what you want to order
        - Check order status: Ask "What's the status of my orders?"
        - Get help: Type "help" or "what can you do?"
        
        For example, you can say: "I want to order 2 blue shirts and 1 red shirt"
        """
        
        return {
            "status": "success",
            "response": help_text
        }
    
    async def _handle_greeting_intent(self, customer_id: int) -> Dict[str, Any]:
        """Handle greeting messages"""
        # Get customer name if available
        db = SessionLocal()
        try:
            customer = db.query(Customer).filter(Customer.id == customer_id).first()
            name = customer.name if customer else "there"
        except Exception:
            name = "there"
        finally:
            db.close()
        
        return {
            "status": "success",
            "response": f"Hello {name}! How can I help you today? You can place an order, check order status, or type 'help' for more information."
        }
    
    async def save_response(self, customer_id: int, message_id: str, response_text: str) -> None:
        """Save a response message to the database"""
        db = SessionLocal()
        try:
            message = Message(
                customer_id=customer_id,
                message_id=message_id,
                content=response_text,
                direction="outgoing"
            )
            db.add(message)
            db.commit()
        except Exception as e:
            db.rollback()
            print(f"Error saving response: {str(e)}")
        finally:
            db.close() 
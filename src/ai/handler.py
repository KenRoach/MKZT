import os
import json
import logging
from typing import Dict, Any, List
import openai
from datetime import datetime, timedelta
from ratelimit import limits, sleep_and_retry
from dotenv import load_dotenv
from src.config.config import OPENAI_API_KEY, AI_MODEL, MAX_TOKENS, TEMPERATURE
from src.utils.database import SessionLocal, Customer, Conversation, Order
from src.utils.website_scraper import WebsiteScraper
from src.crm.handler import CRMHandler

logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

class AIHandler:
    def __init__(self):
        """Initialize the AI handler with OpenAI configuration"""
        self.api_key = os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            raise ValueError("OPENAI_API_KEY environment variable is not set")
        
        openai.api_key = self.api_key
        self.model = os.getenv("OPENAI_MODEL", "gpt-3.5-turbo")
        self.max_tokens = int(os.getenv("OPENAI_MAX_TOKENS", "1000"))
        self.temperature = float(os.getenv("OPENAI_TEMPERATURE", "0.7"))
        
        # Rate limiting: 3 requests per minute
        self.call_ai = sleep_and_retry(limits(calls=3, period=60)(self._call_ai))

    async def _call_ai(self, prompt: str) -> str:
        """Make an API call to OpenAI"""
        try:
            response = await openai.ChatCompletion.acreate(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                max_tokens=self.max_tokens,
                temperature=self.temperature
            )
            return response.choices[0].message.content
        except Exception as e:
            logger.error(f"Error calling OpenAI API: {str(e)}")
            raise

    async def analyze_intent(self, message: str) -> Dict[str, Any]:
        """Analyze the intent of a message"""
        prompt = f"""
        Analyze the following message and determine its intent. 
        Return a JSON object with the following structure:
        {{
            "intent": "greeting|order|order_status|help|unknown",
            "confidence": float between 0 and 1,
            "entities": {{
                "order_number": "string or null",
                "items": ["list of items or empty"],
                "shipping_address": "string or null"
            }}
        }}

        Message: {message}
        """

        try:
            response = await self.call_ai(prompt)
            return json.loads(response)
        except json.JSONDecodeError:
            logger.error("Failed to parse AI response as JSON")
            return {
                "intent": "unknown",
                "confidence": 0.0,
                "entities": {
                    "order_number": None,
                    "items": [],
                    "shipping_address": None
                }
            }

    async def extract_order_details(self, message: str) -> Dict[str, Any]:
        """Extract order details from a message"""
        prompt = f"""
        Extract order details from the following message.
        Return a JSON object with the following structure:
        {{
            "items": [
                {{
                    "name": "string",
                    "quantity": integer,
                    "price": float or null
                }}
            ],
            "shipping_address": {{
                "street": "string",
                "city": "string",
                "state": "string",
                "zip_code": "string",
                "country": "string"
            }},
            "total_amount": float or null
        }}

        Message: {message}
        """

        try:
            response = await self.call_ai(prompt)
            return json.loads(response)
        except json.JSONDecodeError:
            logger.error("Failed to parse AI response as JSON")
            return {
                "items": [],
                "shipping_address": None,
                "total_amount": None
            }

    async def generate_response(self, intent: str, context: Dict[str, Any]) -> str:
        """Generate a response based on the intent and context"""
        prompt = f"""
        Generate a natural response for the following intent and context.
        The response should be friendly and helpful.

        Intent: {intent}
        Context: {json.dumps(context, indent=2)}
        """

        try:
            return await self.call_ai(prompt)
        except Exception as e:
            logger.error(f"Error generating response: {str(e)}")
            return "I apologize, but I'm having trouble processing your request. Please try again later."

    async def process_message(self, message: str, phone_number: str) -> str:
        """Process incoming message using AI and store in database"""
        try:
            # Get or create customer
            db = SessionLocal()
            customer = db.query(Customer).filter(Customer.phone_number == phone_number).first()
            if not customer:
                customer = Customer(phone_number=phone_number)
                db.add(customer)
                db.commit()
                db.refresh(customer)
            
            # Process message with AI
            response = await self._generate_ai_response(message, customer.id, db)
            
            # Store conversation
            conversation = Conversation(
                customer_id=customer.id,
                message=message,
                response=response
            )
            db.add(conversation)
            db.commit()
            
            return response
        except Exception as e:
            return f"Error processing message: {str(e)}"
        finally:
            db.close()

    async def _generate_ai_response(self, message: str, customer_id: int, db) -> str:
        """Generate AI response based on message and context"""
        try:
            # Get customer context
            context = await self._get_customer_context(customer_id, db)
            
            # Check if message is about ordering
            if self._is_order_related(message):
                # Search for products with descriptions
                products = await this.website_scraper.search_products(message)
                
                # Format products with descriptions
                formatted_products = [{
                    "name": product["name"],
                    "price": product["price"],
                    "description": product.get("description", "No description available")
                } for product in products]
                
                # Generate order-related response
                response = await this.client.chat.completions.create(
                    model=AI_MODEL,
                    messages=[
                        {"role": "system", "content": "You are a helpful assistant that helps customers with their orders. Include product descriptions in your responses when available."},
                        {"role": "user", "content": f"Context: {json.dumps(context)}\nProducts: {json.dumps(formatted_products)}\nMessage: {message}"}
                    ],
                    max_tokens=MAX_TOKENS,
                    temperature=TEMPERATURE
                )
                return response.choices[0].message.content
            else:
                # Generate general response
                response = await this.client.chat.completions.create(
                    model=AI_MODEL,
                    messages=[
                        {"role": "system", "content": "You are a helpful assistant that helps customers with their orders."},
                        {"role": "user", "content": f"Context: {json.dumps(context)}\nMessage: {message}"}
                    ],
                    max_tokens=MAX_TOKENS,
                    temperature=TEMPERATURE
                )
                return response.choices[0].message.content
        except Exception as e:
            return f"Error generating response: {str(e)}"

    def _is_order_related(self, message: str) -> bool:
        """Check if message is related to ordering"""
        order_keywords = ["order", "buy", "purchase", "product", "price", "cost", "shipping", "delivery"]
        return any(keyword in message.lower() for keyword in order_keywords)

    async def search_website(self, query: str) -> str:
        """Search website content using AI"""
        try:
            # Search for products
            products = await self.website_scraper.search_products(query)
            
            # Generate response with product information
            response = await this.client.chat.completions.create(
                model=AI_MODEL,
                messages=[
                    {"role": "system", "content": "Search the website for relevant information about products and services."},
                    {"role": "user", "content": f"Products: {json.dumps(products)}\nQuery: {query}"}
                ],
                max_tokens=MAX_TOKENS,
                temperature=TEMPERATURE
            )
            return response.choices[0].message.content
        except Exception as e:
            return f"Error searching website: {str(e)}"

    async def search_crm(self, query: str) -> str:
        """Search CRM data using AI"""
        try:
            # Search customers in CRM
            customers = await self.crm_handler.search_customers(query)
            
            # Generate response with customer information
            response = await this.client.chat.completions.create(
                model=AI_MODEL,
                messages=[
                    {"role": "system", "content": "Search the CRM for customer information and order history."},
                    {"role": "user", "content": f"Customers: {json.dumps(customers)}\nQuery: {query}"}
                ],
                max_tokens=MAX_TOKENS,
                temperature=TEMPERATURE
            )
            return response.choices[0].message.content
        except Exception as e:
            return f"Error searching CRM: {str(e)}" 
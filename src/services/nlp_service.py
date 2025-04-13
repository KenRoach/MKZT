import os
from typing import Dict, Any, Optional
import openai
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class NLPService:
    def __init__(self):
        """Initialize the NLP service with OpenAI configuration"""
        self.api_key = os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            raise ValueError("Missing OPENAI_API_KEY in environment variables")
        
        openai.api_key = self.api_key
        self.model = os.getenv("OPENAI_MODEL", "gpt-4")
        self.temperature = float(os.getenv("OPENAI_TEMPERATURE", "0.7"))
        self.max_tokens = int(os.getenv("OPENAI_MAX_TOKENS", "1000"))
    
    async def extract_order_details(self, message: str) -> Dict[str, Any]:
        """
        Extract order details from a message using GPT-4
        
        Args:
            message: The message to analyze
            
        Returns:
            Dict containing extracted order details
        """
        try:
            # Create a prompt for GPT-4
            prompt = f"""
            Extract order details from the following message. Return a JSON object with these fields:
            - items: List of items with name, quantity, and any special instructions
            - total_amount: Total order amount (if mentioned)
            - delivery_address: Delivery address (if mentioned)
            - special_instructions: Any special instructions for the order
            
            Message: {message}
            
            Return only the JSON object, no additional text.
            """
            
            # Call GPT-4
            response = await openai.ChatCompletion.acreate(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are an order extraction assistant. Extract order details from messages and return them in a structured JSON format."},
                    {"role": "user", "content": prompt}
                ],
                temperature=self.temperature,
                max_tokens=self.max_tokens
            )
            
            # Parse the response
            extracted_data = response.choices[0].message.content
            
            # Clean and validate the extracted data
            order_details = self._clean_extracted_data(extracted_data)
            
            return order_details
            
        except Exception as e:
            print(f"Error extracting order details: {e}")
            return {
                "items": [],
                "total_amount": None,
                "delivery_address": None,
                "special_instructions": None
            }
    
    def _clean_extracted_data(self, extracted_data: str) -> Dict[str, Any]:
        """
        Clean and validate the extracted data from GPT-4
        
        Args:
            extracted_data: Raw JSON string from GPT-4
            
        Returns:
            Cleaned and validated order details
        """
        try:
            # Remove any markdown formatting
            cleaned_data = extracted_data.strip('`').strip()
            if cleaned_data.startswith('json'):
                cleaned_data = cleaned_data[4:].strip()
            
            # Parse the JSON
            import json
            data = json.loads(cleaned_data)
            
            # Validate and set default values
            return {
                "items": data.get("items", []),
                "total_amount": data.get("total_amount"),
                "delivery_address": data.get("delivery_address"),
                "special_instructions": data.get("special_instructions")
            }
            
        except Exception as e:
            print(f"Error cleaning extracted data: {e}")
            return {
                "items": [],
                "total_amount": None,
                "delivery_address": None,
                "special_instructions": None
            }
    
    async def enrich_order_details(self, order_details: Dict[str, Any]) -> Dict[str, Any]:
        """
        Enrich order details with additional information using GPT-4
        
        Args:
            order_details: Basic order details
            
        Returns:
            Enriched order details
        """
        try:
            # Create a prompt for enrichment
            prompt = f"""
            Enrich the following order details with additional information:
            {order_details}
            
            Add these fields if possible:
            - estimated_preparation_time: Estimated time to prepare the order
            - suggested_addons: Relevant add-ons or complementary items
            - dietary_restrictions: Any dietary restrictions based on the order
            - order_priority: Priority level (high/medium/low) based on items and instructions
            
            Return only the JSON object with both original and new fields, no additional text.
            """
            
            # Call GPT-4
            response = await openai.ChatCompletion.acreate(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are an order enrichment assistant. Add valuable information to order details."},
                    {"role": "user", "content": prompt}
                ],
                temperature=self.temperature,
                max_tokens=self.max_tokens
            )
            
            # Parse and clean the response
            enriched_data = self._clean_extracted_data(response.choices[0].message.content)
            
            # Merge with original data
            order_details.update(enriched_data)
            
            return order_details
            
        except Exception as e:
            print(f"Error enriching order details: {e}")
            return order_details

# Create a singleton instance
nlp_service = NLPService() 
from typing import Dict, Any, List
from datetime import datetime
import asyncio
from enum import Enum
from deep_translator import GoogleTranslator
from langdetect import detect
import json
import os

class SupportedLanguages(Enum):
    EN = "en"
    ES = "es"
    PT = "pt"

class EnhancedMultilingualHandler:
    def __init__(self):
        self.translators = {
            "es": GoogleTranslator(source='auto', target='es'),
            "en": GoogleTranslator(source='auto', target='en'),
            "pt": GoogleTranslator(source='auto', target='pt')
        }
        self.load_message_templates()
        
    def load_message_templates(self):
        """Load message templates from JSON file"""
        with open('src/templates/message_templates.json', 'r', encoding='utf-8') as f:
            self.templates = json.load(f)

    async def translate_text(self, text: str, target_lang: str) -> str:
        """Translate text to target language"""
        try:
            if target_lang not in self.translators:
                raise ValueError(f"Unsupported language: {target_lang}")
            return self.translators[target_lang].translate(text)
        except Exception as e:
            logger.error(f"Translation error: {str(e)}")
            return text

    async def detect_language(self, text: str) -> str:
        """Detect message language"""
        try:
            detected = detect(text)
            return detected if detected in ["en", "es", "pt"] else "en"
        except:
            return "en"

    async def generate_rich_message(self, 
                                  template_key: str, 
                                  data: Dict[str, Any], 
                                  language: str) -> Dict[str, Any]:
        """Generate rich message with media and interactive elements"""
        base_template = self.templates[language][template_key]
        
        message = {
            "text": base_template["text"].format(**data),
            "components": []
        }
        
        # Add media components if specified
        if "media" in base_template:
            message["media"] = {
                "type": base_template["media"]["type"],
                "url": base_template["media"]["url"].format(**data)
            }
            
        # Add interactive components
        if "buttons" in base_template:
            message["components"].append({
                "type": "buttons",
                "buttons": [
                    {
                        "type": "reply",
                        "reply": {
                            "id": btn["id"],
                            "title": btn["text"].format(**data)
                        }
                    } for btn in base_template["buttons"]
                ]
            })
            
        # Add location if needed
        if "location" in data:
            message["components"].append({
                "type": "location",
                "location": {
                    "latitude": data["location"]["lat"],
                    "longitude": data["location"]["lng"],
                    "name": data["location"]["name"],
                    "address": data["location"]["address"]
                }
            })
            
        return message

class AdvancedOrderTracking:
    def __init__(self):
        self.tracking_data = {}
        
    async def update_order_status(self, 
                                order_id: str, 
                                status: str, 
                                details: Dict[str, Any]) -> Dict[str, Any]:
        """Update order status with detailed tracking"""
        timestamp = datetime.now().isoformat()
        
        if order_id not in self.tracking_data:
            self.tracking_data[order_id] = {
                "status_history": [],
                "current_status": status,
                "metrics": {
                    "preparation_time": 0,
                    "delivery_time": 0,
                    "total_time": 0
                }
            }
            
        self.tracking_data[order_id]["status_history"].append({
            "status": status,
            "timestamp": timestamp,
            "details": details
        })
        
        # Update metrics
        await self._update_metrics(order_id)
        
        return {
            "order_id": order_id,
            "current_status": status,
            "timestamp": timestamp,
            "metrics": self.tracking_data[order_id]["metrics"]
        }
        
    async def _update_metrics(self, order_id: str) -> None:
        """Update order metrics"""
        history = self.tracking_data[order_id]["status_history"]
        metrics = self.tracking_data[order_id]["metrics"]
        
        # Calculate preparation time
        prep_start = next((x for x in history if x["status"] == "confirmed"), None)
        prep_end = next((x for x in history if x["status"] == "ready_for_pickup"), None)
        
        if prep_start and prep_end:
            start_time = datetime.fromisoformat(prep_start["timestamp"])
            end_time = datetime.fromisoformat(prep_end["timestamp"])
            metrics["preparation_time"] = (end_time - start_time).total_seconds() / 60
            
        # Calculate delivery time
        delivery_start = next((x for x in history if x["status"] == "in_delivery"), None)
        delivery_end = next((x for x in history if x["status"] == "delivered"), None)
        
        if delivery_start and delivery_end:
            start_time = datetime.fromisoformat(delivery_start["timestamp"])
            end_time = datetime.fromisoformat(delivery_end["timestamp"])
            metrics["delivery_time"] = (end_time - start_time).total_seconds() / 60
            
        # Update total time
        metrics["total_time"] = metrics["preparation_time"] + metrics["delivery_time"] 
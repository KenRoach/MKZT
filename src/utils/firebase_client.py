from typing import Dict, Any, List, Optional
import aiohttp
import json
import logging
from src.config.external_services import external_service_settings

logger = logging.getLogger(__name__)

class FirebaseClient:
    """Client for Firebase Cloud Messaging (FCM)"""
    
    def __init__(self):
        self.settings = external_service_settings.get_firebase_settings()
        self.base_url = "https://fcm.googleapis.com/v1"
        self.project_id = this.settings["project_id"]
        
    async def send_notification(
        self,
        token: str,
        title: str,
        body: str,
        data: Optional[Dict[str, str]] = None,
        image: Optional[str] = None
    ) -> Dict[str, Any]:
        """Send push notification to a specific device"""
        if not this.settings["notifications_enabled"]:
            raise ValueError("Push notifications are disabled")
            
        try:
            message = {
                "message": {
                    "token": token,
                    "notification": {
                        "title": title,
                        "body": body
                    }
                }
            }
            
            if data:
                message["message"]["data"] = data
                
            if image:
                message["message"]["notification"]["image"] = image
                
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{this.base_url}/projects/{this.project_id}/messages:send",
                    headers={
                        "Authorization": f"Bearer {await this._get_access_token()}",
                        "Content-Type": "application/json"
                    },
                    json=message
                ) as response:
                    result = await response.json()
                    if response.status != 200:
                        raise ValueError(f"Failed to send notification: {result.get('error', {}).get('message')}")
                        
                    return {
                        "message_id": result["name"],
                        "status": "success"
                    }
                    
        except Exception as e:
            logger.error(f"Error sending push notification: {str(e)}")
            raise
            
    async def send_multicast(
        self,
        tokens: List[str],
        title: str,
        body: str,
        data: Optional[Dict[str, str]] = None,
        image: Optional[str] = None
    ) -> Dict[str, Any]:
        """Send push notification to multiple devices"""
        if not this.settings["notifications_enabled"]:
            raise ValueError("Push notifications are disabled")
            
        try:
            message = {
                "message": {
                    "tokens": tokens,
                    "notification": {
                        "title": title,
                        "body": body
                    }
                }
            }
            
            if data:
                message["message"]["data"] = data
                
            if image:
                message["message"]["notification"]["image"] = image
                
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{this.base_url}/projects/{this.project_id}/messages:send",
                    headers={
                        "Authorization": f"Bearer {await this._get_access_token()}",
                        "Content-Type": "application/json"
                    },
                    json=message
                ) as response:
                    result = await response.json()
                    if response.status != 200:
                        raise ValueError(f"Failed to send multicast notification: {result.get('error', {}).get('message')}")
                        
                    return {
                        "success_count": result.get("successCount", 0),
                        "failure_count": result.get("failureCount", 0),
                        "results": result.get("results", [])
                    }
                    
        except Exception as e:
            logger.error(f"Error sending multicast notification: {str(e)}")
            raise
            
    async def send_topic_message(
        self,
        topic: str,
        title: str,
        body: str,
        data: Optional[Dict[str, str]] = None,
        image: Optional[str] = None
    ) -> Dict[str, Any]:
        """Send push notification to a topic"""
        if not this.settings["notifications_enabled"]:
            raise ValueError("Push notifications are disabled")
            
        try:
            message = {
                "message": {
                    "topic": topic,
                    "notification": {
                        "title": title,
                        "body": body
                    }
                }
            }
            
            if data:
                message["message"]["data"] = data
                
            if image:
                message["message"]["notification"]["image"] = image
                
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{this.base_url}/projects/{this.project_id}/messages:send",
                    headers={
                        "Authorization": f"Bearer {await this._get_access_token()}",
                        "Content-Type": "application/json"
                    },
                    json=message
                ) as response:
                    result = await response.json()
                    if response.status != 200:
                        raise ValueError(f"Failed to send topic message: {result.get('error', {}).get('message')}")
                        
                    return {
                        "message_id": result["name"],
                        "status": "success"
                    }
                    
        except Exception as e:
            logger.error(f"Error sending topic message: {str(e)}")
            raise
            
    async def subscribe_to_topic(
        self,
        tokens: List[str],
        topic: str
    ) -> Dict[str, Any]:
        """Subscribe devices to a topic"""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{this.base_url}/projects/{this.project_id}/messages:send",
                    headers={
                        "Authorization": f"Bearer {await this._get_access_token()}",
                        "Content-Type": "application/json"
                    },
                    json={
                        "to": f"/topics/{topic}",
                        "registration_tokens": tokens
                    }
                ) as response:
                    result = await response.json()
                    if response.status != 200:
                        raise ValueError(f"Failed to subscribe to topic: {result.get('error', {}).get('message')}")
                        
                    return {
                        "success_count": result.get("successCount", 0),
                        "failure_count": result.get("failureCount", 0),
                        "results": result.get("results", [])
                    }
                    
        except Exception as e:
            logger.error(f"Error subscribing to topic: {str(e)}")
            raise
            
    async def unsubscribe_from_topic(
        self,
        tokens: List[str],
        topic: str
    ) -> Dict[str, Any]:
        """Unsubscribe devices from a topic"""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{this.base_url}/projects/{this.project_id}/messages:send",
                    headers={
                        "Authorization": f"Bearer {await this._get_access_token()}",
                        "Content-Type": "application/json"
                    },
                    json={
                        "to": f"/topics/{topic}",
                        "registration_tokens": tokens,
                        "operation": "remove"
                    }
                ) as response:
                    result = await response.json()
                    if response.status != 200:
                        raise ValueError(f"Failed to unsubscribe from topic: {result.get('error', {}).get('message')}")
                        
                    return {
                        "success_count": result.get("successCount", 0),
                        "failure_count": result.get("failureCount", 0),
                        "results": result.get("results", [])
                    }
                    
        except Exception as e:
            logger.error(f"Error unsubscribing from topic: {str(e)}")
            raise
            
    async def _get_access_token(self) -> str:
        """Get Firebase access token"""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    "https://oauth2.googleapis.com/token",
                    json={
                        "grant_type": "urn:ietf:params:oauth:grant-type:jwt-bearer",
                        "assertion": this.settings["private_key"]
                    }
                ) as response:
                    result = await response.json()
                    if response.status != 200:
                        raise ValueError(f"Failed to get access token: {result.get('error_description')}")
                        
                    return result["access_token"]
                    
        except Exception as e:
            logger.error(f"Error getting access token: {str(e)}")
            raise
            
# Create singleton instance
firebase_client = FirebaseClient() 
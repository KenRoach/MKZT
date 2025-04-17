import os
from typing import Dict, Any, List, Optional
from dotenv import load_dotenv
from firebase_admin import messaging, credentials, initialize_app
from src.utils.logger import logger, RequestContext, log_execution_time

# Load environment variables
load_dotenv()

class NotificationHandler:
    def __init__(self):
        cred = credentials.Certificate(os.getenv("FIREBASE_CREDENTIALS_PATH"))
        initialize_app(cred)
        self.logger = logger
    
    @log_execution_time(logger)
    async def send_notification(self, token: str, title: str, body: str, data: Optional[Dict[str, str]] = None) -> Dict[str, Any]:
        """Send a notification to a specific device"""
        try:
            self.logger.info(
                "Sending notification",
                token=token,
                title=title,
                has_data=bool(data)
            )
            
            message = messaging.Message(
                notification=messaging.Notification(
                    title=title,
                    body=body
                ),
                data=data or {},
                token=token
            )
            
            response = messaging.send(message)
            
            self.logger.info(
                "Notification sent successfully",
                message_id=response
            )
            
            return {
                "status": "success",
                "message_id": response,
                "message": "Notification sent successfully"
            }
            
        except Exception as e:
            self.logger.exception(
                "Error sending notification",
                error=str(e),
                token=token
            )
            return {
                "status": "error",
                "message": str(e)
            }
    
    @log_execution_time(logger)
    async def send_multicast(self, tokens: List[str], title: str, body: str, data: Optional[Dict[str, str]] = None) -> Dict[str, Any]:
        """Send a notification to multiple devices"""
        try:
            self.logger.info(
                "Sending multicast notification",
                token_count=len(tokens),
                title=title,
                has_data=bool(data)
            )
            
            message = messaging.MulticastMessage(
                notification=messaging.Notification(
                    title=title,
                    body=body
                ),
                data=data or {},
                tokens=tokens
            )
            
            response = messaging.send_multicast(message)
            
            self.logger.info(
                "Multicast notification sent successfully",
                success_count=response.success_count,
                failure_count=response.failure_count
            )
            
            return {
                "status": "success",
                "success_count": response.success_count,
                "failure_count": response.failure_count,
                "message": "Multicast notification sent successfully"
            }
            
        except Exception as e:
            self.logger.exception(
                "Error sending multicast notification",
                error=str(e),
                token_count=len(tokens)
            )
            return {
                "status": "error",
                "message": str(e)
            }
    
    @log_execution_time(logger)
    async def send_topic_message(self, topic: str, title: str, body: str, data: Optional[Dict[str, str]] = None) -> Dict[str, Any]:
        """Send a notification to a topic"""
        try:
            self.logger.info(
                "Sending topic message",
                topic=topic,
                title=title,
                has_data=bool(data)
            )
            
            message = messaging.Message(
                notification=messaging.Notification(
                    title=title,
                    body=body
                ),
                data=data or {},
                topic=topic
            )
            
            response = messaging.send(message)
            
            self.logger.info(
                "Topic message sent successfully",
                topic=topic,
                message_id=response
            )
            
            return {
                "status": "success",
                "message_id": response,
                "message": "Topic message sent successfully"
            }
            
        except Exception as e:
            self.logger.exception(
                "Error sending topic message",
                error=str(e),
                topic=topic
            )
            return {
                "status": "error",
                "message": str(e)
            }
    
    @log_execution_time(logger)
    async def subscribe_to_topic(self, tokens: List[str], topic: str) -> Dict[str, Any]:
        """Subscribe devices to a topic"""
        try:
            self.logger.info(
                "Subscribing devices to topic",
                token_count=len(tokens),
                topic=topic
            )
            
            response = messaging.subscribe_to_topic(tokens, topic)
            
            self.logger.info(
                "Devices subscribed successfully",
                topic=topic,
                success_count=response.success_count,
                failure_count=response.failure_count
            )
            
            return {
                "status": "success",
                "success_count": response.success_count,
                "failure_count": response.failure_count,
                "message": "Devices subscribed successfully"
            }
            
        except Exception as e:
            self.logger.exception(
                "Error subscribing to topic",
                error=str(e),
                topic=topic,
                token_count=len(tokens)
            )
            return {
                "status": "error",
                "message": str(e)
            }
    
    @log_execution_time(logger)
    async def unsubscribe_from_topic(self, tokens: List[str], topic: str) -> Dict[str, Any]:
        """Unsubscribe devices from a topic"""
        try:
            self.logger.info(
                "Unsubscribing devices from topic",
                token_count=len(tokens),
                topic=topic
            )
            
            response = messaging.unsubscribe_from_topic(tokens, topic)
            
            self.logger.info(
                "Devices unsubscribed successfully",
                topic=topic,
                success_count=response.success_count,
                failure_count=response.failure_count
            )
            
            return {
                "status": "success",
                "success_count": response.success_count,
                "failure_count": response.failure_count,
                "message": "Devices unsubscribed successfully"
            }
            
        except Exception as e:
            self.logger.exception(
                "Error unsubscribing from topic",
                error=str(e),
                topic=topic,
                token_count=len(tokens)
            )
            return {
                "status": "error",
                "message": str(e)
            } 
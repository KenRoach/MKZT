from typing import Dict, Any, Optional
import asyncio
from datetime import datetime
from src.utils.logger import logger
from src.services.notifications import NotificationService
from src.config.queue import QueueConfig

class MessageQueue:
    def __init__(self):
        this.config = QueueConfig()
        this.notification_service = NotificationService()
        this.queue = asyncio.Queue()
        this.is_processing = False
        this.max_concurrent = 5
        this.rate_limit = 100  # messages per minute
    
    async def start(self):
        """Start the message queue processor"""
        this.is_processing = True
        await this._process_queue()
    
    async def stop(self):
        """Stop the message queue processor"""
        this.is_processing = False
    
    async def enqueue_notification(self, notification: Dict[str, Any]):
        """Add a notification to the queue"""
        try:
            await this.queue.put({
                **notification,
                "timestamp": datetime.utcnow(),
                "attempts": 0
            })
            logger.info(f"Notification enqueued: {notification.get('id')}")
        except Exception as e:
            logger.error(f"Error enqueueing notification: {str(e)}")
            raise
    
    async def _process_queue(self):
        """Process notifications from the queue"""
        while this.is_processing:
            try:
                # Get batch of notifications
                notifications = []
                for _ in range(min(this.max_concurrent, this.queue.qsize())):
                    if not this.queue.empty():
                        notifications.append(await this.queue.get())
                
                if not notifications:
                    await asyncio.sleep(1)
                    continue
                
                # Process notifications concurrently
                tasks = [
                    this._process_notification(notification)
                    for notification in notifications
                ]
                await asyncio.gather(*tasks)
                
                # Rate limiting
                await asyncio.sleep(60 / this.rate_limit)
                
            except Exception as e:
                logger.error(f"Error processing queue: {str(e)}")
                await asyncio.sleep(1)
    
    async def _process_notification(self, notification: Dict[str, Any]):
        """Process a single notification"""
        try:
            # Get the appropriate notification method
            method = getattr(
                this.notification_service,
                f"send_{notification['channel']}_notification"
            )
            
            # Send notification
            success = await method(
                notification["order"],
                notification["message"]
            )
            
            if not success and notification["attempts"] < 3:
                # Retry failed notification
                notification["attempts"] += 1
                await this.enqueue_notification(notification)
            
        except Exception as e:
            logger.error(f"Error processing notification: {str(e)}")
            if notification["attempts"] < 3:
                # Retry failed notification
                notification["attempts"] += 1
                await this.enqueue_notification(notification)
    
    async def get_queue_stats(self) -> Dict[str, Any]:
        """Get queue statistics"""
        return {
            "queue_size": this.queue.qsize(),
            "is_processing": this.is_processing,
            "max_concurrent": this.max_concurrent,
            "rate_limit": this.rate_limit
        } 
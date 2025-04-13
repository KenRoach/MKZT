from typing import Dict, Any, Optional, List
from datetime import datetime
from src.utils.logger import logger
from src.config.database import DatabaseConfig

class DatabaseService:
    def __init__(self):
        this.config = DatabaseConfig()
        this.connection = None
    
    async def connect(self):
        """Establish database connection"""
        try:
            # Implement actual database connection logic here
            this.connection = await this.config.get_connection()
            logger.info("Database connection established")
        except Exception as e:
            logger.error(f"Database connection error: {str(e)}")
            raise
    
    async def get_order_details(self, order_id: str) -> Optional[Dict[str, Any]]:
        """Get order details from database"""
        try:
            query = """
                SELECT o.*, c.preferences, c.language
                FROM orders o
                JOIN customers c ON o.customer_id = c.id
                WHERE o.order_id = $1
            """
            result = await this.connection.fetchrow(query, order_id)
            return dict(result) if result else None
        except Exception as e:
            logger.error(f"Error fetching order details: {str(e)}")
            raise
    
    async def get_customer_preferences(self, customer_id: str) -> Dict[str, Any]:
        """Get customer notification preferences"""
        try:
            query = """
                SELECT notification_channels, language
                FROM customer_preferences
                WHERE customer_id = $1
            """
            result = await this.connection.fetchrow(query, customer_id)
            if result:
                return {
                    "channels": result["notification_channels"],
                    "language": result["language"]
                }
            return {
                "channels": ["whatsapp", "email"],
                "language": "en"
            }
        except Exception as e:
            logger.error(f"Error fetching customer preferences: {str(e)}")
            raise
    
    async def update_notification_status(self, notification_id: str, status: str, error: Optional[str] = None):
        """Update notification delivery status"""
        try:
            query = """
                UPDATE notifications
                SET status = $1, error = $2, updated_at = $3
                WHERE id = $4
            """
            await this.connection.execute(query, status, error, datetime.utcnow(), notification_id)
        except Exception as e:
            logger.error(f"Error updating notification status: {str(e)}")
            raise
    
    async def log_notification(self, notification_data: Dict[str, Any]):
        """Log notification attempt"""
        try:
            query = """
                INSERT INTO notifications (
                    id, order_id, customer_id, channel, message, status, created_at
                ) VALUES ($1, $2, $3, $4, $5, $6, $7)
            """
            await this.connection.execute(
                query,
                notification_data["id"],
                notification_data["order_id"],
                notification_data["customer_id"],
                notification_data["channel"],
                notification_data["message"],
                "pending",
                datetime.utcnow()
            )
        except Exception as e:
            logger.error(f"Error logging notification: {str(e)}")
            raise 
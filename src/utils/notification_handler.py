import os
import smtplib
import logging
import json
import aiohttp
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Dict, Any, List, Optional, Set
from datetime import datetime, timedelta
from twilio.rest import Client
from src.utils.logger import get_logger

# Get logger
logger = get_logger(__name__)

class NotificationHandler:
    """Handler for sending notifications about important events"""
    
    def __init__(self):
        """Initialize the notification handler"""
        self.slack_webhook_url = os.getenv("SLACK_WEBHOOK_URL")
        self.smtp_server = os.getenv("SMTP_SERVER", "smtp.gmail.com")
        self.smtp_port = int(os.getenv("SMTP_PORT", "587"))
        self.smtp_username = os.getenv("SMTP_USERNAME")
        self.smtp_password = os.getenv("SMTP_PASSWORD")
        self.from_email = os.getenv("FROM_EMAIL", "notifications@example.com")
        self.admin_emails = os.getenv("ADMIN_EMAILS", "").split(",")
        self.environment = os.getenv("ENVIRONMENT", "development")
        
        # Twilio configuration
        self.twilio_account_sid = os.getenv("TWILIO_ACCOUNT_SID")
        self.twilio_auth_token = os.getenv("TWILIO_AUTH_TOKEN")
        self.twilio_from_number = os.getenv("TWILIO_FROM_NUMBER")
        self.admin_phone_numbers = os.getenv("ADMIN_PHONE_NUMBERS", "").split(",")
        
        # Initialize Twilio client if credentials are available
        self.twilio_client = None
        if self.twilio_account_sid and self.twilio_auth_token:
            self.twilio_client = Client(self.twilio_account_sid, self.twilio_auth_token)
        
        self.notification_thresholds = {
            "error_rate": float(os.getenv("ERROR_RATE_THRESHOLD", "0.1")),  # 10% error rate
            "response_time": float(os.getenv("RESPONSE_TIME_THRESHOLD", "2.0")),  # 2 seconds
            "consecutive_errors": int(os.getenv("CONSECUTIVE_ERRORS_THRESHOLD", "5"))  # 5 consecutive errors
        }
        self.error_count = 0
        self.consecutive_errors = 0
        self.last_notification_time = {}
        
        # Rate limiting configuration
        self.sms_rate_limit = int(os.getenv("SMS_RATE_LIMIT", "10"))  # Max SMS per hour
        self.sms_cooldown_minutes = int(os.getenv("SMS_COOLDOWN_MINUTES", "30"))  # Cooldown between SMS
        self.sms_notification_history = {}  # Track SMS notifications by type
        self.last_sms_time = {}  # Track last SMS time by recipient
        
        # Notification preferences
        self.notification_preferences = self._load_notification_preferences()
    
    def _load_notification_preferences(self) -> Dict[str, Dict[str, Set[str]]]:
        """Load notification preferences from environment or use defaults"""
        preferences = {}
        
        # Default preferences - all channels enabled
        default_channels = {"slack", "email", "sms"}
        
        # Load admin preferences from environment
        for email in self.admin_emails:
            if not email:
                continue
                
            # Get preferences from environment variables
            pref_key = f"ADMIN_PREFS_{email.replace('@', '_').replace('.', '_').upper()}"
            channels_str = os.getenv(pref_key, "")
            
            if channels_str:
                # Parse channels from environment
                channels = set(channels_str.split(","))
                # Validate channels
                valid_channels = {"slack", "email", "sms"}
                channels = channels.intersection(valid_channels)
                preferences[email] = channels
            else:
                # Use default preferences
                preferences[email] = default_channels.copy()
        
        # Load phone number preferences
        for phone in self.admin_phone_numbers:
            if not phone:
                continue
                
            # Get preferences from environment variables
            pref_key = f"ADMIN_PREFS_{phone.replace('+', '').replace('-', '_')}"
            channels_str = os.getenv(pref_key, "")
            
            if channels_str:
                # Parse channels from environment
                channels = set(channels_str.split(","))
                # Validate channels
                valid_channels = {"slack", "email", "sms"}
                channels = channels.intersection(valid_channels)
                preferences[phone] = channels
            else:
                # Use default preferences
                preferences[phone] = default_channels.copy()
        
        return preferences
    
    def get_preferred_channels(self, recipient: str) -> Set[str]:
        """Get preferred notification channels for a recipient"""
        return self.notification_preferences.get(recipient, {"slack", "email", "sms"})
    
    def update_preferences(self, recipient: str, channels: Set[str]) -> bool:
        """Update notification preferences for a recipient"""
        # Validate channels
        valid_channels = {"slack", "email", "sms"}
        channels = channels.intersection(valid_channels)
        
        if not channels:
            logger.warning(f"Cannot set empty channels for {recipient}")
            return False
        
        self.notification_preferences[recipient] = channels
        logger.info(f"Updated notification preferences for {recipient}: {channels}")
        return True

    def _can_send_sms(self, notification_type: str, recipient: str) -> bool:
        """Check if SMS can be sent based on rate limiting rules"""
        current_time = datetime.now()
        
        # Check cooldown period for this recipient
        if recipient in self.last_sms_time:
            time_since_last = current_time - self.last_sms_time[recipient]
            if time_since_last < timedelta(minutes=self.sms_cooldown_minutes):
                logger.info(f"SMS cooldown active for {recipient}, {self.sms_cooldown_minutes - time_since_last.seconds // 60} minutes remaining")
                return False
        
        # Check rate limit for this notification type
        if notification_type in self.sms_notification_history:
            # Clean up old entries
            self.sms_notification_history[notification_type] = [
                t for t in self.sms_notification_history[notification_type]
                if current_time - t < timedelta(hours=1)
            ]
            
            # Check if rate limit is exceeded
            if len(self.sms_notification_history[notification_type]) >= self.sms_rate_limit:
                logger.info(f"SMS rate limit exceeded for {notification_type}")
                return False
        
        return True

    def _record_sms_sent(self, notification_type: str, recipient: str):
        """Record that an SMS was sent"""
        current_time = datetime.now()
        
        # Record time for this recipient
        self.last_sms_time[recipient] = current_time
        
        # Record notification type
        if notification_type not in self.sms_notification_history:
            self.sms_notification_history[notification_type] = []
        self.sms_notification_history[notification_type].append(current_time)

    async def send_email_notification(
        self, 
        subject: str, 
        message: str, 
        recipients: Optional[List[str]] = None
    ) -> bool:
        """Send an email notification"""
        if not self.smtp_username or not self.smtp_password:
            logger.warning("SMTP credentials not configured")
            return False

        try:
            recipients = recipients or self.admin_emails
            if not recipients:
                logger.warning("No recipients specified for email notification")
                return False
            
            # Filter recipients based on preferences
            filtered_recipients = [
                r for r in recipients 
                if "email" in self.get_preferred_channels(r)
            ]
            
            if not filtered_recipients:
                logger.info("No recipients with email preferences")
                return False
            
            msg = MIMEMultipart()
            msg["From"] = self.from_email
            msg["To"] = ", ".join(filtered_recipients)
            msg["Subject"] = f"[{self.environment.upper()}] {subject}"
            
            msg.attach(MIMEText(message, "plain"))
            
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls()
                server.login(self.smtp_username, self.smtp_password)
                server.send_message(msg)
            
            logger.info(f"Email notification sent to {msg['To']}")
            return True
        
        except Exception as e:
            logger.error(f"Failed to send email notification: {str(e)}")
            return False
    
    async def send_slack_notification(self, message: str, level: str = "info") -> bool:
        """Send a notification to Slack"""
        if not self.slack_webhook_url:
            logger.warning("Slack webhook URL not configured")
            return False

        try:
            payload = {
                "text": f"[{level.upper()}] {message}",
                "username": "WhatsApp Bot Monitor",
                "icon_emoji": ":robot_face:"
            }

            async with aiohttp.ClientSession() as session:
                async with session.post(self.slack_webhook_url, json=payload) as response:
                    if response.status == 200:
                        logger.info(f"Slack notification sent: {message}")
                        return True
                    else:
                        logger.error(f"Failed to send Slack notification: {response.status}")
                        return False

        except Exception as e:
            logger.error(f"Error sending Slack notification: {str(e)}")
            return False
    
    async def send_sms_notification(
        self, 
        message: str, 
        recipients: Optional[List[str]] = None,
        notification_type: str = "general",
        priority: str = "normal",
        include_link: bool = False,
        link_url: Optional[str] = None
    ) -> bool:
        """Send an SMS notification using Twilio with rate limiting and formatting options"""
        if not self.twilio_client or not self.twilio_from_number:
            logger.warning("Twilio credentials not configured")
            return False

        try:
            recipients = recipients or self.admin_phone_numbers
            if not recipients:
                logger.warning("No phone numbers configured for SMS notifications")
                return False
            
            # Filter recipients based on preferences
            filtered_recipients = [
                r for r in recipients 
                if "sms" in self.get_preferred_channels(r)
            ]
            
            if not filtered_recipients:
                logger.info("No recipients with SMS preferences")
                return False

            # Format message based on priority
            formatted_message = self._format_sms_message(
                message, 
                notification_type, 
                priority,
                include_link,
                link_url
            )

            success = False
            for phone_number in filtered_recipients:
                # Check rate limiting
                if not self._can_send_sms(notification_type, phone_number):
                    logger.info(f"Skipping SMS to {phone_number} due to rate limiting")
                    continue
                
                # Send the SMS
                self.twilio_client.messages.create(
                    body=formatted_message,
                    from_=self.twilio_from_number,
                    to=phone_number
                )
                
                # Record that SMS was sent
                self._record_sms_sent(notification_type, phone_number)
                logger.info(f"SMS notification sent to {phone_number}")
                success = True
            
            return success

        except Exception as e:
            logger.error(f"Failed to send SMS notification: {str(e)}")
            return False
    
    def _format_sms_message(
        self, 
        message: str, 
        notification_type: str, 
        priority: str = "normal",
        include_link: bool = False,
        link_url: Optional[str] = None
    ) -> str:
        """Format SMS message with appropriate styling and information density"""
        # Start with environment prefix
        formatted = f"[{self.environment.upper()}] "
        
        # Add priority indicator
        if priority == "high":
            formatted += "🚨 "
        elif priority == "medium":
            formatted += "⚠️ "
        elif priority == "low":
            formatted += "ℹ️ "
        
        # Add notification type indicator
        if notification_type == "health_alert":
            formatted += "HEALTH: "
        elif notification_type == "error_alert":
            formatted += "ERROR: "
        elif notification_type == "metrics_alert":
            formatted += "METRICS: "
        
        # Add the main message
        formatted += message
        
        # Add link if requested
        if include_link and link_url:
            formatted += f"\n\nView details: {link_url}"
        
        # Add timestamp
        formatted += f"\n\nTime: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        
        return formatted

    async def notify_health_status(self, health_status: Dict[str, Any]) -> None:
        """Send notification about health status"""
        if health_status["status"] == "unhealthy":
            message = "🚨 *Unhealthy Status Detected*\n\n"
            for check, details in health_status["checks"].items():
                if details["status"] == "unhealthy":
                    message += f"*{check}*: {details['value']} (threshold: {details['threshold']})\n"
            
            message += f"\nEnvironment: {self.environment}"
            
            # Send to all channels based on preferences
            await self.send_slack_notification(message, "error")
            await self.send_email_notification(
                "Unhealthy Status Detected",
                message.replace("*", "").replace("🚨", "⚠️"),
                self.admin_emails
            )
            # Send SMS only for high severity issues
            if any(check["severity"] == "high" for check in health_status["checks"].values()):
                # Create a concise SMS message
                sms_message = "Unhealthy: "
                for check, details in health_status["checks"].items():
                    if details["status"] == "unhealthy" and details["severity"] == "high":
                        sms_message += f"{check}: {details['value']}, "
                
                await self.send_sms_notification(
                    sms_message.rstrip(", "),
                    notification_type="health_alert",
                    priority="high",
                    include_link=True,
                    link_url=f"{os.getenv('DASHBOARD_URL', 'http://localhost:8000')}/health"
                )

    async def notify_error(self, error: Exception, context: Dict[str, Any] = None) -> None:
        """Send notification about an error"""
        message = f"❌ *Error Occurred*\n\n"
        message += f"*Error Type*: {type(error).__name__}\n"
        message += f"*Message*: {str(error)}\n"
        
        if context:
            message += "\n*Context*:\n"
            for key, value in context.items():
                message += f"- {key}: {value}\n"
        
        message += f"\nEnvironment: {self.environment}"
        
        # Send to all channels based on preferences
        await self.send_slack_notification(message, "error")
        await self.send_email_notification(
            f"Error: {type(error).__name__}",
            message.replace("*", "").replace("❌", "⚠️"),
            self.admin_emails
        )
        # Send SMS for errors
        await self.send_sms_notification(
            f"Error: {type(error).__name__} - {str(error)}",
            notification_type="error_alert",
            priority="high",
            include_link=True,
            link_url=f"{os.getenv('DASHBOARD_URL', 'http://localhost:8000')}/errors"
        )

    async def notify_metrics(self, metrics: Dict[str, Any]) -> None:
        """Send notification about current metrics"""
        # Only send notifications if there are concerning metrics
        if (metrics["error_rate"] > 0.1 or 
            metrics["consecutive_errors"] > 0 or 
            metrics["system_metrics"]["current_cpu_usage_percent"] > 80):
            
            message = "📊 *Metrics Update*\n\n"
            message += f"*Total Requests*: {metrics['total_requests']}\n"
            message += f"*Error Rate*: {metrics['error_rate']:.2%}\n"
            message += f"*Avg Response Time*: {metrics['avg_response_time']:.2f}s\n"
            message += f"*Uptime*: {metrics['uptime_seconds'] / 3600:.1f}h\n"
            
            if metrics.get('request_types'):
                message += "\n*Request Types*:\n"
                for req_type, count in metrics['request_types'].items():
                    message += f"- {req_type}: {count}\n"
            
            if metrics.get('system_metrics'):
                message += "\n*System Metrics*:\n"
                message += f"- Memory Usage: {metrics['system_metrics']['current_memory_usage_mb']:.1f}MB\n"
                message += f"- CPU Usage: {metrics['system_metrics']['current_cpu_usage_percent']:.1f}%\n"
            
            if metrics['consecutive_errors'] > 0:
                message += f"\n*Consecutive Errors*: {metrics['consecutive_errors']}\n"
            
            message += f"\nEnvironment: {self.environment}"
            
            # Send to all channels based on preferences
            await self.send_slack_notification(message, "info")
            await self.send_email_notification(
                "Metrics Update",
                message.replace("*", "").replace("📊", "📈"),
                self.admin_emails
            )
            
            # Determine priority based on metrics
            priority = "normal"
            if metrics["error_rate"] > 0.2 or metrics["consecutive_errors"] > 5:
                priority = "high"
            elif metrics["error_rate"] > 0.1 or metrics["system_metrics"]["current_cpu_usage_percent"] > 80:
                priority = "medium"
                
            # Send SMS for concerning metrics
            await self.send_sms_notification(
                f"Metrics: Error {metrics['error_rate']:.1%}, CPU {metrics['system_metrics']['current_cpu_usage_percent']:.1f}%",
                notification_type="metrics_alert",
                priority=priority,
                include_link=True,
                link_url=f"{os.getenv('DASHBOARD_URL', 'http://localhost:8000')}/metrics"
            )
    
    async def check_metrics(self, metrics: Dict[str, Any]) -> Dict[str, Any]:
        """Check metrics and send notifications if thresholds are exceeded"""
        try:
            notifications = []
            
            # Calculate error rate
            total_requests = 0
            total_errors = 0
            
            for key, data in metrics.get("requests", {}).items():
                total_requests += data.get("count", 0)
            
            for key, data in metrics.get("errors", {}).items():
                total_errors += data.get("count", 0)
            
            error_rate = total_errors / total_requests if total_requests > 0 else 0
            
            # Check error rate threshold
            if error_rate > self.notification_thresholds["error_rate"]:
                subject = "High Error Rate Alert"
                message = (
                    f"The error rate has exceeded the threshold of "
                    f"{self.notification_thresholds['error_rate'] * 100}%.\n"
                    f"Current error rate: {error_rate * 100:.2f}%\n"
                    f"Total requests: {total_requests}\n"
                    f"Total errors: {total_errors}"
                )
                
                email_result = await self.send_email_notification(subject, message)
                slack_result = await self.send_slack_notification(
                    f"*High Error Rate Alert*\n"
                    f"Error rate: {error_rate * 100:.2f}% (threshold: {self.notification_thresholds['error_rate'] * 100}%)\n"
                    f"Total requests: {total_requests}\n"
                    f"Total errors: {total_errors}"
                )
                
                notifications.append({
                    "type": "high_error_rate",
                    "email": email_result,
                    "slack": slack_result
                })
            
            # Check response time threshold
            for key, data in metrics.get("processing_times", {}).items():
                avg_time = data.get("avg_time", 0)
                
                if avg_time > self.notification_thresholds["response_time"]:
                    subject = "High Response Time Alert"
                    message = (
                        f"The average response time for {key} has exceeded the threshold of "
                        f"{self.notification_thresholds['response_time']} seconds.\n"
                        f"Current average time: {avg_time:.2f} seconds\n"
                        f"Total requests: {data.get('count', 0)}"
                    )
                    
                    email_result = await self.send_email_notification(subject, message)
                    slack_result = await self.send_slack_notification(
                        f"*High Response Time Alert*\n"
                        f"Operation: {key}\n"
                        f"Avg time: {avg_time:.2f}s (threshold: {self.notification_thresholds['response_time']}s)\n"
                        f"Total requests: {data.get('count', 0)}"
                    )
                    
                    notifications.append({
                        "type": "high_response_time",
                        "operation": key,
                        "email": email_result,
                        "slack": slack_result
                    })
            
            # Check consecutive errors
            if self.consecutive_errors >= self.notification_thresholds["consecutive_errors"]:
                subject = "Consecutive Errors Alert"
                message = (
                    f"The system has encountered {self.consecutive_errors} consecutive errors.\n"
                    f"This may indicate a systemic issue that requires attention."
                )
                
                email_result = await self.send_email_notification(subject, message)
                slack_result = await self.send_slack_notification(
                    f"*Consecutive Errors Alert*\n"
                    f"The system has encountered {self.consecutive_errors} consecutive errors.\n"
                    f"This may indicate a systemic issue that requires attention."
                )
                
                notifications.append({
                    "type": "consecutive_errors",
                    "email": email_result,
                    "slack": slack_result
                })
                
                # Reset consecutive errors count after notification
                self.consecutive_errors = 0
            
            return {
                "status": "success",
                "message": f"Checked metrics and sent {len(notifications)} notifications",
                "notifications": notifications
            }
        
        except Exception as e:
            error_msg = f"Error checking metrics: {str(e)}"
            logger.error(error_msg)
            return {"status": "error", "message": error_msg}
    
    def reset_error_counts(self):
        """Reset error counts"""
        self.error_count = 0
        self.consecutive_errors = 0
        logger.info("Error counts reset") 
import aiohttp
import smtplib
from email.mime.text import MIMEText
from datetime import datetime, timedelta
from typing import List, Dict
import json
import logging
from src.config.monitoring import monitoring_settings
from src.utils.logger import logger

class SecurityAlertManager:
    def __init__(self):
        self.alert_history: Dict[str, List[datetime]] = {}

    async def send_slack_alert(self, message: str, severity: str = "warning"):
        """Send alert to Slack"""
        if not monitoring_settings.SLACK_WEBHOOK_URL:
            return

        try:
            payload = {
                "text": f"*Security Alert* - {severity.upper()}\n{message}",
                "attachments": [{
                    "color": "danger" if severity == "critical" else "warning",
                    "fields": [{
                        "title": "Timestamp",
                        "value": datetime.utcnow().isoformat(),
                        "short": True
                    }]
                }]
            }

            async with aiohttp.ClientSession() as session:
                async with session.post(
                    monitoring_settings.SLACK_WEBHOOK_URL,
                    json=payload
                ) as response:
                    if response.status != 200:
                        logger.error(f"Failed to send Slack alert: {await response.text()}")

        except Exception as e:
            logger.error(f"Error sending Slack alert: {str(e)}")

    async def send_email_alert(self, subject: str, message: str):
        """Send email alert"""
        if not monitoring_settings.EMAIL_ALERTS_ENABLED:
            return

        try:
            msg = MIMEText(message)
            msg['Subject'] = f"Security Alert: {subject}"
            msg['From'] = "security-alerts@yourdomain.com"
            msg['To'] = ", ".join(monitoring_settings.ALERT_EMAIL_ADDRESSES)

            # Configure your SMTP settings here
            with smtplib.SMTP('smtp.yourdomain.com', 587) as server:
                server.starttls()
                server.login('username', 'password')
                server.send_message(msg)

        except Exception as e:
            logger.error(f"Error sending email alert: {str(e)}")

    async def alert(self, alert_type: str, message: str, severity: str = "warning"):
        """Send alert through all configured channels"""
        # Check alert frequency
        if not self._should_send_alert(alert_type):
            return

        # Log the alert
        logger.warning(f"Security Alert ({severity}): {message}")

        # Send to all configured channels
        await self.send_slack_alert(message, severity)
        
        if severity == "critical":
            await self.send_email_alert(alert_type, message)

    def _should_send_alert(self, alert_type: str) -> bool:
        """Prevent alert fatigue by limiting frequency"""
        now = datetime.utcnow()
        
        if alert_type not in self.alert_history:
            self.alert_history[alert_type] = []
            
        # Clean old alerts
        self.alert_history[alert_type] = [
            t for t in self.alert_history[alert_type]
            if t > now - timedelta(minutes=15)
        ]
        
        # Check frequency
        if len(self.alert_history[alert_type]) >= 3:
            return False
            
        self.alert_history[alert_type].append(now)
        return True

alert_manager = SecurityAlertManager() 
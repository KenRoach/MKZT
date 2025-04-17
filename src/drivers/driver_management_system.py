from typing import Dict, Any, List
from datetime import datetime, timedelta
from decimal import Decimal
from enum import Enum
import json

class DriverStatus(Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    ON_DELIVERY = "on_delivery"
    BREAK = "break"

class DriverManagementSystem:
    def __init__(self):
        self.active_sessions = {}
        self.load_templates()
        
    def load_templates(self):
        """Load driver dashboard templates"""
        with open('src/templates/driver_templates.json', 'r', encoding='utf-8') as f:
            self.templates = json.load(f)

    async def authenticate_driver(self, credentials: str) -> Dict[str, Any]:
        """Authenticate driver and create session"""
        try:
            # In real implementation, verify against database
            driver_data = await self._verify_driver_credentials(credentials)
            
            if driver_data:
                session = {
                    "driver_id": driver_data["id"],
                    "name": driver_data["name"],
                    "status": DriverStatus.ACTIVE,
                    "last_activity": datetime.now(),
                    "current_view": "main_menu"
                }
                self.active_sessions[driver_data["id"]] = session
                
                return await self._generate_welcome_message(session)
            else:
                return {
                    "status": "error",
                    "message": "Credenciales inválidas. Por favor intenta nuevamente."
                }
        except Exception as e:
            logger.error(f"Driver authentication error: {str(e)}")
            return {"status": "error", "message": str(e)}

    async def get_daily_deliveries(self, driver_id: str) -> Dict[str, Any]:
        """Get driver's daily delivery summary"""
        try:
            deliveries = await self._fetch_daily_deliveries(driver_id)
            
            summary = {
                "total_deliveries": len(deliveries),
                "active_hours": sum(d["duration"] for d in deliveries) / 3600,
                "average_time": sum(d["duration"] for d in deliveries) / 
                              len(deliveries) / 60 if deliveries else 0,
                "zones_covered": list(set(d["zone"] for d in deliveries)),
                "deliveries": deliveries
            }
            
            return {
                "status": "success",
                "summary": summary,
                "message": self._format_delivery_summary(summary)
            }
        except Exception as e:
            logger.error(f"Error fetching deliveries: {str(e)}")
            return {"status": "error", "message": str(e)}

    async def get_earnings_summary(self, driver_id: str) -> Dict[str, Any]:
        """Get driver's earnings summary"""
        try:
            earnings = await self._fetch_weekly_earnings(driver_id)
            
            summary = {
                "total_earnings": earnings["delivery_fees"] + earnings["tips"],
                "tips": earnings["tips"],
                "average_per_delivery": (earnings["delivery_fees"] + 
                                       earnings["tips"]) / earnings["total_deliveries"]
                                       if earnings["total_deliveries"] > 0 else 0,
                "total_deliveries": earnings["total_deliveries"]
            }
            
            return {
                "status": "success",
                "summary": summary,
                "message": self._format_earnings_summary(summary)
            }
        except Exception as e:
            logger.error(f"Error fetching earnings: {str(e)}")
            return {"status": "error", "message": str(e)}

    async def get_mileage_summary(self, driver_id: str) -> Dict[str, Any]:
        """Get driver's mileage summary"""
        try:
            mileage = await self._fetch_weekly_mileage(driver_id)
            
            summary = {
                "total_km": mileage["total_km"],
                "daily_average": mileage["total_km"] / 
                                len(mileage["daily_records"]),
                "maintenance_alert": mileage.get("maintenance_alert", False)
            }
            
            return {
                "status": "success",
                "summary": summary,
                "message": self._format_mileage_summary(summary)
            }
        except Exception as e:
            logger.error(f"Error fetching mileage: {str(e)}")
            return {"status": "error", "message": str(e)}

    def _format_delivery_summary(self, summary: Dict[str, Any]) -> str:
        """Format delivery summary message"""
        template = self.templates["es"]["daily_deliveries"]
        
        return template["summary"].format(
            total=summary["total_deliveries"],
            hours=f"{summary['active_hours']:.1f}",
            avg_time=f"{summary['average_time']:.0f}",
            zones=", ".join(summary["zones_covered"])
        )

    def _format_earnings_summary(self, summary: Dict[str, Any]) -> str:
        """Format earnings summary message"""
        template = self.templates["es"]["earnings"]
        
        return template["summary"].format(
            total=f"{summary['total_earnings']:.2f}",
            tips=f"{summary['tips']:.2f}",
            average=f"{summary['average_per_delivery']:.2f}",
            deliveries=summary["total_deliveries"]
        )

    def _format_mileage_summary(self, summary: Dict[str, Any]) -> str:
        """Format mileage summary message"""
        template = self.templates["es"]["mileage"]
        
        message = template["summary"].format(
            total=f"{summary['total_km']:.1f}",
            daily_avg=f"{summary['daily_average']:.1f}",
            maintenance_alert=summary['maintenance_alert']
        )
        
        return message 
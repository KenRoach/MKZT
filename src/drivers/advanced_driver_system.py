from typing import Dict, Any, List
from datetime import datetime, timedelta
from enum import Enum
import asyncio
from decimal import Decimal

class DriverStatus(Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    ON_DELIVERY = "on_delivery"
    BREAK = "break"
    NEARBY_ONLY = "nearby_only"
    HIGH_DEMAND = "high_demand"

class DeliveryIssue(Enum):
    CUSTOMER_ABSENT = "customer_absent"
    WRONG_ADDRESS = "wrong_address"
    RESTAURANT_DELAY = "restaurant_delay"
    TRAFFIC_DELAY = "traffic_delay"
    APP_ISSUE = "app_issue"
    OTHER = "other"

class AdvancedDriverSystem:
    def __init__(self):
        self.load_templates()
        self.active_drivers = {}
        self.delivery_logs = {}
        self.earnings_data = {}
        self.vehicle_data = {}
        self.performance_metrics = {}
        
    async def process_voice_command(self, 
                                  driver_id: str, 
                                  command: str) -> Dict[str, Any]:
        """Process voice commands from driver"""
        try:
            command = command.lower()
            
            if "gané" in command or "ganancia" in command:
                return await self.get_earnings_summary(driver_id)
            elif "pedidos" in command or "entregas" in command:
                return await self.get_assigned_deliveries(driver_id)
            elif "documentos" in command:
                return await self.get_document_status(driver_id)
            elif "problema" in command or "reportar" in command:
                return await self.initiate_issue_report(driver_id)
            elif "libre" in command or "disponible" in command:
                return await self.update_driver_status(driver_id, DriverStatus.ACTIVE)
            elif "kilómetros" in command or "kilometraje" in command:
                return await self.get_mileage_summary(driver_id)
            elif "ayuda" in command or "soporte" in command:
                return await self.request_support(driver_id)
                
            return {
                "status": "error",
                "message": "Comando no reconocido. Por favor intenta de nuevo."
            }
        except Exception as e:
            logger.error(f"Voice command error: {str(e)}")
            return {"status": "error", "message": str(e)}

    async def get_delivery_management(self, 
                                    driver_id: str, 
                                    filter_type: str = "today") -> Dict[str, Any]:
        """Get comprehensive delivery management data"""
        try:
            return {
                "assigned_deliveries": await self._get_assigned_deliveries(
                    driver_id,
                    filter_type
                ),
                "completed_deliveries": await self._get_completed_deliveries(
                    driver_id,
                    filter_type
                ),
                "pending_pickups": await self._get_pending_pickups(driver_id),
                "average_times": await self._calculate_delivery_times(driver_id),
                "active_issues": await self._get_active_issues(driver_id)
            }
        except Exception as e:
            logger.error(f"Delivery management error: {str(e)}")
            return {"status": "error", "message": str(e)}

    async def get_earnings_control(self, 
                                 driver_id: str, 
                                 period: str = "today") -> Dict[str, Any]:
        """Get comprehensive earnings data"""
        try:
            return {
                "current_earnings": await self._calculate_current_earnings(
                    driver_id,
                    period
                ),
                "tips": await self._calculate_tips(driver_id, period),
                "payment_history": await self._get_payment_history(driver_id),
                "earnings_breakdown": await self._generate_earnings_breakdown(
                    driver_id,
                    period
                )
            }
        except Exception as e:
            logger.error(f"Earnings control error: {str(e)}")
            return {"status": "error", "message": str(e)}

    async def get_vehicle_documentation(self, 
                                      driver_id: str) -> Dict[str, Any]:
        """Get vehicle and documentation status"""
        try:
            return {
                "insurance": await self._get_insurance_status(driver_id),
                "maintenance": await self._get_maintenance_schedule(driver_id),
                "vehicle_info": await self._get_vehicle_info(driver_id),
                "pending_documents": await self._check_pending_documents(driver_id),
                "document_expiry": await self._get_document_expiry_dates(driver_id)
            }
        except Exception as e:
            logger.error(f"Vehicle documentation error: {str(e)}")
            return {"status": "error", "message": str(e)}

    async def get_performance_tracking(self, 
                                     driver_id: str) -> Dict[str, Any]:
        """Get comprehensive performance metrics"""
        try:
            return {
                "mileage": await self._calculate_mileage(driver_id),
                "frequent_routes": await self._analyze_routes(driver_id),
                "reputation": await self._get_reputation_metrics(driver_id),
                "efficiency_alerts": await self._generate_efficiency_alerts(driver_id),
                "performance_trends": await self._analyze_performance_trends(driver_id)
            }
        except Exception as e:
            logger.error(f"Performance tracking error: {str(e)}")
            return {"status": "error", "message": str(e)}

    async def manage_availability(self, 
                                driver_id: str, 
                                action: str,
                                details: Dict[str, Any] = None) -> Dict[str, Any]:
        """Manage driver availability and preferences"""
        try:
            if action == "update_status":
                return await self._update_driver_status(
                    driver_id,
                    details["status"]
                )
            elif action == "request_day_off":
                return await self._request_day_off(
                    driver_id,
                    details["date"]
                )
            elif action == "set_delivery_mode":
                return await self._set_delivery_mode(
                    driver_id,
                    details["mode"]
                )
            elif action == "toggle_high_demand":
                return await self._toggle_high_demand_mode(driver_id)
                
            return {
                "status": "error",
                "message": "Acción no válida"
            }
        except Exception as e:
            logger.error(f"Availability management error: {str(e)}")
            return {"status": "error", "message": str(e)}

    async def get_support_tools(self, 
                              driver_id: str, 
                              tool_type: str) -> Dict[str, Any]:
        """Access support tools and resources"""
        try:
            if tool_type == "report_incident":
                return await self._create_incident_report(driver_id)
            elif tool_type == "request_support":
                return await self._request_operations_support(driver_id)
            elif tool_type == "guidelines":
                return await self._get_delivery_guidelines()
            elif tool_type == "regulations":
                return await self._get_driver_regulations()
            elif tool_type == "update_info":
                return await self._get_profile_update_options(driver_id)
                
            return {
                "status": "error",
                "message": "Herramienta no encontrada"
            }
        except Exception as e:
            logger.error(f"Support tools error: {str(e)}")
            return {"status": "error", "message": str(e)}

    async def _calculate_current_earnings(self, 
                                        driver_id: str, 
                                        period: str) -> Dict[str, Any]:
        """Calculate detailed earnings for the specified period"""
        earnings_data = self.earnings_data.get(driver_id, {})
        
        if period == "today":
            start_date = datetime.now().date()
        elif period == "week":
            start_date = datetime.now().date() - timedelta(days=7)
        elif period == "month":
            start_date = datetime.now().date() - timedelta(days=30)
            
        relevant_earnings = [
            earning for earning in earnings_data.get("earnings", [])
            if datetime.fromisoformat(earning["date"]).date() >= start_date
        ]
        
        return {
            "total": sum(e["amount"] for e in relevant_earnings),
            "tips": sum(e["tips"] for e in relevant_earnings),
            "base_pay": sum(e["base_pay"] for e in relevant_earnings),
            "bonuses": sum(e["bonuses"] for e in relevant_earnings),
            "period_summary": {
                "start_date": start_date.isoformat(),
                "end_date": datetime.now().date().isoformat(),
                "total_deliveries": len(relevant_earnings),
                "average_per_delivery": sum(e["amount"] for e in relevant_earnings) / 
                                     len(relevant_earnings) if relevant_earnings else 0
            }
        }

    async def _analyze_performance_trends(self, 
                                        driver_id: str) -> Dict[str, Any]:
        """Analyze driver performance trends"""
        metrics = self.performance_metrics.get(driver_id, {})
        
        return {
            "delivery_time_trend": self._calculate_trend(
                metrics.get("delivery_times", [])
            ),
            "customer_satisfaction_trend": self._calculate_trend(
                metrics.get("ratings", [])
            ),
            "earnings_trend": self._calculate_trend(
                metrics.get("earnings", [])
            ),
            "efficiency_score": self._calculate_efficiency_score(metrics),
            "areas_for_improvement": self._identify_improvement_areas(metrics)
        }

    async def _get_vehicle_info(self, driver_id: str) -> Dict[str, Any]:
        """Get comprehensive vehicle information"""
        vehicle_data = self.vehicle_data.get(driver_id, {})
        
        return {
            "vehicle": {
                "plate": vehicle_data.get("plate"),
                "model": vehicle_data.get("model"),
                "year": vehicle_data.get("year"),
                "type": vehicle_data.get("type")
            },
            "insurance": {
                "policy_number": vehicle_data.get("insurance", {}).get("policy_number"),
                "expiry_date": vehicle_data.get("insurance", {}).get("expiry_date"),
                "status": vehicle_data.get("insurance", {}).get("status"),
                "coverage_type": vehicle_data.get("insurance", {}).get("coverage_type")
            },
            "maintenance": {
                "last_service": vehicle_data.get("maintenance", {}).get("last_service"),
                "next_service": vehicle_data.get("maintenance", {}).get("next_service"),
                "service_history": vehicle_data.get("maintenance", {}).get("history", [])
            },
            "documents": {
                "license": vehicle_data.get("documents", {}).get("license"),
                "registration": vehicle_data.get("documents", {}).get("registration"),
                "inspection": vehicle_data.get("documents", {}).get("inspection")
            }
        } 
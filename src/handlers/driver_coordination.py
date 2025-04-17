from typing import Dict, Any, List
from datetime import datetime
from enum import Enum
from src.utils.logger import logger

class DriverStatus(Enum):
    AVAILABLE = "available"
    ASSIGNED = "assigned"
    PICKING_UP = "picking_up"
    DELIVERING = "delivering"
    COMPLETED = "completed"

class DriverCoordinationHandler:
    def __init__(self):
        self.active_drivers: Dict[str, Dict[str, Any]] = {}
        self.active_deliveries: Dict[str, Dict[str, Any]] = {}
    
    async def process_driver_message(self, driver_id: str, message: str) -> Dict[str, Any]:
        """Process incoming message from driver"""
        try:
            if "recoger" in message.lower():
                return await self._handle_pickup_confirmation(driver_id, message)
            elif "entregado" in message.lower():
                return await self._handle_delivery_confirmation(driver_id, message)
            
            return {
                "status": "error",
                "message": "No se pudo determinar la acción a realizar"
            }
            
        except Exception as e:
            logger.error(f"Error processing driver message: {str(e)}")
            return {"status": "error", "message": str(e)}
    
    async def assign_driver(self, order_id: str) -> Dict[str, Any]:
        """Assign available driver to order"""
        try:
            # Find available driver (simplified logic)
            available_driver = await self._find_available_driver()
            
            if not available_driver:
                return {
                    "status": "error",
                    "message": "No hay conductores disponibles"
                }
            
            # Update driver status
            self.active_drivers[available_driver["id"]]["status"] = DriverStatus.ASSIGNED
            
            # Create delivery assignment
            self.active_deliveries[order_id] = {
                "driver_id": available_driver["id"],
                "status": DriverStatus.ASSIGNED,
                "assigned_at": datetime.now(),
                "pickup_sequence": await self._calculate_pickup_sequence(order_id)
            }
            
            return {
                "status": "success",
                "driver": available_driver,
                "delivery": self.active_deliveries[order_id]
            }
            
        except Exception as e:
            logger.error(f"Error assigning driver: {str(e)}")
            return {"status": "error", "message": str(e)}
    
    async def get_driver_location(self, driver_id: str) -> Dict[str, Any]:
        """Get current driver location"""
        try:
            # Simplified location tracking
            driver = self.active_drivers.get(driver_id)
            if not driver:
                return {
                    "status": "error",
                    "message": "Conductor no encontrado"
                }
            
            return {
                "status": "success",
                "location": driver["current_location"],
                "route_id": driver["current_route_id"]
            }
            
        except Exception as e:
            logger.error(f"Error getting driver location: {str(e)}")
            return {"status": "error", "message": str(e)} 
from typing import Dict, Any, List
from datetime import datetime, time
import asyncio
from enum import Enum
from decimal import Decimal

class MealType(Enum):
    BREAKFAST = "breakfast"
    LUNCH = "lunch"
    DINNER = "dinner"
    SNACK = "snack"

class NutritionTracker:
    def __init__(self):
        self.load_templates()
        self.food_database = self._load_food_database()
        self.user_logs = {}
        self.reminders = {}
        
    async def process_meal_input(self, 
                               user_id: str, 
                               meal_text: str) -> Dict[str, Any]:
        """Process natural language meal input and calculate calories"""
        try:
            # Parse meal components
            meal_components = await self._parse_meal_components(meal_text)
            
            # Calculate calories
            calorie_breakdown = await self._calculate_calories(meal_components)
            
            return {
                "status": "success",
                "components": meal_components,
                "calories": calorie_breakdown,
                "total_calories": sum(c["calories"] for c in calorie_breakdown),
                "meal_time": datetime.now().strftime("%I:%M %p")
            }
        except Exception as e:
            logger.error(f"Error processing meal input: {str(e)}")
            return {"status": "error", "message": str(e)}

    async def save_meal_log(self, 
                          user_id: str, 
                          meal_data: Dict[str, Any]) -> Dict[str, Any]:
        """Save meal log to user's history"""
        try:
            if user_id not in self.user_logs:
                self.user_logs[user_id] = []
                
            log_entry = {
                "timestamp": datetime.now(),
                "meal_components": meal_data["components"],
                "calories": meal_data["calories"],
                "total_calories": meal_data["total_calories"]
            }
            
            self.user_logs[user_id].append(log_entry)
            
            return {
                "status": "success",
                "message": "Meal logged successfully",
                "daily_total": await self._calculate_daily_total(user_id)
            }
        except Exception as e:
            logger.error(f"Error saving meal log: {str(e)}")
            return {"status": "error", "message": str(e)}

    async def set_meal_reminder(self, 
                              user_id: str, 
                              meal_type: MealType,
                              reminder_time: time) -> Dict[str, Any]:
        """Set meal reminder for user"""
        try:
            if user_id not in self.reminders:
                self.reminders[user_id] = {}
                
            self.reminders[user_id][meal_type] = {
                "time": reminder_time,
                "active": True
            }
            
            return {
                "status": "success",
                "message": f"Reminder set for {meal_type.value} at {reminder_time.strftime('%I:%M %p')}",
                "next_reminder": reminder_time.strftime("%I:%M %p")
            }
        except Exception as e:
            logger.error(f"Error setting reminder: {str(e)}")
            return {"status": "error", "message": str(e)}

    async def _parse_meal_components(self, meal_text: str) -> List[Dict[str, Any]]:
        """Parse natural language meal description into components"""
        # Use NLP to identify food items and quantities
        components = []
        words = meal_text.lower().split()
        
        current_quantity = 1
        current_food = ""
        
        for word in words:
            if word.isdigit():
                current_quantity = int(word)
            elif word in self.food_database:
                components.append({
                    "food": word,
                    "quantity": current_quantity,
                    "unit": self.food_database[word]["unit"]
                })
                current_quantity = 1
                
        return components

    async def _calculate_calories(self, 
                                components: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Calculate calories for each meal component"""
        calorie_breakdown = []
        
        for component in components:
            food_data = self.food_database[component["food"]]
            calories = food_data["calories_per_unit"] * component["quantity"]
            
            calorie_breakdown.append({
                "food": component["food"],
                "quantity": component["quantity"],
                "unit": component["unit"],
                "calories": calories,
                "emoji": food_data["emoji"]
            })
            
        return calorie_breakdown

    async def _calculate_daily_total(self, user_id: str) -> int:
        """Calculate total calories for the current day"""
        today = datetime.now().date()
        daily_logs = [
            log for log in self.user_logs[user_id]
            if log["timestamp"].date() == today
        ]
        
        return sum(log["total_calories"] for log in daily_logs)

    def _load_food_database(self) -> Dict[str, Any]:
        """Load food database with calorie information"""
        return {
            "tostada": {
                "calories_per_unit": 70,
                "unit": "unidad",
                "emoji": "🥖"
            },
            "aguacate": {
                "calories_per_unit": 120,
                "unit": "medio",
                "emoji": "🥑"
            },
            "café con leche": {
                "calories_per_unit": 90,
                "unit": "taza",
                "emoji": "☕"
            }
            # Add more foods...
        } 
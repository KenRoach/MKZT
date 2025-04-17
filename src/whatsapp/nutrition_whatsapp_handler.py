from typing import Dict, Any
from src.nutrition.calorie_tracking_system import NutritionTracker, MealType
from twilio.rest import Client
import os

class NutritionWhatsAppHandler:
    def __init__(self):
        self.nutrition_tracker = NutritionTracker()
        self.twilio_client = Client(
            os.getenv("TWILIO_ACCOUNT_SID"),
            os.getenv("TWILIO_AUTH_TOKEN")
        )
        self.whatsapp_number = os.getenv("TWILIO_WHATSAPP_NUMBER")
        
    async def process_nutrition_message(self, message_data: Dict[str, Any]) -> None:
        """Process nutrition-related WhatsApp messages"""
        try:
            if "credentials" in message_data:
                # Handle login
                response = await self._handle_login(message_data)
            else:
                # Process user input
                response = await self._process_user_input(
                    message_data["user_id"],
                    message_data["text"]
                )
                
            await self._send_message(
                message_data["phone_number"],
                response["message"]
            )
            
        except Exception as e:
            logger.error(f"Error processing nutrition message: {str(e)}")
            await self._send_error_message(message_data["phone_number"])

    async def _process_user_input(self, 
                                user_id: str, 
                                text: str) -> Dict[str, Any]:
        """Process user menu selections and meal inputs"""
        text = text.lower()
        
        if text == "6":
            return self._generate_meal_input_prompt()
        elif "desayuné" in text or "desayune" in text:
            meal_data = await self.nutrition_tracker.process_meal_input(user_id, text)
            return self._format_calorie_calculation(meal_data, MealType.BREAKFAST)
        elif text in ["si", "sí", "guárdalo"]:
            return await self._handle_meal_save(user_id)
        elif "recuérdame" in text:
            return await self._handle_reminder_setting(user_id, text)
        else:
            return {
                "status": "error",
                "message": "Por favor selecciona una opción válida o describe tu comida."
            }

    def _generate_meal_input_prompt(self) -> Dict[str, Any]:
        """Generate meal input prompt message"""
        template = self.templates["es"]["meal_input"]
        
        message = template["prompt"] + "\n\n"
        message += "\n".join(template["examples"])
        
        return {
            "status": "success",
            "message": message
        }

    def _format_calorie_calculation(self, 
                                  meal_data: Dict[str, Any], 
                                  meal_type: MealType) -> Dict[str, Any]:
        """Format calorie calculation message"""
        template = self.templates["es"]["calorie_calculation"]
        
        message = template["header"]
        
        for component in meal_data["calories"]:
            message += template["item_format"].format(
                emoji=component["emoji"],
                quantity=component["quantity"],
                food=component["food"],
                calories=component["calories"]
            ) + "\n"
            
        message += "\n" + template["total"].format(
            total=meal_data["total_calories"]
        ) + "\n\n"
        
        message += template["save_prompt"].format(
            meal_type=meal_type.value
        )
        
        return {
            "status": "success",
            "message": message,
            "meal_data": meal_data
        }

    async def _handle_meal_save(self, user_id: str) -> Dict[str, Any]:
        """Handle meal saving confirmation"""
        save_result = await self.nutrition_tracker.save_meal_log(
            user_id,
            self.current_meal_data[user_id]
        )
        
        template = self.templates["es"]["meal_saved"]
        
        message = template["confirmation"].format(
            meal_type=self.current_meal_type[user_id].value,
            time=self.current_meal_data[user_id]["meal_time"]
        ) + "\n"
        
        message += template["daily_total"].format(
            total=save_result["daily_total"]
        ) + "\n\n"
        
        message += template["next_steps"].format(
            next_meal=self._get_next_meal_type(
                self.current_meal_type[user_id]
            ).value
        )
        
        return {
            "status": "success",
            "message": message
        }

    async def _handle_reminder_setting(self, 
                                     user_id: str, 
                                     text: str) -> Dict[str, Any]:
        """Handle reminder setting request"""
        reminder_time = time(12, 0)  # Default to noon
        meal_type = MealType.LUNCH
        
        reminder_result = await self.nutrition_tracker.set_meal_reminder(
            user_id,
            meal_type,
            reminder_time
        )
        
        template = self.templates["es"]["reminder_set"]
        
        message = template["confirmation"].format(
            time=reminder_result["next_reminder"],
            meal_type=meal_type.value
        ) + "\n\n"
        
        message += template["next_step"] + "\n\n"
        message += template["recipe_prompt"]
        
        return {
            "status": "success",
            "message": message
        }

    def _get_next_meal_type(self, current_meal: MealType) -> MealType:
        """Get next meal type based on current meal"""
        meal_sequence = {
            MealType.BREAKFAST: MealType.LUNCH,
            MealType.LUNCH: MealType.DINNER,
            MealType.DINNER: MealType.BREAKFAST,
            MealType.SNACK: MealType.DINNER
        }
        return meal_sequence.get(current_meal, MealType.LUNCH) 
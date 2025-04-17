from typing import Dict, Any, List
from datetime import datetime
import numpy as np
from src.utils.logger import logger

class RatingSystem:
    def __init__(self):
        self.weights = {
            "food_quality": 0.35,
            "delivery_time": 0.25,
            "driver_service": 0.20,
            "packaging": 0.10,
            "value_for_money": 0.10
        }
    
    async def submit_rating(self, order_id: str, ratings: Dict[str, float],
                          feedback: str = None) -> Dict[str, Any]:
        """Submit comprehensive rating for an order"""
        try:
            # Calculate weighted average
            weighted_rating = sum(
                ratings[key] * self.weights.get(key, 0)
                for key in ratings
            )
            
            # Store rating
            stored_rating = await self._store_rating(
                order_id=order_id,
                ratings=ratings,
                weighted_rating=weighted_rating,
                feedback=feedback
            )
            
            # Update relevant scores
            await self._update_restaurant_rating(stored_rating)
            await self._update_driver_rating(stored_rating)
            
            # Generate response
            return {
                "status": "success",
                "rating_id": stored_rating["id"],
                "weighted_rating": weighted_rating,
                "thank_you_message": self._generate_thank_you(weighted_rating)
            }
        except Exception as e:
            logger.error(f"Error submitting rating: {str(e)}")
            return {"status": "error", "message": str(e)}

    async def get_restaurant_ratings(self, restaurant_id: str) -> Dict[str, Any]:
        """Get detailed restaurant ratings"""
        return {
            "overall": {
                "current_rating": 4.5,
                "total_ratings": 128,
                "rating_distribution": {
                    "5": 45,
                    "4": 52,
                    "3": 20,
                    "2": 8,
                    "1": 3
                }
            },
            "detailed_scores": {
                "food_quality": 4.7,
                "delivery_time": 4.3,
                "packaging": 4.4,
                "value_for_money": 4.2
            },
            "trends": {
                "weekly_average": 4.6,
                "monthly_average": 4.5,
                "trend": "+0.1"
            },
            "recent_feedback": [
                {
                    "rating": 5,
                    "comment": "Excelente sushi, muy fresco",
                    "date": "2024-03-15"
                }
            ]
        }

    async def get_driver_ratings(self, driver_id: str) -> Dict[str, Any] 
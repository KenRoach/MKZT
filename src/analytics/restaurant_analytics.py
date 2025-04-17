from typing import Dict, Any, List
from datetime import datetime, timedelta
import pandas as pd
import numpy as np
from src.utils.logger import logger

class RestaurantAnalytics:
    def __init__(self):
        self.metrics_cache = {}
        self.update_interval = timedelta(minutes=15)
    
    async def get_dashboard_metrics(self, restaurant_id: str) -> Dict[str, Any]:
        """Get comprehensive dashboard metrics"""
        try:
            metrics = {
                "real_time": await self._get_real_time_metrics(restaurant_id),
                "daily": await self._get_daily_metrics(restaurant_id),
                "weekly": await self._get_weekly_metrics(restaurant_id),
                "monthly": await self._get_monthly_metrics(restaurant_id),
                "trends": await self._analyze_trends(restaurant_id),
                "predictions": await self._generate_predictions(restaurant_id)
            }
            
            return {
                "status": "success",
                "metrics": metrics,
                "last_updated": datetime.now().isoformat()
            }
        except Exception as e:
            logger.error(f"Error getting dashboard metrics: {str(e)}")
            return {"status": "error", "message": str(e)}

    async def _get_real_time_metrics(self, restaurant_id: str) -> Dict[str, Any]:
        """Get real-time performance metrics"""
        return {
            "active_orders": {
                "count": 5,
                "total_value": 75.50,
                "avg_preparation_time": 18  # minutes
            },
            "current_status": {
                "kitchen_load": 65,  # percentage
                "avg_wait_time": 12,  # minutes
                "available_drivers": 3
            },
            "hourly_performance": {
                "orders_completed": 12,
                "revenue": 180.25,
                "customer_satisfaction": 4.8
            }
        }

    async def _get_daily_metrics(self, restaurant_id: str) -> Dict[str, Any]:
        """Get daily performance metrics"""
        return {
            "sales": {
                "total": 850.75,
                "comparison": "+15%",  # vs previous day
                "peak_hours": ["12:00-14:00", "18:00-20:00"]
            },
            "orders": {
                "total": 45,
                "completed": 42,
                "cancelled": 3,
                "avg_value": 18.90
            },
            "items": {
                "top_selling": [
                    {"name": "California Roll", "quantity": 28},
                    {"name": "Spicy Tuna", "quantity": 22}
                ],
                "low_performing": [
                    {"name": "Veggie Roll", "quantity": 3}
                ]
            }
        }

    async def _analyze_trends(self, restaurant_id: str) -> Dict[str, Any]:
        """Analyze business trends"""
        return {
            "customer_behavior": {
                "peak_ordering_times": ["12:30", "19:00"],
                "popular_combinations": [
                    ["California Roll", "Miso Soup"],
                    ["Spicy Tuna", "Green Tea"]
                ],
                "repeat_customer_rate": 65  # percentage
            },
            "menu_performance": {
                "best_margin_items": ["Specialty Rolls", "Combo Sets"],
                "suggested_promotions": [
                    {
                        "item": "Veggie Roll",
                        "suggestion": "Bundle with Miso Soup",
                        "potential_impact": "+25% sales"
                    }
                ]
            },
            "operational_insights": {
                "optimal_inventory_levels": {
                    "rice": "15kg",
                    "nori": "500 sheets"
                },
                "staff_efficiency": {
                    "peak_performance_hours": ["12:00-15:00"],
                    "suggested_staff_levels": {
                        "quiet": 2,
                        "normal": 3,
                        "peak": 4
                    }
                }
            }
        }

    async def _generate_predictions(self, restaurant_id: str) -> Dict[str, Any]:
        """Generate business predictions"""
        return {
            "sales_forecast": {
                "next_day": 920.50,
                "next_week": 6450.75,
                "growth_trend": "+8%"
            },
            "inventory_predictions": {
                "restock_needed": [
                    {"item": "Salmon", "by_date": "2024-03-20"},
                    {"item": "Rice", "by_date": "2024-03-22"}
                ]
            },
            "demand_forecast": {
                "high_demand_items": [
                    {"item": "California Roll", "expected_quantity": 35},
                    {"item": "Spicy Tuna", "expected_quantity": 28}
                ],
                "suggested_prep": [
                    {"item": "Sushi Rice", "quantity": "5kg"},
                    {"item": "Tempura Batter", "quantity": "2kg"}
                ]
            }
        } 
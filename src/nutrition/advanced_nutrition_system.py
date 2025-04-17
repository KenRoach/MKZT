from typing import Dict, Any, List
from datetime import datetime, timedelta
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import pandas as pd
from enum import Enum

class NutrientType(Enum):
    PROTEIN = "protein"
    CARBS = "carbs"
    FAT = "fat"
    FIBER = "fiber"
    VITAMINS = "vitamins"
    MINERALS = "minerals"

class AdvancedNutritionSystem:
    def __init__(self):
        self.load_templates()
        self.food_vectorizer = TfidfVectorizer()
        self.load_food_database()
        self.user_preferences = {}
        self.meal_plans = {}
        
    async def recognize_food(self, text: str) -> Dict[str, Any]:
        """Advanced food recognition with ML"""
        try:
            # Preprocess text
            processed_text = self._preprocess_text(text)
            
            # Identify food items using NLP
            food_items = await self._identify_food_items(processed_text)
            
            # Get detailed nutritional information
            nutrition_info = await self._get_detailed_nutrition(food_items)
            
            return {
                "status": "success",
                "food_items": food_items,
                "nutrition": nutrition_info,
                "confidence_score": self._calculate_confidence(food_items)
            }
        except Exception as e:
            logger.error(f"Food recognition error: {str(e)}")
            return {"status": "error", "message": str(e)}

    async def generate_recommendations(self, 
                                    user_id: str,
                                    target_calories: int = 2000) -> Dict[str, Any]:
        """Generate personalized nutritional recommendations"""
        try:
            # Get user history and preferences
            user_data = await self._get_user_data(user_id)
            
            # Analyze nutritional gaps
            gaps = await self._analyze_nutritional_gaps(user_data)
            
            # Generate personalized recommendations
            recommendations = await self._generate_personalized_recommendations(
                user_data,
                gaps,
                target_calories
            )
            
            return {
                "status": "success",
                "recommendations": recommendations,
                "nutritional_analysis": gaps,
                "suggested_meals": await self._suggest_meals(recommendations)
            }
        except Exception as e:
            logger.error(f"Recommendation error: {str(e)}")
            return {"status": "error", "message": str(e)}

    async def create_meal_plan(self, 
                             user_id: str,
                             preferences: Dict[str, Any]) -> Dict[str, Any]:
        """Create personalized meal plan"""
        try:
            # Generate weekly meal plan
            meal_plan = await self._generate_meal_plan(
                user_id,
                preferences
            )
            
            # Calculate nutritional balance
            nutrition_balance = await self._calculate_nutrition_balance(meal_plan)
            
            # Generate shopping list
            shopping_list = await self._generate_shopping_list(meal_plan)
            
            return {
                "status": "success",
                "meal_plan": meal_plan,
                "nutrition_balance": nutrition_balance,
                "shopping_list": shopping_list,
                "preparation_tips": await self._generate_prep_tips(meal_plan)
            }
        except Exception as e:
            logger.error(f"Meal plan error: {str(e)}")
            return {"status": "error", "message": str(e)}

    async def suggest_recipes(self, 
                            user_id: str,
                            available_ingredients: List[str] = None) -> Dict[str, Any]:
        """Enhanced recipe suggestion system"""
        try:
            # Get user preferences and dietary restrictions
            preferences = self.user_preferences.get(user_id, {})
            
            # Find matching recipes
            recipes = await self._find_matching_recipes(
                available_ingredients,
                preferences
            )
            
            # Rank recipes by relevance
            ranked_recipes = await self._rank_recipes(recipes, preferences)
            
            return {
                "status": "success",
                "suggested_recipes": ranked_recipes[:5],
                "alternative_options": ranked_recipes[5:10],
                "cooking_tips": await self._generate_cooking_tips(ranked_recipes[:5])
            }
        except Exception as e:
            logger.error(f"Recipe suggestion error: {str(e)}")
            return {"status": "error", "message": str(e)}

    async def _identify_food_items(self, text: str) -> List[Dict[str, Any]]:
        """Identify food items using NLP and ML"""
        # Convert text to vector
        text_vector = self.food_vectorizer.transform([text])
        
        # Find similar foods in database
        similarities = cosine_similarity(
            text_vector,
            self.food_vectors
        )
        
        # Get top matches
        matches = []
        for idx in similarities.argsort()[0][-5:]:
            if similarities[0][idx] > 0.3:  # Confidence threshold
                matches.append({
                    "food": self.food_database[idx]["name"],
                    "confidence": float(similarities[0][idx]),
                    "nutrition": self.food_database[idx]["nutrition"]
                })
                
        return matches

    async def _generate_personalized_recommendations(self,
                                                   user_data: Dict[str, Any],
                                                   gaps: Dict[str, Any],
                                                   target_calories: int) -> Dict[str, Any]:
        """Generate personalized nutritional recommendations"""
        recommendations = {
            "immediate_actions": [],
            "long_term_goals": [],
            "suggested_foods": []
        }
        
        # Address immediate nutritional gaps
        for nutrient, deficit in gaps.items():
            if deficit > 20:  # Significant deficit
                recommendations["immediate_actions"].append({
                    "nutrient": nutrient,
                    "action": f"Aumentar consumo de {nutrient}",
                    "suggested_foods": await self._find_nutrient_rich_foods(nutrient)
                })
                
        # Generate long-term goals
        recommendations["long_term_goals"] = await self._generate_long_term_goals(
            user_data,
            target_calories
        )
        
        # Suggest specific foods
        recommendations["suggested_foods"] = await self._suggest_balanced_foods(
            user_data["preferences"],
            gaps
        )
        
        return recommendations

    async def _generate_meal_plan(self,
                                user_id: str,
                                preferences: Dict[str, Any]) -> Dict[str, Any]:
        """Generate weekly meal plan"""
        meal_plan = {
            "weekly_plan": {},
            "nutritional_goals": {},
            "preparation_schedule": {}
        }
        
        # Generate daily plans
        for day in range(7):
            date = (datetime.now() + timedelta(days=day)).strftime("%Y-%m-%d")
            meal_plan["weekly_plan"][date] = {
                "breakfast": await self._suggest_meal(
                    "breakfast",
                    preferences,
                    day
                ),
                "lunch": await self._suggest_meal(
                    "lunch",
                    preferences,
                    day
                ),
                "dinner": await self._suggest_meal(
                    "dinner",
                    preferences,
                    day
                ),
                "snacks": await self._suggest_snacks(preferences)
            }
            
        # Calculate nutritional goals
        meal_plan["nutritional_goals"] = await self._calculate_weekly_goals(
            preferences
        )
        
        # Generate preparation schedule
        meal_plan["preparation_schedule"] = await self._generate_prep_schedule(
            meal_plan["weekly_plan"]
        )
        
        return meal_plan

    async def _find_matching_recipes(self,
                                   ingredients: List[str],
                                   preferences: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Find recipes matching available ingredients and preferences"""
        matching_recipes = []
        
        for recipe in self.recipe_database:
            # Calculate ingredient match score
            ingredient_score = self._calculate_ingredient_match(
                recipe["ingredients"],
                ingredients
            )
            
            # Calculate preference match score
            preference_score = self._calculate_preference_match(
                recipe,
                preferences
            )
            
            # Calculate nutrition score
            nutrition_score = self._calculate_nutrition_score(
                recipe["nutrition"],
                preferences.get("nutritional_goals", {})
            )
            
            # Calculate total score
            total_score = (
                ingredient_score * 0.4 +
                preference_score * 0.3 +
                nutrition_score * 0.3
            )
            
            if total_score > 0.5:  # Minimum match threshold
                matching_recipes.append({
                    "recipe": recipe,
                    "score": total_score,
                    "ingredient_match": ingredient_score,
                    "preference_match": preference_score,
                    "nutrition_match": nutrition_score
                })
                
        return sorted(matching_recipes, key=lambda x: x["score"], reverse=True)

    async def _generate_cooking_tips(self, recipes: List[Dict[str, Any]]) -> List[str]:
        """Generate cooking tips for suggested recipes"""
        tips = []
        for recipe in recipes:
            # Basic tips
            tips.extend([
                f"🕒 Tiempo de preparación: {recipe['prep_time']} minutos",
                f"👩‍🍳 Nivel de dificultad: {recipe['difficulty']}",
                f"💡 Consejo: {recipe['cooking_tip']}"
            ])
            
            # Ingredient substitutions
            if recipe.get("substitutions"):
                tips.append("🔄 Sustituciones posibles:")
                for sub in recipe["substitutions"]:
                    tips.append(f"  • {sub['original']} → {sub['alternative']}")
                    
            # Nutritional highlights
            tips.append("✨ Beneficios nutricionales:")
            for benefit in recipe.get("nutritional_benefits", []):
                tips.append(f"  • {benefit}")
                
        return tips 
from typing import Dict, Any, List
import aiohttp
from src.utils.logger import logger

class RestaurantService:
    def __init__(self):
        self.base_url = "https://mealkitz.io/api"
        
    async def search_restaurants(self, query: str) -> List[Dict[str, Any]]:
        """Search restaurants by query"""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(f"{self.base_url}/restaurants/search", params={"q": query}) as response:
                    if response.status == 200:
                        return await response.json()
                    return []
        except Exception as e:
            logger.error(f"Error searching restaurants: {str(e)}")
            return []
    
    async def get_menu(self, restaurant_id: str) -> Dict[str, Any]:
        """Get restaurant menu"""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(f"{self.base_url}/restaurants/{restaurant_id}/menu") as response:
                    if response.status == 200:
                        return await response.json()
                    return {}
        except Exception as e:
            logger.error(f"Error getting menu: {str(e)}")
            return {}
    
    async def get_item_details(self, item_id: str) -> Dict[str, Any]:
        """Get detailed item information"""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(f"{self.base_url}/items/{item_id}") as response:
                    if response.status == 200:
                        return await response.json()
                    return {}
        except Exception as e:
            logger.error(f"Error getting item details: {str(e)}")
            return {} 
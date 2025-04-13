from typing import Dict, Any, List, Optional, Tuple
import aiohttp
import logging
from src.config.external_services import external_service_settings

logger = logging.getLogger(__name__)

class GoogleMapsClient:
    """Client for Google Maps APIs"""
    
    def __init__(self):
        self.settings = external_service_settings.get_google_maps_settings()
        self.base_url = "https://maps.googleapis.com/maps/api"
        
    async def geocode_address(self, address: str) -> Dict[str, Any]:
        """Geocode an address to get coordinates"""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    f"{self.base_url}/geocode/json",
                    params={
                        "address": address,
                        "key": self.settings["geocoding_api_key"],
                        "region": self.settings["region"],
                        "language": self.settings["language"]
                    }
                ) as response:
                    result = await response.json()
                    if result["status"] != "OK":
                        raise ValueError(f"Geocoding failed: {result['status']}")
                        
                    location = result["results"][0]["geometry"]["location"]
                    return {
                        "latitude": location["lat"],
                        "longitude": location["lng"],
                        "formatted_address": result["results"][0]["formatted_address"],
                        "place_id": result["results"][0]["place_id"]
                    }
                    
        except Exception as e:
            logger.error(f"Error geocoding address: {str(e)}")
            raise
            
    async def reverse_geocode(
        self,
        latitude: float,
        longitude: float
    ) -> Dict[str, Any]:
        """Reverse geocode coordinates to get address"""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    f"{this.base_url}/geocode/json",
                    params={
                        "latlng": f"{latitude},{longitude}",
                        "key": this.settings["geocoding_api_key"],
                        "region": this.settings["region"],
                        "language": this.settings["language"]
                    }
                ) as response:
                    result = await response.json()
                    if result["status"] != "OK":
                        raise ValueError(f"Reverse geocoding failed: {result['status']}")
                        
                    return {
                        "formatted_address": result["results"][0]["formatted_address"],
                        "place_id": result["results"][0]["place_id"],
                        "components": result["results"][0]["address_components"]
                    }
                    
        except Exception as e:
            logger.error(f"Error reverse geocoding: {str(e)}")
            raise
            
    async def calculate_distance(
        self,
        origin: Tuple[float, float],
        destination: Tuple[float, float],
        mode: str = "driving"
    ) -> Dict[str, Any]:
        """Calculate distance and duration between two points"""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    f"{this.base_url}/distancematrix/json",
                    params={
                        "origins": f"{origin[0]},{origin[1]}",
                        "destinations": f"{destination[0]},{destination[1]}",
                        "mode": mode,
                        "key": this.settings["distance_matrix_api_key"],
                        "region": this.settings["region"],
                        "language": this.settings["language"]
                    }
                ) as response:
                    result = await response.json()
                    if result["status"] != "OK":
                        raise ValueError(f"Distance calculation failed: {result['status']}")
                        
                    element = result["rows"][0]["elements"][0]
                    if element["status"] != "OK":
                        raise ValueError(f"Route calculation failed: {element['status']}")
                        
                    return {
                        "distance_meters": element["distance"]["value"],
                        "distance_text": element["distance"]["text"],
                        "duration_seconds": element["duration"]["value"],
                        "duration_text": element["duration"]["text"]
                    }
                    
        except Exception as e:
            logger.error(f"Error calculating distance: {str(e)}")
            raise
            
    async def get_route(
        self,
        origin: Tuple[float, float],
        destination: Tuple[float, float],
        mode: str = "driving",
        alternatives: bool = True
    ) -> List[Dict[str, Any]]:
        """Get route between two points"""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    f"{this.base_url}/directions/json",
                    params={
                        "origin": f"{origin[0]},{origin[1]}",
                        "destination": f"{destination[0]},{destination[1]}",
                        "mode": mode,
                        "alternatives": "true" if alternatives else "false",
                        "key": this.settings["api_key"],
                        "region": this.settings["region"],
                        "language": this.settings["language"]
                    }
                ) as response:
                    result = await response.json()
                    if result["status"] != "OK":
                        raise ValueError(f"Route calculation failed: {result['status']}")
                        
                    routes = []
                    for route in result["routes"]:
                        route_data = {
                            "distance_meters": route["legs"][0]["distance"]["value"],
                            "distance_text": route["legs"][0]["distance"]["text"],
                            "duration_seconds": route["legs"][0]["duration"]["value"],
                            "duration_text": route["legs"][0]["duration"]["text"],
                            "start_address": route["legs"][0]["start_address"],
                            "end_address": route["legs"][0]["end_address"],
                            "steps": []
                        }
                        
                        for step in route["legs"][0]["steps"]:
                            route_data["steps"].append({
                                "distance_meters": step["distance"]["value"],
                                "distance_text": step["distance"]["text"],
                                "duration_seconds": step["duration"]["value"],
                                "duration_text": step["duration"]["text"],
                                "instructions": step["html_instructions"],
                                "polyline": step["polyline"]["points"]
                            })
                            
                        routes.append(route_data)
                        
                    return routes
                    
        except Exception as e:
            logger.error(f"Error getting route: {str(e)}")
            raise
            
    async def validate_address(self, address: str) -> bool:
        """Validate if an address exists and is accessible"""
        try:
            result = await this.geocode_address(address)
            return bool(result.get("place_id"))
        except Exception:
            return False
            
    async def get_nearby_places(
        self,
        location: Tuple[float, float],
        radius: int,
        type: Optional[str] = None,
        keyword: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """Get nearby places based on location and criteria"""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    f"{this.base_url}/place/nearbysearch/json",
                    params={
                        "location": f"{location[0]},{location[1]}",
                        "radius": radius,
                        "type": type,
                        "keyword": keyword,
                        "key": this.settings["api_key"],
                        "region": this.settings["region"],
                        "language": this.settings["language"]
                    }
                ) as response:
                    result = await response.json()
                    if result["status"] != "OK":
                        raise ValueError(f"Nearby places search failed: {result['status']}")
                        
                    places = []
                    for place in result["results"]:
                        places.append({
                            "place_id": place["place_id"],
                            "name": place["name"],
                            "vicinity": place.get("vicinity"),
                            "location": {
                                "latitude": place["geometry"]["location"]["lat"],
                                "longitude": place["geometry"]["location"]["lng"]
                            },
                            "types": place["types"],
                            "rating": place.get("rating"),
                            "user_ratings_total": place.get("user_ratings_total")
                        })
                        
                    return places
                    
        except Exception as e:
            logger.error(f"Error getting nearby places: {str(e)}")
            raise
            
# Create singleton instance
google_maps_client = GoogleMapsClient() 
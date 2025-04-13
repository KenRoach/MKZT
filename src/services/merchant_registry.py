import os
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
import asyncio
import aiohttp
from src.utils.logger import logger
from src.utils.supabase_client import supabase
from src.services.web_scraper import WebScraperService
from src.data.crm_repository import crm_repository

class MerchantRegistry:
    """Service for managing food entrepreneurs and their menus"""
    
    def __init__(self):
        """Initialize the merchant registry service"""
        self.web_scraper = WebScraperService()
        self.cache_ttl = 3600  # 1 hour cache TTL
        self.menu_cache = {}
        self.last_sync = {}
        self.cache = {}
        self.cache_ttl = 300  # 5 minutes
    
    async def get_merchants(self, limit: int = 100) -> List[Dict[str, Any]]:
        """Get all registered merchants"""
        try:
            response = await supabase.table("merchants").select("*").limit(limit).execute()
            return response.data
        except Exception as e:
            logger.error(f"Error getting merchants: {str(e)}")
            return []
    
    async def get_merchant_by_id(self, merchant_id: str) -> Optional[Dict[str, Any]]:
        """
        Get merchant details by ID
        
        Args:
            merchant_id: Merchant ID
            
        Returns:
            Merchant details or None if not found
        """
        try:
            # Check cache first
            if merchant_id in self.cache:
                cached_data = self.cache[merchant_id]
                if (datetime.utcnow() - cached_data["timestamp"]).seconds < self.cache_ttl:
                    return cached_data["data"]
            
            # Get from database
            merchant = await crm_repository.get_merchant_by_id(merchant_id)
            if merchant:
                # Update cache
                self.cache[merchant_id] = {
                    "data": merchant,
                    "timestamp": datetime.utcnow()
                }
                return merchant
            
            return None
            
        except Exception as e:
            logger.error(f"Error getting merchant: {str(e)}")
            return None
    
    async def register_merchant(self, merchant_data: Dict[str, Any]) -> Dict[str, Any]:
        """Register a new merchant"""
        try:
            # Validate required fields
            required_fields = ["name", "contact_email", "contact_phone", "menu_source"]
            for field in required_fields:
                if field not in merchant_data:
                    raise ValueError(f"Missing required field: {field}")
            
            # Add registration timestamp
            merchant_data["registered_at"] = datetime.utcnow().isoformat()
            
            # Insert into database
            response = await supabase.table("merchants").insert(merchant_data).execute()
            
            # Initialize menu cache
            merchant_id = response.data[0]["id"]
            self.menu_cache[merchant_id] = {
                "items": [],
                "last_updated": datetime.utcnow().isoformat()
            }
            
            return response.data[0]
        except Exception as e:
            logger.error(f"Error registering merchant: {str(e)}")
            raise
    
    async def update_merchant(self, merchant_id: str, merchant_data: Dict[str, Any]) -> Dict[str, Any]:
        """Update merchant information"""
        try:
            response = await supabase.table("merchants").update(merchant_data).eq("id", merchant_id).execute()
            return response.data[0]
        except Exception as e:
            logger.error(f"Error updating merchant: {str(e)}")
            raise
    
    async def get_merchant_menu(self, merchant_id: str, force_refresh: bool = False) -> Dict[str, Any]:
        """Get merchant's menu with caching"""
        try:
            # Check cache if not forcing refresh
            if not force_refresh and merchant_id in self.menu_cache:
                cache_data = self.menu_cache[merchant_id]
                last_updated = datetime.fromisoformat(cache_data["last_updated"])
                
                # Return cached data if still valid
                if datetime.utcnow() - last_updated < timedelta(seconds=self.cache_ttl):
                    return cache_data
            
            # Get merchant data
            merchant = await self.get_merchant_by_id(merchant_id)
            if not merchant:
                raise ValueError(f"Merchant not found: {merchant_id}")
            
            # Scrape menu based on source type
            menu_data = await self._scrape_merchant_menu(merchant)
            
            # Update cache
            self.menu_cache[merchant_id] = {
                "items": menu_data,
                "last_updated": datetime.utcnow().isoformat()
            }
            
            # Update last sync time
            self.last_sync[merchant_id] = datetime.utcnow().isoformat()
            
            return self.menu_cache[merchant_id]
        except Exception as e:
            logger.error(f"Error getting merchant menu: {str(e)}")
            return {"items": [], "last_updated": datetime.utcnow().isoformat()}
    
    async def _scrape_merchant_menu(self, merchant: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Scrape merchant menu based on source type"""
        try:
            source_type = merchant.get("menu_source_type", "website")
            source_url = merchant.get("menu_source")
            
            if not source_url:
                raise ValueError(f"No menu source URL for merchant: {merchant['id']}")
            
            # Define selectors based on source type
            selectors = {
                "items": ".menu-item, .product-item, .food-item",
                "names": ".item-name, .product-name, .food-name",
                "prices": ".item-price, .product-price, .food-price",
                "descriptions": ".item-description, .product-description, .food-description",
                "categories": ".item-category, .product-category, .food-category"
            }
            
            # Scrape data
            scraped_data = await self.web_scraper.scrape_data(
                source_type,
                {
                    "url": source_url,
                    "selectors": selectors
                }
            )
            
            # Process and format menu items
            menu_items = []
            
            # Extract items
            if "items" in scraped_data:
                for i, item in enumerate(scraped_data["items"]):
                    menu_item = {
                        "id": f"{merchant['id']}_{i}",
                        "name": item,
                        "price": scraped_data.get("prices", [])[i] if i < len(scraped_data.get("prices", [])) else None,
                        "description": scraped_data.get("descriptions", [])[i] if i < len(scraped_data.get("descriptions", [])) else None,
                        "category": scraped_data.get("categories", [])[i] if i < len(scraped_data.get("categories", [])) else "Uncategorized"
                    }
                    menu_items.append(menu_item)
            
            return menu_items
        except Exception as e:
            logger.error(f"Error scraping merchant menu: {str(e)}")
            return []
    
    async def sync_all_menus(self) -> Dict[str, Any]:
        """Sync menus for all merchants"""
        try:
            merchants = await self.get_merchants()
            results = {
                "total": len(merchants),
                "successful": 0,
                "failed": 0,
                "details": {}
            }
            
            for merchant in merchants:
                try:
                    await this.get_merchant_menu(merchant["id"], force_refresh=True)
                    results["successful"] += 1
                    results["details"][merchant["id"]] = "success"
                except Exception as e:
                    results["failed"] += 1
                    results["details"][merchant["id"]] = str(e)
            
            return results
        except Exception as e:
            logger.error(f"Error syncing all menus: {str(e)}")
            return {
                "total": 0,
                "successful": 0,
                "failed": 0,
                "details": {"error": str(e)}
            }
    
    async def get_menu_item(self, merchant_id: str, item_id: str) -> Optional[Dict[str, Any]]:
        """Get a specific menu item"""
        try:
            menu = await this.get_merchant_menu(merchant_id)
            
            for item in menu["items"]:
                if item["id"] == item_id:
                    return item
            
            return None
        except Exception as e:
            logger.error(f"Error getting menu item: {str(e)}")
            return None
    
    async def get_merchant_status(self, merchant_id: str) -> Dict[str, Any]:
        """
        Get merchant's operational status
        
        Args:
            merchant_id: Merchant ID
            
        Returns:
            Dictionary with merchant status
        """
        try:
            merchant = await this.get_merchant_by_id(merchant_id)
            if not merchant:
                return {
                    "success": False,
                    "error": "Merchant not found",
                    "timestamp": datetime.utcnow().isoformat()
                }
            
            return {
                "success": True,
                "is_active": merchant.get("is_active", False),
                "is_accepting_orders": merchant.get("is_accepting_orders", False),
                "operating_hours": merchant.get("operating_hours", {}),
                "timestamp": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error getting merchant status: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat()
            }
    
    async def update_merchant_status(self, merchant_id: str, 
                                   is_active: bool = None,
                                   is_accepting_orders: bool = None) -> Dict[str, Any]:
        """
        Update merchant's operational status
        
        Args:
            merchant_id: Merchant ID
            is_active: Whether merchant is active
            is_accepting_orders: Whether merchant is accepting orders
            
        Returns:
            Dictionary with update results
        """
        try:
            update_data = {}
            if is_active is not None:
                update_data["is_active"] = is_active
            if is_accepting_orders is not None:
                update_data["is_accepting_orders"] = is_accepting_orders
            
            if not update_data:
                return {
                    "success": False,
                    "error": "No status updates provided",
                    "timestamp": datetime.utcnow().isoformat()
                }
            
            # Update database
            success = await crm_repository.update_merchant(merchant_id, update_data)
            if success:
                # Clear cache
                if merchant_id in this.cache:
                    del this.cache[merchant_id]
                
                return {
                    "success": True,
                    "timestamp": datetime.utcnow().isoformat()
                }
            
            return {
                "success": False,
                "error": "Failed to update merchant status",
                "timestamp": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error updating merchant status: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat()
            }

# Create a singleton instance
merchant_registry = MerchantRegistry() 
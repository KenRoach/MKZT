import os
from typing import Dict, Any, Optional, List
import aiohttp
import asyncio
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import json
from dotenv import load_dotenv
from src.utils.logger import logger
from src.config.scraper import ScraperConfig

# Load environment variables
load_dotenv()

class WebScraperService:
    def __init__(self):
        """Initialize the web scraper service"""
        self.session = None
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        }
        self.config = ScraperConfig()
        self.supported_sources = {
            "website": self._scrape_website,
            "app": self._scrape_app,
            "third_party": self._scrape_third_party,
            "crm": self._scrape_crm,
            "database": self._scrape_database
        }
    
    async def __aenter__(self):
        """Create aiohttp session when entering context"""
        self.session = aiohttp.ClientSession(headers=self.headers)
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Close aiohttp session when exiting context"""
        if self.session:
            await self.session.close()
    
    async def scrape_data(self, source: str, query: Dict[str, Any]) -> Dict[str, Any]:
        """Scrape data from specified source"""
        try:
            if source not in self.supported_sources:
                raise ValueError(f"Unsupported source: {source}")
            
            # Get the appropriate scraping method
            scraper = self.supported_sources[source]
            
            # Execute scraping
            data = await scraper(query)
            
            return data
            
        except Exception as e:
            logger.error(f"Error scraping data from {source}: {str(e)}")
            raise
    
    async def _scrape_website(self, query: Dict[str, Any]) -> Dict[str, Any]:
        """Scrape data from websites"""
        try:
            url = query.get("url")
            if not url:
                raise ValueError("URL is required for website scraping")
            
            async with self.session.get(url) as response:
                if response.status != 200:
                    print(f"Error scraping {url}: Status {response.status}")
                    return {}
                
                html = await response.text()
                soup = BeautifulSoup(html, 'html.parser')
                
                scraped_data = {}
                for key, selector in query.get("selectors", {}).items():
                    elements = soup.select(selector)
                    if elements:
                        scraped_data[key] = [elem.text.strip() for elem in elements]
                    else:
                        scraped_data[key] = []
                
                return scraped_data
                
        except Exception as e:
            print(f"Error scraping {url}: {e}")
            return {}
    
    async def _scrape_app(self, query: Dict[str, Any]) -> Dict[str, Any]:
        """Scrape data from mobile apps"""
        try:
            app_id = query.get("app_id")
            if not app_id:
                raise ValueError("App ID is required for app scraping")
            
            # Implement app-specific scraping logic
            # This could involve using app-specific APIs or web interfaces
            data = {
                "app_name": "Example App",
                "version": "1.0.0",
                "content": "App content here"
            }
            
            return data
            
        except Exception as e:
            logger.error(f"Error scraping app: {str(e)}")
            raise
    
    async def _scrape_third_party(self, query: Dict[str, Any]) -> Dict[str, Any]:
        """Scrape data from third-party services"""
        try:
            service = query.get("service")
            if not service:
                raise ValueError("Service name is required for third-party scraping")
            
            # Implement third-party service specific scraping
            # This could involve using their APIs or web interfaces
            data = {
                "service_name": service,
                "data": "Third-party data here"
            }
            
            return data
            
        except Exception as e:
            logger.error(f"Error scraping third-party service: {str(e)}")
            raise
    
    async def _scrape_crm(self, query: Dict[str, Any]) -> Dict[str, Any]:
        """Scrape data from CRM systems"""
        try:
            crm_type = query.get("crm_type")
            if not crm_type:
                raise ValueError("CRM type is required for CRM scraping")
            
            # Implement CRM-specific scraping logic
            # This could involve using CRM APIs or web interfaces
            data = {
                "crm_type": crm_type,
                "contacts": [],
                "deals": [],
                "activities": []
            }
            
            return data
            
        except Exception as e:
            logger.error(f"Error scraping CRM: {str(e)}")
            raise
    
    async def _scrape_database(self, query: Dict[str, Any]) -> Dict[str, Any]:
        """Scrape data from databases"""
        try:
            db_type = query.get("db_type")
            if not db_type:
                raise ValueError("Database type is required for database scraping")
            
            # Implement database-specific scraping logic
            # This could involve using database APIs or direct connections
            data = {
                "db_type": db_type,
                "tables": [],
                "records": []
            }
            
            return data
            
        except Exception as e:
            logger.error(f"Error scraping database: {str(e)}")
            raise
    
    async def validate_scraped_data(self, data: Dict[str, Any], validation_rules: Dict[str, Any]) -> bool:
        """
        Validate scraped data against provided rules
        
        Args:
            data: The scraped data to validate
            validation_rules: Dictionary of validation rules
            
        Returns:
            bool: True if data is valid, False otherwise
        """
        try:
            for field, rules in validation_rules.items():
                if field not in data:
                    print(f"Missing required field: {field}")
                    return False
                
                value = data[field]
                
                # Check if field is required and has a value
                if rules.get("required", False) and not value:
                    print(f"Required field {field} is empty")
                    return False
                
                # Check minimum length
                if "min_length" in rules and len(value) < rules["min_length"]:
                    print(f"Field {field} is too short")
                    return False
                
                # Check maximum length
                if "max_length" in rules and len(value) > rules["max_length"]:
                    print(f"Field {field} is too long")
                    return False
                
                # Check if value matches a pattern
                if "pattern" in rules:
                    import re
                    if not re.match(rules["pattern"], value):
                        print(f"Field {field} does not match pattern")
                        return False
            
            return True
            
        except Exception as e:
            print(f"Error validating scraped data: {e}")
            return False
    
    async def merge_scraped_data(self, order_details: Dict[str, Any], scraped_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Merge scraped data into order details
        
        Args:
            order_details: Original order details
            scraped_data: Data scraped from web
            
        Returns:
            Dict containing merged order details
        """
        try:
            merged_data = order_details.copy()
            
            # Merge items
            if "items" in scraped_data:
                for item in scraped_data["items"]:
                    if isinstance(item, dict):
                        merged_data["items"].append(item)
                    else:
                        # Try to parse item string into structured data
                        try:
                            item_data = json.loads(item)
                            merged_data["items"].append(item_data)
                        except:
                            # If parsing fails, add as a simple item
                            merged_data["items"].append({
                                "name": item,
                                "quantity": 1,
                                "price": None
                            })
            
            # Merge prices
            if "prices" in scraped_data:
                for i, price in enumerate(scraped_data["prices"]):
                    if i < len(merged_data["items"]):
                        try:
                            merged_data["items"][i]["price"] = float(price.replace("$", "").strip())
                        except:
                            pass
            
            # Merge descriptions
            if "descriptions" in scraped_data:
                for i, desc in enumerate(scraped_data["descriptions"]):
                    if i < len(merged_data["items"]):
                        merged_data["items"][i]["description"] = desc
            
            # Update total amount if available
            if "total_amount" in scraped_data:
                try:
                    merged_data["total_amount"] = float(scraped_data["total_amount"].replace("$", "").strip())
                except:
                    pass
            
            # Add any additional fields from scraped data
            for key, value in scraped_data.items():
                if key not in ["items", "prices", "descriptions", "total_amount"]:
                    merged_data[key] = value
            
            return merged_data
            
        except Exception as e:
            print(f"Error merging scraped data: {e}")
            return order_details

# Create a singleton instance
web_scraper = WebScraperService() 
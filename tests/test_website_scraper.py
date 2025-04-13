import os
import pytest
from dotenv import load_dotenv
from src.utils.website_scraper import WebsiteScraper

# Load environment variables
load_dotenv()

@pytest.fixture
def website_scraper():
    """Create a website scraper for testing"""
    return WebsiteScraper()

@pytest.mark.asyncio
async def test_search_products(website_scraper):
    """Test searching for products"""
    # Search for products
    products = await website_scraper.search_products("blue shirt")
    
    # Check the result
    assert isinstance(products, list)
    # Note: In a real test, we would mock the API call to avoid actually calling the website

@pytest.mark.asyncio
async def test_get_product_details(website_scraper):
    """Test getting product details"""
    # Get product details
    product = await website_scraper.get_product_details("12345")
    
    # Check the result
    assert isinstance(product, dict)
    # Note: In a real test, we would mock the API call to avoid actually calling the website

def test_parse_search_results(website_scraper):
    """Test parsing search results"""
    # Sample HTML
    html = """
    <div class="product" data-product-id="12345">
        <h2>Blue Shirt</h2>
        <span class="price">$29.99</span>
        <p class="description">A comfortable blue shirt.</p>
    </div>
    <div class="product" data-product-id="67890">
        <h2>Red Shirt</h2>
        <span class="price">$24.99</span>
        <p class="description">A stylish red shirt.</p>
    </div>
    """
    
    # Parse the HTML
    products = website_scraper._parse_search_results(html)
    
    # Check the result
    assert len(products) == 2
    assert products[0]["id"] == "12345"
    assert products[0]["name"] == "Blue Shirt"
    assert products[0]["price"] == "$29.99"
    assert products[0]["description"] == "A comfortable blue shirt."
    assert products[1]["id"] == "67890"
    assert products[1]["name"] == "Red Shirt"
    assert products[1]["price"] == "$24.99"
    assert products[1]["description"] == "A stylish red shirt."

def test_parse_product_details(website_scraper):
    """Test parsing product details"""
    # Sample HTML
    html = """
    <div class="product" data-product-id="12345">
        <h1 class="product-name">Blue Shirt</h1>
        <span class="price">$29.99</span>
        <div class="description">A comfortable blue shirt.</div>
        <div class="specifications">
            <div class="spec">
                <span class="key">Size</span>
                <span class="value">M</span>
            </div>
            <div class="spec">
                <span class="key">Color</span>
                <span class="value">Blue</span>
            </div>
            <div class="spec">
                <span class="key">Material</span>
                <span class="value">Cotton</span>
            </div>
        </div>
    </div>
    """
    
    # Parse the HTML
    product = website_scraper._parse_product_details(html)
    
    # Check the result
    assert product["id"] == "12345"
    assert product["name"] == "Blue Shirt"
    assert product["price"] == "$29.99"
    assert product["description"] == "A comfortable blue shirt."
    assert product["specifications"]["Size"] == "M"
    assert product["specifications"]["Color"] == "Blue"
    assert product["specifications"]["Material"] == "Cotton" 
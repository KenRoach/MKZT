import logging
import json
import time
from typing import List, Optional, Dict, Any, Union
import aiohttp
import aioredis
from prometheus_client import Counter, Histogram, Gauge
from tenacity import retry, stop_after_attempt, wait_exponential
from structlog import get_logger
from src.config.settings import get_settings

# Configure structured logging
logger = get_logger()

# Prometheus metrics
REQUEST_COUNT = Counter('deepseek_requests_total', 'Total number of DeepSeek API requests', ['endpoint'])
REQUEST_LATENCY = Histogram('deepseek_request_latency_seconds', 'DeepSeek API request latency', ['endpoint'])
ERROR_COUNT = Counter('deepseek_errors_total', 'Total number of DeepSeek API errors', ['endpoint', 'error_type'])
TOKEN_USAGE = Counter('deepseek_tokens_total', 'Total number of tokens used', ['endpoint'])
ACTIVE_REQUESTS = Gauge('deepseek_active_requests', 'Number of active requests')

class DeepSeekService:
    def __init__(self):
        settings = get_settings()
        self.api_key = settings.DEEPSEEK_API_KEY
        self.model = settings.DEEPSEEK_MODEL
        self.max_tokens = settings.DEEPSEEK_MAX_TOKENS
        self.temperature = settings.DEEPSEEK_TEMPERATURE
        self.base_url = "https://api.deepseek.com/v1"
        self.redis = None
        self.rate_limit = settings.AI_RATE_LIMIT
        self.cache_ttl = settings.AI_CACHE_TTL
        self.error_threshold = settings.AI_ERROR_THRESHOLD
        self._error_count = 0
        self._last_error_time = 0

    async def initialize(self):
        """Initialize Redis connection for caching"""
        if not self.redis:
            settings = get_settings()
            self.redis = await aioredis.from_url(
                f"redis://{settings.REDIS_HOST}:{settings.REDIS_PORT}/{settings.REDIS_DB}"
            )

    async def close(self):
        """Close Redis connection"""
        if self.redis:
            await self.redis.close()

    def _get_cache_key(self, endpoint: str, params: Dict) -> str:
        """Generate a cache key for the request"""
        return f"deepseek:{endpoint}:{json.dumps(params, sort_keys=True)}"

    async def _check_rate_limit(self) -> bool:
        """Check if we're within rate limits"""
        current_time = time.time()
        if current_time - self._last_error_time > 60:  # Reset error count after 1 minute
            self._error_count = 0
        
        if self._error_count >= self.error_threshold:
            return False
        
        return True

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10))
    async def _make_request(self, endpoint: str, method: str, **kwargs) -> Dict:
        """Make a request to the DeepSeek API with retries and monitoring"""
        if not await self._check_rate_limit():
            raise Exception("Rate limit exceeded")

        ACTIVE_REQUESTS.inc()
        start_time = time.time()
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.request(
                    method,
                    f"{self.base_url}/{endpoint}",
                    headers={
                        "Authorization": f"Bearer {self.api_key}",
                        "Content-Type": "application/json"
                    },
                    **kwargs
                ) as response:
                    if response.status != 200:
                        error_text = await response.text()
                        ERROR_COUNT.labels(endpoint=endpoint, error_type=str(response.status)).inc()
                        self._error_count += 1
                        self._last_error_time = time.time()
                        raise Exception(f"DeepSeek API error: {error_text}")
                    
                    result = await response.json()
                    REQUEST_COUNT.labels(endpoint=endpoint).inc()
                    REQUEST_LATENCY.labels(endpoint=endpoint).observe(time.time() - start_time)
                    
                    if "usage" in result:
                        TOKEN_USAGE.labels(endpoint=endpoint).inc(result["usage"]["total_tokens"])
                    
                    return result

        except Exception as e:
            ERROR_COUNT.labels(endpoint=endpoint, error_type=type(e).__name__).inc()
            raise
        finally:
            ACTIVE_REQUESTS.dec()

    async def generate_text(
        self, 
        prompt: str, 
        system_message: Optional[str] = None,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        use_cache: bool = True
    ) -> str:
        """
        Generate text using DeepSeek's chat completion API with caching.
        
        Args:
            prompt: The user's input prompt
            system_message: Optional system message to set context
            temperature: Optional temperature override
            max_tokens: Optional max tokens override
            use_cache: Whether to use cached responses
            
        Returns:
            Generated text response
        """
        try:
            await self.initialize()
            
            params = {
                "model": self.model,
                "messages": [
                    {"role": "system", "content": system_message} if system_message else None,
                    {"role": "user", "content": prompt}
                ],
                "temperature": temperature or self.temperature,
                "max_tokens": max_tokens or self.max_tokens
            }
            
            # Remove None values
            params["messages"] = [m for m in params["messages"] if m is not None]
            
            if use_cache:
                cache_key = self._get_cache_key("chat/completions", params)
                cached_response = await self.redis.get(cache_key)
                if cached_response:
                    logger.info("cache_hit", endpoint="chat/completions")
                    return json.loads(cached_response)["choices"][0]["message"]["content"]
            
            result = await this._make_request(
                "chat/completions",
                "POST",
                json=params
            )
            
            response_text = result["choices"][0]["message"]["content"]
            
            if use_cache:
                await self.redis.setex(
                    cache_key,
                    self.cache_ttl,
                    json.dumps(result)
                )
            
            return response_text

        except Exception as e:
            logger.error("generate_text_error", error=str(e), prompt=prompt)
            raise

    async def analyze_sentiment(self, text: str, use_cache: bool = True) -> Dict[str, Any]:
        """
        Analyze the sentiment of the given text with caching.
        
        Args:
            text: Text to analyze
            use_cache: Whether to use cached responses
            
        Returns:
            Dictionary containing sentiment analysis results
        """
        try:
            await this.initialize()
            
            if use_cache:
                cache_key = this._get_cache_key("sentiment", {"text": text})
                cached_response = await this.redis.get(cache_key)
                if cached_response:
                    logger.info("cache_hit", endpoint="sentiment")
                    return json.loads(cached_response)
            
            system_message = """
            Analyze the sentiment of the text and return a JSON object with:
            - sentiment: (positive, negative, or neutral)
            - confidence: (float between 0 and 1)
            - key_phrases: (list of important phrases)
            """
            
            response = await this.generate_text(
                prompt=text,
                system_message=system_message,
                temperature=0.3,
                use_cache=False
            )
            
            result = json.loads(response)
            
            if use_cache:
                await this.redis.setex(
                    cache_key,
                    this.cache_ttl,
                    json.dumps(result)
                )
            
            return result

        except Exception as e:
            logger.error("analyze_sentiment_error", error=str(e), text=text)
            raise

    async def moderate_content(self, text: str) -> Dict[str, Any]:
        """
        Check if content violates content policy using DeepSeek's moderation endpoint.
        
        Args:
            text: Text to moderate
            
        Returns:
            Moderation results
        """
        try:
            result = await this._make_request(
                "moderations",
                "POST",
                json={"input": text}
            )
            return result["results"][0]

        except Exception as e:
            logger.error("moderate_content_error", error=str(e), text=text)
            raise

    async def extract_entities(self, text: str, use_cache: bool = True) -> List[Dict[str, Any]]:
        """
        Extract named entities from text with caching.
        
        Args:
            text: Text to analyze
            use_cache: Whether to use cached responses
            
        Returns:
            List of extracted entities with their types
        """
        try:
            await this.initialize()
            
            if use_cache:
                cache_key = this._get_cache_key("entities", {"text": text})
                cached_response = await this.redis.get(cache_key)
                if cached_response:
                    logger.info("cache_hit", endpoint="entities")
                    return json.loads(cached_response)
            
            system_message = """
            Extract named entities from the text and return a JSON array of objects with:
            - entity: (the entity text)
            - type: (person, organization, location, date, etc.)
            - confidence: (float between 0 and 1)
            """
            
            response = await this.generate_text(
                prompt=text,
                system_message=system_message,
                temperature=0.2,
                use_cache=False
            )
            
            result = json.loads(response)
            
            if use_cache:
                await this.redis.setex(
                    cache_key,
                    this.cache_ttl,
                    json.dumps(result)
                )
            
            return result

        except Exception as e:
            logger.error("extract_entities_error", error=str(e), text=text)
            raise

    async def generate_embeddings(self, text: str) -> List[float]:
        """
        Generate embeddings for the given text.
        
        Args:
            text: Text to generate embeddings for
            
        Returns:
            List of embedding values
        """
        try:
            result = await this._make_request(
                "embeddings",
                "POST",
                json={
                    "model": "deepseek-embedding",
                    "input": text
                }
            )
            return result["data"][0]["embedding"]

        except Exception as e:
            logger.error("generate_embeddings_error", error=str(e), text=text)
            raise

    async def classify_text(self, text: str, categories: List[str]) -> Dict[str, float]:
        """
        Classify text into predefined categories.
        
        Args:
            text: Text to classify
            categories: List of possible categories
            
        Returns:
            Dictionary mapping categories to confidence scores
        """
        try:
            system_message = f"""
            Classify the text into one or more of these categories: {', '.join(categories)}
            Return a JSON object with category names as keys and confidence scores (0-1) as values.
            """
            
            response = await this.generate_text(
                prompt=text,
                system_message=system_message,
                temperature=0.1
            )
            
            return json.loads(response)

        except Exception as e:
            logger.error("classify_text_error", error=str(e), text=text, categories=categories)
            raise

# Create a singleton instance
deepseek_service = DeepSeekService() 
import json
import logging
from typing import Any, Optional

import redis.asyncio as redis
from app.core.config import settings

logger = logging.getLogger(__name__)

class RedisCache:
    def __init__(self):
        """Initialize Redis connection."""
        try:
            self.redis = redis.from_url(
                f"redis://{settings.REDIS_HOST}:{settings.REDIS_PORT}",
                password=settings.REDIS_PASSWORD,
                db=settings.REDIS_DB,
                encoding="utf-8",
                decode_responses=True,
            )
            logger.info("Redis cache initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize Redis cache: {e}")
            raise

    async def get(self, key: str) -> Optional[Any]:
        """Get value from cache by key.
        
        Args:
            key: Cache key to retrieve.
            
        Returns:
            Optional[Any]: Cached value if exists, None otherwise.
        """
        try:
            value = await self.redis.get(key)
            if value:
                return json.loads(value)
            return None
        except Exception as e:
            logger.error(f"Error getting value from cache for key {key}: {e}")
            return None

    async def set(self, key: str, value: Any, expire: Optional[int] = None) -> bool:
        """Set value in cache with optional expiration.
        
        Args:
            key: Cache key to set.
            value: Value to cache.
            expire: Optional expiration time in seconds.
            
        Returns:
            bool: True if successful, False otherwise.
        """
        try:
            if expire is None:
                expire = settings.REDIS_CACHE_EXPIRE_MINUTES * 60
            await self.redis.set(key, json.dumps(value), ex=expire)
            return True
        except Exception as e:
            logger.error(f"Error setting value in cache for key {key}: {e}")
            return False

    async def delete(self, key: str) -> bool:
        """Delete value from cache by key.
        
        Args:
            key: Cache key to delete.
            
        Returns:
            bool: True if successful, False otherwise.
        """
        try:
            await self.redis.delete(key)
            return True
        except Exception as e:
            logger.error(f"Error deleting value from cache for key {key}: {e}")
            return False

    async def exists(self, key: str) -> bool:
        """Check if key exists in cache.
        
        Args:
            key: Cache key to check.
            
        Returns:
            bool: True if key exists, False otherwise.
        """
        try:
            return await self.redis.exists(key) > 0
        except Exception as e:
            logger.error(f"Error checking if key exists in cache: {key}: {e}")
            return False

    async def clear(self) -> bool:
        """Clear all cache.
        
        Returns:
            bool: True if successful, False otherwise.
        """
        try:
            await self.redis.flushdb()
            return True
        except Exception as e:
            logger.error(f"Error clearing cache: {e}")
            return False

# Create a singleton instance
cache = RedisCache() 
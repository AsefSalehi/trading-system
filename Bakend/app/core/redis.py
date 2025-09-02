import redis.asyncio as redis
from typing import Optional, Any
import json
from datetime import timedelta

from app.core.config import settings
from app.core.logging import logger


class RedisClient:
    def __init__(self):
        self.redis: Optional[redis.Redis] = None
    
    async def connect(self):
        """Connect to Redis"""
        try:
            self.redis = redis.from_url(
                settings.REDIS_URL,
                encoding="utf-8",
                decode_responses=True
            )
            # Test connection
            await self.redis.ping()
            logger.info("Successfully connected to Redis")
        except Exception as e:
            logger.error(f"Failed to connect to Redis: {e}")
            raise
    
    async def disconnect(self):
        """Disconnect from Redis"""
        if self.redis:
            await self.redis.close()
            logger.info("Disconnected from Redis")
    
    async def get(self, key: str) -> Optional[Any]:
        """Get value from Redis"""
        try:
            if not self.redis:
                await self.connect()
            
            value = await self.redis.get(key)
            if value:
                return json.loads(value)
            return None
        except Exception as e:
            logger.error(f"Error getting key {key} from Redis: {e}")
            return None
    
    async def set(
        self, 
        key: str, 
        value: Any, 
        expire: Optional[timedelta] = None
    ) -> bool:
        """Set value in Redis"""
        try:
            if not self.redis:
                await self.connect()
            
            json_value = json.dumps(value, default=str)
            result = await self.redis.set(key, json_value)
            
            if expire:
                await self.redis.expire(key, int(expire.total_seconds()))
            
            return result
        except Exception as e:
            logger.error(f"Error setting key {key} in Redis: {e}")
            return False
    
    async def delete(self, key: str) -> bool:
        """Delete key from Redis"""
        try:
            if not self.redis:
                await self.connect()
            
            result = await self.redis.delete(key)
            return bool(result)
        except Exception as e:
            logger.error(f"Error deleting key {key} from Redis: {e}")
            return False
    
    async def exists(self, key: str) -> bool:
        """Check if key exists in Redis"""
        try:
            if not self.redis:
                await self.connect()
            
            result = await self.redis.exists(key)
            return bool(result)
        except Exception as e:
            logger.error(f"Error checking key {key} existence in Redis: {e}")
            return False


# Global Redis client instance
redis_client = RedisClient()
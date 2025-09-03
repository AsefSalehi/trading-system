from functools import wraps
from typing import Optional, Any, Callable
from datetime import timedelta
import hashlib
import json

from app.core.redis import redis_client
from app.core.logging import logger


def cache_key_builder(*args, **kwargs) -> str:
    """Build cache key from function arguments"""
    # Create a hash of the arguments
    key_data = {"args": args, "kwargs": kwargs}
    key_string = json.dumps(key_data, sort_keys=True, default=str)
    key_hash = hashlib.md5(key_string.encode()).hexdigest()
    return key_hash


def cache(
    expire: timedelta = timedelta(minutes=5), key_prefix: str = "cache"
) -> Callable:
    """
    Decorator for caching function results in Redis

    Args:
        expire: Cache expiration time
        key_prefix: Prefix for cache keys
    """

    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def wrapper(*args, **kwargs) -> Any:
            # Build cache key
            cache_key = (
                f"{key_prefix}:{func.__name__}:{cache_key_builder(*args, **kwargs)}"
            )

            try:
                # Try to get from cache
                cached_result = await redis_client.get(cache_key)
                if cached_result is not None:
                    logger.debug(f"Cache hit for key: {cache_key}")
                    return cached_result

                # Cache miss - execute function
                logger.debug(f"Cache miss for key: {cache_key}")
                result = await func(*args, **kwargs)

                # Store in cache
                await redis_client.set(cache_key, result, expire)
                return result

            except Exception as e:
                logger.error(f"Cache error for key {cache_key}: {e}")
                # Fallback to executing function without cache
                return await func(*args, **kwargs)

        return wrapper

    return decorator


async def invalidate_cache_pattern(pattern: str) -> bool:
    """
    Invalidate cache keys matching a pattern

    Args:
        pattern: Redis key pattern (e.g., "crypto:*")
    """
    try:
        if not redis_client.redis:
            await redis_client.connect()

        # Get all keys matching pattern
        keys = await redis_client.redis.keys(pattern)
        if keys:
            # Delete all matching keys
            await redis_client.redis.delete(*keys)
            logger.info(
                f"Invalidated {len(keys)} cache keys matching pattern: {pattern}"
            )
            return True
        return True
    except Exception as e:
        logger.error(f"Error invalidating cache pattern {pattern}: {e}")
        return False

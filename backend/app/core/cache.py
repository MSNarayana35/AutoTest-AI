"""
Caching utilities for API responses
"""
import json
from typing import Optional, Any
from functools import wraps
import hashlib

# Simple in-memory cache (can be replaced with Redis in production)
_cache_store = {}

class Cache:
    """Simple cache implementation with TTL support"""
    
    @staticmethod
    def get(key: str) -> Optional[Any]:
        """Get value from cache"""
        if key in _cache_store:
            return _cache_store[key]
        return None
    
    @staticmethod
    def set(key: str, value: Any, ttl: int = 300) -> None:
        """Set value in cache with TTL (default 5 minutes)"""
        _cache_store[key] = value
        # In production, implement TTL with Redis or similar
    
    @staticmethod
    def delete(key: str) -> None:
        """Delete value from cache"""
        if key in _cache_store:
            del _cache_store[key]
    
    @staticmethod
    def delete_pattern(pattern: str) -> None:
        """Delete all keys matching pattern"""
        keys_to_delete = [k for k in _cache_store.keys() if pattern in k]
        for key in keys_to_delete:
            del _cache_store[key]
    
    @staticmethod
    def clear() -> None:
        """Clear all cache"""
        _cache_store.clear()


def cache_key(*args, **kwargs) -> str:
    """Generate cache key from arguments"""
    key_data = f"{args}_{kwargs}"
    return hashlib.md5(key_data.encode()).hexdigest()


def cached(ttl: int = 300, key_prefix: str = ""):
    """
    Decorator to cache function results
    
    Args:
        ttl: Time to live in seconds (default 5 minutes)
        key_prefix: Prefix for cache key
    """
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Generate cache key
            cache_key_str = f"{key_prefix}:{func.__name__}:{cache_key(*args, **kwargs)}"
            
            # Try to get from cache
            cached_value = Cache.get(cache_key_str)
            if cached_value is not None:
                return cached_value
            
            # Call function and cache result
            result = await func(*args, **kwargs)
            Cache.set(cache_key_str, result, ttl)
            return result
        
        return wrapper
    return decorator


def invalidate_cache(pattern: str):
    """Invalidate cache entries matching pattern"""
    Cache.delete_pattern(pattern)


# Cache invalidation helpers
def invalidate_project_cache(project_id: int):
    """Invalidate all cache entries for a project"""
    Cache.delete_pattern(f"project:{project_id}")
    Cache.delete_pattern("dashboard")  # Dashboard shows aggregated stats


def invalidate_dashboard_cache():
    """Invalidate dashboard cache"""
    Cache.delete_pattern("dashboard")

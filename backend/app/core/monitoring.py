"""
Performance monitoring and logging utilities
"""
import time
import logging
from functools import wraps
from typing import Callable
from datetime import datetime

# Configure logger
logger = logging.getLogger("autotest_performance")
logger.setLevel(logging.INFO)

# File handler for performance logs
handler = logging.FileHandler("performance.log")
handler.setFormatter(logging.Formatter(
    '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
))
logger.addHandler(handler)


def log_performance(threshold_ms: float = 1000):
    """
    Decorator to log slow operations
    
    Args:
        threshold_ms: Log operations slower than this (milliseconds)
    """
    def decorator(func: Callable):
        @wraps(func)
        async def async_wrapper(*args, **kwargs):
            start = time.time()
            try:
                result = await func(*args, **kwargs)
                elapsed_ms = (time.time() - start) * 1000
                
                if elapsed_ms > threshold_ms:
                    logger.warning(
                        f"SLOW: {func.__name__} took {elapsed_ms:.2f}ms "
                        f"(threshold: {threshold_ms}ms)"
                    )
                else:
                    logger.info(f"{func.__name__} completed in {elapsed_ms:.2f}ms")
                
                return result
            except Exception as e:
                elapsed_ms = (time.time() - start) * 1000
                logger.error(
                    f"ERROR in {func.__name__} after {elapsed_ms:.2f}ms: {str(e)}"
                )
                raise
        
        @wraps(func)
        def sync_wrapper(*args, **kwargs):
            start = time.time()
            try:
                result = func(*args, **kwargs)
                elapsed_ms = (time.time() - start) * 1000
                
                if elapsed_ms > threshold_ms:
                    logger.warning(
                        f"SLOW: {func.__name__} took {elapsed_ms:.2f}ms "
                        f"(threshold: {threshold_ms}ms)"
                    )
                else:
                    logger.info(f"{func.__name__} completed in {elapsed_ms:.2f}ms")
                
                return result
            except Exception as e:
                elapsed_ms = (time.time() - start) * 1000
                logger.error(
                    f"ERROR in {func.__name__} after {elapsed_ms:.2f}ms: {str(e)}"
                )
                raise
        
        # Return appropriate wrapper based on function type
        import asyncio
        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        return sync_wrapper
    
    return decorator


class PerformanceMetrics:
    """Track performance metrics in memory"""
    
    def __init__(self):
        self.metrics = {}
    
    def record(self, operation: str, duration_ms: float):
        """Record an operation's duration"""
        if operation not in self.metrics:
            self.metrics[operation] = {
                'count': 0,
                'total_ms': 0,
                'min_ms': float('inf'),
                'max_ms': 0,
                'avg_ms': 0
            }
        
        m = self.metrics[operation]
        m['count'] += 1
        m['total_ms'] += duration_ms
        m['min_ms'] = min(m['min_ms'], duration_ms)
        m['max_ms'] = max(m['max_ms'], duration_ms)
        m['avg_ms'] = m['total_ms'] / m['count']
    
    def get_stats(self, operation: str = None):
        """Get statistics for an operation or all operations"""
        if operation:
            return self.metrics.get(operation, {})
        return self.metrics
    
    def reset(self):
        """Reset all metrics"""
        self.metrics.clear()


# Global metrics instance
metrics = PerformanceMetrics()


def track_time(operation: str):
    """Context manager to track operation time"""
    class Timer:
        def __enter__(self):
            self.start = time.time()
            return self
        
        def __exit__(self, *args):
            elapsed_ms = (time.time() - self.start) * 1000
            metrics.record(operation, elapsed_ms)
            logger.info(f"{operation}: {elapsed_ms:.2f}ms")
    
    return Timer()


# Middleware for request timing
class PerformanceMiddleware:
    """ASGI middleware to track request performance"""
    
    def __init__(self, app):
        self.app = app
    
    async def __call__(self, scope, receive, send):
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return
        
        start = time.time()
        
        async def send_wrapper(message):
            if message["type"] == "http.response.start":
                elapsed_ms = (time.time() - start) * 1000
                path = scope.get("path", "unknown")
                method = scope.get("method", "unknown")
                
                # Log slow requests
                if elapsed_ms > 500:
                    logger.warning(
                        f"SLOW REQUEST: {method} {path} took {elapsed_ms:.2f}ms"
                    )
                
                metrics.record(f"{method} {path}", elapsed_ms)
            
            await send(message)
        
        await self.app(scope, receive, send_wrapper)

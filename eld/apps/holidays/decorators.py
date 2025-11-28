from functools import wraps
from django.core.cache import cache
from django.http import JsonResponse
import hashlib
import json

def cache_view(timeout=300, key_prefix='view'):
    """
    Decorator to cache view results in Redis
    
    Usage:
        @cache_view(timeout=3600, key_prefix='holidays')
        def my_view(request):
            ...
    """
    def decorator(view_func):
        @wraps(view_func)
        def wrapper(request, *args, **kwargs):
            # Build cache key from request parameters
            cache_key_parts = [
                key_prefix,
                request.path,
                request.GET.urlencode(),
                str(request.user.id if request.user.is_authenticated else 'anon')
            ]
            cache_key = hashlib.md5(''.join(cache_key_parts).encode()).hexdigest()
            
            # Try to get from cache
            cached_response = cache.get(cache_key)
            if cached_response is not None:
                return cached_response
            
            # Generate response
            response = view_func(request, *args, **kwargs)
            
            # Cache the response
            cache.set(cache_key, response, timeout)
            
            return response
        return wrapper
    return decorator

def cache_queryset(timeout=300, key_prefix='qs'):
    """
    Decorator to cache queryset results
    
    Usage:
        @cache_queryset(timeout=1800, key_prefix='holidays_list')
        def get_holidays(country=None, year=None):
            ...
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Build cache key from function args
            key_parts = [key_prefix, func.__name__]
            key_parts.extend([str(arg) for arg in args])
            key_parts.extend([f"{k}={v}" for k, v in sorted(kwargs.items())])
            
            cache_key = hashlib.md5(''.join(key_parts).encode()).hexdigest()
            
            # Try cache
            cached_result = cache.get(cache_key)
            if cached_result is not None:
                return cached_result
            
            # Execute function
            result = func(*args, **kwargs)
            
            # Cache result
            cache.set(cache_key, result, timeout)
            
            return result
        return wrapper
    return decorator

def invalidate_cache(pattern):
    """
    Invalidate all cache keys matching a pattern
    
    Usage:
        invalidate_cache('holidays_*')
    """
    # Note: This is a simplified version. For production,
    # consider using django-redis which supports pattern deletion
    try:
        from django_redis import get_redis_connection
        conn = get_redis_connection("default")
        keys = conn.keys(pattern)
        if keys:
            conn.delete(*keys)
        return len(keys)
    except ImportError:
        # Fallback: clear entire cache
        cache.clear()
        return 0
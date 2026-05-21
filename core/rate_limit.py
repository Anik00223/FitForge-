import time
from django.core.cache import cache
from functools import wraps
from django.http import JsonResponse

def rate_limit(key_prefix, limit, window):
    """
    Simple rate limiter using Django cache.
    Limits requests to `limit` per `window` seconds.
    """
    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(request, *args, **kwargs):
            if not request.user.is_authenticated:
                return JsonResponse({"error": "Unauthorized"}, status=401)
                
            cache_key = f"rate_limit_{key_prefix}_{request.user.id}"
            
            # Get current requests in window
            requests = cache.get(cache_key, [])
            now = time.time()
            
            # Clean up old requests
            requests = [req_time for req_time in requests if now - req_time < window]
            
            if len(requests) >= limit:
                return JsonResponse(
                    {"error": f"Rate limit exceeded. Try again in {window} seconds."}, 
                    status=429
                )
                
            requests.append(now)
            cache.set(cache_key, requests, window)
            
            return view_func(request, *args, **kwargs)
        return _wrapped_view
    return decorator

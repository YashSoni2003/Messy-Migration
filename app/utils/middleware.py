from functools import wraps
from flask import request, jsonify
import time
from collections import defaultdict, deque

class SimpleRateLimiter:
    """Simple in-memory rate limiter."""
    
    def __init__(self, max_requests=100, window_seconds=60):
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self.requests = defaultdict(deque)
    
    def is_allowed(self, client_id):
        """Check if request is allowed for client."""
        now = time.time()
        client_requests = self.requests[client_id]
        
        while client_requests and client_requests[0] < now - self.window_seconds:
            client_requests.popleft()
        
        if len(client_requests) >= self.max_requests:
            return False
        
    
        client_requests.append(now)
        return True

rate_limiter = SimpleRateLimiter()

def rate_limit(max_requests=10, window_seconds=60):
    """Rate limiting decorator."""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            client_id = request.remote_addr
            
            if not rate_limiter.is_allowed(client_id):
                return jsonify({
                    'success': False,
                    'error': 'Rate limit exceeded. Please try again later.',
                    'retry_after': window_seconds
                }), 429
            
            return f(*args, **kwargs)
        return decorated_function
    return decorator

def validate_json_request():
    """Validate that request contains valid JSON."""
    if not request.is_json:
        return jsonify({
            'success': False,
            'error': 'Content-Type must be application/json'
        }), 400
    
    try:
        request.get_json()
        return None
    except Exception:
        return jsonify({
            'success': False,
            'error': 'Invalid JSON in request body'
        }), 400

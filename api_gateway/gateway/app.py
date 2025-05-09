"""
API Gateway Implementation with Python and Flask

This module demonstrates how to build a simple API gateway that routes requests
to multiple backend services. It handles authentication, request routing, load balancing,
and response caching.

Key Concepts:
- API routing and proxying
- Request transformation
- Response caching
- Authentication and authorization
- Rate limiting
- Service discovery (simulated)
"""

from flask import Flask, request, jsonify, Response
import requests
import json
import time
import os
import hashlib
import random
import threading
import logging
from functools import wraps
from werkzeug.contrib.cache import SimpleCache

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('api_gateway')

# Initialize Flask application
app = Flask(__name__)

# Configuration
class Config:
    # API key for gateway access (in production use a secure secret manager)
    API_KEY = os.getenv('API_KEY', 'test-api-key')
    
    # Cache settings
    CACHE_ENABLED = True
    CACHE_TIMEOUT = 300  # 5 minutes
    
    # Rate limiting
    RATE_LIMIT_ENABLED = True
    RATE_LIMIT_WINDOW = 60  # 1 minute window
    RATE_LIMIT_MAX_REQUESTS = 100  # max 100 requests per minute
    
    # Service discovery (simulated)
    SERVICES = {
        'user_service': ['http://localhost:8001', 'http://localhost:8002'],
        'product_service': ['http://localhost:8011', 'http://localhost:8012'],
        'order_service': ['http://localhost:8021', 'http://localhost:8022']
    }

# Initialize cache
cache = SimpleCache()

# In-memory rate limiting storage
# In production, use Redis or another distributed store
rate_limits = {}
rate_limit_lock = threading.Lock()

# --- Middleware and Decorators ---

def require_api_key(f):
    """Decorator to require API key for access."""
    @wraps(f)
    def decorated(*args, **kwargs):
        api_key = request.headers.get('X-API-Key')
        
        if not api_key or api_key != Config.API_KEY:
            return jsonify({'error': 'Invalid or missing API key'}), 401
            
        return f(*args, **kwargs)
    return decorated

def rate_limit(f):
    """Decorator to apply rate limiting."""
    @wraps(f)
    def decorated(*args, **kwargs):
        if not Config.RATE_LIMIT_ENABLED:
            return f(*args, **kwargs)
        
        # Get client identifier (IP or API key if available)
        client_id = request.headers.get('X-API-Key', request.remote_addr)
        
        with rate_limit_lock:
            # Initialize or get current rate limit data for client
            now = int(time.time())
            window_start = now - Config.RATE_LIMIT_WINDOW
            
            if client_id in rate_limits:
                # Clean up old requests
                rate_limits[client_id] = [ts for ts in rate_limits[client_id] if ts > window_start]
                request_count = len(rate_limits[client_id])
            else:
                rate_limits[client_id] = []
                request_count = 0
            
            # Check if rate limit exceeded
            if request_count >= Config.RATE_LIMIT_MAX_REQUESTS:
                return jsonify({
                    'error': 'Rate limit exceeded',
                    'limit': Config.RATE_LIMIT_MAX_REQUESTS,
                    'window': Config.RATE_LIMIT_WINDOW,
                    'retry_after': Config.RATE_LIMIT_WINDOW - (now - min(rate_limits[client_id]))
                }), 429
            
            # Record this request
            rate_limits[client_id].append(now)
        
        # Add rate limit headers to response
        response = f(*args, **kwargs)
        
        if isinstance(response, tuple):
            response_obj, status_code = response
            headers = {}
        else:
            response_obj = response
            status_code = 200
            headers = {}
        
        if isinstance(response_obj, Response):
            response_obj.headers['X-RateLimit-Limit'] = str(Config.RATE_LIMIT_MAX_REQUESTS)
            response_obj.headers['X-RateLimit-Remaining'] = str(Config.RATE_LIMIT_MAX_REQUESTS - request_count - 1)
            response_obj.headers['X-RateLimit-Reset'] = str(now + Config.RATE_LIMIT_WINDOW)
            return response_obj
        
        headers['X-RateLimit-Limit'] = str(Config.RATE_LIMIT_MAX_REQUESTS)
        headers['X-RateLimit-Remaining'] = str(Config.RATE_LIMIT_MAX_REQUESTS - request_count - 1)
        headers['X-RateLimit-Reset'] = str(now + Config.RATE_LIMIT_WINDOW)
        
        if isinstance(response, tuple) and len(response) == 2:
            return response_obj, status_code, headers
        return response_obj, 200, headers
    
    return decorated

# --- Helper Functions ---

def get_cache_key(service, path, query_string, headers=None):
    """Generate a cache key from request details."""
    cache_key_parts = [service, path, query_string]
    
    # Include relevant headers in cache key if specified
    if headers:
        for header in headers:
            value = request.headers.get(header)
            if value:
                cache_key_parts.append(f"{header}:{value}")
    
    # Create a hash of all parts for the cache key
    key = hashlib.md5(json.dumps(cache_key_parts).encode()).hexdigest()
    return f"apigw:{key}"

def get_service_url(service):
    """Get a backend service URL with basic load balancing."""
    if service not in Config.SERVICES:
        return None
    
    service_urls = Config.SERVICES[service]
    
    if not service_urls:
        return None
    
    # Simple round-robin load balancing
    # In production, use a more sophisticated approach or a service mesh
    return random.choice(service_urls)

def forward_request(service, path, method, headers=None, data=None, params=None):
    """Forward a request to a backend service."""
    service_url = get_service_url(service)
    
    if not service_url:
        return jsonify({'error': f'Service {service} not found'}), 404
    
    url = f"{service_url}/{path.lstrip('/')}"
    
    # Prepare headers
    request_headers = {}
    if headers:
        for header in headers:
            value = request.headers.get(header)
            if value:
                request_headers[header] = value
    
    # Add gateway identifier
    request_headers['X-Gateway-Source'] = 'api-gateway'
    
    try:
        # Forward the request to the service
        response = requests.request(
            method=method,
            url=url,
            headers=request_headers,
            params=params or request.args,
            json=data
        )
        
        # Prepare response
        gateway_response = Response(
            response.content,
            status=response.status_code,
            content_type=response.headers.get('Content-Type', 'application/json')
        )
        
        # Forward relevant headers
        for header in ['Content-Type', 'Content-Length', 'Content-Language', 'ETag']:
            if header in response.headers:
                gateway_response.headers[header] = response.headers[header]
        
        return gateway_response
    
    except requests.RequestException as e:
        logger.error(f"Error forwarding request to {service}: {str(e)}")
        return jsonify({
            'error': 'Service unavailable',
            'message': str(e)
        }), 503

# --- API Routes ---

@app.route('/health')
def health_check():
    """API Gateway health check endpoint"""
    return jsonify({
        'status': 'ok',
        'message': 'API Gateway is running'
    })

@app.route('/api/<service>/<path:path>', methods=['GET', 'POST', 'PUT', 'DELETE', 'PATCH'])
@require_api_key
@rate_limit
def api_gateway(service, path):
    """Main API Gateway route that handles all service requests"""
    method = request.method
    logger.info(f"{method} request to /{service}/{path}")
    
    # Check if the service exists in our service registry
    if service not in Config.SERVICES:
        return jsonify({'error': f'Service {service} not found'}), 404
    
    # For cacheable requests (GET)
    if method == 'GET' and Config.CACHE_ENABLED:
        # Generate cache key
        cache_key = get_cache_key(service, path, request.query_string.decode('utf-8'))
        
        # Check cache
        cached_response = cache.get(cache_key)
        if cached_response:
            logger.info(f"Cache hit for {cache_key}")
            return jsonify(cached_response)
    
    # Handle request based on method
    if method == 'GET':
        response = forward_request(
            service=service,
            path=path,
            method=method,
            headers=['Authorization', 'Accept', 'Accept-Language'],
            params=request.args
        )
        
        # Cache successful GET responses
        if Config.CACHE_ENABLED and response.status_code == 200:
            try:
                response_data = json.loads(response.data)
                cache_key = get_cache_key(service, path, request.query_string.decode('utf-8'))
                cache.set(cache_key, response_data, timeout=Config.CACHE_TIMEOUT)
                logger.info(f"Cached response for {cache_key}")
            except (json.JSONDecodeError, TypeError) as e:
                logger.error(f"Failed to cache response: {str(e)}")
        
        return response
    
    elif method in ['POST', 'PUT', 'PATCH']:
        # For data modification requests
        json_data = request.get_json(silent=True)
        return forward_request(
            service=service,
            path=path,
            method=method,
            headers=['Authorization', 'Content-Type'],
            data=json_data
        )
    
    elif method == 'DELETE':
        # For deletion requests
        return forward_request(
            service=service,
            path=path,
            method=method,
            headers=['Authorization']
        )
    
    # Method not allowed
    return jsonify({'error': 'Method not allowed'}), 405

# --- Admin Routes ---

@app.route('/admin/cache/clear', methods=['POST'])
@require_api_key
def clear_cache():
    """Clear the API Gateway cache"""
    if not Config.CACHE_ENABLED:
        return jsonify({'message': 'Cache is disabled'}), 200
    
    cache.clear()
    return jsonify({'message': 'Cache cleared successfully'})

@app.route('/admin/services', methods=['GET'])
@require_api_key
def list_services():
    """List all registered services"""
    return jsonify({
        'services': Config.SERVICES
    })

@app.route('/admin/rate-limits', methods=['GET'])
@require_api_key
def list_rate_limits():
    """List current rate limit data"""
    if not Config.RATE_LIMIT_ENABLED:
        return jsonify({'message': 'Rate limiting is disabled'}), 200
    
    result = {}
    with rate_limit_lock:
        for client_id, timestamps in rate_limits.items():
            # Only include requests within the current window
            now = int(time.time())
            window_start = now - Config.RATE_LIMIT_WINDOW
            current_requests = [ts for ts in timestamps if ts > window_start]
            
            if current_requests:
                result[client_id] = {
                    'request_count': len(current_requests),
                    'remaining': max(0, Config.RATE_LIMIT_MAX_REQUESTS - len(current_requests)),
                    'reset': window_start + Config.RATE_LIMIT_WINDOW
                }
    
    return jsonify({
        'rate_limits': result,
        'config': {
            'window': Config.RATE_LIMIT_WINDOW,
            'max_requests': Config.RATE_LIMIT_MAX_REQUESTS
        }
    })

# --- Documentation Routes ---

@app.route('/')
def api_documentation():
    """API Gateway documentation page"""
    return jsonify({
        'name': 'Python API Gateway',
        'version': '1.0.0',
        'description': 'A simple API Gateway built with Python and Flask',
        'endpoints': {
            '/api/{service}/{path}': 'Main gateway endpoint that proxies requests to backend services',
            '/health': 'Health check endpoint',
            '/admin/cache/clear': 'Clear the API Gateway cache',
            '/admin/services': 'List all registered services',
            '/admin/rate-limits': 'List current rate limit data'
        },
        'services': list(Config.SERVICES.keys())
    })

# --- Error Handlers ---

@app.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Resource not found'}), 404

@app.errorhandler(500)
def server_error(error):
    logger.error(f"Server error: {str(error)}")
    return jsonify({'error': 'Internal server error'}), 500

# --- Run the application ---

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    
    print(f"Starting API Gateway on port {port}...")
    print(f"Available services: {', '.join(Config.SERVICES.keys())}")
    
    # In production, use a production-ready server like Gunicorn
    app.run(host='0.0.0.0', port=port, debug=True)

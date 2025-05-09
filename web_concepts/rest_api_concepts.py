"""
REST API Concepts in Python

This module demonstrates the core REST API concepts in Python using Flask.
REST (Representational State Transfer) is an architectural style for designing networked applications.

Key Concepts:
- RESTful architecture principles
- Resource-based routing
- HTTP methods for CRUD operations
- JSON data format
- Status codes
- API versioning
- Basic authentication
- API documentation
"""

from flask import Flask, jsonify, request, make_response
from functools import wraps
import uuid
import datetime
import base64

# Create Flask application
app = Flask(__name__)

# --- Mock Database ---
# In a real application, you would use a proper database
users_db = {
    "1": {"id": "1", "username": "alice", "email": "alice@example.com", "role": "admin", "created_at": "2023-01-01T10:00:00Z"},
    "2": {"id": "2", "username": "bob", "email": "bob@example.com", "role": "user", "created_at": "2023-01-02T11:30:00Z"},
    "3": {"id": "3", "username": "charlie", "email": "charlie@example.com", "role": "user", "created_at": "2023-01-03T09:15:00Z"}
}

products_db = {
    "1": {"id": "1", "name": "Laptop", "price": 999.99, "category": "electronics", "in_stock": True},
    "2": {"id": "2", "name": "Smartphone", "price": 499.99, "category": "electronics", "in_stock": True},
    "3": {"id": "3", "name": "Headphones", "price": 99.99, "category": "accessories", "in_stock": False}
}

# --- Authentication ---

def require_auth(f):
    """Basic authentication decorator for API endpoints."""
    @wraps(f)
    def decorated(*args, **kwargs):
        # Check for Authorization header
        auth_header = request.headers.get('Authorization')
        
        if not auth_header or not auth_header.startswith('Basic '):
            return jsonify({'error': 'Authentication required'}), 401
        
        # Decode credentials
        try:
            encoded_credentials = auth_header[6:]  # Remove 'Basic ' prefix
            decoded_credentials = base64.b64decode(encoded_credentials).decode('utf-8')
            username, password = decoded_credentials.split(':')
            
            # Simple authentication check (in a real app, check against database)
            # For demo purposes, accept 'admin:password' only
            if username != 'admin' or password != 'password':
                return jsonify({'error': 'Invalid credentials'}), 401
            
        except Exception:
            return jsonify({'error': 'Invalid authorization header'}), 401
        
        return f(*args, **kwargs)
    return decorated

# --- API Routes ---

# Root endpoint
@app.route('/api/v1')
def api_root():
    """Root endpoint with API information."""
    return jsonify({
        'name': 'REST API Demo',
        'version': '1.0',
        'description': 'Demonstrating REST API concepts with Python',
        'endpoints': [
            '/api/v1/users',
            '/api/v1/users/<id>',
            '/api/v1/products',
            '/api/v1/products/<id>'
        ]
    })

# --- User Resource Endpoints ---

# List all users (GET)
@app.route('/api/v1/users', methods=['GET'])
def get_users():
    """
    Get all users with optional filtering.
    
    Query Parameters:
    - role: Filter users by role (e.g., ?role=admin)
    - sort: Sort users by field (e.g., ?sort=username)
    - order: Sort order, 'asc' or 'desc' (default: asc)
    """
    users = list(users_db.values())
    
    # Filter by role if provided
    role_filter = request.args.get('role')
    if role_filter:
        users = [user for user in users if user['role'] == role_filter]
    
    # Sort if requested
    sort_by = request.args.get('sort')
    if sort_by and sort_by in users[0].keys():
        order = request.args.get('order', 'asc')
        reverse = (order.lower() == 'desc')
        users = sorted(users, key=lambda user: user[sort_by], reverse=reverse)
    
    return jsonify({
        'count': len(users),
        'results': users
    })

# Get a specific user (GET)
@app.route('/api/v1/users/<user_id>', methods=['GET'])
def get_user(user_id):
    """Get a specific user by ID."""
    user = users_db.get(user_id)
    if not user:
        return jsonify({'error': 'User not found'}), 404
    
    return jsonify(user)

# Create a new user (POST)
@app.route('/api/v1/users', methods=['POST'])
@require_auth
def create_user():
    """
    Create a new user.
    
    Required fields:
    - username: string
    - email: string
    
    Optional fields:
    - role: string (default: 'user')
    """
    # Get request data
    data = request.get_json()
    
    # Validate required fields
    if not data or 'username' not in data or 'email' not in data:
        return jsonify({'error': 'Missing required fields: username and email'}), 400
    
    # Generate new user ID
    user_id = str(len(users_db) + 1)
    
    # Check if username already exists
    for existing_user in users_db.values():
        if existing_user['username'] == data['username']:
            return jsonify({'error': 'Username already exists'}), 409
    
    # Create new user
    new_user = {
        'id': user_id,
        'username': data['username'],
        'email': data['email'],
        'role': data.get('role', 'user'),  # Default role is 'user'
        'created_at': datetime.datetime.now().isoformat() + 'Z'
    }
    
    # Add to database
    users_db[user_id] = new_user
    
    # Return newly created user with 201 Created status
    return jsonify(new_user), 201, {'Location': f'/api/v1/users/{user_id}'}

# Update a user (PUT)
@app.route('/api/v1/users/<user_id>', methods=['PUT'])
@require_auth
def update_user(user_id):
    """
    Update a user (complete replacement).
    
    Required fields:
    - username: string
    - email: string
    - role: string
    """
    # Check if user exists
    if user_id not in users_db:
        return jsonify({'error': 'User not found'}), 404
    
    # Get request data
    data = request.get_json()
    
    # Validate required fields
    if not data or 'username' not in data or 'email' not in data or 'role' not in data:
        return jsonify({'error': 'Missing required fields: username, email, and role'}), 400
    
    # Check if username is being changed to one that already exists
    if data['username'] != users_db[user_id]['username']:
        for existing_user in users_db.values():
            if existing_user['username'] == data['username'] and existing_user['id'] != user_id:
                return jsonify({'error': 'Username already exists'}), 409
    
    # Update user
    users_db[user_id] = {
        'id': user_id,
        'username': data['username'],
        'email': data['email'],
        'role': data['role'],
        'created_at': users_db[user_id]['created_at']  # Preserve creation date
    }
    
    return jsonify(users_db[user_id])

# Partially update a user (PATCH)
@app.route('/api/v1/users/<user_id>', methods=['PATCH'])
@require_auth
def patch_user(user_id):
    """
    Partially update a user.
    
    Optional fields (at least one required):
    - username: string
    - email: string
    - role: string
    """
    # Check if user exists
    if user_id not in users_db:
        return jsonify({'error': 'User not found'}), 404
    
    # Get request data
    data = request.get_json()
    
    # Validate that at least one field is provided
    if not data or not any(field in data for field in ['username', 'email', 'role']):
        return jsonify({'error': 'No valid fields to update'}), 400
    
    # Check if username is being changed to one that already exists
    if 'username' in data and data['username'] != users_db[user_id]['username']:
        for existing_user in users_db.values():
            if existing_user['username'] == data['username'] and existing_user['id'] != user_id:
                return jsonify({'error': 'Username already exists'}), 409
    
    # Update only provided fields
    user = users_db[user_id]
    for field in ['username', 'email', 'role']:
        if field in data:
            user[field] = data[field]
    
    return jsonify(user)

# Delete a user (DELETE)
@app.route('/api/v1/users/<user_id>', methods=['DELETE'])
@require_auth
def delete_user(user_id):
    """Delete a user by ID."""
    # Check if user exists
    if user_id not in users_db:
        return jsonify({'error': 'User not found'}), 404
    
    # Delete user
    del users_db[user_id]
    
    # Return 204 No Content
    return '', 204

# --- Product Resource Endpoints ---

# List all products (GET)
@app.route('/api/v1/products', methods=['GET'])
def get_products():
    """
    Get all products with optional filtering.
    
    Query Parameters:
    - category: Filter products by category (e.g., ?category=electronics)
    - in_stock: Filter products by availability (e.g., ?in_stock=true)
    - min_price: Filter products by minimum price (e.g., ?min_price=100)
    - max_price: Filter products by maximum price (e.g., ?max_price=500)
    """
    products = list(products_db.values())
    
    # Filter by category
    category = request.args.get('category')
    if category:
        products = [product for product in products if product['category'] == category]
    
    # Filter by stock status
    in_stock = request.args.get('in_stock')
    if in_stock is not None:
        in_stock_bool = (in_stock.lower() == 'true')
        products = [product for product in products if product['in_stock'] == in_stock_bool]
    
    # Filter by price range
    min_price = request.args.get('min_price')
    if min_price:
        try:
            min_price_float = float(min_price)
            products = [product for product in products if product['price'] >= min_price_float]
        except ValueError:
            return jsonify({'error': 'Invalid min_price parameter'}), 400
    
    max_price = request.args.get('max_price')
    if max_price:
        try:
            max_price_float = float(max_price)
            products = [product for product in products if product['price'] <= max_price_float]
        except ValueError:
            return jsonify({'error': 'Invalid max_price parameter'}), 400
    
    return jsonify({
        'count': len(products),
        'results': products
    })

# Get a specific product (GET)
@app.route('/api/v1/products/<product_id>', methods=['GET'])
def get_product(product_id):
    """Get a specific product by ID."""
    product = products_db.get(product_id)
    if not product:
        return jsonify({'error': 'Product not found'}), 404
    
    return jsonify(product)

# Create a new product (POST)
@app.route('/api/v1/products', methods=['POST'])
@require_auth
def create_product():
    """
    Create a new product.
    
    Required fields:
    - name: string
    - price: number
    - category: string
    
    Optional fields:
    - in_stock: boolean (default: true)
    """
    # Get request data
    data = request.get_json()
    
    # Validate required fields
    if not data or 'name' not in data or 'price' not in data or 'category' not in data:
        return jsonify({'error': 'Missing required fields: name, price, and category'}), 400
    
    # Validate price
    try:
        price = float(data['price'])
        if price < 0:
            return jsonify({'error': 'Price must be non-negative'}), 400
    except (ValueError, TypeError):
        return jsonify({'error': 'Price must be a number'}), 400
    
    # Generate new product ID
    product_id = str(len(products_db) + 1)
    
    # Create new product
    new_product = {
        'id': product_id,
        'name': data['name'],
        'price': price,
        'category': data['category'],
        'in_stock': data.get('in_stock', True)  # Default is True
    }
    
    # Add to database
    products_db[product_id] = new_product
    
    # Return newly created product with 201 Created status
    return jsonify(new_product), 201, {'Location': f'/api/v1/products/{product_id}'}

# Update a product (PUT)
@app.route('/api/v1/products/<product_id>', methods=['PUT'])
@require_auth
def update_product(product_id):
    """
    Update a product (complete replacement).
    
    Required fields:
    - name: string
    - price: number
    - category: string
    - in_stock: boolean
    """
    # Check if product exists
    if product_id not in products_db:
        return jsonify({'error': 'Product not found'}), 404
    
    # Get request data
    data = request.get_json()
    
    # Validate required fields
    if not data or 'name' not in data or 'price' not in data or 'category' not in data or 'in_stock' not in data:
        return jsonify({'error': 'Missing required fields: name, price, category, and in_stock'}), 400
    
    # Validate price
    try:
        price = float(data['price'])
        if price < 0:
            return jsonify({'error': 'Price must be non-negative'}), 400
    except (ValueError, TypeError):
        return jsonify({'error': 'Price must be a number'}), 400
    
    # Update product
    products_db[product_id] = {
        'id': product_id,
        'name': data['name'],
        'price': price,
        'category': data['category'],
        'in_stock': data['in_stock']
    }
    
    return jsonify(products_db[product_id])

# Delete a product (DELETE)
@app.route('/api/v1/products/<product_id>', methods=['DELETE'])
@require_auth
def delete_product(product_id):
    """Delete a product by ID."""
    # Check if product exists
    if product_id not in products_db:
        return jsonify({'error': 'Product not found'}), 404
    
    # Delete product
    del products_db[product_id]
    
    # Return 204 No Content
    return '', 204

# --- API Documentation Endpoint ---

@app.route('/api/v1/docs')
def api_docs():
    """API documentation endpoint."""
    return jsonify({
        'name': 'REST API Demo Documentation',
        'base_url': '/api/v1',
        'authentication': {
            'type': 'Basic Auth',
            'credentials': 'admin:password'
        },
        'resources': {
            'users': {
                'endpoints': [
                    {'method': 'GET', 'path': '/users', 'description': 'List all users'},
                    {'method': 'GET', 'path': '/users/<id>', 'description': 'Get a specific user'},
                    {'method': 'POST', 'path': '/users', 'description': 'Create a new user', 'auth_required': True},
                    {'method': 'PUT', 'path': '/users/<id>', 'description': 'Update a user', 'auth_required': True},
                    {'method': 'PATCH', 'path': '/users/<id>', 'description': 'Partially update a user', 'auth_required': True},
                    {'method': 'DELETE', 'path': '/users/<id>', 'description': 'Delete a user', 'auth_required': True}
                ]
            },
            'products': {
                'endpoints': [
                    {'method': 'GET', 'path': '/products', 'description': 'List all products'},
                    {'method': 'GET', 'path': '/products/<id>', 'description': 'Get a specific product'},
                    {'method': 'POST', 'path': '/products', 'description': 'Create a new product', 'auth_required': True},
                    {'method': 'PUT', 'path': '/products/<id>', 'description': 'Update a product', 'auth_required': True},
                    {'method': 'DELETE', 'path': '/products/<id>', 'description': 'Delete a product', 'auth_required': True}
                ]
            }
        }
    })

# --- Health Check Endpoint ---

@app.route('/api/v1/health')
def health_check():
    """Health check endpoint."""
    return jsonify({
        'status': 'ok',
        'timestamp': datetime.datetime.now().isoformat() + 'Z',
        'version': '1.0'
    })

# --- Error Handlers ---

@app.errorhandler(404)
def not_found(error):
    """Handle 404 errors."""
    return jsonify({'error': 'Not found'}), 404

@app.errorhandler(400)
def bad_request(error):
    """Handle 400 errors."""
    return jsonify({'error': 'Bad request'}), 400

@app.errorhandler(405)
def method_not_allowed(error):
    """Handle 405 errors."""
    return jsonify({'error': 'Method not allowed'}), 405

@app.errorhandler(500)
def server_error(error):
    """Handle 500 errors."""
    return jsonify({'error': 'Internal server error'}), 500

# --- REST API Principles Explanation ---

"""
REST Architecture Principles Demonstrated:

1. Resource-Based URLs:
   - URLs represent resources (e.g., /users, /products)
   - Resources are nouns, not verbs

2. HTTP Methods for CRUD Operations:
   - GET: Read a resource
   - POST: Create a new resource
   - PUT: Update a resource (complete replacement)
   - PATCH: Partially update a resource
   - DELETE: Remove a resource

3. Stateless Communication:
   - Server doesn't store client state between requests
   - Each request contains all information needed to process it

4. Uniform Interface:
   - Consistent URL patterns for resources
   - Standard HTTP methods and status codes
   - Resource representations (JSON)

5. Status Codes:
   - 200 OK: Successful request
   - 201 Created: Resource created successfully
   - 204 No Content: Successful request with no content to return
   - 400 Bad Request: Invalid input
   - 401 Unauthorized: Authentication required
   - 404 Not Found: Resource doesn't exist
   - 409 Conflict: Request conflicts with current state
   - 500 Internal Server Error: Server-side error

6. RESTful Best Practices:
   - API versioning (/api/v1/...)
   - Filtering, sorting, and pagination
   - Consistent error responses
   - Hypermedia links (HATEOAS) can be added
"""

# --- Run Application ---

if __name__ == '__main__':
    print("REST API Demo Running!")
    print("Try these endpoints:")
    print("  - http://localhost:5000/api/v1")
    print("  - http://localhost:5000/api/v1/users")
    print("  - http://localhost:5000/api/v1/products")
    print("  - http://localhost:5000/api/v1/docs")
    app.run(debug=True)

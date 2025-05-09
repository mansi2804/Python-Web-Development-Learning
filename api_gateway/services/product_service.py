"""
Product Service - Mock Microservice for API Gateway Demo

This module simulates a product management microservice that handles product-related 
operations such as listing, creating, updating, and deleting products.

This is a simplified example to demonstrate API Gateway functionality.
"""

from flask import Flask, request, jsonify
import uuid
import time
import json
import os

app = Flask(__name__)

# In-memory product database (in a real service, this would use a persistent database)
PRODUCTS = {
    "1": {
        "id": "1",
        "name": "Laptop Pro X",
        "description": "High-performance laptop with 16GB RAM and 512GB SSD",
        "price": 1299.99,
        "category": "electronics",
        "in_stock": True,
        "created_at": "2023-01-10T09:00:00Z"
    },
    "2": {
        "id": "2",
        "name": "Smartphone Ultra",
        "description": "Latest smartphone with 6.5-inch display and 128GB storage",
        "price": 899.99,
        "category": "electronics",
        "in_stock": True,
        "created_at": "2023-01-15T10:30:00Z"
    },
    "3": {
        "id": "3",
        "name": "Wireless Headphones",
        "description": "Noise-cancelling wireless headphones with 20-hour battery life",
        "price": 199.99,
        "category": "accessories",
        "in_stock": True,
        "created_at": "2023-02-05T14:45:00Z"
    },
    "4": {
        "id": "4",
        "name": "Smart Watch",
        "description": "Fitness tracker and smartwatch with heart rate monitoring",
        "price": 249.99,
        "category": "wearables",
        "in_stock": False,
        "created_at": "2023-02-20T11:15:00Z"
    }
}

# In-memory category database
CATEGORIES = {
    "electronics": {
        "id": "electronics",
        "name": "Electronics",
        "description": "Electronic devices and gadgets"
    },
    "accessories": {
        "id": "accessories",
        "name": "Accessories",
        "description": "Product accessories and add-ons"
    },
    "wearables": {
        "id": "wearables",
        "name": "Wearables",
        "description": "Wearable technology and devices"
    }
}

# --- Helper Functions ---

def get_timestamp():
    """Get current ISO format timestamp."""
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())

def generate_id():
    """Generate a unique ID."""
    return str(uuid.uuid4())

# --- API Routes ---

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint."""
    return jsonify({
        "status": "ok",
        "service": "product-service",
        "version": "1.0.0"
    })

@app.route('/products', methods=['GET'])
def get_products():
    """Get all products with optional filtering."""
    # Extract query parameters for filtering
    category = request.args.get('category')
    in_stock = request.args.get('in_stock')
    min_price = request.args.get('min_price')
    max_price = request.args.get('max_price')
    
    # Start with all products
    result = list(PRODUCTS.values())
    
    # Apply filters if provided
    if category:
        result = [p for p in result if p['category'] == category]
    
    if in_stock is not None:
        in_stock_bool = in_stock.lower() == 'true'
        result = [p for p in result if p['in_stock'] == in_stock_bool]
    
    if min_price is not None:
        try:
            min_price_float = float(min_price)
            result = [p for p in result if p['price'] >= min_price_float]
        except ValueError:
            pass
    
    if max_price is not None:
        try:
            max_price_float = float(max_price)
            result = [p for p in result if p['price'] <= max_price_float]
        except ValueError:
            pass
    
    return jsonify(result)

@app.route('/products/<product_id>', methods=['GET'])
def get_product(product_id):
    """Get a specific product by ID."""
    product = PRODUCTS.get(product_id)
    if not product:
        return jsonify({"error": "Product not found"}), 404
    
    return jsonify(product)

@app.route('/products', methods=['POST'])
def create_product():
    """Create a new product."""
    data = request.get_json()
    
    # Validate required fields
    if not data or not data.get('name') or not data.get('price'):
        return jsonify({"error": "Name and price are required"}), 400
    
    # Create new product
    product_id = generate_id()
    new_product = {
        "id": product_id,
        "name": data['name'],
        "description": data.get('description', ''),
        "price": float(data['price']),
        "category": data.get('category', ''),
        "in_stock": data.get('in_stock', True),
        "created_at": get_timestamp()
    }
    
    PRODUCTS[product_id] = new_product
    
    return jsonify(new_product), 201

@app.route('/products/<product_id>', methods=['PUT'])
def update_product(product_id):
    """Update an existing product."""
    if product_id not in PRODUCTS:
        return jsonify({"error": "Product not found"}), 404
    
    data = request.get_json()
    if not data:
        return jsonify({"error": "No data provided"}), 400
    
    product = PRODUCTS[product_id]
    
    # Update product fields
    if 'name' in data:
        product['name'] = data['name']
    
    if 'description' in data:
        product['description'] = data['description']
    
    if 'price' in data:
        product['price'] = float(data['price'])
    
    if 'category' in data:
        product['category'] = data['category']
    
    if 'in_stock' in data:
        product['in_stock'] = bool(data['in_stock'])
    
    return jsonify(product)

@app.route('/products/<product_id>', methods=['DELETE'])
def delete_product(product_id):
    """Delete a product."""
    if product_id not in PRODUCTS:
        return jsonify({"error": "Product not found"}), 404
    
    del PRODUCTS[product_id]
    
    return jsonify({"message": f"Product {product_id} deleted successfully"})

@app.route('/products/search', methods=['GET'])
def search_products():
    """Search products by query."""
    query = request.args.get('q', '').lower()
    if not query:
        return jsonify({"error": "Search query is required"}), 400
    
    # Search in name and description
    results = []
    for product in PRODUCTS.values():
        if (query in product['name'].lower() or 
            query in product['description'].lower()):
            results.append(product)
    
    return jsonify(results)

@app.route('/categories', methods=['GET'])
def get_categories():
    """Get all product categories."""
    return jsonify(list(CATEGORIES.values()))

@app.route('/categories/<category_id>', methods=['GET'])
def get_category(category_id):
    """Get a specific category by ID."""
    category = CATEGORIES.get(category_id)
    if not category:
        return jsonify({"error": "Category not found"}), 404
    
    return jsonify(category)

@app.route('/categories/<category_id>/products', methods=['GET'])
def get_category_products(category_id):
    """Get all products in a category."""
    if category_id not in CATEGORIES:
        return jsonify({"error": "Category not found"}), 404
    
    products = [p for p in PRODUCTS.values() if p['category'] == category_id]
    return jsonify(products)

# --- Run the application ---

if __name__ == '__main__':
    # Get instance number from environment variable or command line
    instance = os.environ.get('INSTANCE', '1')
    port = 8010 + int(instance)
    
    print(f"Starting Product Service (Instance {instance}) on port {port}...")
    app.run(host='0.0.0.0', port=port, debug=True)

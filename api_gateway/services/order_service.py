"""
Order Service - Mock Microservice for API Gateway Demo

This module simulates an order management microservice that handles order-related 
operations such as creating orders, updating status, and retrieving order history.

This is a simplified example to demonstrate API Gateway functionality.
"""

from flask import Flask, request, jsonify
import uuid
import time
import json
import os
from datetime import datetime

app = Flask(__name__)

# In-memory order database (in a real service, this would use a persistent database)
ORDERS = {
    "1": {
        "id": "1",
        "user_id": "1",
        "status": "delivered",
        "items": [
            {"product_id": "1", "quantity": 1, "price": 1299.99},
            {"product_id": "3", "quantity": 1, "price": 199.99}
        ],
        "total": 1499.98,
        "shipping_address": {
            "street": "123 Main St",
            "city": "Anytown",
            "state": "CA",
            "zip": "12345",
            "country": "USA"
        },
        "created_at": "2023-01-20T09:15:00Z",
        "updated_at": "2023-01-25T14:30:00Z"
    },
    "2": {
        "id": "2",
        "user_id": "1",
        "status": "shipped",
        "items": [
            {"product_id": "4", "quantity": 1, "price": 249.99}
        ],
        "total": 249.99,
        "shipping_address": {
            "street": "123 Main St",
            "city": "Anytown",
            "state": "CA",
            "zip": "12345",
            "country": "USA"
        },
        "created_at": "2023-02-10T11:20:00Z",
        "updated_at": "2023-02-12T16:45:00Z"
    },
    "3": {
        "id": "3",
        "user_id": "2",
        "status": "processing",
        "items": [
            {"product_id": "2", "quantity": 1, "price": 899.99},
            {"product_id": "3", "quantity": 2, "price": 199.99}
        ],
        "total": 1299.97,
        "shipping_address": {
            "street": "456 Oak Ave",
            "city": "Other City",
            "state": "NY",
            "zip": "67890",
            "country": "USA"
        },
        "created_at": "2023-03-05T10:10:00Z",
        "updated_at": "2023-03-05T10:10:00Z"
    }
}

# Order status workflow
ORDER_STATUSES = ["pending", "processing", "shipped", "delivered", "cancelled"]

# --- Helper Functions ---

def get_timestamp():
    """Get current ISO format timestamp."""
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())

def generate_id():
    """Generate a unique ID."""
    return str(uuid.uuid4())

def calculate_total(items):
    """Calculate order total from items."""
    return sum(item["quantity"] * item["price"] for item in items)

# --- API Routes ---

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint."""
    return jsonify({
        "status": "ok",
        "service": "order-service",
        "version": "1.0.0"
    })

@app.route('/orders', methods=['GET'])
def get_orders():
    """Get all orders with optional filtering."""
    # Extract query parameters for filtering
    user_id = request.args.get('user_id')
    status = request.args.get('status')
    from_date = request.args.get('from_date')
    to_date = request.args.get('to_date')
    
    # Start with all orders
    result = list(ORDERS.values())
    
    # Apply filters if provided
    if user_id:
        result = [o for o in result if o['user_id'] == user_id]
    
    if status:
        result = [o for o in result if o['status'] == status]
    
    if from_date:
        try:
            from_date_obj = datetime.fromisoformat(from_date.replace('Z', '+00:00'))
            result = [o for o in result if datetime.fromisoformat(o['created_at'].replace('Z', '+00:00')) >= from_date_obj]
        except ValueError:
            pass
    
    if to_date:
        try:
            to_date_obj = datetime.fromisoformat(to_date.replace('Z', '+00:00'))
            result = [o for o in result if datetime.fromisoformat(o['created_at'].replace('Z', '+00:00')) <= to_date_obj]
        except ValueError:
            pass
    
    return jsonify(result)

@app.route('/orders/<order_id>', methods=['GET'])
def get_order(order_id):
    """Get a specific order by ID."""
    order = ORDERS.get(order_id)
    if not order:
        return jsonify({"error": "Order not found"}), 404
    
    return jsonify(order)

@app.route('/orders', methods=['POST'])
def create_order():
    """Create a new order."""
    data = request.get_json()
    
    # Validate required fields
    if not data or not data.get('user_id') or not data.get('items') or not data.get('shipping_address'):
        return jsonify({"error": "User ID, items, and shipping address are required"}), 400
    
    # Validate items
    items = data['items']
    if not isinstance(items, list) or len(items) == 0:
        return jsonify({"error": "Items must be a non-empty array"}), 400
    
    for item in items:
        if not item.get('product_id') or not item.get('quantity') or not item.get('price'):
            return jsonify({"error": "Each item must have product_id, quantity, and price"}), 400
    
    # Create new order
    order_id = generate_id()
    timestamp = get_timestamp()
    
    new_order = {
        "id": order_id,
        "user_id": data['user_id'],
        "status": "pending",
        "items": items,
        "total": calculate_total(items),
        "shipping_address": data['shipping_address'],
        "created_at": timestamp,
        "updated_at": timestamp
    }
    
    ORDERS[order_id] = new_order
    
    return jsonify(new_order), 201

@app.route('/orders/<order_id>', methods=['PUT'])
def update_order(order_id):
    """Update an existing order."""
    if order_id not in ORDERS:
        return jsonify({"error": "Order not found"}), 404
    
    data = request.get_json()
    if not data:
        return jsonify({"error": "No data provided"}), 400
    
    order = ORDERS[order_id]
    
    # Update order fields
    if 'status' in data:
        new_status = data['status']
        if new_status not in ORDER_STATUSES:
            return jsonify({"error": f"Invalid status. Must be one of: {', '.join(ORDER_STATUSES)}"}), 400
        order['status'] = new_status
    
    if 'shipping_address' in data:
        order['shipping_address'] = data['shipping_address']
    
    if 'items' in data:
        items = data['items']
        # Validate items
        if not isinstance(items, list) or len(items) == 0:
            return jsonify({"error": "Items must be a non-empty array"}), 400
        
        for item in items:
            if not item.get('product_id') or not item.get('quantity') or not item.get('price'):
                return jsonify({"error": "Each item must have product_id, quantity, and price"}), 400
        
        order['items'] = items
        order['total'] = calculate_total(items)
    
    order['updated_at'] = get_timestamp()
    
    return jsonify(order)

@app.route('/orders/<order_id>', methods=['DELETE'])
def delete_order(order_id):
    """Delete an order."""
    if order_id not in ORDERS:
        return jsonify({"error": "Order not found"}), 404
    
    # In a real application, you might want to archive the order instead of deleting it
    del ORDERS[order_id]
    
    return jsonify({"message": f"Order {order_id} deleted successfully"})

@app.route('/orders/<order_id>/status', methods=['PUT'])
def update_order_status(order_id):
    """Update an order's status."""
    if order_id not in ORDERS:
        return jsonify({"error": "Order not found"}), 404
    
    data = request.get_json()
    if not data or 'status' not in data:
        return jsonify({"error": "Status is required"}), 400
    
    new_status = data['status']
    if new_status not in ORDER_STATUSES:
        return jsonify({"error": f"Invalid status. Must be one of: {', '.join(ORDER_STATUSES)}"}), 400
    
    order = ORDERS[order_id]
    
    # Update status and timestamp
    order['status'] = new_status
    order['updated_at'] = get_timestamp()
    
    return jsonify(order)

@app.route('/users/<user_id>/orders', methods=['GET'])
def get_user_orders(user_id):
    """Get all orders for a specific user."""
    user_orders = [o for o in ORDERS.values() if o['user_id'] == user_id]
    return jsonify(user_orders)

@app.route('/stats/orders', methods=['GET'])
def get_order_stats():
    """Get order statistics."""
    status_counts = {}
    for status in ORDER_STATUSES:
        status_counts[status] = len([o for o in ORDERS.values() if o['status'] == status])
    
    total_orders = len(ORDERS)
    total_revenue = sum(o['total'] for o in ORDERS.values())
    
    return jsonify({
        "total_orders": total_orders,
        "total_revenue": total_revenue,
        "status_breakdown": status_counts
    })

# --- Run the application ---

if __name__ == '__main__':
    # Get instance number from environment variable or command line
    instance = os.environ.get('INSTANCE', '1')
    port = 8020 + int(instance)
    
    print(f"Starting Order Service (Instance {instance}) on port {port}...")
    app.run(host='0.0.0.0', port=port, debug=True)

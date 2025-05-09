"""
User Service - Mock Microservice for API Gateway Demo

This module simulates a user management microservice that handles user-related operations
such as authentication, user profiles, and user management.

This is a simplified example to demonstrate API Gateway functionality.
"""

from flask import Flask, request, jsonify
import uuid
import time
import json
import os

app = Flask(__name__)

# In-memory user database (in a real service, this would use a persistent database)
USERS = {
    "1": {
        "id": "1",
        "username": "john_doe",
        "email": "john@example.com",
        "full_name": "John Doe",
        "created_at": "2023-01-15T10:00:00Z",
        "role": "user"
    },
    "2": {
        "id": "2",
        "username": "jane_smith",
        "email": "jane@example.com",
        "full_name": "Jane Smith",
        "created_at": "2023-02-20T14:30:00Z",
        "role": "admin"
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
        "service": "user-service",
        "version": "1.0.0"
    })

@app.route('/users', methods=['GET'])
def get_users():
    """Get all users."""
    # Extract query parameters for filtering
    role = request.args.get('role')
    
    # Apply filters if provided
    result = list(USERS.values())
    if role:
        result = [user for user in result if user['role'] == role]
    
    return jsonify(result)

@app.route('/users/<user_id>', methods=['GET'])
def get_user(user_id):
    """Get a specific user by ID."""
    user = USERS.get(user_id)
    if not user:
        return jsonify({"error": "User not found"}), 404
    
    return jsonify(user)

@app.route('/users', methods=['POST'])
def create_user():
    """Create a new user."""
    data = request.get_json()
    
    # Validate required fields
    if not data or not data.get('username') or not data.get('email'):
        return jsonify({"error": "Username and email are required"}), 400
    
    # Check if username already exists
    for user in USERS.values():
        if user['username'] == data['username']:
            return jsonify({"error": "Username already exists"}), 409
    
    # Create new user
    user_id = generate_id()
    new_user = {
        "id": user_id,
        "username": data['username'],
        "email": data['email'],
        "full_name": data.get('full_name', ''),
        "created_at": get_timestamp(),
        "role": data.get('role', 'user')
    }
    
    USERS[user_id] = new_user
    
    return jsonify(new_user), 201

@app.route('/users/<user_id>', methods=['PUT'])
def update_user(user_id):
    """Update an existing user."""
    if user_id not in USERS:
        return jsonify({"error": "User not found"}), 404
    
    data = request.get_json()
    if not data:
        return jsonify({"error": "No data provided"}), 400
    
    user = USERS[user_id]
    
    # Update user fields
    if 'username' in data:
        # Check if username already exists
        for uid, u in USERS.items():
            if u['username'] == data['username'] and uid != user_id:
                return jsonify({"error": "Username already exists"}), 409
        user['username'] = data['username']
    
    if 'email' in data:
        user['email'] = data['email']
    
    if 'full_name' in data:
        user['full_name'] = data['full_name']
    
    if 'role' in data:
        user['role'] = data['role']
    
    return jsonify(user)

@app.route('/users/<user_id>', methods=['DELETE'])
def delete_user(user_id):
    """Delete a user."""
    if user_id not in USERS:
        return jsonify({"error": "User not found"}), 404
    
    del USERS[user_id]
    
    return jsonify({"message": f"User {user_id} deleted successfully"})

@app.route('/users/search', methods=['GET'])
def search_users():
    """Search users by query."""
    query = request.args.get('q', '').lower()
    if not query:
        return jsonify({"error": "Search query is required"}), 400
    
    # Search in username, email, and full_name
    results = []
    for user in USERS.values():
        if (query in user['username'].lower() or 
            query in user['email'].lower() or 
            query in user['full_name'].lower()):
            results.append(user)
    
    return jsonify(results)

@app.route('/auth/login', methods=['POST'])
def login():
    """Simulate user login."""
    data = request.get_json()
    
    if not data or not data.get('username') or not data.get('password'):
        return jsonify({"error": "Username and password are required"}), 400
    
    # This is a mock authentication - in a real service, you would verify credentials securely
    # Find user by username
    user = None
    for u in USERS.values():
        if u['username'] == data['username']:
            user = u
            break
    
    if not user:
        return jsonify({"error": "Invalid credentials"}), 401
    
    # In a real service, you would verify the password hash
    
    # Generate a mock auth token
    auth_token = f"mock-token-{generate_id()}"
    
    return jsonify({
        "token": auth_token,
        "user_id": user['id'],
        "expires_in": 3600  # 1 hour
    })

# --- Run the application ---

if __name__ == '__main__':
    # Get instance number from environment variable or command line
    instance = os.environ.get('INSTANCE', '1')
    port = 8000 + int(instance)
    
    print(f"Starting User Service (Instance {instance}) on port {port}...")
    app.run(host='0.0.0.0', port=port, debug=True)

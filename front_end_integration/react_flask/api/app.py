"""
Flask API Backend for React Integration Example

This Flask application provides a RESTful API for a task management system.
It demonstrates how to create a backend API that can be consumed by a React frontend.

Key concepts demonstrated:
- RESTful API design with Flask
- JSON request/response handling
- CORS configuration for cross-origin requests
- JWT authentication
- Database operations with SQLAlchemy (simulated with in-memory data)
"""

from flask import Flask, jsonify, request, make_response
from flask_cors import CORS
import uuid
import jwt
import datetime
import os
from functools import wraps
import json

# Initialize Flask app
app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key'  # In production, use a real secret key stored securely
CORS(app)  # Enable CORS for all routes and origins

# Simulated database (in a real app, use a database like SQLite, PostgreSQL, etc.)
TASKS = [
    {
        'id': '1',
        'title': 'Learn Flask',
        'description': 'Study Flask framework and REST API development',
        'status': 'completed',
        'created_at': '2023-01-15T10:30:00Z'
    },
    {
        'id': '2',
        'title': 'Learn React',
        'description': 'Study React library and hooks for frontend development',
        'status': 'in_progress',
        'created_at': '2023-01-16T14:45:00Z'
    },
    {
        'id': '3',
        'title': 'Build Full-stack Application',
        'description': 'Integrate Flask backend with React frontend',
        'status': 'pending',
        'created_at': '2023-01-17T09:15:00Z'
    }
]

# Mock user database
USERS = {
    'user@example.com': {
        'password': 'password123',  # In a real app, store hashed passwords
        'name': 'Demo User'
    }
}

# Authentication decorator
def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        
        # Check if token is in headers
        if 'Authorization' in request.headers:
            auth_header = request.headers['Authorization']
            if auth_header.startswith('Bearer '):
                token = auth_header.split(' ')[1]
        
        if not token:
            return jsonify({'message': 'Token is missing!'}), 401
        
        try:
            # Decode the token
            data = jwt.decode(token, app.config['SECRET_KEY'], algorithms=["HS256"])
            current_user = data['email']
        except:
            return jsonify({'message': 'Token is invalid!'}), 401
            
        return f(current_user, *args, **kwargs)
    
    return decorated

# Routes
@app.route('/api/tasks', methods=['GET'])
@token_required
def get_tasks(current_user):
    """Get all tasks"""
    return jsonify(TASKS)

@app.route('/api/tasks/<task_id>', methods=['GET'])
@token_required
def get_task(current_user, task_id):
    """Get a specific task by ID"""
    task = next((task for task in TASKS if task['id'] == task_id), None)
    if task:
        return jsonify(task)
    return jsonify({'message': 'Task not found'}), 404

@app.route('/api/tasks', methods=['POST'])
@token_required
def create_task(current_user):
    """Create a new task"""
    if not request.json or not 'title' in request.json:
        return jsonify({'message': 'Title is required'}), 400
    
    task = {
        'id': str(uuid.uuid4()),
        'title': request.json['title'],
        'description': request.json.get('description', ''),
        'status': request.json.get('status', 'pending'),
        'created_at': datetime.datetime.now().isoformat() + 'Z'
    }
    
    TASKS.append(task)
    return jsonify(task), 201

@app.route('/api/tasks/<task_id>', methods=['PUT'])
@token_required
def update_task(current_user, task_id):
    """Update an existing task"""
    task = next((task for task in TASKS if task['id'] == task_id), None)
    if not task:
        return jsonify({'message': 'Task not found'}), 404
    
    if not request.json:
        return jsonify({'message': 'No data provided'}), 400
    
    # Update task fields
    task['title'] = request.json.get('title', task['title'])
    task['description'] = request.json.get('description', task['description'])
    task['status'] = request.json.get('status', task['status'])
    
    return jsonify(task)

@app.route('/api/tasks/<task_id>', methods=['DELETE'])
@token_required
def delete_task(current_user, task_id):
    """Delete a task"""
    global TASKS
    initial_count = len(TASKS)
    TASKS = [task for task in TASKS if task['id'] != task_id]
    
    if len(TASKS) < initial_count:
        return jsonify({'message': 'Task deleted'})
    return jsonify({'message': 'Task not found'}), 404

@app.route('/api/login', methods=['POST'])
def login():
    """User login endpoint"""
    auth = request.authorization
    
    if not auth or not auth.username or not auth.password:
        # Try to get credentials from JSON body
        data = request.get_json()
        if data and 'email' in data and 'password' in data:
            auth_username = data['email']
            auth_password = data['password']
        else:
            return make_response('Could not verify', 401, {'WWW-Authenticate': 'Basic realm="Login required"'})
    else:
        auth_username = auth.username
        auth_password = auth.password
    
    if auth_username not in USERS or USERS[auth_username]['password'] != auth_password:
        return make_response('Could not verify', 401, {'WWW-Authenticate': 'Basic realm="Login required"'})
    
    # Generate JWT token
    token = jwt.encode({
        'email': auth_username,
        'name': USERS[auth_username]['name'],
        'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=24)
    }, app.config['SECRET_KEY'], algorithm="HS256")
    
    return jsonify({
        'token': token,
        'user': {
            'email': auth_username,
            'name': USERS[auth_username]['name']
        }
    })

@app.route('/api/register', methods=['POST'])
def register():
    """User registration endpoint"""
    data = request.get_json()
    
    if not data or not data.get('email') or not data.get('password') or not data.get('name'):
        return jsonify({'message': 'Missing required fields'}), 400
    
    email = data['email']
    
    if email in USERS:
        return jsonify({'message': 'User already exists'}), 400
    
    # In a real app, hash the password before storing
    USERS[email] = {
        'password': data['password'],
        'name': data['name']
    }
    
    return jsonify({'message': 'User created successfully'}), 201

@app.route('/api/user', methods=['GET'])
@token_required
def get_user(current_user):
    """Get current user information"""
    if current_user not in USERS:
        return jsonify({'message': 'User not found'}), 404
    
    return jsonify({
        'email': current_user,
        'name': USERS[current_user]['name']
    })

# Health check endpoint (no authentication required)
@app.route('/api/health', methods=['GET'])
def health_check():
    """API health check endpoint"""
    return jsonify({
        'status': 'ok',
        'message': 'API is running'
    })

# Error handlers
@app.errorhandler(404)
def not_found(error):
    return jsonify({'message': 'Resource not found'}), 404

@app.errorhandler(500)
def server_error(error):
    return jsonify({'message': 'Server error'}), 500

# Run the application
if __name__ == '__main__':
    app.run(debug=True)

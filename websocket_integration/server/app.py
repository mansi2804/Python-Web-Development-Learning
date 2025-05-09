"""
WebSocket Chat Server using Flask-SocketIO

This module demonstrates how to implement a real-time chat application using WebSockets
with Flask-SocketIO. It handles user connections, message broadcasting, and room-based
communication.

Key Concepts:
- WebSocket protocol basics
- Real-time bidirectional communication
- Broadcasting messages to connected clients
- Room-based communication
- Managing user connections and disconnections
"""

from flask import Flask, render_template
from flask_socketio import SocketIO, emit, join_room, leave_room
from flask_cors import CORS
import os
import json
from datetime import datetime

# Initialize Flask application
app = Flask(__name__, static_folder='../client', static_url_path='')
app.config['SECRET_KEY'] = 'your-secret-key'  # For session management
CORS(app)  # Enable CORS for all routes

# Initialize SocketIO with the app
socketio = SocketIO(app, cors_allowed_origins="*")

# In-memory storage for active users and chat history
active_users = {}  # {session_id: {username, room}}
chat_history = {}  # {room: [message objects]}

# Maximum number of messages to store per room
MAX_HISTORY = 50

@app.route('/')
def index():
    """Serve the client application"""
    return app.send_static_file('index.html')

@app.route('/health')
def health():
    """Health check endpoint"""
    return {'status': 'ok', 'message': 'WebSocket server is running'}

@socketio.on('connect')
def handle_connect():
    """Handle client connection"""
    print(f'Client connected: {request.sid}')
    emit('connection_response', {'status': 'connected'})

@socketio.on('disconnect')
def handle_disconnect():
    """Handle client disconnection"""
    if request.sid in active_users:
        user_data = active_users[request.sid]
        username = user_data['username']
        room = user_data['room']
        
        # Remove user from active users
        del active_users[request.sid]
        
        # Notify room that user has left
        emit('user_left', {
            'username': username,
            'timestamp': datetime.now().isoformat(),
            'active_users': get_room_users(room)
        }, to=room)
        
        print(f'Client disconnected: {username} from room {room}')

@socketio.on('join')
def handle_join(data):
    """Handle a user joining a chat room"""
    username = data.get('username')
    room = data.get('room', 'general')
    
    if not username:
        emit('error', {'message': 'Username is required'})
        return
    
    # Store user data
    active_users[request.sid] = {
        'username': username,
        'room': room
    }
    
    # Join the room
    join_room(room)
    
    # Initialize chat history for the room if it doesn't exist
    if room not in chat_history:
        chat_history[room] = []
    
    # Send chat history to the user
    emit('chat_history', chat_history[room])
    
    # Notify room that user has joined
    join_message = {
        'type': 'system',
        'content': f'{username} has joined the room',
        'username': 'System',
        'timestamp': datetime.now().isoformat()
    }
    
    chat_history[room].append(join_message)
    trim_history(room)
    
    emit('user_joined', {
        'username': username,
        'timestamp': datetime.now().isoformat(),
        'active_users': get_room_users(room)
    }, to=room)
    
    print(f'User {username} joined room {room}')

@socketio.on('leave')
def handle_leave(data):
    """Handle a user leaving a chat room"""
    if request.sid not in active_users:
        return
    
    user_data = active_users[request.sid]
    username = user_data['username']
    room = user_data['room']
    
    # Leave the room
    leave_room(room)
    
    # Update user data
    if 'room' in data:
        user_data['room'] = data['room']
    
    # Notify room that user has left
    leave_message = {
        'type': 'system',
        'content': f'{username} has left the room',
        'username': 'System',
        'timestamp': datetime.now().isoformat()
    }
    
    chat_history[room].append(leave_message)
    trim_history(room)
    
    emit('user_left', {
        'username': username,
        'timestamp': datetime.now().isoformat(),
        'active_users': get_room_users(room)
    }, to=room)
    
    print(f'User {username} left room {room}')

@socketio.on('message')
def handle_message(data):
    """Handle chat messages"""
    if request.sid not in active_users:
        emit('error', {'message': 'You must join a room first'})
        return
    
    user_data = active_users[request.sid]
    username = user_data['username']
    room = user_data['room']
    message_content = data.get('message', '').strip()
    
    if not message_content:
        return
    
    # Create message object
    message = {
        'type': 'user',
        'content': message_content,
        'username': username,
        'timestamp': datetime.now().isoformat()
    }
    
    # Add message to chat history
    chat_history[room].append(message)
    trim_history(room)
    
    # Broadcast message to the room
    emit('new_message', message, to=room)
    
    print(f'Message from {username} in room {room}: {message_content}')

@socketio.on('typing')
def handle_typing(data):
    """Broadcast typing notification to other users in the room"""
    if request.sid not in active_users:
        return
    
    user_data = active_users[request.sid]
    username = user_data['username']
    room = user_data['room']
    is_typing = data.get('typing', False)
    
    # Broadcast typing status to other users in the room
    emit('user_typing', {
        'username': username,
        'typing': is_typing
    }, to=room, include_self=False)

def get_room_users(room):
    """Get a list of users in a specific room"""
    room_users = []
    
    for sid, user_data in active_users.items():
        if user_data['room'] == room:
            room_users.append(user_data['username'])
    
    return room_users

def trim_history(room):
    """Trim chat history to maximum size"""
    if room in chat_history and len(chat_history[room]) > MAX_HISTORY:
        chat_history[room] = chat_history[room][-MAX_HISTORY:]

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    
    print(f'Starting WebSocket server on port {port}...')
    print('Navigate to http://localhost:5000 to use the chat application')
    
    socketio.run(app, host='0.0.0.0', port=port, debug=True)

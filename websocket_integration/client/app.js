/**
 * WebSocket Chat Application - Client-side JavaScript
 * Python WebSocket Integration Example
 */

// DOM Elements
const loginContainer = document.getElementById('login-container');
const chatContainer = document.getElementById('chat-container');
const loginForm = document.getElementById('login-form');
const messageForm = document.getElementById('message-form');
const messageInput = document.getElementById('message-input');
const messagesContainer = document.getElementById('messages-container');
const usersList = document.getElementById('users-list');
const connectionStatus = document.getElementById('connection-status');
const currentRoomElement = document.getElementById('current-room');
const currentUserElement = document.getElementById('current-user');
const leaveButton = document.getElementById('leave-btn');
const typingIndicator = document.getElementById('typing-indicator');
const typingUsername = document.getElementById('typing-username');

// State variables
let socket = null;
let username = '';
let currentRoom = '';
let typingTimeout = null;

// Connection status updater
function updateConnectionStatus(status) {
    connectionStatus.textContent = status;
    connectionStatus.className = 'badge';
    
    switch (status) {
        case 'Connected':
            connectionStatus.classList.add('bg-success');
            break;
        case 'Disconnected':
            connectionStatus.classList.add('bg-danger');
            break;
        case 'Connecting...':
            connectionStatus.classList.add('bg-warning', 'text-dark');
            break;
        default:
            connectionStatus.classList.add('bg-secondary');
    }
}

// Connect to WebSocket server
function connectToServer() {
    updateConnectionStatus('Connecting...');
    
    // Connect to the WebSocket server
    // In production, you would use the actual server URL
    const serverUrl = window.location.hostname === 'localhost' 
        ? 'http://localhost:5000' 
        : window.location.origin;
    
    socket = io(serverUrl);
    
    // Connection event handlers
    socket.on('connect', () => {
        updateConnectionStatus('Connected');
        console.log('Connected to WebSocket server');
    });
    
    socket.on('disconnect', () => {
        updateConnectionStatus('Disconnected');
        console.log('Disconnected from WebSocket server');
    });
    
    socket.on('connect_error', (error) => {
        updateConnectionStatus('Connection Error');
        console.error('Connection error:', error);
    });
    
    // Chat event handlers
    socket.on('connection_response', (data) => {
        console.log('Connection response:', data);
    });
    
    socket.on('chat_history', (messages) => {
        // Clear messages container
        messagesContainer.innerHTML = '';
        
        // Add each message to the container
        messages.forEach(addMessageToChat);
        
        // Scroll to bottom
        scrollToBottom();
    });
    
    socket.on('new_message', (message) => {
        addMessageToChat(message);
        scrollToBottom();
    });
    
    socket.on('user_joined', (data) => {
        // Update active users list
        updateActiveUsers(data.active_users);
    });
    
    socket.on('user_left', (data) => {
        // Update active users list
        updateActiveUsers(data.active_users);
    });
    
    socket.on('user_typing', (data) => {
        if (data.typing) {
            typingUsername.textContent = data.username;
            typingIndicator.classList.remove('d-none');
        } else {
            typingIndicator.classList.add('d-none');
        }
    });
    
    socket.on('error', (data) => {
        console.error('Error from server:', data.message);
        alert(`Error: ${data.message}`);
    });
}

// Join chat room
function joinRoom(username, room) {
    if (!socket) {
        alert('Not connected to the server');
        return;
    }
    
    socket.emit('join', { username, room });
}

// Send chat message
function sendMessage(message) {
    if (!socket) {
        alert('Not connected to the server');
        return;
    }
    
    socket.emit('message', { message });
}

// Leave chat room
function leaveRoom() {
    if (!socket) {
        alert('Not connected to the server');
        return;
    }
    
    socket.emit('leave', {});
    showLoginForm();
}

// Format timestamp
function formatTimestamp(timestamp) {
    const date = new Date(timestamp);
    return date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
}

// Add message to chat
function addMessageToChat(message) {
    const messageElement = document.createElement('div');
    messageElement.classList.add('message');
    
    // Determine message type and add appropriate class
    if (message.type === 'system') {
        messageElement.classList.add('message-system');
        messageElement.innerHTML = `
            <div class="message-content">${message.content}</div>
            <div class="message-time">${formatTimestamp(message.timestamp)}</div>
        `;
    } else {
        // Check if this is the current user's message
        const isCurrentUser = message.username === username;
        messageElement.classList.add(isCurrentUser ? 'message-user' : 'message-other');
        
        messageElement.innerHTML = `
            <div class="message-header">
                <span class="message-sender">${isCurrentUser ? 'You' : message.username}</span>
                <span class="message-time">${formatTimestamp(message.timestamp)}</span>
            </div>
            <div class="message-content">${message.content}</div>
        `;
    }
    
    // Insert before typing indicator if it exists
    if (!typingIndicator.classList.contains('d-none')) {
        messagesContainer.insertBefore(messageElement, typingIndicator);
    } else {
        messagesContainer.appendChild(messageElement);
    }
}

// Update active users list
function updateActiveUsers(users) {
    // Clear current list
    usersList.innerHTML = '';
    
    // Add each user
    users.forEach(user => {
        const userItem = document.createElement('li');
        userItem.classList.add('list-group-item', 'user-item');
        
        // Highlight current user
        if (user === username) {
            userItem.classList.add('active');
            userItem.innerHTML = `${user} <span class="badge bg-light text-dark float-end">You</span>`;
        } else {
            userItem.textContent = user;
        }
        
        usersList.appendChild(userItem);
    });
}

// Scroll chat to bottom
function scrollToBottom() {
    messagesContainer.scrollTop = messagesContainer.scrollHeight;
}

// Show chat interface
function showChatInterface() {
    loginContainer.classList.add('d-none');
    chatContainer.classList.remove('d-none');
    currentUserElement.textContent = username;
    currentRoomElement.textContent = currentRoom;
    messageInput.focus();
}

// Show login form
function showLoginForm() {
    chatContainer.classList.add('d-none');
    loginContainer.classList.remove('d-none');
}

// Event: Login form submit
loginForm.addEventListener('submit', (e) => {
    e.preventDefault();
    
    username = document.getElementById('username').value.trim();
    currentRoom = document.getElementById('room').value.trim() || 'general';
    
    if (!username) {
        alert('Please enter a username');
        return;
    }
    
    // Connect to server if not already connected
    if (!socket) {
        connectToServer();
    }
    
    // Join room
    joinRoom(username, currentRoom);
    showChatInterface();
});

// Event: Message form submit
messageForm.addEventListener('submit', (e) => {
    e.preventDefault();
    
    const message = messageInput.value.trim();
    if (!message) return;
    
    // Send message
    sendMessage(message);
    
    // Clear input
    messageInput.value = '';
    messageInput.focus();
    
    // Clear typing status
    if (typingTimeout) {
        clearTimeout(typingTimeout);
        socket.emit('typing', { typing: false });
    }
});

// Event: Leave button click
leaveButton.addEventListener('click', () => {
    leaveRoom();
});

// Event: Message input typing
messageInput.addEventListener('input', () => {
    // Clear existing timeout
    if (typingTimeout) clearTimeout(typingTimeout);
    
    // Emit typing event
    socket.emit('typing', { typing: true });
    
    // Set timeout to stop "typing" after 2 seconds of inactivity
    typingTimeout = setTimeout(() => {
        socket.emit('typing', { typing: false });
    }, 2000);
});

// Initialize the application
document.addEventListener('DOMContentLoaded', () => {
    showLoginForm();
});

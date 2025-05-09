"""
Authentication Concepts in Python Web Development

This module demonstrates various authentication methods commonly used in web applications.
It includes implementations of:
- Basic Authentication
- Session-based Authentication
- Token-based Authentication (JWT)
- OAuth 2.0 Flow (simplified)

These examples use Flask for simplicity but the concepts apply to any web framework.
"""

from flask import Flask, request, jsonify, session, redirect, url_for, render_template_string
from functools import wraps
import base64
import os
import json
import time
import hmac
import hashlib
import uuid
import requests
from urllib.parse import urlencode
import jwt

# Create Flask application
app = Flask(__name__)
app.secret_key = os.urandom(24)  # For session management

# --- Mock User Database ---
# In a real application, you would use a proper database with securely hashed passwords
USERS = {
    "alice": {
        "username": "alice",
        "password": "password123",  # NEVER store plain text passwords in real apps
        "email": "alice@example.com",
        "role": "admin"
    },
    "bob": {
        "username": "bob",
        "password": "password456",
        "email": "bob@example.com",
        "role": "user"
    }
}

# --- JWT Configuration ---
JWT_SECRET = "your-secret-key"  # In production, use a secure secret key
JWT_ALGORITHM = "HS256"
JWT_EXPIRATION = 3600  # 1 hour in seconds

# --- OAuth Configuration ---
# These would be provided by the OAuth provider (e.g., Google, GitHub)
OAUTH_CLIENT_ID = "your-client-id"
OAUTH_CLIENT_SECRET = "your-client-secret"
OAUTH_REDIRECT_URI = "http://localhost:5000/oauth/callback"
OAUTH_AUTH_URL = "https://example.com/oauth/authorize"  # Example OAuth provider URLs
OAUTH_TOKEN_URL = "https://example.com/oauth/token"
OAUTH_USER_INFO_URL = "https://example.com/oauth/userinfo"

# --- 1. Basic Authentication ---

def require_basic_auth(f):
    """Basic authentication decorator."""
    @wraps(f)
    def decorated(*args, **kwargs):
        auth_header = request.headers.get('Authorization')
        
        if not auth_header or not auth_header.startswith('Basic '):
            return jsonify({"error": "Basic authentication required"}), 401, {
                'WWW-Authenticate': 'Basic realm="Login Required"'
            }
        
        try:
            # Extract and decode credentials
            encoded_credentials = auth_header[6:]  # Remove 'Basic ' prefix
            decoded_credentials = base64.b64decode(encoded_credentials).decode('utf-8')
            username, password = decoded_credentials.split(':')
            
            # Validate credentials
            if username not in USERS or USERS[username]['password'] != password:
                return jsonify({"error": "Invalid credentials"}), 401
            
            # Attach user to request
            request.user = USERS[username]
            
        except Exception as e:
            return jsonify({"error": "Invalid authorization header"}), 401
        
        return f(*args, **kwargs)
    return decorated

@app.route('/api/basic/profile')
@require_basic_auth
def basic_profile():
    """Example endpoint using Basic Authentication."""
    return jsonify({
        "username": request.user["username"],
        "email": request.user["email"],
        "role": request.user["role"]
    })

# --- 2. Session-based Authentication ---

@app.route('/login', methods=['POST'])
def login():
    """Login endpoint for session-based authentication."""
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')
    
    if not username or not password:
        return jsonify({"error": "Username and password required"}), 400
    
    # Validate credentials
    if username not in USERS or USERS[username]['password'] != password:
        return jsonify({"error": "Invalid credentials"}), 401
    
    # Store user info in session
    session['user_id'] = username
    session['user_role'] = USERS[username]['role']
    
    return jsonify({
        "message": "Login successful",
        "username": username
    })

@app.route('/logout')
def logout():
    """Logout endpoint for session-based authentication."""
    # Clear session
    session.clear()
    return jsonify({"message": "Logout successful"})

def require_session_auth(f):
    """Session authentication decorator."""
    @wraps(f)
    def decorated(*args, **kwargs):
        if 'user_id' not in session:
            return jsonify({"error": "Authentication required"}), 401
        
        # Attach user to request
        request.user = USERS[session['user_id']]
        
        return f(*args, **kwargs)
    return decorated

@app.route('/api/session/profile')
@require_session_auth
def session_profile():
    """Example endpoint using Session Authentication."""
    return jsonify({
        "username": request.user["username"],
        "email": request.user["email"],
        "role": request.user["role"]
    })

# --- 3. Token-based Authentication (JWT) ---

def generate_jwt(username):
    """Generate a JWT token for a user."""
    payload = {
        "sub": username,
        "iat": int(time.time()),
        "exp": int(time.time()) + JWT_EXPIRATION,
        "role": USERS[username]["role"]
    }
    
    return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)

@app.route('/api/token', methods=['POST'])
def get_token():
    """Endpoint to obtain a JWT token."""
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')
    
    if not username or not password:
        return jsonify({"error": "Username and password required"}), 400
    
    # Validate credentials
    if username not in USERS or USERS[username]['password'] != password:
        return jsonify({"error": "Invalid credentials"}), 401
    
    # Generate token
    token = generate_jwt(username)
    
    return jsonify({
        "access_token": token,
        "token_type": "Bearer",
        "expires_in": JWT_EXPIRATION
    })

def require_jwt_auth(f):
    """JWT authentication decorator."""
    @wraps(f)
    def decorated(*args, **kwargs):
        auth_header = request.headers.get('Authorization')
        
        if not auth_header or not auth_header.startswith('Bearer '):
            return jsonify({"error": "Bearer token required"}), 401
        
        token = auth_header[7:]  # Remove 'Bearer ' prefix
        
        try:
            # Verify and decode token
            payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
            username = payload["sub"]
            
            if username not in USERS:
                return jsonify({"error": "Invalid token"}), 401
            
            # Check if token is expired
            if int(time.time()) > payload["exp"]:
                return jsonify({"error": "Token expired"}), 401
            
            # Attach user to request
            request.user = USERS[username]
            request.token_payload = payload
            
        except jwt.InvalidTokenError:
            return jsonify({"error": "Invalid token"}), 401
        
        return f(*args, **kwargs)
    return decorated

@app.route('/api/jwt/profile')
@require_jwt_auth
def jwt_profile():
    """Example endpoint using JWT Authentication."""
    return jsonify({
        "username": request.user["username"],
        "email": request.user["email"],
        "role": request.user["role"],
        "token_exp": request.token_payload["exp"]
    })

# --- 4. OAuth 2.0 Flow ---

@app.route('/oauth/login')
def oauth_login():
    """Start OAuth 2.0 Authorization Code Flow."""
    # Generate a random state to prevent CSRF
    state = str(uuid.uuid4())
    session['oauth_state'] = state
    
    # Redirect user to OAuth provider
    params = {
        'client_id': OAUTH_CLIENT_ID,
        'redirect_uri': OAUTH_REDIRECT_URI,
        'response_type': 'code',
        'scope': 'profile email',
        'state': state
    }
    redirect_url = f"{OAUTH_AUTH_URL}?{urlencode(params)}"
    
    return redirect(redirect_url)

@app.route('/oauth/callback')
def oauth_callback():
    """Handle callback from OAuth provider."""
    error = request.args.get('error')
    if error:
        return jsonify({"error": error}), 400
    
    code = request.args.get('code')
    state = request.args.get('state')
    
    # Verify state to prevent CSRF
    if not state or state != session.get('oauth_state'):
        return jsonify({"error": "Invalid state parameter"}), 400
    
    # Exchange code for access token
    token_payload = {
        'grant_type': 'authorization_code',
        'code': code,
        'redirect_uri': OAUTH_REDIRECT_URI,
        'client_id': OAUTH_CLIENT_ID,
        'client_secret': OAUTH_CLIENT_SECRET
    }
    
    # In a real app, make an actual HTTP request
    # This is a simulation for demonstration purposes
    # response = requests.post(OAUTH_TOKEN_URL, data=token_payload)
    # token_data = response.json()
    
    # Simulate token response
    token_data = {
        'access_token': 'simulated-access-token',
        'token_type': 'Bearer',
        'expires_in': 3600,
        'refresh_token': 'simulated-refresh-token'
    }
    
    # Get user info using access token
    # In a real app, make an actual HTTP request
    # headers = {'Authorization': f"Bearer {token_data['access_token']}"}
    # user_response = requests.get(OAUTH_USER_INFO_URL, headers=headers)
    # user_info = user_response.json()
    
    # Simulate user info response
    user_info = {
        'id': '12345',
        'email': 'oauth_user@example.com',
        'name': 'OAuth User'
    }
    
    # Store user info in session
    session['user_id'] = user_info['id']
    session['user_email'] = user_info['email']
    session['user_name'] = user_info['name']
    session['access_token'] = token_data['access_token']
    
    return redirect('/oauth/profile')

@app.route('/oauth/profile')
def oauth_profile():
    """Display OAuth user profile."""
    if 'user_id' not in session or 'access_token' not in session:
        return redirect('/oauth/login')
    
    return jsonify({
        'id': session['user_id'],
        'name': session['user_name'],
        'email': session['user_email']
    })

# --- 5. Role-Based Access Control (RBAC) ---

def require_role(role):
    """Decorator for role-based access control."""
    def decorator(f):
        @wraps(f)
        def decorated(*args, **kwargs):
            # Ensure user is authenticated (using session in this example)
            if 'user_id' not in session:
                return jsonify({"error": "Authentication required"}), 401
            
            user_role = session.get('user_role')
            
            # Check if user has required role
            if user_role != role:
                return jsonify({"error": "Access denied. Insufficient permissions."}), 403
            
            return f(*args, **kwargs)
        return decorated
    return decorator

@app.route('/api/admin/dashboard')
@require_session_auth
@require_role('admin')
def admin_dashboard():
    """Admin-only endpoint."""
    return jsonify({
        "message": "Admin dashboard",
        "stats": {
            "users": len(USERS),
            "active_sessions": 42  # Just an example value
        }
    })

# --- 6. Multi-Factor Authentication (MFA) Simulation ---

# In a real application, you would use a proper TOTP library like pyotp
def generate_totp_code(secret, time_step=30):
    """Generate a simple TOTP code (this is a simplified example)."""
    counter = int(time.time() / time_step)
    hmac_hash = hmac.new(
        secret.encode(),
        counter.to_bytes(8, byteorder='big'),
        hashlib.sha1
    ).digest()
    
    offset = hmac_hash[-1] & 0xf
    code = ((hmac_hash[offset] & 0x7f) << 24 |
            (hmac_hash[offset + 1] & 0xff) << 16 |
            (hmac_hash[offset + 2] & 0xff) << 8 |
            (hmac_hash[offset + 3] & 0xff))
    
    return code % 1000000  # 6-digit code

@app.route('/api/mfa/setup', methods=['POST'])
@require_session_auth
def mfa_setup():
    """Set up MFA for a user."""
    # Generate a secret key for the user
    # In a real app, this would be stored securely in the database
    secret = base64.b32encode(os.urandom(10)).decode('utf-8')
    session['mfa_secret'] = secret
    
    # Return the secret and a current code for verification
    current_code = generate_totp_code(secret)
    
    return jsonify({
        "secret": secret,
        "current_code": current_code,
        "message": "Scan this secret with your authenticator app"
    })

@app.route('/api/mfa/verify', methods=['POST'])
@require_session_auth
def mfa_verify():
    """Verify a MFA code."""
    data = request.get_json()
    code = data.get('code')
    
    if not code:
        return jsonify({"error": "MFA code required"}), 400
    
    # Get the secret from the session (in a real app, retrieve from database)
    secret = session.get('mfa_secret')
    if not secret:
        return jsonify({"error": "MFA not set up"}), 400
    
    # Generate the current code
    current_code = generate_totp_code(secret)
    
    # Verify the code
    if int(code) != current_code:
        return jsonify({"error": "Invalid MFA code"}), 401
    
    # Mark user as MFA verified
    session['mfa_verified'] = True
    
    return jsonify({
        "message": "MFA verification successful"
    })

# --- 7. Password Reset Flow ---

# Store password reset tokens (in a real app, use a database)
RESET_TOKENS = {}

@app.route('/api/password/forgot', methods=['POST'])
def forgot_password():
    """Request a password reset."""
    data = request.get_json()
    email = data.get('email')
    
    if not email:
        return jsonify({"error": "Email required"}), 400
    
    # Find user by email
    user = None
    for u in USERS.values():
        if u['email'] == email:
            user = u
            break
    
    if not user:
        # Don't reveal if email exists or not for security
        return jsonify({
            "message": "If an account with that email exists, a password reset link has been sent."
        })
    
    # Generate a reset token
    token = str(uuid.uuid4())
    expiry = int(time.time()) + 3600  # 1 hour
    
    # Store token
    RESET_TOKENS[token] = {
        "username": user['username'],
        "expiry": expiry
    }
    
    # In a real app, send an email with the reset link
    reset_link = f"http://localhost:5000/reset-password?token={token}"
    
    return jsonify({
        "message": "If an account with that email exists, a password reset link has been sent.",
        "reset_link": reset_link  # Only included for demonstration
    })

@app.route('/api/password/reset', methods=['POST'])
def reset_password():
    """Reset a password using a token."""
    data = request.get_json()
    token = data.get('token')
    new_password = data.get('new_password')
    
    if not token or not new_password:
        return jsonify({"error": "Token and new password required"}), 400
    
    # Validate token
    if token not in RESET_TOKENS:
        return jsonify({"error": "Invalid or expired token"}), 400
    
    token_data = RESET_TOKENS[token]
    
    # Check if token is expired
    if int(time.time()) > token_data['expiry']:
        del RESET_TOKENS[token]
        return jsonify({"error": "Token expired"}), 400
    
    # Update password
    username = token_data['username']
    USERS[username]['password'] = new_password
    
    # Delete used token
    del RESET_TOKENS[token]
    
    return jsonify({
        "message": "Password reset successful"
    })

# --- 8. API Key Authentication ---

# API keys (in a real app, use a secure database and proper hashing)
API_KEYS = {
    "api_key_1": {
        "client": "mobile_app",
        "permissions": ["read"]
    },
    "api_key_2": {
        "client": "admin_dashboard",
        "permissions": ["read", "write"]
    }
}

def require_api_key(permissions=None):
    """API key authentication decorator."""
    def decorator(f):
        @wraps(f)
        def decorated(*args, **kwargs):
            api_key = request.headers.get('X-API-Key')
            
            if not api_key or api_key not in API_KEYS:
                return jsonify({"error": "Invalid API key"}), 401
            
            # Check permissions if specified
            if permissions:
                client_permissions = API_KEYS[api_key]["permissions"]
                if not all(perm in client_permissions for perm in permissions):
                    return jsonify({"error": "Insufficient permissions"}), 403
            
            # Attach client info to request
            request.client = API_KEYS[api_key]["client"]
            
            return f(*args, **kwargs)
        return decorated
    return decorator

@app.route('/api/data')
@require_api_key(permissions=["read"])
def get_data():
    """API endpoint requiring an API key with read permission."""
    return jsonify({
        "client": request.client,
        "data": {
            "message": "This is protected data accessible with an API key"
        }
    })

@app.route('/api/data', methods=['POST'])
@require_api_key(permissions=["write"])
def update_data():
    """API endpoint requiring an API key with write permission."""
    data = request.get_json()
    
    return jsonify({
        "client": request.client,
        "message": "Data updated successfully",
        "received": data
    })

# --- HTML Templates for Authentication Demos ---

# Simple login form
LOGIN_FORM = """
<!DOCTYPE html>
<html>
<head>
    <title>Login</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 0; padding: 20px; }
        .container { max-width: 400px; margin: 0 auto; }
        .form-group { margin-bottom: 15px; }
        label { display: block; margin-bottom: 5px; }
        input[type="text"], input[type="password"] { width: 100%; padding: 8px; box-sizing: border-box; }
        button { background: #4CAF50; color: white; padding: 10px 15px; border: none; cursor: pointer; }
        .error { color: red; margin-bottom: 15px; }
    </style>
</head>
<body>
    <div class="container">
        <h1>Login</h1>
        <div id="error-message" class="error" style="display: none;"></div>
        <div class="form-group">
            <label for="username">Username:</label>
            <input type="text" id="username" name="username">
        </div>
        <div class="form-group">
            <label for="password">Password:</label>
            <input type="password" id="password" name="password">
        </div>
        <button onclick="login()">Login</button>
        <p>Try: username=alice, password=password123</p>
    </div>
    
    <script>
        function login() {
            const username = document.getElementById('username').value;
            const password = document.getElementById('password').value;
            
            if (!username || !password) {
                showError('Username and password are required');
                return;
            }
            
            fetch('/login', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ username, password }),
            })
            .then(response => response.json())
            .then(data => {
                if (data.error) {
                    showError(data.error);
                } else {
                    window.location.href = '/profile';
                }
            })
            .catch(error => {
                showError('An error occurred');
            });
        }
        
        function showError(message) {
            const errorElement = document.getElementById('error-message');
            errorElement.textContent = message;
            errorElement.style.display = 'block';
        }
    </script>
</body>
</html>
"""

# User profile page
PROFILE_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>User Profile</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 0; padding: 20px; }
        .container { max-width: 600px; margin: 0 auto; }
        .profile { background: #f9f9f9; padding: 20px; border-radius: 5px; }
        .logout { margin-top: 20px; }
        .logout a { background: #f44336; color: white; padding: 10px 15px; text-decoration: none; }
    </style>
</head>
<body>
    <div class="container">
        <h1>User Profile</h1>
        <div class="profile">
            <h2>{{ username }}</h2>
            <p><strong>Email:</strong> {{ email }}</p>
            <p><strong>Role:</strong> {{ role }}</p>
        </div>
        <div class="logout">
            <a href="/logout">Logout</a>
        </div>
    </div>
</body>
</html>
"""

@app.route('/')
def index():
    """HTML login form."""
    return render_template_string(LOGIN_FORM)

@app.route('/profile')
@require_session_auth
def profile():
    """HTML profile page."""
    return render_template_string(
        PROFILE_TEMPLATE,
        username=request.user["username"],
        email=request.user["email"],
        role=request.user["role"]
    )

# --- Authentication Concepts Explanation ---

"""
Authentication Concepts Demonstrated:

1. Basic Authentication:
   - Simple username/password transmitted in HTTP headers
   - Base64 encoded (not encrypted)
   - Sent with every request
   - Suitable for API authentication over HTTPS

2. Session-based Authentication:
   - User logs in once and receives a session cookie
   - Server stores session information
   - Stateful - server needs to maintain session data
   - Common in traditional web applications

3. Token-based Authentication (JWT):
   - Stateless - server doesn't need to store tokens
   - Self-contained - token includes all necessary information
   - Signed to prevent tampering
   - Can include expiration and other claims
   - Suitable for APIs and single-page applications

4. OAuth 2.0:
   - For third-party authentication
   - Allows delegated access without sharing credentials
   - Common flow: Authorization Code Grant
   - Used for "Login with Google/Facebook/GitHub" etc.

5. Role-Based Access Control (RBAC):
   - Restricts access based on user roles
   - Provides more granular security control
   - Can be combined with any authentication method

6. Multi-Factor Authentication (MFA):
   - Requires multiple forms of verification
   - Typically: something you know (password) + something you have (phone/token)
   - Time-based One-Time Password (TOTP) is a common implementation

7. Password Reset Flow:
   - Secure way to reset forgotten passwords
   - Uses time-limited tokens sent to verified email addresses
   - Follows security best practices to prevent account takeover

8. API Key Authentication:
   - Simple method for machine-to-machine authentication
   - No user context, typically tied to an application or client
   - Can include permissions or scopes

Security Best Practices:
1. Always use HTTPS
2. Store passwords securely (hashed with bcrypt/Argon2, not plain text)
3. Implement rate limiting to prevent brute force attacks
4. Use secure cookies with HttpOnly and Secure flags
5. Validate all user input
6. Implement proper logout mechanisms
7. Use short-lived tokens and secure token storage
8. Follow the principle of least privilege
"""

# --- Run Application ---

if __name__ == '__main__':
    print("Authentication Demo Running!")
    print("Open http://localhost:5000/ in your browser")
    app.run(debug=True)

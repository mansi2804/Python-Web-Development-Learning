"""
HTTP Basics in Python

This module demonstrates the core HTTP concepts in Python using the requests library
for client-side requests and a simple HTTP server for server-side responses.

Key Concepts:
- HTTP Methods (GET, POST, PUT, DELETE)
- HTTP Status Codes
- HTTP Headers
- Request and Response Structure
- URL Parsing
- Query Parameters
- Basic HTTP Server
"""

import requests
import json
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs
import threading
import time

# --- CLIENT-SIDE HTTP REQUESTS ---

def demonstrate_http_methods():
    """
    Demonstrate the main HTTP methods using the requests library.
    
    HTTP Methods:
    - GET: Retrieve data
    - POST: Create data
    - PUT: Update data (complete replacement)
    - PATCH: Update data (partial update)
    - DELETE: Delete data
    """
    # Define a test API endpoint (using JSONPlaceholder)
    base_url = "https://jsonplaceholder.typicode.com"
    
    print("\n=== HTTP Methods ===")
    
    # GET request - retrieve data
    print("\n1. GET Request:")
    response = requests.get(f"{base_url}/posts/1")
    print(f"Status Code: {response.status_code}")
    print(f"Response: {response.json()}")
    
    # POST request - create data
    print("\n2. POST Request:")
    new_post = {
        "title": "Python HTTP Basics",
        "body": "Learning about HTTP with Python",
        "userId": 1
    }
    response = requests.post(f"{base_url}/posts", json=new_post)
    print(f"Status Code: {response.status_code}")
    print(f"Response: {response.json()}")
    
    # PUT request - update (replace) data
    print("\n3. PUT Request:")
    updated_post = {
        "id": 1,
        "title": "Updated Title",
        "body": "Updated content",
        "userId": 1
    }
    response = requests.put(f"{base_url}/posts/1", json=updated_post)
    print(f"Status Code: {response.status_code}")
    print(f"Response: {response.json()}")
    
    # PATCH request - partial update
    print("\n4. PATCH Request:")
    patch_data = {
        "title": "Patched Title"
    }
    response = requests.patch(f"{base_url}/posts/1", json=patch_data)
    print(f"Status Code: {response.status_code}")
    print(f"Response: {response.json()}")
    
    # DELETE request - delete data
    print("\n5. DELETE Request:")
    response = requests.delete(f"{base_url}/posts/1")
    print(f"Status Code: {response.status_code}")
    if response.text:
        print(f"Response: {response.text}")
    else:
        print("Empty response (as expected for DELETE)")

def demonstrate_http_status_codes():
    """
    Demonstrate common HTTP status codes.
    
    Status Code Categories:
    - 1xx: Informational
    - 2xx: Success
    - 3xx: Redirection
    - 4xx: Client Error
    - 5xx: Server Error
    """
    print("\n=== HTTP Status Codes ===")
    
    # 200 OK - Successful request
    response = requests.get("https://httpbin.org/status/200")
    print(f"\n200 OK: {response.status_code} - {response.reason}")
    
    # 201 Created - Resource created
    response = requests.get("https://httpbin.org/status/201")
    print(f"201 Created: {response.status_code} - {response.reason}")
    
    # 204 No Content - Request succeeded but no content returned
    response = requests.get("https://httpbin.org/status/204")
    print(f"204 No Content: {response.status_code} - {response.reason}")
    
    # 301 Moved Permanently - Resource has moved permanently
    response = requests.get("https://httpbin.org/status/301", allow_redirects=False)
    print(f"301 Moved Permanently: {response.status_code} - {response.reason}")
    
    # 400 Bad Request - Client error (invalid syntax)
    response = requests.get("https://httpbin.org/status/400")
    print(f"400 Bad Request: {response.status_code} - {response.reason}")
    
    # 401 Unauthorized - Authentication required
    response = requests.get("https://httpbin.org/status/401")
    print(f"401 Unauthorized: {response.status_code} - {response.reason}")
    
    # 403 Forbidden - Server understands but refuses to authorize
    response = requests.get("https://httpbin.org/status/403")
    print(f"403 Forbidden: {response.status_code} - {response.reason}")
    
    # 404 Not Found - Resource not found
    response = requests.get("https://httpbin.org/status/404")
    print(f"404 Not Found: {response.status_code} - {response.reason}")
    
    # 500 Internal Server Error - Server error
    response = requests.get("https://httpbin.org/status/500")
    print(f"500 Internal Server Error: {response.status_code} - {response.reason}")

def demonstrate_http_headers():
    """
    Demonstrate HTTP headers in requests and responses.
    
    Common Headers:
    - Content-Type: Type of content being sent or received
    - Authorization: Authentication credentials
    - User-Agent: Client software information
    - Accept: Media types the client can process
    - Cache-Control: Caching directives
    """
    print("\n=== HTTP Headers ===")
    
    # Set custom headers in request
    custom_headers = {
        'User-Agent': 'Python HTTP Tutorial',
        'Accept': 'application/json',
        'X-Custom-Header': 'Custom Value'
    }
    
    # Send request with custom headers
    response = requests.get("https://httpbin.org/headers", headers=custom_headers)
    
    print("\nRequest Headers Sent:")
    request_headers = response.json()['headers']
    for key, value in request_headers.items():
        print(f"{key}: {value}")
    
    print("\nResponse Headers Received:")
    for key, value in response.headers.items():
        print(f"{key}: {value}")

def demonstrate_url_parsing():
    """
    Demonstrate URL parsing and query parameter handling.
    
    URL Components:
    - Scheme (http, https)
    - Netloc (domain, port)
    - Path
    - Query parameters
    - Fragment
    """
    print("\n=== URL Parsing and Query Parameters ===")
    
    # Example URL with query parameters
    url = "https://example.com/search?q=python&category=programming&page=1#results"
    
    # Parse URL
    parsed_url = urlparse(url)
    
    print(f"\nURL: {url}")
    print(f"Scheme: {parsed_url.scheme}")
    print(f"Network Location: {parsed_url.netloc}")
    print(f"Path: {parsed_url.path}")
    print(f"Query: {parsed_url.query}")
    print(f"Fragment: {parsed_url.fragment}")
    
    # Parse query parameters
    query_params = parse_qs(parsed_url.query)
    print("\nQuery Parameters:")
    for key, value in query_params.items():
        print(f"{key}: {value[0]}")
    
    # Sending request with query parameters
    params = {
        'q': 'python',
        'category': 'programming',
        'page': 1
    }
    response = requests.get("https://httpbin.org/get", params=params)
    print(f"\nFull URL with parameters: {response.url}")
    print(f"Response: {response.json()['args']}")

# --- SERVER-SIDE HTTP HANDLING ---

class SimpleHTTPRequestHandler(BaseHTTPRequestHandler):
    """
    A simple HTTP request handler to demonstrate server-side HTTP concepts.
    
    This handler supports:
    - GET requests returning JSON
    - POST requests that process a JSON payload
    - Basic routing based on path
    """
    
    def _set_headers(self, status_code=200, content_type='application/json'):
        """Set response headers."""
        self.send_response(status_code)
        self.send_header('Content-Type', content_type)
        self.send_header('Server', 'PythonHTTPDemo/1.0')
        self.end_headers()
    
    def _get_request_body(self):
        """Get and parse JSON request body."""
        content_length = int(self.headers.get('Content-Length', 0))
        body = self.rfile.read(content_length).decode('utf-8')
        return json.loads(body) if body else None
    
    def _parse_query_params(self):
        """Parse query parameters from the URL."""
        parsed_url = urlparse(self.path)
        return parse_qs(parsed_url.query)
    
    def do_GET(self):
        """Handle GET requests."""
        # Basic routing based on path
        parsed_url = urlparse(self.path)
        path = parsed_url.path
        
        if path == '/':
            # Root endpoint
            self._set_headers()
            response = {"message": "Welcome to the Python HTTP Server", "endpoints": ["/", "/users", "/echo"]}
            self.wfile.write(json.dumps(response).encode())
        
        elif path == '/users':
            # Users endpoint (example resource)
            self._set_headers()
            users = [
                {"id": 1, "name": "Alice", "email": "alice@example.com"},
                {"id": 2, "name": "Bob", "email": "bob@example.com"},
                {"id": 3, "name": "Charlie", "email": "charlie@example.com"},
            ]
            self.wfile.write(json.dumps(users).encode())
        
        elif path == '/echo':
            # Echo query parameters
            params = self._parse_query_params()
            self._set_headers()
            response = {"echo": params}
            self.wfile.write(json.dumps(response).encode())
        
        else:
            # 404 Not Found
            self._set_headers(404)
            response = {"error": "Not Found", "path": path}
            self.wfile.write(json.dumps(response).encode())
    
    def do_POST(self):
        """Handle POST requests."""
        if self.path == '/echo':
            # Echo back the POST data
            data = self._get_request_body()
            self._set_headers(201)  # 201 Created
            response = {"received": data}
            self.wfile.write(json.dumps(response).encode())
        
        elif self.path == '/users':
            # Create a new user (simulated)
            data = self._get_request_body()
            
            # Validate required fields
            if not data or 'name' not in data or 'email' not in data:
                self._set_headers(400)  # 400 Bad Request
                response = {"error": "Missing required fields: name and email"}
                self.wfile.write(json.dumps(response).encode())
                return
            
            # Simulate creating a new user
            user = {
                "id": 4,  # In a real app, this would be generated
                "name": data['name'],
                "email": data['email']
            }
            
            self._set_headers(201)  # 201 Created
            response = {"message": "User created successfully", "user": user}
            self.wfile.write(json.dumps(response).encode())
        
        else:
            # 404 Not Found
            self._set_headers(404)
            response = {"error": "Not Found", "path": self.path}
            self.wfile.write(json.dumps(response).encode())
    
    def do_PUT(self):
        """Handle PUT requests."""
        parsed_url = urlparse(self.path)
        path = parsed_url.path
        
        if path.startswith('/users/'):
            # Extract user ID from path
            try:
                user_id = int(path.split('/')[2])
                data = self._get_request_body()
                
                # Validate required fields
                if not data or 'name' not in data or 'email' not in data:
                    self._set_headers(400)  # 400 Bad Request
                    response = {"error": "Missing required fields: name and email"}
                    self.wfile.write(json.dumps(response).encode())
                    return
                
                # Simulate updating a user
                user = {
                    "id": user_id,
                    "name": data['name'],
                    "email": data['email']
                }
                
                self._set_headers(200)  # 200 OK
                response = {"message": f"User {user_id} updated successfully", "user": user}
                self.wfile.write(json.dumps(response).encode())
                
            except (IndexError, ValueError):
                self._set_headers(400)  # 400 Bad Request
                response = {"error": "Invalid user ID"}
                self.wfile.write(json.dumps(response).encode())
        else:
            # 404 Not Found
            self._set_headers(404)
            response = {"error": "Not Found", "path": path}
            self.wfile.write(json.dumps(response).encode())
    
    def do_DELETE(self):
        """Handle DELETE requests."""
        parsed_url = urlparse(self.path)
        path = parsed_url.path
        
        if path.startswith('/users/'):
            # Extract user ID from path
            try:
                user_id = int(path.split('/')[2])
                
                # Simulate deleting a user
                self._set_headers(204)  # 204 No Content
                # No response body for 204 status
                
            except (IndexError, ValueError):
                self._set_headers(400)  # 400 Bad Request
                response = {"error": "Invalid user ID"}
                self.wfile.write(json.dumps(response).encode())
        else:
            # 404 Not Found
            self._set_headers(404)
            response = {"error": "Not Found", "path": path}
            self.wfile.write(json.dumps(response).encode())

def start_http_server(port=8000):
    """Start a simple HTTP server in a separate thread."""
    server = HTTPServer(('localhost', port), SimpleHTTPRequestHandler)
    thread = threading.Thread(target=server.serve_forever)
    thread.daemon = True
    thread.start()
    print(f"\n=== HTTP Server Started on http://localhost:{port} ===")
    return server

def test_http_server(port=8000):
    """Test the HTTP server with various requests."""
    base_url = f"http://localhost:{port}"
    
    print("\n=== Testing HTTP Server ===")
    
    # Test GET request to root
    print("\n1. GET /")
    response = requests.get(f"{base_url}/")
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}")
    
    # Test GET request to users
    print("\n2. GET /users")
    response = requests.get(f"{base_url}/users")
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}")
    
    # Test GET request with query parameters
    print("\n3. GET /echo with query parameters")
    response = requests.get(f"{base_url}/echo?name=Python&version=3.9&type=interpreted")
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}")
    
    # Test POST request
    print("\n4. POST /users")
    data = {"name": "Dave", "email": "dave@example.com"}
    response = requests.post(f"{base_url}/users", json=data)
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}")
    
    # Test PUT request
    print("\n5. PUT /users/1")
    data = {"name": "Alice Updated", "email": "alice.new@example.com"}
    response = requests.put(f"{base_url}/users/1", json=data)
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}")
    
    # Test DELETE request
    print("\n6. DELETE /users/2")
    response = requests.delete(f"{base_url}/users/2")
    print(f"Status: {response.status_code}")
    if response.text:
        print(f"Response: {response.text}")
    else:
        print("Empty response (as expected for 204 status)")
    
    # Test unknown endpoint
    print("\n7. GET /unknown")
    response = requests.get(f"{base_url}/unknown")
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}")

def main():
    """Main function to demonstrate HTTP concepts."""
    print("=== Python HTTP Basics Demo ===")
    
    # Client-side demonstrations
    demonstrate_http_methods()
    demonstrate_http_status_codes()
    demonstrate_http_headers()
    demonstrate_url_parsing()
    
    # Server-side demonstrations
    server = start_http_server()
    time.sleep(1)  # Give server time to start
    test_http_server()
    
    # Keep server running for a while
    try:
        print("\nServer is running. Press Ctrl+C to stop.")
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\nShutting down server...")
        server.shutdown()
        print("Server stopped.")

if __name__ == "__main__":
    main()

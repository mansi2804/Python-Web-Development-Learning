"""
Flask Routing Examples

This module demonstrates various routing techniques in Flask.
Routing is the process of mapping URLs to handler functions.

Key Concepts:
- Basic routes
- Dynamic routes with URL variables
- Route converters
- HTTP methods
- URL building
"""

from flask import Flask, request, redirect, url_for

app = Flask(__name__)

# Basic route
@app.route('/')
def index():
    """Root endpoint returning a simple welcome message."""
    return '''
    <h1>Flask Routing Examples</h1>
    <ul>
        <li><a href="/hello/world">Basic parameter</a></li>
        <li><a href="/user/42">Integer parameter</a></li>
        <li><a href="/path/nested/route/example">Path parameter</a></li>
        <li><a href="/methods">GET method</a></li>
        <li>
            <form action="/methods" method="post">
                <button type="submit">POST method</button>
            </form>
        </li>
    </ul>
    '''

# Dynamic route with string parameter
@app.route('/hello/<name>')
def hello(name):
    """
    Dynamic route that accepts a string parameter.
    URL variables are passed as arguments to the view function.
    """
    return f'<h1>Hello, {name}!</h1>'

# Dynamic route with type converter
@app.route('/user/<int:user_id>')
def show_user(user_id):
    """
    Dynamic route with integer type converter.
    Flask supports these converters:
    - string: accepts any text without slashes (default)
    - int: accepts integers
    - float: accepts floating point values
    - path: like string but also accepts slashes
    - uuid: accepts UUID strings
    """
    return f'<h1>User ID: {user_id}</h1><p>This must be an integer.</p>'

# Path converter example
@app.route('/path/<path:subpath>')
def show_subpath(subpath):
    """Path converter that accepts slashes within the parameter."""
    return f'<h1>Subpath: {subpath}</h1><p>Notice this route can include forward slashes.</p>'

# Multiple HTTP methods
@app.route('/methods', methods=['GET', 'POST'])
def methods_demo():
    """
    Function handling multiple HTTP methods.
    Different logic is executed depending on the request method.
    """
    if request.method == 'POST':
        return '<h1>You sent a POST request</h1><a href="/methods">Back to GET</a>'
    else:
        return '''
        <h1>You sent a GET request</h1>
        <form method="post">
            <button type="submit">Send POST request</button>
        </form>
        '''

# URL building example
@app.route('/redirect-to-user/<int:user_id>')
def redirect_to_user(user_id):
    """
    Demonstrates URL building with url_for function.
    This is safer than hardcoding URLs, as it handles escaping.
    """
    # url_for takes the function name and any parameters needed
    return redirect(url_for('show_user', user_id=user_id))

if __name__ == '__main__':
    app.run(debug=True)

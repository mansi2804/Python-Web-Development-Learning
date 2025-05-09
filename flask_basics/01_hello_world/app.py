"""
Flask Hello World Application

This is a simple Flask application demonstrating the basics of setting up a web server
and creating routes. Flask is a lightweight WSGI web application framework designed
to make getting started quick and easy.

Key Concepts:
- Flask application instance
- Basic routing
- Running the development server
"""

from flask import Flask

# Create a Flask application instance
# The __name__ variable is a special Python variable that gets set to the name of the module
# in which it is used. Flask uses this to determine the root path of the application.
app = Flask(__name__)

# Route decorator maps a URL path to a function
# This is the simplest possible route - the root URL "/"
@app.route('/')
def hello_world():
    """Return a simple greeting message for the root URL."""
    return 'Hello, World! Welcome to Flask!'

# Additional route demonstrating a different URL path
@app.route('/about')
def about():
    """Return information about this demo application."""
    return 'This is a simple Flask application demonstrating basic routing.'

# Run the application if this file is executed directly
if __name__ == '__main__':
    # Debug mode provides helpful error messages and auto-reloads the server when code changes
    app.run(debug=True)
    # Note: Debug mode should be turned off in production environments

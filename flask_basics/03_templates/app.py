"""
Flask Template Examples

This module demonstrates how to use templates in Flask with the Jinja2 template engine.
Templates allow you to separate your Python code from your HTML, making your application
more maintainable and following the MVC (Model-View-Controller) pattern.

Key Concepts:
- Basic template rendering
- Template variables
- Template control structures (loops, conditionals)
- Template inheritance
- Template filters
"""

from flask import Flask, render_template
from datetime import datetime
import random

app = Flask(__name__)

# Sample data (acting as our "model")
class User:
    def __init__(self, username, email):
        self.username = username
        self.email = email

sample_users = [
    User('alice', 'alice@example.com'),
    User('bob', 'bob@example.com'),
    User('charlie', 'charlie@example.com'),
    User('dave', 'dave@example.com')
]

products = [
    {'id': 1, 'name': 'Laptop', 'price': 999.99, 'in_stock': True},
    {'id': 2, 'name': 'Smartphone', 'price': 699.99, 'in_stock': True},
    {'id': 3, 'name': 'Headphones', 'price': 199.99, 'in_stock': False},
    {'id': 4, 'name': 'Mouse', 'price': 29.99, 'in_stock': True},
    {'id': 5, 'name': 'Keyboard', 'price': 79.99, 'in_stock': False}
]

@app.route('/')
def index():
    """Render the index template with basic variable passing."""
    return render_template('index.html', 
                          title='Flask Templates',
                          current_time=datetime.now(),
                          random_number=random.randint(1, 100))

@app.route('/users')
def user_list():
    """Demonstrate rendering a list of objects and using a loop in the template."""
    return render_template('users.html', 
                          title='User List',
                          users=sample_users)

@app.route('/products')
def product_list():
    """
    Demonstrate more complex template features:
    - Conditionals
    - Loops with dictionaries
    - Formatting values
    """
    return render_template('products.html',
                          title='Product Catalog',
                          products=products)

@app.route('/inheritance')
def template_inheritance():
    """Demonstrate template inheritance through a different page."""
    return render_template('child.html',
                          title='Template Inheritance',
                          content='This page demonstrates how template inheritance works in Jinja2.')

@app.template_filter('currency')
def currency_filter(value):
    """
    Custom template filter for formatting currency.
    Template filters transform values directly in the template.
    """
    return f"${value:.2f}"

if __name__ == '__main__':
    app.run(debug=True)

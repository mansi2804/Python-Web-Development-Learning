"""
Basic HTML/CSS Integration with Python Flask

This module demonstrates how to integrate HTML and CSS with a Flask application.
It covers static file serving, templating, and basic form handling.

Key Concepts:
- Flask templating with Jinja2
- Serving static files (CSS, JavaScript, images)
- HTML forms and Flask form handling
- Responsive design integration
"""

from flask import Flask, render_template, request, redirect, url_for, flash, session
import os
import json
from datetime import datetime

# Create Flask application
app = Flask(__name__)
app.secret_key = 'development-key-for-demo-only'  # For flash messages and sessions

# --- Data Storage (In a real app, use a database) ---
DATA_FILE = os.path.join(os.path.dirname(__file__), 'data', 'products.json')

def load_products():
    """Load product data from JSON file."""
    try:
        if os.path.exists(DATA_FILE):
            with open(DATA_FILE, 'r') as f:
                return json.load(f)
        else:
            # Ensure data directory exists
            os.makedirs(os.path.dirname(DATA_FILE), exist_ok=True)
            # Return default products
            return [
                {
                    "id": 1,
                    "name": "Laptop",
                    "description": "Powerful laptop with the latest CPU and ample storage.",
                    "price": 999.99,
                    "image": "laptop.jpg",
                    "category": "Electronics"
                },
                {
                    "id": 2,
                    "name": "Smartphone",
                    "description": "Feature-rich smartphone with high-resolution camera.",
                    "price": 499.99,
                    "image": "smartphone.jpg",
                    "category": "Electronics"
                },
                {
                    "id": 3,
                    "name": "Headphones",
                    "description": "Noise-cancelling headphones for immersive audio experience.",
                    "price": 149.99,
                    "image": "headphones.jpg",
                    "category": "Accessories"
                }
            ]
    except Exception as e:
        print(f"Error loading products: {e}")
        return []

def save_products(products):
    """Save product data to JSON file."""
    try:
        with open(DATA_FILE, 'w') as f:
            json.dump(products, f, indent=2)
        return True
    except Exception as e:
        print(f"Error saving products: {e}")
        return False

def get_product_by_id(product_id):
    """Get a product by ID."""
    products = load_products()
    for product in products:
        if product['id'] == product_id:
            return product
    return None

# --- Routes ---

@app.route('/')
def index():
    """Home page route."""
    products = load_products()
    return render_template('index.html', products=products)

@app.route('/about')
def about():
    """About page route."""
    return render_template('about.html')

@app.route('/contact', methods=['GET', 'POST'])
def contact():
    """Contact page with form handling."""
    if request.method == 'POST':
        name = request.form.get('name', '')
        email = request.form.get('email', '')
        message = request.form.get('message', '')
        
        # In a real app, you would save this to a database or send an email
        # For demo purposes, just show a flash message
        flash(f"Thanks for your message, {name}! We'll respond to {email} soon.", 'success')
        return redirect(url_for('contact'))
    
    return render_template('contact.html')

@app.route('/products')
def products():
    """Products listing page."""
    products = load_products()
    category = request.args.get('category', '')
    
    # Filter by category if specified
    if category:
        products = [p for p in products if p['category'] == category]
    
    # Get unique categories for filter dropdown
    categories = sorted(set(p['category'] for p in load_products()))
    
    return render_template('products.html', products=products, categories=categories, selected_category=category)

@app.route('/products/<int:product_id>')
def product_detail(product_id):
    """Product detail page."""
    product = get_product_by_id(product_id)
    if not product:
        flash('Product not found', 'error')
        return redirect(url_for('products'))
    
    return render_template('product_detail.html', product=product)

@app.route('/products/add', methods=['GET', 'POST'])
def add_product():
    """Add a new product."""
    if request.method == 'POST':
        products = load_products()
        
        # Generate a new ID
        new_id = max([p['id'] for p in products], default=0) + 1
        
        # Create new product
        new_product = {
            'id': new_id,
            'name': request.form.get('name', ''),
            'description': request.form.get('description', ''),
            'price': float(request.form.get('price', 0)),
            'image': request.form.get('image', 'default.jpg'),
            'category': request.form.get('category', 'Other')
        }
        
        # Add to products list
        products.append(new_product)
        
        # Save to JSON file
        if save_products(products):
            flash('Product added successfully!', 'success')
        else:
            flash('Error saving product', 'error')
            
        return redirect(url_for('products'))
    
    # Get unique categories for dropdown
    categories = sorted(set(p['category'] for p in load_products()))
    
    return render_template('add_product.html', categories=categories)

@app.route('/products/<int:product_id>/edit', methods=['GET', 'POST'])
def edit_product(product_id):
    """Edit an existing product."""
    product = get_product_by_id(product_id)
    if not product:
        flash('Product not found', 'error')
        return redirect(url_for('products'))
    
    if request.method == 'POST':
        products = load_products()
        
        # Find the product to update
        for p in products:
            if p['id'] == product_id:
                p['name'] = request.form.get('name', '')
                p['description'] = request.form.get('description', '')
                p['price'] = float(request.form.get('price', 0))
                p['image'] = request.form.get('image', p['image'])
                p['category'] = request.form.get('category', 'Other')
                break
        
        # Save to JSON file
        if save_products(products):
            flash('Product updated successfully!', 'success')
        else:
            flash('Error updating product', 'error')
            
        return redirect(url_for('product_detail', product_id=product_id))
    
    # Get unique categories for dropdown
    categories = sorted(set(p['category'] for p in load_products()))
    
    return render_template('edit_product.html', product=product, categories=categories)

@app.route('/products/<int:product_id>/delete', methods=['POST'])
def delete_product(product_id):
    """Delete a product."""
    products = load_products()
    
    # Filter out the product to delete
    updated_products = [p for p in products if p['id'] != product_id]
    
    if len(updated_products) < len(products):
        # Product was found and removed
        if save_products(updated_products):
            flash('Product deleted successfully!', 'success')
        else:
            flash('Error deleting product', 'error')
    else:
        flash('Product not found', 'error')
    
    return redirect(url_for('products'))

# Custom filters for Jinja2 templates
@app.template_filter('currency')
def currency_format(value):
    """Format a number as currency."""
    return f"${value:.2f}"

@app.template_filter('truncate_description')
def truncate_description(text, length=100):
    """Truncate text to a specific length."""
    if len(text) <= length:
        return text
    return text[:length] + '...'

# Context processor for all templates
@app.context_processor
def utility_processor():
    """Add utility functions to template context."""
    def current_year():
        return datetime.now().year
    
    def categories_list():
        categories = sorted(set(p['category'] for p in load_products()))
        return categories
    
    return {
        'current_year': current_year,
        'categories_list': categories_list
    }

# --- Run the application ---
if __name__ == '__main__':
    app.run(debug=True)

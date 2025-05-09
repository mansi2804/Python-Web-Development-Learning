"""
Flask Database Integration Example

This module demonstrates how to integrate a database with Flask using SQLAlchemy.
SQLAlchemy is a SQL toolkit and Object-Relational Mapping (ORM) library for Python.

Key Concepts:
- Database configuration with Flask-SQLAlchemy
- Model definition with SQLAlchemy ORM
- Basic CRUD operations (Create, Read, Update, Delete)
- Database relationships
- Database migrations (mentioned but not implemented here)
"""

from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import os

app = Flask(__name__)
app.config['SECRET_KEY'] = 'database-example-secret-key'

# SQLite database configuration
base_dir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(base_dir, 'app.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize the database
db = SQLAlchemy(app)

# Define database models using SQLAlchemy's ORM
class User(db.Model):
    """User model with basic information and relationship to posts."""
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Define a one-to-many relationship with Post model
    posts = db.relationship('Post', backref='author', lazy=True)
    
    def __repr__(self):
        return f'<User {self.username}>'

class Post(db.Model):
    """Post model with relationship to a user."""
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    content = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Foreign key to link to the User model
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    
    # Define many-to-many relationship with Tag model
    tags = db.relationship('Tag', secondary='post_tags', backref=db.backref('posts', lazy='dynamic'))
    
    def __repr__(self):
        return f'<Post {self.title}>'

class Tag(db.Model):
    """Tag model for categorizing posts."""
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False)
    
    def __repr__(self):
        return f'<Tag {self.name}>'

# Association table for many-to-many relationship between Post and Tag
post_tags = db.Table('post_tags',
    db.Column('post_id', db.Integer, db.ForeignKey('post.id'), primary_key=True),
    db.Column('tag_id', db.Integer, db.ForeignKey('tag.id'), primary_key=True)
)

# Home page route
@app.route('/')
def index():
    """Display all users and posts."""
    users = User.query.all()
    posts = Post.query.order_by(Post.created_at.desc()).all()
    return render_template('index.html', users=users, posts=posts)

# User routes
@app.route('/users')
def list_users():
    """List all users."""
    users = User.query.all()
    return render_template('users.html', users=users)

@app.route('/users/create', methods=['GET', 'POST'])
def create_user():
    """Create a new user."""
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        
        # Check if user already exists
        existing_user = User.query.filter_by(username=username).first()
        if existing_user:
            flash('Username already exists', 'error')
            return redirect(url_for('create_user'))
            
        existing_email = User.query.filter_by(email=email).first()
        if existing_email:
            flash('Email already exists', 'error')
            return redirect(url_for('create_user'))
        
        # Create new user
        user = User(username=username, email=email)
        db.session.add(user)
        db.session.commit()
        
        flash('User created successfully', 'success')
        return redirect(url_for('list_users'))
        
    return render_template('create_user.html')

@app.route('/users/<int:user_id>')
def view_user(user_id):
    """View user details and their posts."""
    user = User.query.get_or_404(user_id)
    return render_template('view_user.html', user=user)

@app.route('/users/<int:user_id>/edit', methods=['GET', 'POST'])
def edit_user(user_id):
    """Edit an existing user."""
    user = User.query.get_or_404(user_id)
    
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        
        # Check if username exists and is not the current user
        existing_user = User.query.filter_by(username=username).first()
        if existing_user and existing_user.id != user_id:
            flash('Username already exists', 'error')
            return redirect(url_for('edit_user', user_id=user_id))
            
        # Check if email exists and is not the current user
        existing_email = User.query.filter_by(email=email).first()
        if existing_email and existing_email.id != user_id:
            flash('Email already exists', 'error')
            return redirect(url_for('edit_user', user_id=user_id))
        
        # Update user
        user.username = username
        user.email = email
        db.session.commit()
        
        flash('User updated successfully', 'success')
        return redirect(url_for('view_user', user_id=user_id))
        
    return render_template('edit_user.html', user=user)

@app.route('/users/<int:user_id>/delete', methods=['POST'])
def delete_user(user_id):
    """Delete a user and all their posts."""
    user = User.query.get_or_404(user_id)
    
    # Delete all posts by this user first (cascade delete not implemented in this example)
    for post in user.posts:
        db.session.delete(post)
    
    # Delete the user
    db.session.delete(user)
    db.session.commit()
    
    flash('User deleted successfully', 'success')
    return redirect(url_for('list_users'))

# Post routes
@app.route('/posts')
def list_posts():
    """List all posts."""
    posts = Post.query.order_by(Post.created_at.desc()).all()
    return render_template('posts.html', posts=posts)

@app.route('/posts/create', methods=['GET', 'POST'])
def create_post():
    """Create a new post."""
    if request.method == 'POST':
        title = request.form['title']
        content = request.form['content']
        user_id = request.form['user_id']
        
        # Create new post
        post = Post(title=title, content=content, user_id=user_id)
        
        # Add tags if provided
        tag_names = request.form.get('tags', '').split(',')
        for tag_name in tag_names:
            tag_name = tag_name.strip()
            if tag_name:
                # Get or create tag
                tag = Tag.query.filter_by(name=tag_name).first()
                if not tag:
                    tag = Tag(name=tag_name)
                    db.session.add(tag)
                
                post.tags.append(tag)
        
        db.session.add(post)
        db.session.commit()
        
        flash('Post created successfully', 'success')
        return redirect(url_for('list_posts'))
        
    users = User.query.all()
    tags = Tag.query.all()
    return render_template('create_post.html', users=users, tags=tags)

@app.route('/posts/<int:post_id>')
def view_post(post_id):
    """View post details."""
    post = Post.query.get_or_404(post_id)
    return render_template('view_post.html', post=post)

@app.route('/posts/<int:post_id>/edit', methods=['GET', 'POST'])
def edit_post(post_id):
    """Edit an existing post."""
    post = Post.query.get_or_404(post_id)
    
    if request.method == 'POST':
        post.title = request.form['title']
        post.content = request.form['content']
        post.user_id = request.form['user_id']
        
        # Update tags
        post.tags.clear()
        tag_names = request.form.get('tags', '').split(',')
        for tag_name in tag_names:
            tag_name = tag_name.strip()
            if tag_name:
                # Get or create tag
                tag = Tag.query.filter_by(name=tag_name).first()
                if not tag:
                    tag = Tag(name=tag_name)
                    db.session.add(tag)
                
                post.tags.append(tag)
        
        db.session.commit()
        
        flash('Post updated successfully', 'success')
        return redirect(url_for('view_post', post_id=post_id))
        
    users = User.query.all()
    # Format tags for display
    tag_string = ', '.join([tag.name for tag in post.tags])
    return render_template('edit_post.html', post=post, users=users, tag_string=tag_string)

@app.route('/posts/<int:post_id>/delete', methods=['POST'])
def delete_post(post_id):
    """Delete a post."""
    post = Post.query.get_or_404(post_id)
    db.session.delete(post)
    db.session.commit()
    
    flash('Post deleted successfully', 'success')
    return redirect(url_for('list_posts'))

# Initialize the database tables
@app.before_first_request
def create_tables():
    """Create all database tables before first request."""
    db.create_all()
    
    # Add some initial data if the database is empty
    if not User.query.first():
        # Create sample users
        user1 = User(username='admin', email='admin@example.com')
        user2 = User(username='demo', email='demo@example.com')
        db.session.add_all([user1, user2])
        db.session.commit()
        
        # Create sample tags
        tag1 = Tag(name='Flask')
        tag2 = Tag(name='SQLAlchemy')
        tag3 = Tag(name='Python')
        db.session.add_all([tag1, tag2, tag3])
        db.session.commit()
        
        # Create sample posts
        post1 = Post(
            title='Getting Started with Flask',
            content='Flask is a micro web framework written in Python...',
            user_id=1,
            tags=[tag1, tag3]
        )
        post2 = Post(
            title='SQLAlchemy ORM Tutorial',
            content='SQLAlchemy is the Python SQL toolkit and Object Relational Mapper...',
            user_id=1,
            tags=[tag2, tag3]
        )
        post3 = Post(
            title='Flask with SQLAlchemy',
            content='Integrating Flask with SQLAlchemy is straightforward...',
            user_id=2,
            tags=[tag1, tag2, tag3]
        )
        db.session.add_all([post1, post2, post3])
        db.session.commit()

if __name__ == '__main__':
    app.run(debug=True)

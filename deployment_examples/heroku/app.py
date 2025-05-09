"""
Sample Flask Application for Heroku Deployment

This is a simple Flask application configured for deployment to Heroku.
It includes proper database configuration, logging setup, and other
best practices for production deployment.
"""

import os
import logging
import sys
from datetime import datetime
from flask import Flask, jsonify, request, render_template
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_cors import CORS
from whitenoise import WhiteNoise

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger(__name__)

# Initialize Flask app
app = Flask(__name__)

# Enable CORS
CORS(app)

# Configure static file serving with WhiteNoise
app.wsgi_app = WhiteNoise(app.wsgi_app, root='static/')

# Database configuration
database_url = os.environ.get('DATABASE_URL', 'sqlite:///app.db')
# Fix Heroku's postgres:// vs postgresql:// issue
if database_url.startswith('postgres://'):
    database_url = database_url.replace('postgres://', 'postgresql://', 1)

app.config.update(
    SECRET_KEY=os.environ.get('SECRET_KEY', 'dev-key-for-testing'),
    SQLALCHEMY_DATABASE_URI=database_url,
    SQLALCHEMY_TRACK_MODIFICATIONS=False,
    DEBUG=os.environ.get('FLASK_ENV') == 'development',
)

# Initialize SQLAlchemy and Flask-Migrate
db = SQLAlchemy(app)
migrate = Migrate(app, db)

# Models
class Task(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=True)
    completed = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'description': self.description,
            'completed': self.completed,
            'created_at': self.created_at.isoformat()
        }

# Routes
@app.route('/')
def index():
    """Render the homepage."""
    app.logger.info('Homepage accessed')
    return render_template('index.html', app_name="Heroku Flask Demo")

@app.route('/api/tasks', methods=['GET'])
def get_tasks():
    """Get all tasks."""
    tasks = Task.query.all()
    return jsonify([task.to_dict() for task in tasks])

@app.route('/api/tasks/<int:task_id>', methods=['GET'])
def get_task(task_id):
    """Get a specific task by ID."""
    task = Task.query.get_or_404(task_id)
    return jsonify(task.to_dict())

@app.route('/api/tasks', methods=['POST'])
def create_task():
    """Create a new task."""
    data = request.get_json()
    
    if not data or 'title' not in data:
        return jsonify({'error': 'Title is required'}), 400
    
    task = Task(
        title=data['title'],
        description=data.get('description', ''),
        completed=data.get('completed', False)
    )
    
    db.session.add(task)
    db.session.commit()
    
    app.logger.info(f'Created task: {task.id}')
    return jsonify(task.to_dict()), 201

@app.route('/api/tasks/<int:task_id>', methods=['PUT'])
def update_task(task_id):
    """Update an existing task."""
    task = Task.query.get_or_404(task_id)
    data = request.get_json()
    
    if 'title' in data:
        task.title = data['title']
    
    if 'description' in data:
        task.description = data['description']
    
    if 'completed' in data:
        task.completed = data['completed']
    
    db.session.commit()
    app.logger.info(f'Updated task: {task.id}')
    
    return jsonify(task.to_dict())

@app.route('/api/tasks/<int:task_id>', methods=['DELETE'])
def delete_task(task_id):
    """Delete a task."""
    task = Task.query.get_or_404(task_id)
    
    db.session.delete(task)
    db.session.commit()
    app.logger.info(f'Deleted task: {task_id}')
    
    return jsonify({'message': 'Task deleted'})

@app.route('/health')
def health_check():
    """Health check endpoint for monitoring."""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.utcnow().isoformat(),
        'environment': os.environ.get('FLASK_ENV', 'production')
    })

# Error handlers
@app.errorhandler(404)
def not_found_error(error):
    """Handle 404 errors."""
    app.logger.warning(f'404 error: {request.path}')
    return jsonify({'error': 'Resource not found'}), 404

@app.errorhandler(500)
def internal_error(error):
    """Handle 500 errors."""
    db.session.rollback()  # Roll back the session in case of database errors
    app.logger.error(f'Server Error: {error}')
    return jsonify({'error': 'Internal server error'}), 500

# Create all database tables
with app.app_context():
    if not app.config['SQLALCHEMY_DATABASE_URI'].startswith('postgresql'):
        # Only auto-create tables for SQLite (for development)
        # In production, we use Flask-Migrate
        db.create_all()
        app.logger.info('Created database tables (SQLite only)')

# Run the application
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)

#!/usr/bin/env python
"""
Database management script for Heroku deployments.
This script handles database migrations and initialization.
"""

import os
import sys
import logging
from urllib.parse import urlparse

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger(__name__)

def parse_database_url():
    """Parse the DATABASE_URL environment variable."""
    try:
        url = os.environ.get('DATABASE_URL')
        if not url:
            logger.warning("DATABASE_URL not found. Using default SQLite database.")
            return {
                'engine': 'sqlite',
                'name': 'app.db',
                'user': None,
                'password': None,
                'host': None,
                'port': None
            }
        
        # Parse the URL
        parsed_url = urlparse(url)
        
        # Handle Heroku's postgres:// vs postgresql:// issue
        engine = parsed_url.scheme
        if engine == 'postgres':
            engine = 'postgresql'
        
        # Extract database details
        db_info = {
            'engine': engine,
            'name': parsed_url.path[1:],  # Remove leading slash
            'user': parsed_url.username,
            'password': parsed_url.password,
            'host': parsed_url.hostname,
            'port': parsed_url.port
        }
        
        logger.info(f"Parsed database: {engine}://{db_info['host']}:{db_info['port']}/{db_info['name']}")
        return db_info
    
    except Exception as e:
        logger.error(f"Error parsing DATABASE_URL: {e}")
        sys.exit(1)

def run_migrations():
    """Run database migrations."""
    logger.info("Starting database migrations...")
    
    db_info = parse_database_url()
    
    # Import Flask app and SQLAlchemy instance
    try:
        # In a real app, you might use Flask-Migrate or Alembic
        # This is a simplified example
        from app import app, db
        
        with app.app_context():
            logger.info("Creating all database tables...")
            db.create_all()
            logger.info("Database tables created successfully!")
    
    except ImportError:
        logger.error("Could not import Flask application. Make sure app.py exists.")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Migration error: {e}")
        sys.exit(1)

def seed_data():
    """Seed initial data if the database is empty."""
    logger.info("Checking if database needs seeding...")
    
    try:
        from app import app, db, Task
        
        with app.app_context():
            # Check if we need to seed data
            task_count = Task.query.count()
            
            if task_count == 0:
                logger.info("Seeding initial data...")
                
                # Create sample tasks
                tasks = [
                    Task(title="Learn Flask", description="Study Flask web framework", completed=True),
                    Task(title="Deploy to Heroku", description="Follow the deployment guide", completed=False),
                    Task(title="Add a database", description="Integrate PostgreSQL with the application", completed=False)
                ]
                
                db.session.add_all(tasks)
                db.session.commit()
                
                logger.info(f"Added {len(tasks)} sample tasks to the database")
            else:
                logger.info(f"Database already contains {task_count} tasks. Skipping seed.")
    
    except Exception as e:
        logger.error(f"Error seeding data: {e}")
        # Don't exit the process here, as this is not a critical error

def main():
    """Main function to run all database management tasks."""
    logger.info("Starting database management...")
    
    # Run migrations
    run_migrations()
    
    # Seed initial data
    seed_data()
    
    logger.info("Database management completed successfully!")

if __name__ == "__main__":
    main()

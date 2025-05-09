"""
Database connection module for FastAPI application.

This module sets up the SQLAlchemy engine, session management, and database dependency.
It uses SQLite for simplicity, but can be configured to use other databases.

Key concepts:
- SQLAlchemy engine creation
- Session management
- Dependency injection for database sessions
"""

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os

# Database URL
# Using SQLite for simplicity - for production, use PostgreSQL, MySQL, etc.
# Example PostgreSQL URL: postgresql://user:password@localhost/dbname
SQLALCHEMY_DATABASE_URL = "sqlite:///./books.db"

# Create the SQLAlchemy engine
engine = create_engine(
    SQLALCHEMY_DATABASE_URL, 
    connect_args={"check_same_thread": False}  # Only needed for SQLite
)

# Create a SessionLocal class
# Each instance of this class will be a database session
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create a Base class
# This class will be inherited by all the SQLAlchemy models
Base = declarative_base()

# Database dependency
def get_db():
    """
    Database session dependency.
    
    This function creates a new database session for each request.
    It will be closed when the request is finished.
    
    Yields:
        Session: SQLAlchemy database session
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

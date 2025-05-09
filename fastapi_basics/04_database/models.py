"""
SQLAlchemy models for the Book Management API.

This module defines the database models using SQLAlchemy ORM.
These models map to database tables and define the structure and relationships.

Key concepts:
- SQLAlchemy model definition
- Table relationships (one-to-many)
- Column types and constraints
- Model methods
"""

from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, Text, Float, Date, DateTime, func
from sqlalchemy.orm import relationship
from datetime import datetime

from database import Base

class Author(Base):
    """
    Author model for book authors.
    
    Attributes:
        id: Primary key
        name: Author's full name
        bio: Author's biography
        created_at: Timestamp of creation
        updated_at: Timestamp of last update
        books: Relationship to books written by this author
    """
    __tablename__ = "authors"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), unique=True, nullable=False)
    bio = Column(Text)
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)
    
    # Relationship with Book model (one-to-many)
    books = relationship("Book", back_populates="author", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Author {self.name}>"

class Category(Base):
    """
    Category model for book categorization.
    
    Attributes:
        id: Primary key
        name: Category name
        description: Category description
        created_at: Timestamp of creation
        updated_at: Timestamp of last update
        books: Relationship to books in this category
    """
    __tablename__ = "categories"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50), unique=True, nullable=False)
    description = Column(Text)
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)
    
    # Relationship with Book model (one-to-many)
    books = relationship("Book", back_populates="category", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Category {self.name}>"

class Book(Base):
    """
    Book model for book information.
    
    Attributes:
        id: Primary key
        title: Book title
        description: Book description
        publication_date: Date of publication
        price: Book price
        is_available: Whether the book is available
        created_at: Timestamp of creation
        updated_at: Timestamp of last update
        author_id: Foreign key to author
        author: Relationship to author
        category_id: Foreign key to category
        category: Relationship to category
    """
    __tablename__ = "books"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(200), nullable=False, index=True)
    description = Column(Text)
    publication_date = Column(Date)
    price = Column(Float(precision=2), nullable=False)
    is_available = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)
    
    # Foreign keys and relationships
    author_id = Column(Integer, ForeignKey("authors.id"), nullable=False)
    author = relationship("Author", back_populates="books")
    
    category_id = Column(Integer, ForeignKey("categories.id"), nullable=False)
    category = relationship("Category", back_populates="books")
    
    def __repr__(self):
        return f"<Book {self.title}>"

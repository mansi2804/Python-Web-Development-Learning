"""
FastAPI Database Integration Example

This module demonstrates how to integrate a database with FastAPI using SQLAlchemy ORM.
It implements a simple RESTful API for a book management system.

Key Concepts:
- SQLAlchemy ORM integration
- Pydantic models for request/response
- Database models
- Dependency injection
- CRUD operations with database
- Migrations with Alembic (mentioned but not implemented)
"""

from fastapi import FastAPI, Depends, HTTPException, status, Query, Path
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime
import uvicorn
import os

# Import local modules
from models import Base, Book, Author, Category
from schemas import (
    BookCreate, BookUpdate, BookResponse,
    AuthorCreate, AuthorResponse,
    CategoryCreate, CategoryResponse
)
from database import engine, SessionLocal, get_db

# Create the database tables
Base.metadata.create_all(bind=engine)

# Create FastAPI application
app = FastAPI(
    title="Book Management API",
    description="FastAPI application with SQLAlchemy ORM",
    version="0.1.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify the origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Helper Functions ---

def get_author(db: Session, author_id: int):
    """Get author by ID."""
    author = db.query(Author).filter(Author.id == author_id).first()
    if author is None:
        raise HTTPException(status_code=404, detail=f"Author with ID {author_id} not found")
    return author

def get_category(db: Session, category_id: int):
    """Get category by ID."""
    category = db.query(Category).filter(Category.id == category_id).first()
    if category is None:
        raise HTTPException(status_code=404, detail=f"Category with ID {category_id} not found")
    return category

def get_book(db: Session, book_id: int):
    """Get book by ID."""
    book = db.query(Book).filter(Book.id == book_id).first()
    if book is None:
        raise HTTPException(status_code=404, detail=f"Book with ID {book_id} not found")
    return book

# --- Author Routes ---

@app.post("/authors/", response_model=AuthorResponse, status_code=status.HTTP_201_CREATED)
def create_author(author: AuthorCreate, db: Session = Depends(get_db)):
    """
    Create a new author.
    
    Args:
        author: Author data
        db: Database session dependency
        
    Returns:
        The created author
    """
    # Check if author with same name already exists
    existing_author = db.query(Author).filter(Author.name == author.name).first()
    if existing_author:
        raise HTTPException(
            status_code=400,
            detail=f"Author with name '{author.name}' already exists"
        )
    
    # Create new author
    db_author = Author(
        name=author.name,
        bio=author.bio
    )
    db.add(db_author)
    db.commit()
    db.refresh(db_author)
    return db_author

@app.get("/authors/", response_model=List[AuthorResponse])
def read_authors(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    db: Session = Depends(get_db)
):
    """
    Get all authors with pagination.
    
    Args:
        skip: Number of authors to skip
        limit: Maximum number of authors to return
        db: Database session dependency
        
    Returns:
        List of authors
    """
    authors = db.query(Author).offset(skip).limit(limit).all()
    return authors

@app.get("/authors/{author_id}", response_model=AuthorResponse)
def read_author(author_id: int = Path(..., gt=0), db: Session = Depends(get_db)):
    """
    Get a specific author by ID.
    
    Args:
        author_id: Author ID
        db: Database session dependency
        
    Returns:
        The author data
        
    Raises:
        HTTPException: If author not found
    """
    return get_author(db, author_id)

# --- Category Routes ---

@app.post("/categories/", response_model=CategoryResponse, status_code=status.HTTP_201_CREATED)
def create_category(category: CategoryCreate, db: Session = Depends(get_db)):
    """
    Create a new category.
    
    Args:
        category: Category data
        db: Database session dependency
        
    Returns:
        The created category
    """
    # Check if category with same name already exists
    existing_category = db.query(Category).filter(Category.name == category.name).first()
    if existing_category:
        raise HTTPException(
            status_code=400,
            detail=f"Category with name '{category.name}' already exists"
        )
    
    # Create new category
    db_category = Category(
        name=category.name,
        description=category.description
    )
    db.add(db_category)
    db.commit()
    db.refresh(db_category)
    return db_category

@app.get("/categories/", response_model=List[CategoryResponse])
def read_categories(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    db: Session = Depends(get_db)
):
    """
    Get all categories with pagination.
    
    Args:
        skip: Number of categories to skip
        limit: Maximum number of categories to return
        db: Database session dependency
        
    Returns:
        List of categories
    """
    categories = db.query(Category).offset(skip).limit(limit).all()
    return categories

@app.get("/categories/{category_id}", response_model=CategoryResponse)
def read_category(category_id: int = Path(..., gt=0), db: Session = Depends(get_db)):
    """
    Get a specific category by ID.
    
    Args:
        category_id: Category ID
        db: Database session dependency
        
    Returns:
        The category data
        
    Raises:
        HTTPException: If category not found
    """
    return get_category(db, category_id)

# --- Book Routes ---

@app.post("/books/", response_model=BookResponse, status_code=status.HTTP_201_CREATED)
def create_book(book: BookCreate, db: Session = Depends(get_db)):
    """
    Create a new book.
    
    Args:
        book: Book data including author_id and category_id
        db: Database session dependency
        
    Returns:
        The created book
        
    Raises:
        HTTPException: If author or category not found
    """
    # Verify author exists
    author = get_author(db, book.author_id)
    
    # Verify category exists
    category = get_category(db, book.category_id)
    
    # Create new book
    db_book = Book(
        title=book.title,
        description=book.description,
        publication_date=book.publication_date,
        price=book.price,
        author_id=book.author_id,
        category_id=book.category_id,
        is_available=book.is_available
    )
    db.add(db_book)
    db.commit()
    db.refresh(db_book)
    return db_book

@app.get("/books/", response_model=List[BookResponse])
def read_books(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    title: Optional[str] = None,
    author_id: Optional[int] = None,
    category_id: Optional[int] = None,
    is_available: Optional[bool] = None,
    db: Session = Depends(get_db)
):
    """
    Get all books with filtering and pagination.
    
    Args:
        skip: Number of books to skip
        limit: Maximum number of books to return
        title: Optional title filter (contains)
        author_id: Optional author filter
        category_id: Optional category filter
        is_available: Optional availability filter
        db: Database session dependency
        
    Returns:
        List of books matching the criteria
    """
    # Start with base query
    query = db.query(Book)
    
    # Apply filters if provided
    if title:
        query = query.filter(Book.title.contains(title))
    if author_id:
        query = query.filter(Book.author_id == author_id)
    if category_id:
        query = query.filter(Book.category_id == category_id)
    if is_available is not None:
        query = query.filter(Book.is_available == is_available)
    
    # Apply pagination
    books = query.offset(skip).limit(limit).all()
    return books

@app.get("/books/{book_id}", response_model=BookResponse)
def read_book(book_id: int = Path(..., gt=0), db: Session = Depends(get_db)):
    """
    Get a specific book by ID.
    
    Args:
        book_id: Book ID
        db: Database session dependency
        
    Returns:
        The book data
        
    Raises:
        HTTPException: If book not found
    """
    return get_book(db, book_id)

@app.put("/books/{book_id}", response_model=BookResponse)
def update_book(
    book_id: int,
    book: BookUpdate,
    db: Session = Depends(get_db)
):
    """
    Update a book by ID.
    
    Args:
        book_id: Book ID to update
        book: Book data to update
        db: Database session dependency
        
    Returns:
        The updated book
        
    Raises:
        HTTPException: If book not found or related entities not found
    """
    # Get existing book
    db_book = get_book(db, book_id)
    
    # Check if author exists if changing
    if book.author_id is not None and book.author_id != db_book.author_id:
        get_author(db, book.author_id)
    
    # Check if category exists if changing
    if book.category_id is not None and book.category_id != db_book.category_id:
        get_category(db, book.category_id)
    
    # Update book attributes
    book_data = book.dict(exclude_unset=True)
    for key, value in book_data.items():
        setattr(db_book, key, value)
    
    db_book.updated_at = datetime.now()
    db.commit()
    db.refresh(db_book)
    return db_book

@app.delete("/books/{book_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_book(book_id: int = Path(..., gt=0), db: Session = Depends(get_db)):
    """
    Delete a book by ID.
    
    Args:
        book_id: Book ID to delete
        db: Database session dependency
        
    Raises:
        HTTPException: If book not found
    """
    # Get existing book
    db_book = get_book(db, book_id)
    
    # Delete the book
    db.delete(db_book)
    db.commit()
    return None

# Run the application
if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)

# To run this application:
# 1. Install dependencies: pip install fastapi uvicorn sqlalchemy
# 2. Run the application: python main.py
#
# Notes on SQLAlchemy and Database Usage:
# - This example uses SQLite by default (see database.py)
# - For production, replace with PostgreSQL, MySQL, etc.
# - Consider using migrations with Alembic for database schema changes
#
# Example API Usage:
# 1. Create categories and authors first
# 2. Then create books referencing those categories and authors
# 3. Use the GET endpoints to query the data

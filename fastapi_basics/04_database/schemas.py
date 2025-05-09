"""
Pydantic schemas for the Book Management API.

This module defines Pydantic models for request validation and response serialization.
These models are separate from the SQLAlchemy ORM models and define the API contract.

Key concepts:
- Pydantic model definition
- Request validation
- Response serialization
- Field validation and constraints
- Model inheritance
"""

from pydantic import BaseModel, Field, validator
from typing import List, Optional
from datetime import date, datetime

# --- Author Schemas ---

class AuthorBase(BaseModel):
    """Base schema for author data."""
    name: str = Field(..., min_length=1, max_length=100, example="Jane Austen")
    bio: Optional[str] = Field(None, example="Jane Austen was an English novelist...")

class AuthorCreate(AuthorBase):
    """Schema for creating an author."""
    pass

class AuthorResponse(AuthorBase):
    """Schema for author responses."""
    id: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        """Config for Pydantic to read data from ORM."""
        orm_mode = True

# --- Category Schemas ---

class CategoryBase(BaseModel):
    """Base schema for category data."""
    name: str = Field(..., min_length=1, max_length=50, example="Fiction")
    description: Optional[str] = Field(None, example="Fictional works of literature...")

class CategoryCreate(CategoryBase):
    """Schema for creating a category."""
    pass

class CategoryResponse(CategoryBase):
    """Schema for category responses."""
    id: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        orm_mode = True

# --- Book Schemas ---

class BookBase(BaseModel):
    """Base schema for book data."""
    title: str = Field(..., min_length=1, max_length=200, example="Pride and Prejudice")
    description: Optional[str] = Field(None, example="A novel of manners by Jane Austen...")
    publication_date: Optional[date] = Field(None, example="1813-01-28")
    price: float = Field(..., gt=0, example=12.99)
    is_available: bool = Field(True, example=True)

class BookCreate(BookBase):
    """Schema for creating a book."""
    author_id: int = Field(..., gt=0, example=1)
    category_id: int = Field(..., gt=0, example=1)
    
    @validator('price')
    def price_must_be_positive(cls, v):
        """Validate that price is positive."""
        if v <= 0:
            raise ValueError('Price must be greater than zero')
        return round(v, 2)  # Round to 2 decimal places

class BookUpdate(BaseModel):
    """Schema for updating a book (all fields optional)."""
    title: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = None
    publication_date: Optional[date] = None
    price: Optional[float] = Field(None, gt=0)
    is_available: Optional[bool] = None
    author_id: Optional[int] = Field(None, gt=0)
    category_id: Optional[int] = Field(None, gt=0)
    
    @validator('price')
    def price_must_be_positive(cls, v):
        """Validate that price is positive if provided."""
        if v is not None and v <= 0:
            raise ValueError('Price must be greater than zero')
        return round(v, 2) if v is not None else None  # Round to 2 decimal places

class BookResponse(BookBase):
    """Schema for book responses."""
    id: int
    author_id: int
    category_id: int
    created_at: datetime
    updated_at: datetime
    
    # Include related models
    author: AuthorResponse
    category: CategoryResponse
    
    class Config:
        orm_mode = True

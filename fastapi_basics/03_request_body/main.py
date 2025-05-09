"""
FastAPI Request Body Example

This module demonstrates how to handle request bodies in FastAPI.
Request bodies are data sent by the client to the API in HTTP requests.

Key Concepts:
- Pydantic models for request validation
- Different HTTP methods (POST, PUT, PATCH, DELETE)
- Field validation with Pydantic
- Nested models and complex data structures
- Response models
"""

from fastapi import FastAPI, HTTPException, status, Body, Query, Path
from pydantic import BaseModel, Field, EmailStr, validator
from typing import List, Dict, Optional, Set, Any, Union
import uuid
from datetime import datetime, date

# Create a FastAPI application instance
app = FastAPI(
    title="FastAPI Request Body Example",
    description="Demonstrates handling request bodies in FastAPI",
    version="0.1.0"
)

# ---------- Pydantic Models for Request/Response Bodies ----------

class ItemBase(BaseModel):
    """Base model for items with common fields."""
    name: str = Field(..., min_length=1, max_length=100, example="Widget")
    description: Optional[str] = Field(None, max_length=1000, example="A fantastic widget")
    price: float = Field(..., gt=0, example=19.99)
    tax: Optional[float] = Field(None, ge=0, example=3.5)
    tags: Set[str] = Field(default_factory=set, example=["gadget", "tool"])

    @validator('name')
    def name_must_not_contain_special_chars(cls, v):
        """Custom validator for the name field."""
        if any(char in v for char in "&<>?;:"):
            raise ValueError('name cannot contain special characters')
        return v.title()
    
    def calculate_total_price(self) -> float:
        """Calculate total price including tax."""
        if self.tax:
            return self.price * (1 + self.tax / 100)
        return self.price

class ItemCreate(ItemBase):
    """Model for creating a new item (without ID)."""
    pass

class Item(ItemBase):
    """Complete item model including ID and timestamps."""
    id: str
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        """Pydantic config for the model."""
        orm_mode = True  # Allows the model to read data from ORM objects

class ItemUpdate(BaseModel):
    """Model for updating an item (all fields optional)."""
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    description: Optional[str] = Field(None, max_length=1000)
    price: Optional[float] = Field(None, gt=0)
    tax: Optional[float] = Field(None, ge=0)
    tags: Optional[Set[str]] = None

class Address(BaseModel):
    """Address model for user profiles."""
    street: str
    city: str
    state: str
    zip_code: str
    country: str = "USA"

class UserBase(BaseModel):
    """Base user model with common fields."""
    username: str = Field(..., min_length=3, max_length=50, example="johndoe")
    email: EmailStr = Field(..., example="john@example.com")
    full_name: Optional[str] = Field(None, example="John Doe")
    birth_date: Optional[date] = Field(None, example="1990-01-01")

class UserCreate(UserBase):
    """Model for creating a user with password."""
    password: str = Field(..., min_length=8, example="securepassword123")

class User(UserBase):
    """Complete user model including ID and timestamps."""
    id: str
    created_at: datetime
    is_active: bool = True
    addresses: List[Address] = []
    
    class Config:
        orm_mode = True

# In-memory "database" for this example
items_db: Dict[str, Item] = {}
users_db: Dict[str, User] = {}

# ---------- API Endpoints ----------

# Create item (POST)
@app.post("/items/", response_model=Item, status_code=status.HTTP_201_CREATED)
async def create_item(item: ItemCreate) -> Item:
    """
    Create a new item.
    
    Args:
        item: The item data to create
        
    Returns:
        The created item with assigned ID and timestamps
        
    Example request body:
    ```json
    {
        "name": "Widget",
        "description": "A fantastic widget",
        "price": 19.99,
        "tax": 3.5,
        "tags": ["gadget", "tool"]
    }
    ```
    """
    # Generate a unique ID and timestamps
    item_id = str(uuid.uuid4())
    now = datetime.now()
    
    # Create the item object
    item_dict = item.dict()
    new_item = Item(
        id=item_id,
        created_at=now,
        **item_dict
    )
    
    # Store in "database"
    items_db[item_id] = new_item
    
    return new_item

# Read all items (GET)
@app.get("/items/", response_model=List[Item])
async def read_items(
    skip: int = Query(0, ge=0, description="Number of items to skip"),
    limit: int = Query(10, ge=1, le=100, description="Max number of items to return"),
    min_price: Optional[float] = Query(None, ge=0, description="Minimum price filter"),
    tag: Optional[str] = Query(None, description="Filter by tag")
) -> List[Item]:
    """
    Get all items with optional filtering.
    
    Args:
        skip: Number of items to skip (pagination)
        limit: Maximum number of items to return
        min_price: Optional minimum price filter
        tag: Optional tag to filter by
        
    Returns:
        List of items matching the criteria
    """
    # Apply filters
    filtered_items = list(items_db.values())
    
    if min_price is not None:
        filtered_items = [item for item in filtered_items if item.price >= min_price]
        
    if tag is not None:
        filtered_items = [item for item in filtered_items if tag in item.tags]
    
    # Apply pagination
    return filtered_items[skip : skip + limit]

# Read one item (GET)
@app.get("/items/{item_id}", response_model=Item)
async def read_item(
    item_id: str = Path(..., title="The ID of the item to get")
) -> Item:
    """
    Get a specific item by ID.
    
    Args:
        item_id: The unique identifier of the item
        
    Returns:
        The item data
        
    Raises:
        HTTPException: If the item is not found
    """
    if item_id not in items_db:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Item with ID {item_id} not found"
        )
    
    return items_db[item_id]

# Update item (PUT)
@app.put("/items/{item_id}", response_model=Item)
async def update_item(
    item_id: str,
    item: ItemBase
) -> Item:
    """
    Update an entire item by ID (complete replacement).
    
    Args:
        item_id: The unique identifier of the item to update
        item: The new item data
        
    Returns:
        The updated item
        
    Raises:
        HTTPException: If the item is not found
    """
    if item_id not in items_db:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Item with ID {item_id} not found"
        )
    
    # Get the existing item to preserve id and created_at
    existing_item = items_db[item_id]
    
    # Update the item
    updated_item = Item(
        id=existing_item.id,
        created_at=existing_item.created_at,
        updated_at=datetime.now(),
        **item.dict()
    )
    
    # Store in "database"
    items_db[item_id] = updated_item
    
    return updated_item

# Partial update item (PATCH)
@app.patch("/items/{item_id}", response_model=Item)
async def partial_update_item(
    item_id: str,
    item: ItemUpdate
) -> Item:
    """
    Partially update an item by ID (only specified fields).
    
    Args:
        item_id: The unique identifier of the item to update
        item: The fields to update
        
    Returns:
        The updated item
        
    Raises:
        HTTPException: If the item is not found
    """
    if item_id not in items_db:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Item with ID {item_id} not found"
        )
    
    # Get the existing item
    existing_item = items_db[item_id]
    
    # Create an update data dictionary, excluding None values
    update_data = item.dict(exclude_unset=True)
    
    # Update the existing item data
    existing_item_dict = existing_item.dict()
    for field, value in update_data.items():
        existing_item_dict[field] = value
    
    # Create the updated item
    updated_item = Item(
        **existing_item_dict,
        updated_at=datetime.now()
    )
    
    # Store in "database"
    items_db[item_id] = updated_item
    
    return updated_item

# Delete item (DELETE)
@app.delete("/items/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_item(item_id: str) -> None:
    """
    Delete an item by ID.
    
    Args:
        item_id: The unique identifier of the item to delete
        
    Raises:
        HTTPException: If the item is not found
    """
    if item_id not in items_db:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Item with ID {item_id} not found"
        )
    
    # Remove from "database"
    del items_db[item_id]

# Create user with complex nested data
@app.post("/users/", response_model=User, status_code=status.HTTP_201_CREATED)
async def create_user(
    user: UserCreate,
    addresses: List[Address] = Body(..., embed=True)  # Nested JSON
) -> User:
    """
    Create a new user with addresses.
    
    Args:
        user: User information including password
        addresses: List of addresses for the user
        
    Returns:
        The created user object
        
    Example request body:
    ```json
    {
        "user": {
            "username": "johndoe",
            "email": "john@example.com",
            "full_name": "John Doe",
            "birth_date": "1990-01-01",
            "password": "securepassword123"
        },
        "addresses": [
            {
                "street": "123 Main St",
                "city": "Anytown",
                "state": "CA",
                "zip_code": "12345",
                "country": "USA"
            }
        ]
    }
    ```
    """
    # Check if username already exists
    for existing_user in users_db.values():
        if existing_user.username == user.username:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Username already registered"
            )
    
    # In a real app, we would hash the password
    # password_hash = hash_password(user.password)
    
    # Generate user ID and timestamp
    user_id = str(uuid.uuid4())
    now = datetime.now()
    
    # Create user without the password field
    user_dict = user.dict(exclude={"password"})
    new_user = User(
        id=user_id,
        created_at=now,
        addresses=addresses,
        **user_dict
    )
    
    # Store in "database"
    users_db[user_id] = new_user
    
    return new_user

# Get user by ID
@app.get("/users/{user_id}", response_model=User)
async def read_user(user_id: str) -> User:
    """
    Get a user by ID.
    
    Args:
        user_id: The unique identifier of the user
        
    Returns:
        The user data
        
    Raises:
        HTTPException: If the user is not found
    """
    if user_id not in users_db:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with ID {user_id} not found"
        )
    
    return users_db[user_id]

# Add example data on startup
@app.on_event("startup")
async def create_example_data():
    """Create example data when the application starts."""
    # Create some example items
    example_items = [
        ItemCreate(
            name="Laptop",
            description="High-performance laptop with 16GB RAM",
            price=1299.99,
            tax=8.5,
            tags={"electronics", "computer"}
        ),
        ItemCreate(
            name="Coffee Mug",
            description="Ceramic mug with Python logo",
            price=12.99,
            tax=5.0,
            tags={"kitchen", "merchandise"}
        ),
        ItemCreate(
            name="Book",
            description="Python Programming: A Comprehensive Guide",
            price=49.99,
            tags={"book", "education"}
        )
    ]
    
    for item in example_items:
        item_id = str(uuid.uuid4())
        now = datetime.now()
        
        # Create the item object
        item_dict = item.dict()
        new_item = Item(
            id=item_id,
            created_at=now,
            **item_dict
        )
        
        # Store in "database"
        items_db[item_id] = new_item
    
    # Create an example user
    user_id = str(uuid.uuid4())
    now = datetime.now()
    
    example_user = User(
        id=user_id,
        created_at=now,
        username="demo_user",
        email="demo@example.com",
        full_name="Demo User",
        birth_date=date(1990, 1, 1),
        addresses=[
            Address(
                street="123 Main St",
                city="Anytown",
                state="CA",
                zip_code="12345",
                country="USA"
            )
        ]
    )
    
    users_db[user_id] = example_user

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)

# To run this application:
# 1. Install dependencies: pip install fastapi uvicorn pydantic[email]
# 2. Run the application: python main.py
#    or: uvicorn main:app --reload
#
# Explore the interactive API documentation at:
# - http://localhost:8000/docs
# - http://localhost:8000/redoc

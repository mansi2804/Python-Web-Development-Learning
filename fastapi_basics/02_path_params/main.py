"""
FastAPI Path Parameters Example

This module demonstrates how to use path parameters in FastAPI.
Path parameters are parts of the URL path that are extracted and passed to your functions.

Key Concepts:
- Path parameters with type annotations
- Path parameter validation
- Enum path parameters
- Multiple path parameters
- Path parameters with query parameters
"""

from fastapi import FastAPI, Path, Query, HTTPException
from enum import Enum
from typing import Dict, Optional, List, Union
from pydantic import BaseModel, Field

# Create a FastAPI application instance
app = FastAPI(
    title="FastAPI Path Parameters",
    description="Demonstrates various ways to use path parameters in FastAPI",
    version="0.1.0"
)

# Create an Enum for predefined category options
class CategoryEnum(str, Enum):
    """Enum for product categories."""
    electronics = "electronics"
    clothing = "clothing"
    books = "books"
    food = "food"
    other = "other"

# Create a Pydantic model for structured responses
class Product(BaseModel):
    """Product model with validation."""
    id: int
    name: str
    description: Optional[str] = None
    price: float = Field(..., gt=0, description="The price must be greater than zero")
    category: CategoryEnum
    tags: List[str] = []
    
    class Config:
        schema_extra = {
            "example": {
                "id": 1,
                "name": "Laptop",
                "description": "A high-performance laptop",
                "price": 999.99,
                "category": "electronics",
                "tags": ["computer", "technology"]
            }
        }

# Sample product data (simulating a database)
products = {
    1: Product(
        id=1,
        name="Laptop",
        description="A high-performance laptop",
        price=999.99,
        category=CategoryEnum.electronics,
        tags=["computer", "technology"]
    ),
    2: Product(
        id=2,
        name="T-Shirt",
        description="Cotton t-shirt",
        price=19.99,
        category=CategoryEnum.clothing,
        tags=["apparel", "casual"]
    ),
    3: Product(
        id=3,
        name="Python Cookbook",
        description="Recipes for mastering Python",
        price=39.99,
        category=CategoryEnum.books,
        tags=["programming", "education"]
    )
}

# Basic path parameter
@app.get("/products/{product_id}")
async def read_product(
    product_id: int = Path(..., title="The ID of the product to get", ge=1)
) -> Union[Product, Dict[str, str]]:
    """
    Get product details by ID.
    
    Args:
        product_id: The ID of the product to retrieve (must be >= 1)
        
    Returns:
        The product information or an error message
    
    Raises:
        HTTPException: If the product is not found
    """
    if product_id not in products:
        raise HTTPException(status_code=404, detail="Product not found")
    
    return products[product_id]

# Path parameter with enum type
@app.get("/categories/{category}")
async def read_category(category: CategoryEnum) -> Dict[str, Union[str, List[Product]]]:
    """
    Get products by category.
    
    Args:
        category: The category to filter by (must be one of the predefined categories)
        
    Returns:
        Dict containing the category name and matching products
    """
    filtered_products = [
        product for product in products.values() 
        if product.category == category
    ]
    
    return {
        "category": category,
        "products": filtered_products
    }

# Multiple path parameters
@app.get("/categories/{category}/products/{product_id}")
async def read_product_in_category(
    category: CategoryEnum,
    product_id: int = Path(..., ge=1)
) -> Union[Product, Dict[str, str]]:
    """
    Get a specific product within a category.
    
    Args:
        category: The category to filter by
        product_id: The ID of the product to retrieve
        
    Returns:
        The product information or an error message
        
    Raises:
        HTTPException: If the product is not found or doesn't belong to the specified category
    """
    if product_id not in products:
        raise HTTPException(status_code=404, detail="Product not found")
    
    product = products[product_id]
    if product.category != category:
        raise HTTPException(
            status_code=404, 
            detail=f"Product {product_id} not found in category {category}"
        )
    
    return product

# Path parameters with query parameters
@app.get("/products/{product_id}/similar")
async def read_similar_products(
    product_id: int = Path(..., ge=1),
    max_price: Optional[float] = Query(None, ge=0, description="Maximum price filter"),
    tags: Optional[List[str]] = Query(None, description="Tags to match")
) -> Dict[str, Union[Product, List[Product]]]:
    """
    Get similar products to the specified product.
    
    Args:
        product_id: The ID of the reference product
        max_price: Optional maximum price filter
        tags: Optional tags to match
        
    Returns:
        Dict containing the reference product and similar products
        
    Raises:
        HTTPException: If the reference product is not found
    """
    if product_id not in products:
        raise HTTPException(status_code=404, detail="Product not found")
    
    reference_product = products[product_id]
    
    # Find similar products (same category, optional filters)
    similar_products = []
    for pid, product in products.items():
        # Skip the reference product
        if pid == product_id:
            continue
            
        # Must be in the same category
        if product.category != reference_product.category:
            continue
            
        # Apply max_price filter if provided
        if max_price is not None and product.price > max_price:
            continue
            
        # Apply tags filter if provided
        if tags is not None and not any(tag in product.tags for tag in tags):
            continue
            
        similar_products.append(product)
    
    return {
        "product": reference_product,
        "similar_products": similar_products
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)

# To run this application:
# 1. Install dependencies: pip install fastapi uvicorn
# 2. Run the application: python main.py
#    or: uvicorn main:app --reload
#
# Example URLs to try:
# - http://localhost:8000/products/1
# - http://localhost:8000/categories/electronics
# - http://localhost:8000/categories/electronics/products/1
# - http://localhost:8000/products/1/similar
# - http://localhost:8000/products/1/similar?max_price=50
# - http://localhost:8000/products/1/similar?tags=technology&tags=computer

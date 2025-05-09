"""
FastAPI Hello World Example

This module demonstrates the basic setup for a FastAPI application.
FastAPI is a modern, fast web framework for building APIs with Python,
based on standard Python type hints.

Key Concepts:
- Creating a FastAPI application instance
- Defining route handlers with path operations
- Automatic documentation
- Running the application with Uvicorn
"""

from fastapi import FastAPI
from typing import Dict

# Create a FastAPI application instance
app = FastAPI(
    title="FastAPI Hello World",
    description="A simple FastAPI application demonstrating the basics",
    version="0.1.0"
)

# Define a route using a path operation decorator
@app.get("/")
async def root() -> Dict[str, str]:
    """
    Root endpoint returning a simple greeting message.
    
    Returns:
        dict: A JSON response with a message
    """
    return {"message": "Hello World from FastAPI!"}

# Additional route with a different path
@app.get("/about")
async def about() -> Dict[str, str]:
    """
    About endpoint with information about this demo.
    
    Returns:
        dict: A JSON response with information about the application
    """
    return {
        "app_name": "FastAPI Hello World",
        "framework": "FastAPI",
        "version": "0.1.0",
        "description": "This is a simple FastAPI application demonstrating the basics."
    }

# Health check endpoint
@app.get("/health")
async def health_check() -> Dict[str, str]:
    """
    Health check endpoint for monitoring.
    
    Returns:
        dict: A JSON response indicating the service is up
    """
    return {"status": "ok"}

if __name__ == "__main__":
    # This code block is executed when the script is run directly
    import uvicorn
    
    # Run the application using Uvicorn server
    # host="0.0.0.0" makes the server accessible from any network interface
    # port=8000 is the default port for FastAPI applications
    # reload=True enables auto-reload when code changes
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)

# To run this application:
# 1. Install dependencies: pip install fastapi uvicorn
# 2. Run the application: python main.py
#    or: uvicorn main:app --reload
#
# Once running, you can:
# - Visit http://localhost:8000/ for the main endpoint
# - Visit http://localhost:8000/docs for the automatic interactive API documentation
# - Visit http://localhost:8000/redoc for alternative API documentation

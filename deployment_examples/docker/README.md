# Deploying Python Web Applications with Docker

This guide demonstrates how to containerize and deploy Python web applications using Docker. Docker provides a consistent, isolated environment that makes deployment easier and more reliable across different platforms.

## What is Docker?

Docker is a platform that allows you to develop, ship, and run applications in containers. Containers are lightweight, portable, and isolated environments that package an application with all its dependencies.

Key benefits of Docker for Python web applications:

- **Consistency**: Same environment from development to production
- **Isolation**: Applications run in their own container with their own dependencies
- **Portability**: Deploy the same container across different platforms
- **Scalability**: Easily scale containers up or down based on demand
- **Version Control**: Track changes to both code and environment

## Prerequisites

To follow this guide, you need:

1. [Docker](https://docs.docker.com/get-docker/) installed on your machine
2. Basic understanding of Python web development
3. Git for version control (optional)

## Project Structure

This example uses a simple Flask application, but the principles apply to any Python web framework.

```
docker-example/
├── app/                # Flask application code
│   ├── __init__.py
│   ├── models.py
│   ├── routes.py
│   ├── static/
│   └── templates/
├── Dockerfile          # Docker configuration
├── docker-compose.yml  # Multi-container configuration
├── requirements.txt    # Python dependencies
├── .dockerignore       # Files to exclude from Docker build
└── entrypoint.sh       # Container startup script
```

## Step 1: Create a Dockerfile

The Dockerfile defines how to build your Docker image. Here's a robust example for a Python web application:

```dockerfile
# Use an official Python runtime as the base image
FROM python:3.9-slim

# Set working directory
WORKDIR /app

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    FLASK_APP=run.py \
    FLASK_ENV=production

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the project files
COPY . .

# Create a non-root user and switch to it
RUN useradd -m appuser
USER appuser

# Expose the port the app runs on
EXPOSE 5000

# Run the application
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "run:app"]
```

## Step 2: Create a .dockerignore File

A `.dockerignore` file prevents unnecessary files from being included in your Docker image:

```
__pycache__/
*.py[cod]
*$py.class
*.so
.env
.venv
env/
venv/
ENV/
.git/
.github/
.gitignore
.idea/
.vscode/
*.md
!README.md
Dockerfile
docker-compose.yml
```

## Step 3: Configure Docker Compose

Docker Compose helps manage multi-container applications. Create a `docker-compose.yml` file:

```yaml
version: '3.8'

services:
  web:
    build: .
    container_name: flask-web
    restart: always
    ports:
      - "5000:5000"
    environment:
      - DATABASE_URL=postgresql://postgres:postgres@db:5432/flask_db
      - SECRET_KEY=your_secret_key_here
    depends_on:
      - db
    networks:
      - app-network

  db:
    image: postgres:13
    container_name: postgres-db
    volumes:
      - postgres_data:/var/lib/postgresql/data/
    environment:
      - POSTGRES_USER=postgres
      - POSTGRES_PASSWORD=postgres
      - POSTGRES_DB=flask_db
    networks:
      - app-network

networks:
  app-network:
    driver: bridge

volumes:
  postgres_data:
```

## Step 4: Build and Run the Docker Containers

Build and start your containerized application:

```bash
# Build and start containers in detached mode
docker-compose up -d

# See logs
docker-compose logs -f

# Stop containers
docker-compose down
```

## Step 5: Deploying to Production

When deploying to production, consider:

### 1. Using Docker Registries

Push your Docker image to a registry like Docker Hub or AWS ECR:

```bash
# Log in to Docker Hub
docker login

# Tag your image
docker tag my-flask-app:latest username/my-flask-app:latest

# Push to Docker Hub
docker push username/my-flask-app:latest
```

### 2. Container Orchestration

For production deployments, consider using orchestration platforms:

- **Docker Swarm**: Simple, built into Docker
- **Kubernetes**: Powerful, industry-standard orchestration
- **Amazon ECS/EKS**: AWS container services
- **Google Kubernetes Engine**: Google Cloud's managed Kubernetes

### 3. CI/CD Integration

Automate your Docker builds with CI/CD pipelines (GitHub Actions, Jenkins, GitLab CI):

```yaml
# Example GitHub Actions workflow
name: Build and Deploy

on:
  push:
    branches: [ main ]

jobs:
  build:
    runs-on: ubuntu-latest
    
    steps:
    - uses: actions/checkout@v2
    
    - name: Build and push Docker image
      uses: docker/build-push-action@v2
      with:
        context: .
        push: true
        tags: username/my-flask-app:latest
```

## Best Practices for Docker with Python

1. **Use Multi-Stage Builds** to create smaller images
2. **Pin Package Versions** in requirements.txt for consistency
3. **Don't Run as Root** in your container
4. **Handle Signals Properly** to gracefully shut down your application
5. **Store Secrets Securely** using environment variables or secret management tools
6. **Optimize the Docker Image** to reduce size and build time
7. **Use Health Checks** to ensure your application is running correctly
8. **Log to stdout/stderr** for easy log collection

## Example: Advanced Dockerfile with Multi-Stage Build

```dockerfile
# Build stage
FROM python:3.9-slim AS builder

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip wheel --no-cache-dir --no-deps --wheel-dir /app/wheels -r requirements.txt

# Final stage
FROM python:3.9-slim

WORKDIR /app

# Create a non-root user
RUN useradd -m appuser

# Copy only the wheels and install
COPY --from=builder /app/wheels /wheels
RUN pip install --no-cache /wheels/*

# Copy application code
COPY --chown=appuser:appuser . .

# Switch to non-root user
USER appuser

EXPOSE 5000

HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
  CMD curl -f http://localhost:5000/health || exit 1

CMD ["gunicorn", "--bind", "0.0.0.0:5000", "run:app"]
```

## Conclusion

Docker provides a powerful way to package and deploy Python web applications. By containerizing your application, you ensure that it runs consistently across different environments, from development to production.

This guide covered the basics of Dockerizing a Python web application, but there's much more to explore. As you become more comfortable with Docker, you can implement more advanced patterns like microservices architecture and continuous deployment.

## Additional Resources

- [Docker Documentation](https://docs.docker.com/)
- [Docker Compose Documentation](https://docs.docker.com/compose/)
- [Docker Best Practices for Python](https://pythonspeed.com/docker/)
- [Docker Security Best Practices](https://snyk.io/blog/10-docker-image-security-best-practices/)

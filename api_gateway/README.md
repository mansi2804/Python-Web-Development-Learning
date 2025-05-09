# API Gateway with Python and Flask

This example demonstrates how to implement an API Gateway pattern using Python and Flask. The API Gateway serves as a single entry point for clients to interact with multiple microservices.

## Project Structure

```
api_gateway/
├── gateway/               # API Gateway implementation
│   ├── app.py             # Main API Gateway code
│   └── requirements.txt   # Gateway dependencies
└── services/              # Mock microservices
    ├── user_service.py    # User management service
    ├── product_service.py # Product catalog service 
    └── order_service.py   # Order management service
```

## Key Concepts Demonstrated

1. **Request Routing** - The API Gateway routes client requests to the appropriate backend service
2. **Load Balancing** - Simple implementation of load balancing across service instances
3. **Response Caching** - Caching GET responses to improve performance
4. **Authentication** - API key authentication for gateway access
5. **Rate Limiting** - Basic rate limiting to prevent abuse
6. **Service Discovery** - Simple service registry (simulated)

## How the API Gateway Works

The API Gateway acts as a reverse proxy that sits between clients and backend services. It provides the following benefits:

- **Simplified Client Interface** - Clients only need to interact with a single endpoint
- **Abstracted Service Architecture** - Hides the complexity of the underlying microservices
- **Centralized Cross-Cutting Concerns** - Authentication, monitoring, and rate limiting in one place
- **Reduced Client-Service Chattiness** - Aggregates data from multiple services if needed

## Running the Example

### Start the Mock Microservices

1. Start the User Service (two instances for load balancing):

```bash
# Instance 1
python services/user_service.py

# In another terminal (Instance 2)
INSTANCE=2 python services/user_service.py
```

2. Start the Product Service:

```bash
# Instance 1
python services/product_service.py

# In another terminal (Instance 2)
INSTANCE=2 python services/product_service.py
```

3. Start the Order Service:

```bash
# Instance 1
python services/order_service.py

# In another terminal (Instance 2)
INSTANCE=2 python services/order_service.py
```

### Start the API Gateway

```bash
cd gateway
pip install -r requirements.txt
python app.py
```

The API Gateway will start on http://localhost:5000

## Using the API Gateway

All requests to the backend services should go through the API Gateway using the following pattern:

```
http://localhost:5000/api/{service}/{path}
```

For example:

- Get all users: `GET http://localhost:5000/api/user_service/users`
- Get a specific product: `GET http://localhost:5000/api/product_service/products/1`
- Create a new order: `POST http://localhost:5000/api/order_service/orders`

Remember to include the API key in the request header:

```
X-API-Key: test-api-key
```

## API Gateway Features

### 1. Request Routing

The gateway maps the URL path to the appropriate backend service:

```
/api/user_service/* -> User Service
/api/product_service/* -> Product Service
/api/order_service/* -> Order Service
```

### 2. Load Balancing

The gateway distributes requests across multiple instances of each service.

### 3. Response Caching

GET requests are cached to improve performance and reduce load on backend services.

### 4. Rate Limiting

The gateway limits the number of requests from a client within a time window to prevent abuse.

### 5. Authentication

The gateway validates API keys before forwarding requests to backend services.

### 6. Monitoring and Administration

The gateway provides endpoints for monitoring and administration:

- Health check: `GET http://localhost:5000/health`
- List services: `GET http://localhost:5000/admin/services`
- Clear cache: `POST http://localhost:5000/admin/cache/clear`
- View rate limits: `GET http://localhost:5000/admin/rate-limits`

## API Gateway in Production

For a production-ready API Gateway, consider:

1. **Scalability** - Deploy multiple gateway instances behind a load balancer
2. **Resilience** - Implement circuit breakers to handle service failures
3. **Service Discovery** - Use a dynamic service registry (e.g., Consul, etcd)
4. **Authentication** - Implement OAuth 2.0 or JWT authentication
5. **Monitoring** - Add comprehensive logging, metrics, and tracing
6. **Caching** - Use a distributed cache like Redis
7. **Rate Limiting** - Implement distributed rate limiting

## Related Patterns

- **Backend for Frontend (BFF)** - Create specialized gateways for different client types
- **Circuit Breaker** - Handle failures in backend services gracefully
- **Service Registry** - Dynamic service discovery
- **Edge Service** - API Gateway at the edge of your network

## Learn More

- [Microservices with Python and Flask](https://flask.palletsprojects.com/en/2.0.x/)
- [API Gateway Pattern](https://microservices.io/patterns/apigateway.html)
- [Rate Limiting Algorithms](https://konghq.com/blog/rate-limiting-strategies-techniques/)

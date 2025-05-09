# Python Web Development Learning Project

A comprehensive project for learning web development with Python, covering multiple frameworks, concepts, and deployment strategies. This repository serves as a complete resource for developers wanting to master Python web development from basics to advanced patterns.

## Project Structure

```
./
├── README.md
├── requirements.txt
├── flask_basics/                  # Flask framework examples
│   ├── 01_hello_world/            # Basic application setup
│   ├── 02_routing/                # URL routing and HTTP methods
│   ├── 03_templates/              # Template rendering with Jinja2
│   ├── 04_forms/                  # Form handling and validation
│   └── 05_database/               # SQLAlchemy integration
├── django_basics/                 # Django framework examples
│   ├── blog_project/              # Complete blog application
│   └── README.md                  # Django-specific documentation
├── fastapi_basics/                # FastAPI framework examples
│   ├── 01_hello_world/            # Basic API setup
│   ├── 02_path_params/            # Path parameters and validation
│   ├── 03_request_body/           # Request body processing
│   └── 04_database/               # Database integration
├── web_concepts/                  # Core web development concepts
│   ├── http_basics.py             # HTTP protocol fundamentals
│   ├── rest_api_concepts.py       # RESTful API design principles
│   └── authentication.py          # Authentication methods
├── front_end_integration/         # Frontend with Python backends
│   ├── basic_html_css/            # Simple HTML/CSS integration
│   ├── javascript_ajax/           # AJAX and JavaScript examples
│   └── react_flask/               # React + Flask integration
├── websocket_integration/         # Real-time communication examples
│   └── chat_application/          # WebSocket chat application
├── api_gateway/                   # API Gateway pattern implementation
│   ├── gateway/                   # Main gateway service
│   └── services/                  # Microservices examples
└── deployment_examples/           # Deployment configurations
    ├── docker/                    # Docker containerization
    ├── aws/                       # AWS deployment guides
    └── heroku/                    # Heroku deployment examples
```

## Frameworks Covered

### 1. Flask
A lightweight WSGI web application framework designed to make getting started quick and easy. Perfect for small to medium applications and APIs.

### 2. Django
A high-level Python web framework that encourages rapid development and clean, pragmatic design. Batteries-included and comes with an ORM, admin interface, and many built-in features.

### 3. FastAPI
A modern, fast web framework for building APIs with Python 3.7+ based on standard Python type hints. Known for its high performance and automatic documentation generation.

## Core Concepts Covered

1. **HTTP Fundamentals**: Methods, status codes, headers, and request/response lifecycle
2. **RESTful API Design**: Resource-based architecture, CRUD operations, and API versioning
3. **Authentication & Authorization**: Basic auth, JWT tokens, OAuth, and role-based access control
4. **Database Integration**: ORM patterns, migrations, relationships, and query optimization
5. **Template Rendering**: Server-side rendering with various template engines
6. **Form Handling**: Validation, CSRF protection, and file uploads
7. **WebSockets**: Real-time bidirectional communication
8. **API Gateway Pattern**: Request routing, load balancing, and microservices architecture
9. **Containerization**: Docker deployment for Python web applications

## Getting Started

### Prerequisites

- Python 3.8+ installed
- Virtual environment tool (venv or conda)
- Git for version control

### Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/python-web-development.git
   cd python-web-development
   ```

2. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

### Running Examples

Each directory contains standalone examples that can be run individually. For example, to run a Flask application:

```bash
cd flask_basics/01_hello_world
python app.py
```

For Django projects:

```bash
cd django_basics/blog_project
python manage.py migrate
python manage.py runserver
```

For FastAPI applications:

```bash
cd fastapi_basics/01_hello_world
uvicorn main:app --reload
```

## Learning Path

For beginners, we recommend following this learning path:

1. Start with **Flask Basics** (01_hello_world → 05_database)
2. Learn **Core Web Concepts** (http_basics.py → authentication.py)
3. Explore **Front-end Integration** with Flask
4. Move to **Django Basics** for a full-featured framework
5. Try **FastAPI** for high-performance APIs
6. Implement **WebSockets** for real-time features
7. Study the **API Gateway** pattern for microservices
8. Practice **Deployment** strategies with Docker and cloud platforms

## Contributing

Contributions are welcome! If you'd like to add examples, fix bugs, or improve documentation, please:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- Python Software Foundation
- Flask, Django, and FastAPI communities
- All contributors and learners who helped improve these examples

- Routing and URL handling
- Template rendering
- Form processing and validation
- Database integration (SQLite, PostgreSQL)
- RESTful API design and implementation
- Authentication and authorization
- Frontend integration
- HTTP fundamentals
- Deployment basics

## Getting Started

1. Clone this repository
2. Set up a virtual environment:
   ```
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```
3. Install dependencies:
   ```
   pip install -r requirements.txt
   ```
4. Follow the README files in each directory to explore different frameworks and concepts

## Prerequisites

- Python 3.8 or higher
- Basic understanding of Python syntax
- Basic understanding of HTML/CSS (for frontend sections)

## Learning Path

This project is structured as a learning path:

1. Start with Flask basics to understand core web concepts
2. Move to Django to see a full-featured framework
3. Explore FastAPI for modern API development
4. Study the web concepts directory for deeper understanding
5. Finally, explore frontend integration

Each module contains practical examples with detailed comments explaining key concepts.

## License

This project is open source.


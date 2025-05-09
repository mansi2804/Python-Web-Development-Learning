# Django Basics

This directory contains a simple Django blog application that demonstrates the core concepts of the Django web framework.

## Project Structure

```
blog_project/              # Django project directory
├── blog_project/          # Project settings package
│   ├── __init__.py
│   ├── asgi.py            # ASGI config for async deployment
│   ├── settings.py        # Project settings
│   ├── urls.py            # Main URL routing
│   └── wsgi.py            # WSGI config for deployment
├── blog/                  # Blog application
│   ├── __init__.py
│   ├── admin.py           # Admin site configuration
│   ├── apps.py            # App configuration
│   ├── forms.py           # Form definitions
│   ├── migrations/        # Database migrations
│   ├── models.py          # Data models
│   ├── static/            # Static files
│   ├── templates/         # HTML templates
│   ├── tests.py           # Test cases
│   ├── urls.py            # App-specific URL routing
│   └── views.py           # View functions and classes
├── db.sqlite3             # SQLite database
└── manage.py              # Django command-line utility
```

## Key Concepts Demonstrated

1. **Project Structure** - Django's standard project structure and organization
2. **MTV Architecture** - Model-Template-View pattern
3. **ORM** - Object-Relational Mapping for database interactions
4. **Admin Interface** - Django's built-in administration panel
5. **Forms** - Form handling and validation
6. **Authentication** - User authentication and permissions
7. **Class-based Views** - Django's class-based view system
8. **Templates** - Django template language and template inheritance
9. **Static Files** - Managing CSS, JavaScript, and images
10. **URL Routing** - URL pattern configuration

## Getting Started

1. Navigate to the blog_project directory:
   ```
   cd django_basics/blog_project
   ```

2. Create and apply migrations:
   ```
   python manage.py makemigrations
   python manage.py migrate
   ```

3. Create a superuser:
   ```
   python manage.py createsuperuser
   ```

4. Run the development server:
   ```
   python manage.py runserver
   ```

5. Access the application at http://127.0.0.1:8000/

## Features

- User registration and authentication
- Creating, editing, and deleting blog posts
- Commenting system
- Post categories and tags
- User profiles
- Admin dashboard

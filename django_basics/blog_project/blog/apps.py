"""
Application configuration for the blog app.

This defines the Django application configuration for the blog app.
"""

from django.apps import AppConfig


class BlogConfig(AppConfig):
    """Configuration for the Blog application."""
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'blog'
    
    def ready(self):
        """
        Initialize the application when it's ready.
        
        This imports the signals module to ensure that the signals are connected.
        """
        import blog.signals

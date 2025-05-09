"""
URL patterns for the blog application.

This module defines URL patterns for the blog application.
Key concepts:
- URL patterns
- Path converters
- URL naming
- Including app URLs in project URLs
"""

from django.urls import path
from . import views
from .views import (
    PostListView,
    PostDetailView,
    PostCreateView,
    PostUpdateView,
    PostDeleteView,
    UserPostListView,
    CategoryPostListView,
    TagPostListView,
)

urlpatterns = [
    # Function-based views
    path('', views.home, name='blog-home'),
    path('about/', views.about, name='blog-about'),
    path('search/', views.search_view, name='blog-search'),
    
    # Class-based views for posts
    path('posts/', PostListView.as_view(), name='post-list'),
    path('post/<slug:slug>/', PostDetailView.as_view(), name='post-detail'),
    path('post/new/', PostCreateView.as_view(), name='post-create'),
    path('post/<slug:slug>/update/', PostUpdateView.as_view(), name='post-update'),
    path('post/<slug:slug>/delete/', PostDeleteView.as_view(), name='post-delete'),
    
    # User posts
    path('user/<str:username>/', UserPostListView.as_view(), name='user-posts'),
    
    # Category and tag views
    path('category/<slug:slug>/', CategoryPostListView.as_view(), name='category-detail'),
    path('tag/<slug:slug>/', TagPostListView.as_view(), name='tag-detail'),
]

# URL naming conventions demonstrated here:
# - blog-*: For general blog pages (home, about, search)
# - post-*: For post-related views (list, detail, create, update, delete)
# - user-*: For user-related views
# - category-*, tag-*: For category and tag views

"""
Models for the blog application.

This module defines the database schema for the blog application using Django's ORM.
Key concepts:
- Models as database tables
- Fields as table columns
- Relationships between models
- Meta options for model behavior
- Model methods for custom functionality
"""

from django.db import models
from django.utils import timezone
from django.urls import reverse
from django.contrib.auth.models import User
from PIL import Image

class Profile(models.Model):
    """
    User profile model extending Django's built-in User model.
    
    This demonstrates a one-to-one relationship with the User model.
    """
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    image = models.ImageField(default='default.jpg', upload_to='profile_pics')
    bio = models.TextField(max_length=500, blank=True)
    location = models.CharField(max_length=100, blank=True)
    website = models.URLField(max_length=200, blank=True)
    
    def __str__(self):
        return f'{self.user.username} Profile'
    
    def save(self, *args, **kwargs):
        """Override save method to resize profile images."""
        super().save(*args, **kwargs)
        
        # Resize image if needed
        img = Image.open(self.image.path)
        if img.height > 300 or img.width > 300:
            output_size = (300, 300)
            img.thumbnail(output_size)
            img.save(self.image.path)

class Category(models.Model):
    """
    Category model for categorizing blog posts.
    
    This demonstrates a simple model with basic fields.
    """
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    slug = models.SlugField(max_length=100, unique=True)
    
    class Meta:
        verbose_name_plural = "Categories"
        ordering = ['name']
    
    def __str__(self):
        return self.name
    
    def get_absolute_url(self):
        """Return the URL to access a particular category."""
        return reverse('category-detail', kwargs={'slug': self.slug})

class Tag(models.Model):
    """
    Tag model for tagging blog posts.
    
    This will be used in a many-to-many relationship with Post.
    """
    name = models.CharField(max_length=50, unique=True)
    slug = models.SlugField(max_length=50, unique=True)
    
    class Meta:
        ordering = ['name']
    
    def __str__(self):
        return self.name
    
    def get_absolute_url(self):
        """Return the URL to access a particular tag."""
        return reverse('tag-detail', kwargs={'slug': self.slug})

class Post(models.Model):
    """
    Post model representing a blog post.
    
    This demonstrates:
    - ForeignKey relationship to User (author)
    - ForeignKey relationship to Category
    - ManyToMany relationship to Tag
    - Various field types
    - Custom methods
    """
    title = models.CharField(max_length=200)
    slug = models.SlugField(max_length=200, unique=True)
    content = models.TextField()
    featured_image = models.ImageField(upload_to='post_images', blank=True, null=True)
    date_posted = models.DateTimeField(default=timezone.now)
    date_updated = models.DateTimeField(auto_now=True)
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='posts')
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, related_name='posts', null=True, blank=True)
    tags = models.ManyToManyField(Tag, related_name='posts', blank=True)
    is_published = models.BooleanField(default=True)
    
    class Meta:
        ordering = ['-date_posted']
        
    def __str__(self):
        return self.title
    
    def get_absolute_url(self):
        """Return the URL to access a particular post."""
        return reverse('post-detail', kwargs={'slug': self.slug})
    
    @property
    def comment_count(self):
        """Return the number of comments on this post."""
        return self.comments.count()
    
    @property
    def summary(self):
        """Return a short summary of the post."""
        return self.content[:250] + '...' if len(self.content) > 250 else self.content

class Comment(models.Model):
    """
    Comment model for blog post comments.
    
    This demonstrates:
    - ForeignKey relationship to Post
    - ForeignKey relationship to User (author)
    - Self-referential ForeignKey for nested comments
    """
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='comments')
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='comments')
    parent = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='replies')
    content = models.TextField()
    date_posted = models.DateTimeField(default=timezone.now)
    is_approved = models.BooleanField(default=True)
    
    class Meta:
        ordering = ['date_posted']
    
    def __str__(self):
        return f'Comment by {self.author.username} on {self.post.title}'
    
    @property
    def is_reply(self):
        """Return whether this comment is a reply to another comment."""
        return self.parent is not None

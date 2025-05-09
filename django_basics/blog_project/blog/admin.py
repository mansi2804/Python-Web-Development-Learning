"""
Admin configuration for the blog application.

This module registers models with the Django admin site and customizes their display.
Key concepts:
- Model registration
- ModelAdmin customization
- Inline model admin for related models
- List display, filters, and search
"""

from django.contrib import admin
from .models import Profile, Post, Category, Tag, Comment

@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    """Admin configuration for the Profile model."""
    list_display = ('user', 'location', 'website')
    search_fields = ('user__username', 'location')

class CommentInline(admin.TabularInline):
    """
    Inline admin for comments.
    
    This allows editing comments directly from a post's admin page.
    """
    model = Comment
    extra = 0  # No extra empty forms
    readonly_fields = ('date_posted',)

@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    """
    Admin configuration for the Post model.
    
    This demonstrates:
    - Custom list display
    - List filters
    - Search fields
    - Prepopulated fields
    - Date hierarchy
    - Inline related models
    """
    list_display = ('title', 'author', 'category', 'date_posted', 'is_published')
    list_filter = ('is_published', 'date_posted', 'category', 'author')
    search_fields = ('title', 'content', 'author__username', 'category__name')
    prepopulated_fields = {'slug': ('title',)}
    date_hierarchy = 'date_posted'
    filter_horizontal = ('tags',)
    readonly_fields = ('date_posted', 'date_updated')
    inlines = [CommentInline]
    
    fieldsets = (
        ('Post Information', {
            'fields': ('title', 'slug', 'author', 'content', 'featured_image')
        }),
        ('Categorization', {
            'fields': ('category', 'tags')
        }),
        ('Status', {
            'fields': ('is_published', 'date_posted', 'date_updated')
        }),
    )

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    """Admin configuration for the Category model."""
    list_display = ('name', 'post_count')
    prepopulated_fields = {'slug': ('name',)}
    search_fields = ('name', 'description')
    
    def post_count(self, obj):
        """Return the number of posts in this category."""
        return obj.posts.count()
    post_count.short_description = 'Posts'

@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    """Admin configuration for the Tag model."""
    list_display = ('name', 'post_count')
    prepopulated_fields = {'slug': ('name',)}
    search_fields = ('name',)
    
    def post_count(self, obj):
        """Return the number of posts with this tag."""
        return obj.posts.count()
    post_count.short_description = 'Posts'

@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    """Admin configuration for the Comment model."""
    list_display = ('author', 'post', 'short_content', 'date_posted', 'is_approved')
    list_filter = ('is_approved', 'date_posted', 'author')
    search_fields = ('content', 'author__username', 'post__title')
    readonly_fields = ('date_posted',)
    
    def short_content(self, obj):
        """Return a shortened version of the comment content."""
        return obj.content[:50] + '...' if len(obj.content) > 50 else obj.content
    short_content.short_description = 'Content'

"""
Forms for the blog application.

This module defines Django forms for the blog application.
Key concepts:
- ModelForm: Form based on a Django model
- Form validation
- Custom widgets
- Form Meta options
"""

from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from .models import Profile, Post, Comment, Category, Tag

class UserRegisterForm(UserCreationForm):
    """
    User registration form extending Django's UserCreationForm.
    
    This demonstrates:
    - Extending a built-in form
    - Adding custom fields
    - Custom validation
    """
    email = forms.EmailField(required=True)
    first_name = forms.CharField(max_length=30, required=False, help_text='Optional')
    last_name = forms.CharField(max_length=30, required=False, help_text='Optional')
    
    class Meta:
        model = User
        fields = ['username', 'email', 'first_name', 'last_name', 'password1', 'password2']
    
    def clean_email(self):
        """Custom validation to ensure email is unique."""
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError('This email is already in use. Please use a different email address.')
        return email

class UserUpdateForm(forms.ModelForm):
    """
    Form for updating user information.
    
    This demonstrates a basic ModelForm.
    """
    email = forms.EmailField()
    
    class Meta:
        model = User
        fields = ['username', 'email', 'first_name', 'last_name']

class ProfileUpdateForm(forms.ModelForm):
    """
    Form for updating user profile.
    
    This demonstrates:
    - Form for related model (Profile relates to User)
    - Widget customization
    """
    class Meta:
        model = Profile
        fields = ['image', 'bio', 'location', 'website']
        widgets = {
            'bio': forms.Textarea(attrs={'rows': 4}),
        }

class PostForm(forms.ModelForm):
    """
    Form for creating and updating blog posts.
    
    This demonstrates:
    - Complex form with many field types
    - Many-to-many relationship handling
    - Custom widgets and labels
    """
    # Allow creating a new category on the fly
    new_category = forms.CharField(
        max_length=100, 
        required=False,
        help_text='Optionally create a new category'
    )
    
    # Allow creating new tags on the fly
    new_tags = forms.CharField(
        max_length=100, 
        required=False,
        help_text='Comma-separated tags (e.g., python,django,web)'
    )
    
    class Meta:
        model = Post
        fields = ['title', 'slug', 'content', 'featured_image', 'category', 'tags', 'is_published']
        widgets = {
            'content': forms.Textarea(attrs={'rows': 10}),
            'tags': forms.CheckboxSelectMultiple(),
        }
        help_texts = {
            'slug': 'URL-friendly name (auto-filled from title if left empty)',
            'is_published': 'Uncheck to save as draft',
        }
    
    def clean(self):
        """Custom validation to handle new category and tags."""
        cleaned_data = super().clean()
        
        # Handle new category creation
        new_category = cleaned_data.get('new_category')
        category = cleaned_data.get('category')
        
        if new_category and not category:
            from django.utils.text import slugify
            # Create or get category
            cat, created = Category.objects.get_or_create(
                name=new_category,
                defaults={'slug': slugify(new_category)}
            )
            cleaned_data['category'] = cat
            
        # Handle new tags creation
        new_tags = cleaned_data.get('new_tags')
        if new_tags:
            from django.utils.text import slugify
            tag_names = [t.strip() for t in new_tags.split(',') if t.strip()]
            tags = []
            
            for tag_name in tag_names:
                tag, created = Tag.objects.get_or_create(
                    name=tag_name,
                    defaults={'slug': slugify(tag_name)}
                )
                tags.append(tag)
                
            # Add to existing tags selection
            existing_tags = cleaned_data.get('tags', [])
            for tag in tags:
                if tag not in existing_tags:
                    existing_tags.add(tag)
        
        return cleaned_data
        
    def save(self, commit=True):
        """Override save to handle the slug if empty."""
        instance = super().save(commit=False)
        
        # Generate slug from title if empty
        if not instance.slug:
            from django.utils.text import slugify
            instance.slug = slugify(instance.title)
            
            # Ensure slug is unique
            base_slug = instance.slug
            counter = 1
            while Post.objects.filter(slug=instance.slug).exists():
                instance.slug = f"{base_slug}-{counter}"
                counter += 1
        
        if commit:
            instance.save()
            self.save_m2m()  # Save many-to-many relationships
            
        return instance

class CommentForm(forms.ModelForm):
    """
    Form for creating and updating comments.
    
    This demonstrates a simple ModelForm.
    """
    class Meta:
        model = Comment
        fields = ['content']
        widgets = {
            'content': forms.Textarea(attrs={'rows': 3, 'placeholder': 'Add a comment...'}),
        }
        labels = {
            'content': '',
        }

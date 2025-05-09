"""
Views for the blog application.

This module defines Django views for the blog application.
It demonstrates both function-based views and class-based views.

Key concepts:
- Function-based views
- Class-based views with mixins
- View permissions and authentication
- Form handling in views
- ListView, DetailView, CreateView, UpdateView, DeleteView
"""

from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LoginView, LogoutView
from django.views.generic import (
    ListView, DetailView, CreateView, UpdateView, DeleteView, FormView, TemplateView
)
from django.views.generic.edit import FormMixin
from django.urls import reverse_lazy, reverse
from django.contrib import messages
from django.db.models import Q, Count
from django.http import HttpResponseRedirect
from django.utils.text import slugify

from .models import Post, User, Category, Tag, Comment, Profile
from .forms import (
    UserRegisterForm, UserUpdateForm, ProfileUpdateForm, PostForm, CommentForm
)

# Home view - function-based
def home(request):
    """
    Home page view showing recent posts.
    
    This demonstrates a simple function-based view.
    """
    context = {
        'title': 'Home',
        'posts': Post.objects.filter(is_published=True).order_by('-date_posted')[:5],
        'categories': Category.objects.annotate(post_count=Count('posts')),
        'popular_tags': Tag.objects.annotate(post_count=Count('posts')).order_by('-post_count')[:10],
    }
    return render(request, 'blog/home.html', context)

# About view - function-based
def about(request):
    """Simple about page view."""
    return render(request, 'blog/about.html', {'title': 'About'})

# Post List view - class-based
class PostListView(ListView):
    """
    View to list all published posts.
    
    This demonstrates a class-based ListView.
    """
    model = Post
    template_name = 'blog/post_list.html'
    context_object_name = 'posts'
    paginate_by = 5
    
    def get_queryset(self):
        """Return only published posts ordered by date."""
        return Post.objects.filter(is_published=True).order_by('-date_posted')
    
    def get_context_data(self, **kwargs):
        """Add extra context data."""
        context = super().get_context_data(**kwargs)
        context['title'] = 'Blog Posts'
        context['categories'] = Category.objects.annotate(post_count=Count('posts'))
        context['popular_tags'] = Tag.objects.annotate(post_count=Count('posts')).order_by('-post_count')[:10]
        return context

# Post Detail view - class-based
class PostDetailView(FormMixin, DetailView):
    """
    View to show a specific post.
    
    This demonstrates:
    - DetailView for showing single objects
    - FormMixin for adding a form to a DetailView (for comments)
    """
    model = Post
    template_name = 'blog/post_detail.html'
    context_object_name = 'post'
    form_class = CommentForm
    
    def get_success_url(self):
        """Return URL to redirect to after successful form submission."""
        return reverse('post-detail', kwargs={'slug': self.object.slug})
    
    def get_context_data(self, **kwargs):
        """Add extra context data."""
        context = super().get_context_data(**kwargs)
        context['title'] = self.object.title
        context['comments'] = self.object.comments.filter(parent=None, is_approved=True)
        context['comment_form'] = self.get_form()
        context['related_posts'] = Post.objects.filter(
            category=self.object.category
        ).exclude(id=self.object.id).order_by('-date_posted')[:3]
        return context
    
    def post(self, request, *args, **kwargs):
        """Handle comment form submission."""
        if not request.user.is_authenticated:
            return HttpResponseRedirect(reverse('login'))
        
        self.object = self.get_object()
        form = self.get_form()
        
        if form.is_valid():
            return self.form_valid(form)
        else:
            return self.form_invalid(form)
    
    def form_valid(self, form):
        """Process valid form data."""
        comment = form.save(commit=False)
        comment.post = self.object
        comment.author = self.request.user
        
        # Check if it's a reply
        parent_id = self.request.POST.get('parent_id')
        if parent_id:
            comment.parent = get_object_or_404(Comment, id=parent_id)
            
        comment.save()
        messages.success(self.request, 'Your comment has been posted!')
        return super().form_valid(form)

# User Post List view - class-based
class UserPostListView(ListView):
    """
    View to list posts by a specific user.
    
    This demonstrates filtering a ListView by a URL parameter.
    """
    model = Post
    template_name = 'blog/user_posts.html'
    context_object_name = 'posts'
    paginate_by = 5
    
    def get_queryset(self):
        """Filter posts by username from URL."""
        user = get_object_or_404(User, username=self.kwargs.get('username'))
        return Post.objects.filter(author=user, is_published=True).order_by('-date_posted')
    
    def get_context_data(self, **kwargs):
        """Add extra context data."""
        context = super().get_context_data(**kwargs)
        user = get_object_or_404(User, username=self.kwargs.get('username'))
        context['title'] = f'Posts by {user.username}'
        context['profile_user'] = user
        return context

# Category Post List view - class-based
class CategoryPostListView(ListView):
    """
    View to list posts in a specific category.
    
    This demonstrates:
    - Filtering posts by category
    - URL path converters (slug)
    """
    model = Post
    template_name = 'blog/category_posts.html'
    context_object_name = 'posts'
    paginate_by = 5
    
    def get_queryset(self):
        """Filter posts by category slug from URL."""
        self.category = get_object_or_404(Category, slug=self.kwargs.get('slug'))
        return Post.objects.filter(category=self.category, is_published=True).order_by('-date_posted')
    
    def get_context_data(self, **kwargs):
        """Add extra context data."""
        context = super().get_context_data(**kwargs)
        context['title'] = f'Category: {self.category.name}'
        context['category'] = self.category
        return context

# Tag Post List view - class-based
class TagPostListView(ListView):
    """
    View to list posts with a specific tag.
    
    This demonstrates filtering by a many-to-many relationship.
    """
    model = Post
    template_name = 'blog/tag_posts.html'
    context_object_name = 'posts'
    paginate_by = 5
    
    def get_queryset(self):
        """Filter posts by tag slug from URL."""
        self.tag = get_object_or_404(Tag, slug=self.kwargs.get('slug'))
        return Post.objects.filter(tags=self.tag, is_published=True).order_by('-date_posted')
    
    def get_context_data(self, **kwargs):
        """Add extra context data."""
        context = super().get_context_data(**kwargs)
        context['title'] = f'Tag: {self.tag.name}'
        context['tag'] = self.tag
        return context

# Post Create view - class-based
class PostCreateView(LoginRequiredMixin, CreateView):
    """
    View to create a new post.
    
    This demonstrates:
    - CreateView for creating objects
    - LoginRequiredMixin for requiring authentication
    - Form handling in class-based views
    """
    model = Post
    form_class = PostForm
    template_name = 'blog/post_form.html'
    
    def form_valid(self, form):
        """Set the author to the current user."""
        form.instance.author = self.request.user
        messages.success(self.request, 'Your post has been created!')
        return super().form_valid(form)
    
    def get_context_data(self, **kwargs):
        """Add extra context data."""
        context = super().get_context_data(**kwargs)
        context['title'] = 'Create Post'
        return context

# Post Update view - class-based
class PostUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    """
    View to update an existing post.
    
    This demonstrates:
    - UpdateView for updating objects
    - UserPassesTestMixin for checking permissions
    """
    model = Post
    form_class = PostForm
    template_name = 'blog/post_form.html'
    
    def form_valid(self, form):
        """Process valid form data."""
        form.instance.author = self.request.user
        messages.success(self.request, 'Your post has been updated!')
        return super().form_valid(form)
    
    def test_func(self):
        """Check if the user is the author of the post."""
        post = self.get_object()
        return self.request.user == post.author
    
    def get_context_data(self, **kwargs):
        """Add extra context data."""
        context = super().get_context_data(**kwargs)
        context['title'] = 'Update Post'
        return context

# Post Delete view - class-based
class PostDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    """
    View to delete a post.
    
    This demonstrates:
    - DeleteView for deleting objects
    - success_url for redirect after deletion
    """
    model = Post
    template_name = 'blog/post_confirm_delete.html'
    success_url = reverse_lazy('blog-home')
    
    def test_func(self):
        """Check if the user is the author of the post."""
        post = self.get_object()
        return self.request.user == post.author
    
    def delete(self, request, *args, **kwargs):
        """Add success message after deletion."""
        messages.success(self.request, 'Your post has been deleted!')
        return super().delete(request, *args, **kwargs)
    
    def get_context_data(self, **kwargs):
        """Add extra context data."""
        context = super().get_context_data(**kwargs)
        context['title'] = 'Delete Post'
        return context

# Search view - function-based
def search_view(request):
    """
    Search view for posts.
    
    This demonstrates:
    - Query parameter handling
    - Complex ORM queries with Q objects
    """
    query = request.GET.get('q', '')
    if query:
        results = Post.objects.filter(
            Q(title__icontains=query) | 
            Q(content__icontains=query) |
            Q(author__username__icontains=query) |
            Q(category__name__icontains=query) |
            Q(tags__name__icontains=query),
            is_published=True
        ).distinct()
    else:
        results = Post.objects.none()
        
    context = {
        'title': 'Search Results',
        'query': query,
        'posts': results,
        'count': results.count()
    }
    return render(request, 'blog/search_results.html', context)

# User Registration view - class-based
class UserRegisterView(FormView):
    """
    View for user registration.
    
    This demonstrates:
    - FormView for handling forms not tied to a model instance
    - Redirect after successful form submission
    """
    template_name = 'blog/register.html'
    form_class = UserRegisterForm
    success_url = reverse_lazy('login')
    
    def form_valid(self, form):
        """Save the user and display success message."""
        form.save()
        username = form.cleaned_data.get('username')
        messages.success(self.request, f'Account created for {username}! You can now log in.')
        return super().form_valid(form)
    
    def get_context_data(self, **kwargs):
        """Add extra context data."""
        context = super().get_context_data(**kwargs)
        context['title'] = 'Register'
        return context

# User Login view - class-based
class UserLoginView(LoginView):
    """Custom login view extending Django's LoginView."""
    template_name = 'blog/login.html'
    redirect_authenticated_user = True
    
    def get_context_data(self, **kwargs):
        """Add extra context data."""
        context = super().get_context_data(**kwargs)
        context['title'] = 'Login'
        return context
    
    def form_valid(self, form):
        """Add success message on login."""
        messages.success(self.request, 'You have been logged in successfully!')
        return super().form_valid(form)

# User Logout view - class-based
class UserLogoutView(LogoutView):
    """Custom logout view extending Django's LogoutView."""
    next_page = 'blog-home'
    
    def dispatch(self, request, *args, **kwargs):
        """Add success message on logout."""
        if request.user.is_authenticated:
            messages.info(request, 'You have been logged out successfully!')
        return super().dispatch(request, *args, **kwargs)

# Profile view - class-based
class ProfileView(LoginRequiredMixin, TemplateView):
    """
    View for user profile.
    
    This demonstrates:
    - TemplateView for simple template rendering
    - Multiple forms in one view
    - POST method handling in TemplateView
    """
    template_name = 'blog/profile.html'
    
    def get_context_data(self, **kwargs):
        """Add user and profile forms to context."""
        context = super().get_context_data(**kwargs)
        context['title'] = 'Profile'
        context['u_form'] = UserUpdateForm(instance=self.request.user)
        context['p_form'] = ProfileUpdateForm(instance=self.request.user.profile)
        context['user_posts'] = Post.objects.filter(
            author=self.request.user
        ).order_by('-date_posted')[:5]
        return context
    
    def post(self, request, *args, **kwargs):
        """Handle form submission for profile update."""
        u_form = UserUpdateForm(request.POST, instance=request.user)
        p_form = ProfileUpdateForm(
            request.POST, 
            request.FILES, 
            instance=request.user.profile
        )
        
        if u_form.is_valid() and p_form.is_valid():
            u_form.save()
            p_form.save()
            messages.success(request, 'Your profile has been updated!')
            return redirect('profile')
        
        context = self.get_context_data(**kwargs)
        context['u_form'] = u_form
        context['p_form'] = p_form
        return self.render_to_response(context)

"""
Signals for the blog application.

This module defines Django signals that handle automatic actions when certain events occur.
Key concepts:
- post_save signal: triggered after a model instance is saved
- Automatic profile creation when a user is created
"""

from django.db.models.signals import post_save
from django.contrib.auth.models import User
from django.dispatch import receiver
from .models import Profile

@receiver(post_save, sender=User)
def create_profile(sender, instance, created, **kwargs):
    """
    Signal handler to automatically create a profile when a user is created.
    
    This demonstrates using Django's signals system to perform automatic actions.
    """
    if created:
        Profile.objects.create(user=instance)

@receiver(post_save, sender=User)
def save_profile(sender, instance, **kwargs):
    """
    Signal handler to automatically save a profile when a user is saved.
    """
    instance.profile.save()

from django.contrib.auth.models import User
from django.db import models
from PIL import Image
import os


# Extended user profile to add additional fields
class UserProfile(models.Model):
    """
    Extended user profile for additional user information
    """
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='extended_profile')
    
    # Profile fields
    bio = models.TextField(max_length=500, blank=True, help_text='Tell us about yourself')
    profile_picture = models.ImageField(
        upload_to='profile_pics/', 
        blank=True, 
        null=True,
        help_text='Profile picture (max 5MB)'
    )
    date_of_birth = models.DateField(blank=True, null=True)
    phone_number = models.CharField(max_length=15, blank=True)
    
    # Social Media Links
    website = models.URLField(blank=True, help_text='Your personal website')
    twitter = models.CharField(max_length=50, blank=True, help_text='Twitter username (without @)')
    github = models.CharField(max_length=50, blank=True, help_text='GitHub username')
    linkedin = models.CharField(max_length=50, blank=True, help_text='LinkedIn profile URL')
    
    # Privacy Settings
    is_profile_public = models.BooleanField(default=True, help_text='Make your profile visible to others')
    show_email = models.BooleanField(default=False, help_text='Show email on your public profile')
    
    # Verification
    is_verified = models.BooleanField(default=False, help_text='Verified user badge')
    email_verified = models.BooleanField(default=False)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    last_login_ip = models.GenericIPAddressField(blank=True, null=True)
    
    class Meta:
        verbose_name = 'User Profile'
        verbose_name_plural = 'User Profiles'
    
    def __str__(self):
        return f"{self.user.username}'s Extended Profile"
    
    @property
    def profile_picture_url(self):
        """Return profile picture URL or default"""
        if self.profile_picture and hasattr(self.profile_picture, 'url'):
            return self.profile_picture.url
        return '/static/images/default-avatar.png'
    
    @property
    def posts_count(self):
        """Return count of published posts"""
        return self.user.posts.filter(status='published').count()
    
    @property
    def total_views(self):
        """Return total views across all posts"""
        return self.user.posts.filter(status='published').aggregate(
            total=models.Sum('views')
        )['total'] or 0
    
    @property
    def total_likes(self):
        """Return total likes across all posts"""
        return sum(post.likes.count() for post in self.user.posts.filter(status='published'))
    
    def __str__(self):
        return f"{self.get_full_name()} ({self.email})"
    
    def get_full_name(self):
        """Return the first_name plus the last_name, with a space in between."""
        full_name = f'{self.first_name} {self.last_name}'
        return full_name.strip()
    
    def get_short_name(self):
        """Return the short name for the user."""
        return self.first_name
    
    def save(self, *args, **kwargs):
        # Handle profile picture resizing
        super().save(*args, **kwargs)
        
        if self.profile_picture:
            try:
                img = Image.open(self.profile_picture.path)
                
                # Resize if image is too large
                if img.height > 300 or img.width > 300:
                    output_size = (300, 300)
                    img.thumbnail(output_size)
                    img.save(self.profile_picture.path)
            except Exception as e:
                # Log error but don't fail the save
                pass
    
    @property
    def profile_picture_url(self):
        """Return profile picture URL or default"""
        if self.profile_picture and hasattr(self.profile_picture, 'url'):
            return self.profile_picture.url
        return '/static/images/default-avatar.png'
    
    @property
    def posts_count(self):
        """Return count of published posts"""
        return self.posts.filter(status='published').count()
    
    @property
    def total_views(self):
        """Return total views across all posts"""
        return self.posts.filter(status='published').aggregate(
            total=models.Sum('views')
        )['total'] or 0
    
    @property
    def total_likes(self):
        """Return total likes across all posts"""
        return sum(post.likes.count() for post in self.posts.filter(status='published'))


class UserActivity(models.Model):
    """
    Track user activities for analytics and engagement
    """
    ACTIVITY_TYPES = [
        ('login', 'Login'),
        ('logout', 'Logout'),
        ('post_created', 'Post Created'),
        ('post_updated', 'Post Updated'),
        ('comment_created', 'Comment Created'),
        ('like_added', 'Like Added'),
        ('like_removed', 'Like Removed'),
        ('profile_updated', 'Profile Updated'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='activities')
    activity_type = models.CharField(max_length=20, choices=ACTIVITY_TYPES)
    description = models.TextField(blank=True)
    ip_address = models.GenericIPAddressField(blank=True, null=True)
    user_agent = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = 'User Activity'
        verbose_name_plural = 'User Activities'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', '-created_at']),
            models.Index(fields=['activity_type', '-created_at']),
        ]
    
    def __str__(self):
        return f"{self.user.username} - {self.get_activity_type_display()}"


class UserPreferences(models.Model):
    """
    User preferences and settings
    """
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='preferences')
    
    # Email notifications
    email_on_new_comment = models.BooleanField(default=True)
    email_on_new_follower = models.BooleanField(default=True)
    email_on_post_liked = models.BooleanField(default=True)
    email_weekly_digest = models.BooleanField(default=True)
    
    # Privacy settings
    profile_visibility = models.CharField(
        max_length=10,
        choices=[
            ('public', 'Public'),
            ('private', 'Private'),
            ('friends', 'Friends Only'),
        ],
        default='public'
    )
    
    # Display preferences
    theme = models.CharField(
        max_length=10,
        choices=[
            ('light', 'Light'),
            ('dark', 'Dark'),
            ('auto', 'Auto'),
        ],
        default='auto'
    )
    posts_per_page = models.PositiveIntegerField(default=10, choices=[(5, '5'), (10, '10'), (20, '20'), (50, '50')])
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'User Preferences'
        verbose_name_plural = 'User Preferences'
    
    def __str__(self):
        return f"{self.user.username}'s Preferences"

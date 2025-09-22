from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User
from django.utils.html import format_html
from django.utils.translation import gettext_lazy as _

from .models import UserProfile, UserActivity, UserPreferences


# Inline for UserProfile in User admin
class UserProfileInline(admin.StackedInline):
    model = UserProfile
    can_delete = False
    verbose_name_plural = 'Profile'
    fields = (
        'bio', 'profile_picture', 'website', 'twitter', 'github', 'linkedin',
        'is_profile_public', 'show_email', 'is_verified'
    )


# Extend the User admin
class CustomUserAdmin(BaseUserAdmin):
    inlines = (UserProfileInline,)
    list_display = BaseUserAdmin.list_display + ('get_posts_count', 'get_is_verified')
    
    def get_posts_count(self, obj):
        return obj.posts.filter(status='published').count()
    get_posts_count.short_description = 'Posts'
    
    def get_is_verified(self, obj):
        if hasattr(obj, 'extended_profile') and obj.extended_profile.is_verified:
            return format_html('<span style="color: green;">✓</span>')
        return format_html('<span style="color: red;">✗</span>')
    get_is_verified.short_description = 'Verified'


# Unregister the original User admin and register our custom one
admin.site.unregister(User)
admin.site.register(User, CustomUserAdmin)


@admin.register(UserActivity)
class UserActivityAdmin(admin.ModelAdmin):
    """
    User Activity Admin for monitoring user engagement
    """
    list_display = ('user', 'activity_type', 'description', 'ip_address', 'created_at')
    list_filter = ('activity_type', 'created_at')
    search_fields = ('user__username', 'user__email', 'description')
    readonly_fields = ('created_at',)
    ordering = ('-created_at',)
    
    def has_add_permission(self, request):
        # Activities are created programmatically
        return False
    
    def has_change_permission(self, request, obj=None):
        # Activities should not be edited
        return False


@admin.register(UserPreferences)
class UserPreferencesAdmin(admin.ModelAdmin):
    """
    User Preferences Admin
    """
    list_display = ('user', 'theme', 'profile_visibility', 'posts_per_page', 'updated_at')
    list_filter = ('theme', 'profile_visibility', 'posts_per_page')
    search_fields = ('user__username', 'user__email')
    readonly_fields = ('created_at', 'updated_at')
    
    fieldsets = (
        (_('User'), {'fields': ('user',)}),
        (_('Email Notifications'), {
            'fields': (
                'email_on_new_comment', 'email_on_new_follower', 
                'email_on_post_liked', 'email_weekly_digest'
            )
        }),
        (_('Privacy'), {'fields': ('profile_visibility',)}),
        (_('Display'), {'fields': ('theme', 'posts_per_page')}),
        (_('Timestamps'), {'fields': ('created_at', 'updated_at')}),
    )

from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.signals import user_logged_in, user_logged_out
from django.contrib.auth.models import User
from .models import UserPreferences, UserActivity, UserProfile


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    """
    Create UserProfile instance when a new user is created
    """
    if created:
        UserProfile.objects.create(user=instance)
        UserPreferences.objects.create(user=instance)


@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    """
    Save UserProfile when user is saved
    """
    if hasattr(instance, 'extended_profile'):
        instance.extended_profile.save()
    if hasattr(instance, 'preferences'):
        instance.preferences.save()


@receiver(user_logged_in)
def log_user_login(sender, request, user, **kwargs):
    """
    Log user login activity
    """
    UserActivity.objects.create(
        user=user,
        activity_type='login',
        ip_address=get_client_ip(request),
        user_agent=request.META.get('HTTP_USER_AGENT', '')[:500],
        description=f'User logged in from {get_client_ip(request)}'
    )
    
    # Update last login IP
    user.last_login_ip = get_client_ip(request)
    user.save(update_fields=['last_login_ip'])


@receiver(user_logged_out)
def log_user_logout(sender, request, user, **kwargs):
    """
    Log user logout activity
    """
    if user:
        UserActivity.objects.create(
            user=user,
            activity_type='logout',
            ip_address=get_client_ip(request),
            user_agent=request.META.get('HTTP_USER_AGENT', '')[:500],
            description=f'User logged out from {get_client_ip(request)}'
        )


def get_client_ip(request):
    """
    Get the client's IP address from the request
    """
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip
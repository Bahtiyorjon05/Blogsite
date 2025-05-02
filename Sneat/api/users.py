from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth.models import User
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from myapp.models import UserProfile, UserSettings
from .serializers import UserProfileSerializer, UserSettingsSerializer

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def user_profile(request):
    """
    Get the authenticated user's profile
    """
    try:
        profile = UserProfile.objects.get(user=request.user)
        serializer = UserProfileSerializer(profile)
        return Response(serializer.data)
    except UserProfile.DoesNotExist:
        return Response(
            {'error': 'Profile not found'},
            status=status.HTTP_404_NOT_FOUND
        )


@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def update_profile(request):
    """
    Update the authenticated user's profile
    """
    try:
        profile = UserProfile.objects.get(user=request.user)
        
        # Update user data
        user = request.user
        first_name = request.data.get('first_name')
        last_name = request.data.get('last_name')
        email = request.data.get('email')
        
        if first_name:
            user.first_name = first_name
        
        if last_name:
            user.last_name = last_name
        
        if email and email != user.email:
            # Check if email is already in use
            if User.objects.filter(email=email).exclude(id=user.id).exists():
                return Response(
                    {'error': 'Email is already in use'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            user.email = email
        
        user.save()
        
        # Update profile data
        serializer = UserProfileSerializer(profile, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    except UserProfile.DoesNotExist:
        return Response(
            {'error': 'Profile not found'},
            status=status.HTTP_404_NOT_FOUND
        )


@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def update_settings(request):
    """
    Update the authenticated user's settings
    """
    try:
        settings = UserSettings.objects.get(user=request.user)
        serializer = UserSettingsSerializer(settings, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    except UserSettings.DoesNotExist:
        return Response(
            {'error': 'Settings not found'},
            status=status.HTTP_404_NOT_FOUND
        )


@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def change_password(request):
    """
    Change the authenticated user's password
    """
    user = request.user
    current_password = request.data.get('current_password')
    new_password = request.data.get('new_password')
    confirm_password = request.data.get('confirm_password')
    
    # Check if all fields are provided
    if not current_password or not new_password or not confirm_password:
        return Response(
            {'error': 'All password fields are required'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    # Check if current password is correct
    if not user.check_password(current_password):
        return Response(
            {'error': 'Current password is incorrect'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    # Check if new passwords match
    if new_password != confirm_password:
        return Response(
            {'error': 'New passwords do not match'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    # Validate new password
    try:
        validate_password(new_password, user)
    except ValidationError as e:
        return Response(
            {'error': e.messages},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    # Change password
    user.set_password(new_password)
    user.save()
    
    return Response({'success': 'Password changed successfully'})


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def upload_avatar(request):
    """
    Upload a new avatar for the authenticated user
    """
    try:
        profile = UserProfile.objects.get(user=request.user)
        
        if 'avatar' not in request.FILES:
            return Response(
                {'error': 'No avatar file provided'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Delete old avatar if exists
        if profile.avatar:
            profile.avatar.delete()
        
        # Save new avatar
        profile.avatar = request.FILES['avatar']
        profile.save()
        
        serializer = UserProfileSerializer(profile)
        return Response(serializer.data)
    
    except UserProfile.DoesNotExist:
        return Response(
            {'error': 'Profile not found'},
            status=status.HTTP_404_NOT_FOUND
        )

from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from accounts.models import UserPreferences
from blog.models import Post, Category, Tag, Comment


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    """
    Custom JWT token serializer with additional user data
    """
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        
        # Add custom claims
        token['email'] = user.email
        token['username'] = user.username
        token['full_name'] = user.get_full_name()
        token['is_verified'] = user.is_verified
        
        return token


class UserRegistrationSerializer(serializers.ModelSerializer):
    """
    User registration serializer with validation
    """
    password = serializers.CharField(write_only=True, min_length=8)
    password_confirm = serializers.CharField(write_only=True)
    
    class Meta:
        model = User
        fields = (
            'email', 'username', 'first_name', 'last_name', 
            'password', 'password_confirm'
        )
    
    def validate(self, attrs):
        if attrs['password'] != attrs['password_confirm']:
            raise serializers.ValidationError("Passwords don't match")
        return attrs
    
    def create(self, validated_data):
        validated_data.pop('password_confirm')
        user = User.objects.create_user(**validated_data)
        return user


class UserProfileSerializer(serializers.ModelSerializer):
    """
    User profile serializer for API responses
    """
    class Meta:
        model = User
        fields = (
            'id', 'username', 'email', 'first_name', 'last_name',
            'date_joined', 'is_active'
        )
        read_only_fields = ('id', 'username', 'date_joined')


class UserUpdateSerializer(serializers.ModelSerializer):
    """
    User profile update serializer
    """
    class Meta:
        model = User
        fields = (
            'first_name', 'last_name', 'email'
        )


class PostListSerializer(serializers.ModelSerializer):
    """
    Post list serializer for API
    """
    author = UserProfileSerializer(read_only=True)
    category = serializers.StringRelatedField()
    tags = serializers.StringRelatedField(many=True)
    total_likes = serializers.ReadOnlyField()
    total_comments = serializers.ReadOnlyField()
    reading_time = serializers.ReadOnlyField()
    
    class Meta:
        model = Post
        fields = (
            'id', 'title', 'slug', 'excerpt', 'featured_image',
            'author', 'category', 'tags', 'status', 'date_created',
            'date_updated', 'views', 'total_likes', 'total_comments',
            'reading_time'
        )


class PostDetailSerializer(serializers.ModelSerializer):
    """
    Post detail serializer with full content
    """
    author = UserProfileSerializer(read_only=True)
    category = serializers.StringRelatedField()
    tags = serializers.StringRelatedField(many=True)
    total_likes = serializers.ReadOnlyField()
    total_comments = serializers.ReadOnlyField()
    reading_time = serializers.ReadOnlyField()
    
    class Meta:
        model = Post
        fields = (
            'id', 'title', 'slug', 'content', 'excerpt', 'featured_image',
            'author', 'category', 'tags', 'status', 'date_created',
            'date_updated', 'views', 'total_likes', 'total_comments',
            'reading_time'
        )


class PostCreateUpdateSerializer(serializers.ModelSerializer):
    """
    Post create/update serializer
    """
    class Meta:
        model = Post
        fields = (
            'title', 'content', 'excerpt', 'featured_image',
            'category', 'tags', 'status'
        )
    
    def create(self, validated_data):
        tags_data = validated_data.pop('tags', [])
        post = Post.objects.create(**validated_data)
        post.tags.set(tags_data)
        return post


class CommentSerializer(serializers.ModelSerializer):
    """
    Comment serializer for API
    """
    author = UserProfileSerializer(read_only=True)
    replies = serializers.SerializerMethodField()
    
    class Meta:
        model = Comment
        fields = (
            'id', 'content', 'author', 'post', 'parent',
            'date_created', 'date_updated', 'replies'
        )
        read_only_fields = ('author', 'date_created', 'date_updated')
    
    def get_replies(self, obj):
        if obj.replies.exists():
            return CommentSerializer(obj.replies.all(), many=True).data
        return []


class CategorySerializer(serializers.ModelSerializer):
    """
    Category serializer
    """
    posts_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Category
        fields = ('id', 'name', 'slug', 'description', 'posts_count')
    
    def get_posts_count(self, obj):
        return obj.posts.filter(status='published').count()


class TagSerializer(serializers.ModelSerializer):
    """
    Tag serializer
    """
    posts_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Tag
        fields = ('id', 'name', 'slug', 'posts_count')
    
    def get_posts_count(self, obj):
        return obj.posts.filter(status='published').count()


class UserPreferencesSerializer(serializers.ModelSerializer):
    """
    User preferences serializer
    """
    class Meta:
        model = UserPreferences
        fields = (
            'email_on_new_comment', 'email_on_new_follower',
            'email_on_post_liked', 'email_weekly_digest',
            'profile_visibility', 'theme', 'posts_per_page'
        )
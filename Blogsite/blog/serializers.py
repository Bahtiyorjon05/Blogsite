from rest_framework import serializers
from django.contrib.auth.models import User
from .models import Post, Category, Tag, Comment, UserProfile


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name']


class UserProfileSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    
    class Meta:
        model = UserProfile
        fields = ['id', 'user', 'bio', 'profile_picture', 'website', 'twitter', 'github', 'linkedin']


class CategorySerializer(serializers.ModelSerializer):
    post_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Category
        fields = ['id', 'name', 'slug', 'description', 'created_at', 'post_count']
    
    def get_post_count(self, obj):
        return obj.posts.count()


class TagSerializer(serializers.ModelSerializer):
    post_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Tag
        fields = ['id', 'name', 'slug', 'post_count']
    
    def get_post_count(self, obj):
        return obj.posts.count()


class CommentSerializer(serializers.ModelSerializer):
    author = UserSerializer(read_only=True)
    replies = serializers.SerializerMethodField()
    like_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Comment
        fields = ['id', 'post', 'author', 'content', 'date_created', 'parent', 'replies', 'like_count']
        read_only_fields = ['post', 'author', 'date_created']
    
    def get_replies(self, obj):
        if obj.replies.exists():
            return CommentSerializer(obj.replies.all(), many=True).data
        return []
    
    def get_like_count(self, obj):
        return obj.likes.count()


class PostSerializer(serializers.ModelSerializer):
    author = UserSerializer(read_only=True)
    category = CategorySerializer(read_only=True)
    tags = TagSerializer(many=True, read_only=True)
    comments_count = serializers.SerializerMethodField()
    likes_count = serializers.SerializerMethodField()
    comments = serializers.SerializerMethodField()
    
    class Meta:
        model = Post
        fields = [
            'id', 'title', 'slug', 'content', 'featured_image', 'excerpt',
            'author', 'category', 'tags', 'status', 'date_created', 'date_updated',
            'views', 'comments_count', 'likes_count', 'comments'
        ]
        read_only_fields = ['author', 'date_created', 'date_updated', 'views']
    
    def get_comments_count(self, obj):
        return obj.comments.count()
    
    def get_likes_count(self, obj):
        return obj.likes.count()
    
    def get_comments(self, obj):
        # Only return top-level comments (no replies)
        comments = obj.comments.filter(parent=None)
        return CommentSerializer(comments, many=True).data
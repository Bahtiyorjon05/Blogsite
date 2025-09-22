from rest_framework import generics, status, permissions, filters
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination
from rest_framework_simplejwt.views import TokenObtainPairView
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Q
from django.contrib.auth import get_user_model

from .serializers import (
    CustomTokenObtainPairSerializer, UserRegistrationSerializer,
    UserProfileSerializer, UserUpdateSerializer, PostListSerializer,
    PostDetailSerializer, PostCreateUpdateSerializer, CommentSerializer,
    CategorySerializer, TagSerializer, UserPreferencesSerializer
)
from accounts.models import UserPreferences, UserActivity
from blog.models import Post, Category, Tag, Comment

User = get_user_model()


class CustomTokenObtainPairView(TokenObtainPairView):
    """
    Custom JWT token view with additional user data
    """
    serializer_class = CustomTokenObtainPairSerializer


class UserRegistrationView(generics.CreateAPIView):
    """
    User registration endpoint
    """
    queryset = User.objects.all()
    serializer_class = UserRegistrationSerializer
    permission_classes = [permissions.AllowAny]


class UserProfileView(generics.RetrieveUpdateAPIView):
    """
    User profile view and update
    """
    serializer_class = UserProfileSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_object(self):
        return self.request.user
    
    def get_serializer_class(self):
        if self.request.method in ['PUT', 'PATCH']:
            return UserUpdateSerializer
        return UserProfileSerializer


class UserPreferencesView(generics.RetrieveUpdateAPIView):
    """
    User preferences view and update
    """
    serializer_class = UserPreferencesSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_object(self):
        preferences, created = UserPreferences.objects.get_or_create(
            user=self.request.user
        )
        return preferences


class StandardResultsSetPagination(PageNumberPagination):
    """
    Standard pagination class
    """
    page_size = 20
    page_size_query_param = 'page_size'
    max_page_size = 100


class PostListCreateView(generics.ListCreateAPIView):
    """
    List all posts or create a new post
    """
    queryset = Post.objects.filter(status='published').select_related(
        'author', 'category'
    ).prefetch_related('tags', 'likes')
    serializer_class = PostListSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['category', 'tags', 'author']
    search_fields = ['title', 'content', 'excerpt']
    ordering_fields = ['date_created', 'views', 'title']
    ordering = ['-date_created']
    
    def get_serializer_class(self):
        if self.request.method == 'POST':
            return PostCreateUpdateSerializer
        return PostListSerializer
    
    def perform_create(self, serializer):
        serializer.save(author=self.request.user)
        
        # Log activity
        UserActivity.objects.create(
            user=self.request.user,
            activity_type='post_created',
            description=f'Created post: {serializer.instance.title}'
        )


class PostDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    Retrieve, update or delete a post
    """
    queryset = Post.objects.select_related('author', 'category').prefetch_related('tags', 'likes')
    serializer_class = PostDetailSerializer
    lookup_field = 'slug'
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    
    def get_serializer_class(self):
        if self.request.method in ['PUT', 'PATCH']:
            return PostCreateUpdateSerializer
        return PostDetailSerializer
    
    def get_permissions(self):
        """
        Only author can update/delete their posts
        """
        if self.request.method in ['PUT', 'PATCH', 'DELETE']:
            return [permissions.IsAuthenticated(), IsAuthorOrReadOnly()]
        return [permissions.IsAuthenticatedOrReadOnly()]
    
    def retrieve(self, request, *args, **kwargs):
        """
        Increment view count when post is retrieved
        """
        instance = self.get_object()
        instance.views += 1
        instance.save(update_fields=['views'])
        return super().retrieve(request, *args, **kwargs)


class UserPostsView(generics.ListAPIView):
    """
    List posts by a specific user
    """
    serializer_class = PostListSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    pagination_class = StandardResultsSetPagination
    
    def get_queryset(self):
        username = self.kwargs['username']
        return Post.objects.filter(
            author__username=username,
            status='published'
        ).select_related('author', 'category').prefetch_related('tags', 'likes')


class CategoryListView(generics.ListAPIView):
    """
    List all categories
    """
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [permissions.AllowAny]


class CategoryPostsView(generics.ListAPIView):
    """
    List posts in a category
    """
    serializer_class = PostListSerializer
    permission_classes = [permissions.AllowAny]
    pagination_class = StandardResultsSetPagination
    
    def get_queryset(self):
        category_slug = self.kwargs['slug']
        return Post.objects.filter(
            category__slug=category_slug,
            status='published'
        ).select_related('author', 'category').prefetch_related('tags', 'likes')


class TagListView(generics.ListAPIView):
    """
    List all tags
    """
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = [permissions.AllowAny]


class TagPostsView(generics.ListAPIView):
    """
    List posts with a specific tag
    """
    serializer_class = PostListSerializer
    permission_classes = [permissions.AllowAny]
    pagination_class = StandardResultsSetPagination
    
    def get_queryset(self):
        tag_slug = self.kwargs['slug']
        return Post.objects.filter(
            tags__slug=tag_slug,
            status='published'
        ).select_related('author', 'category').prefetch_related('tags', 'likes')


class CommentListCreateView(generics.ListCreateAPIView):
    """
    List comments for a post or create a new comment
    """
    serializer_class = CommentSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    
    def get_queryset(self):
        post_id = self.kwargs['post_id']
        return Comment.objects.filter(
            post_id=post_id,
            parent=None
        ).select_related('author').prefetch_related('replies')
    
    def perform_create(self, serializer):
        post_id = self.kwargs['post_id']
        post = Post.objects.get(id=post_id)
        serializer.save(author=self.request.user, post=post)
        
        # Log activity
        UserActivity.objects.create(
            user=self.request.user,
            activity_type='comment_created',
            description=f'Commented on post: {post.title}'
        )


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def like_post(request, post_id):
    """
    Like or unlike a post
    """
    try:
        post = Post.objects.get(id=post_id)
        user = request.user
        
        if user in post.likes.all():
            post.likes.remove(user)
            liked = False
            activity_type = 'like_removed'
            message = 'Post unliked successfully'
        else:
            post.likes.add(user)
            liked = True
            activity_type = 'like_added'
            message = 'Post liked successfully'
        
        # Log activity
        UserActivity.objects.create(
            user=user,
            activity_type=activity_type,
            description=f'{"Liked" if liked else "Unliked"} post: {post.title}'
        )
        
        return Response({
            'liked': liked,
            'total_likes': post.total_likes(),
            'message': message
        })
        
    except Post.DoesNotExist:
        return Response(
            {'error': 'Post not found'},
            status=status.HTTP_404_NOT_FOUND
        )


@api_view(['GET'])
@permission_classes([permissions.AllowAny])
def search_posts(request):
    """
    Advanced search functionality
    """
    query = request.GET.get('q', '')
    if not query:
        return Response({'results': []})
    
    # Search in title, content, and author name
    posts = Post.objects.filter(
        Q(title__icontains=query) |
        Q(content__icontains=query) |
        Q(excerpt__icontains=query) |
        Q(author__username__icontains=query) |
        Q(author__first_name__icontains=query) |
        Q(author__last_name__icontains=query) |
        Q(category__name__icontains=query) |
        Q(tags__name__icontains=query),
        status='published'
    ).distinct().select_related('author', 'category').prefetch_related('tags', 'likes')
    
    # Paginate results
    paginator = StandardResultsSetPagination()
    page = paginator.paginate_queryset(posts, request)
    
    serializer = PostListSerializer(page, many=True, context={'request': request})
    return paginator.get_paginated_response(serializer.data)


class IsAuthorOrReadOnly(permissions.BasePermission):
    """
    Custom permission to only allow authors to edit their own posts
    """
    def has_object_permission(self, request, view, obj):
        # Read permissions for any request
        if request.method in permissions.SAFE_METHODS:
            return True
        
        # Write permissions only to the author
        return obj.author == request.user
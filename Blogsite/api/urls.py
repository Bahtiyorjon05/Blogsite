from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenRefreshView

from . import views

# API URL patterns
urlpatterns = [
    # Authentication
    path('auth/login/', views.CustomTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('auth/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('auth/register/', views.UserRegistrationView.as_view(), name='user_register'),
    
    # User Profile
    path('profile/', views.UserProfileView.as_view(), name='user_profile'),
    path('preferences/', views.UserPreferencesView.as_view(), name='user_preferences'),
    
    # Posts
    path('posts/', views.PostListCreateView.as_view(), name='post_list_create'),
    path('posts/<slug:slug>/', views.PostDetailView.as_view(), name='post_detail'),
    path('posts/<int:post_id>/like/', views.like_post, name='post_like'),
    path('posts/<int:post_id>/comments/', views.CommentListCreateView.as_view(), name='post_comments'),
    
    # User Posts
    path('users/<str:username>/posts/', views.UserPostsView.as_view(), name='user_posts'),
    
    # Categories
    path('categories/', views.CategoryListView.as_view(), name='category_list'),
    path('categories/<slug:slug>/posts/', views.CategoryPostsView.as_view(), name='category_posts'),
    
    # Tags
    path('tags/', views.TagListView.as_view(), name='tag_list'),
    path('tags/<slug:slug>/posts/', views.TagPostsView.as_view(), name='tag_posts'),
    
    # Search
    path('search/', views.search_posts, name='search_posts'),
]
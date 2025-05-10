from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

# Set up the API router
router = DefaultRouter()
router.register(r'posts', views.PostViewSet)
router.register(r'categories', views.CategoryViewSet)
router.register(r'tags', views.TagViewSet)

urlpatterns = [
    # Main pages
    path('', views.home, name='home'),
    
    # Post URLs
    path('posts/', views.PostListView.as_view(), name='post_list'),
    path('posts/new/', views.PostCreateView.as_view(), name='create_post'),
    path('posts/<slug:slug>/', views.PostDetailView.as_view(), name='post_detail'),
    path('posts/<slug:slug>/edit/', views.PostUpdateView.as_view(), name='update_post'),
    path('posts/<slug:slug>/delete/', views.PostDeleteView.as_view(), name='delete_post'),
    
    # Comment and like functionality
    path('posts/<slug:slug>/comment/', views.add_comment, name='add_comment'),
    path('posts/<slug:slug>/like/', views.like_post, name='like_post'),
    
    # Category and tag URLs
    path('category/<slug:category_slug>/', views.PostListView.as_view(), name='category_posts'),
    path('tag/<slug:tag_slug>/', views.PostListView.as_view(), name='tag_posts'),
    path('categories/', views.category_list, name='category_list'),
    path('tags/', views.tag_list, name='tag_list'),
    
    # User authentication
    path('register/', views.register, name='register'),
    path('login/', views.user_login, name='login'),
    path('logout/', views.user_logout, name='logout'),
    
    # User profiles
    path('profile/edit/', views.edit_profile, name='edit_profile'),
    path('profile/<str:username>/', views.profile, name='user_profile'),
    path('profile/', views.profile, name='profile'),
    path('dashboard/', views.dashboard, name='dashboard'),
    
    # API endpoints
    path('api/', include(router.urls)),
    path('api/posts-list/', views.post_list_api, name='post_list_api'),
    path('api/posts/<slug:slug>/', views.post_detail_api, name='post_detail_api'),
    path('api/posts/create/', views.post_create_api, name='post_create_api'),
    path('api/posts/<slug:slug>/update/', views.post_update_api, name='post_update_api'),
    path('api/posts/<slug:slug>/delete/', views.post_delete_api, name='post_delete_api'),
]


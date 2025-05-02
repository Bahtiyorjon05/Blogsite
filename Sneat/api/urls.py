from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from . import views
from .dashboard import dashboard_stats, activity_timeline
from .ecommerce import create_order, update_order_status, update_invoice_status, product_search, order_details
from .users import user_profile, update_profile, update_settings, change_password, upload_avatar

router = DefaultRouter()
router.register(r'users', views.UserViewSet, basename='user')
router.register(r'profiles', views.UserProfileViewSet, basename='profile')
router.register(r'settings', views.UserSettingsViewSet, basename='settings')
router.register(r'dashboard-stats', views.DashboardStatsViewSet, basename='dashboard-stats')
router.register(r'tasks', views.TaskViewSet, basename='task')
# New API endpoints
router.register(r'categories', views.CategoryViewSet, basename='category')
router.register(r'products', views.ProductViewSet, basename='product')
router.register(r'orders', views.OrderViewSet, basename='order')
router.register(r'order-items', views.OrderItemViewSet, basename='order-item')
router.register(r'invoices', views.InvoiceViewSet, basename='invoice')

urlpatterns = [
    path('', include(router.urls)),
    path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('register/', views.UserRegistrationView.as_view(), name='register'),
    path('dashboard/stats/', dashboard_stats, name='dashboard-stats'),
    path('dashboard/activity/', activity_timeline, name='activity-timeline'),
    # E-commerce endpoints
    path('orders/create/', create_order, name='create-order'),
    path('orders/<int:order_id>/status/', update_order_status, name='update-order-status'),
    path('orders/<int:order_id>/details/', order_details, name='order-details'),
    path('invoices/<int:invoice_id>/status/', update_invoice_status, name='update-invoice-status'),
    path('products/search/', product_search, name='product-search'),
    # User management endpoints
    path('user/profile/', user_profile, name='user-profile'),
    path('user/profile/update/', update_profile, name='update-profile'),
    path('user/settings/update/', update_settings, name='update-settings'),
    path('user/password/change/', change_password, name='change-password'),
    path('user/avatar/upload/', upload_avatar, name='upload-avatar'),
]

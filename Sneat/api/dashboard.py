from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.db.models import Count, Sum
from django.utils import timezone
from datetime import timedelta
from django.contrib.auth.models import User
from myapp.models import Task, Order, Product, Invoice, Category

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def dashboard_stats(request):
    """
    Get dashboard statistics for the authenticated user
    """
    # Get counts
    task_count = Task.objects.filter(created_by=request.user).count()
    order_count = Order.objects.filter(user=request.user).count()
    
    # For admin users, show all stats
    if request.user.is_staff:
        total_users = User.objects.count()
        total_products = Product.objects.count()
        total_orders = Order.objects.count()
        total_revenue = Order.objects.aggregate(Sum('total_amount'))['total_amount__sum'] or 0
        
        # Recent orders
        recent_orders = Order.objects.all().order_by('-created_at')[:5]
        recent_orders_data = [{
            'id': order.id,
            'customer': order.user.username,
            'amount': float(order.total_amount),
            'status': order.status,
            'date': order.created_at
        } for order in recent_orders]
        
        # Sales data for chart
        today = timezone.now().date()
        last_week = today - timedelta(days=7)
        
        daily_sales = Order.objects.filter(
            created_at__date__gte=last_week
        ).values('created_at__date').annotate(
            total=Sum('total_amount')
        ).order_by('created_at__date')
        
        sales_data = [{
            'date': item['created_at__date'].strftime('%Y-%m-%d'),
            'amount': float(item['total'])
        } for item in daily_sales]
        
        # Product categories
        categories = Category.objects.annotate(
            product_count=Count('products')
        ).values('name', 'product_count')
        
        category_data = [{
            'name': item['name'],
            'count': item['product_count']
        } for item in categories]
        
        # Overdue invoices
        overdue_invoices = Invoice.objects.filter(
            status='unpaid',
            due_date__lt=today
        ).count()
        
        return Response({
            'user_stats': {
                'task_count': task_count,
                'order_count': order_count,
            },
            'admin_stats': {
                'total_users': total_users,
                'total_products': total_products,
                'total_orders': total_orders,
                'total_revenue': float(total_revenue),
                'overdue_invoices': overdue_invoices
            },
            'recent_orders': recent_orders_data,
            'sales_data': sales_data,
            'category_data': category_data
        })
    
    # For regular users, show only their stats
    else:
        # Recent tasks
        recent_tasks = Task.objects.filter(
            created_by=request.user
        ).order_by('-created_at')[:5]
        
        recent_tasks_data = [{
            'id': task.id,
            'title': task.title,
            'status': task.status,
            'due_date': task.due_date
        } for task in recent_tasks]
        
        # Recent orders
        recent_orders = Order.objects.filter(
            user=request.user
        ).order_by('-created_at')[:5]
        
        recent_orders_data = [{
            'id': order.id,
            'amount': float(order.total_amount),
            'status': order.status,
            'date': order.created_at
        } for order in recent_orders]
        
        return Response({
            'task_count': task_count,
            'order_count': order_count,
            'recent_tasks': recent_tasks_data,
            'recent_orders': recent_orders_data
        })


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def activity_timeline(request):
    """
    Get activity timeline for the authenticated user
    """
    # Combine tasks and orders to create a timeline
    timeline = []
    
    # Add tasks to timeline
    tasks = Task.objects.filter(created_by=request.user).order_by('-created_at')[:10]
    for task in tasks:
        timeline.append({
            'type': 'task',
            'id': task.id,
            'title': task.title,
            'status': task.status,
            'date': task.created_at,
            'description': f"Task '{task.title}' was {task.status}"
        })
    
    # Add orders to timeline
    orders = Order.objects.filter(user=request.user).order_by('-created_at')[:10]
    for order in orders:
        timeline.append({
            'type': 'order',
            'id': order.id,
            'title': f"Order #{order.id}",
            'status': order.status,
            'date': order.created_at,
            'description': f"Order #{order.id} was {order.status}"
        })
    
    # Sort timeline by date
    timeline.sort(key=lambda x: x['date'], reverse=True)
    
    return Response({
        'timeline': timeline[:10]  # Return only the 10 most recent items
    })

from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.response import Response
from rest_framework import status
from django.db.models import Sum, F, Q
from django.utils import timezone
from datetime import timedelta
from django.contrib.auth.models import User
from myapp.models import Product, Category, Order, OrderItem, Invoice
from .serializers import ProductSerializer, OrderSerializer, InvoiceSerializer

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_order(request):
    """
    Create a new order with items
    """
    # Get order data
    data = request.data
    items = data.get('items', [])
    
    # Validate items
    if not items:
        return Response({'error': 'No items provided'}, status=status.HTTP_400_BAD_REQUEST)
    
    # Calculate total amount
    total_amount = 0
    order_items = []
    
    for item in items:
        product_id = item.get('product_id')
        quantity = item.get('quantity', 1)
        
        try:
            product = Product.objects.get(id=product_id)
        except Product.DoesNotExist:
            return Response(
                {'error': f'Product with ID {product_id} does not exist'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Check if product is active
        if not product.is_active:
            return Response(
                {'error': f'Product {product.name} is not available'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Check if enough stock
        if product.stock < quantity:
            return Response(
                {'error': f'Not enough stock for {product.name}. Available: {product.stock}'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Calculate item total
        item_total = product.price * quantity
        total_amount += item_total
        
        # Add to order items
        order_items.append({
            'product': product,
            'quantity': quantity,
            'price': product.price
        })
    
    # Create order
    order = Order.objects.create(
        user=request.user,
        total_amount=total_amount,
        status='pending',
        shipping_address=data.get('shipping_address', ''),
        phone_number=data.get('phone_number', ''),
        email=data.get('email', request.user.email)
    )
    
    # Create order items
    for item in order_items:
        OrderItem.objects.create(
            order=order,
            product=item['product'],
            quantity=item['quantity'],
            price=item['price']
        )
        
        # Update product stock
        product = item['product']
        product.stock -= item['quantity']
        product.save()
    
    # Create invoice
    due_date = timezone.now().date() + timedelta(days=15)
    invoice_number = f"INV-{order.id}-{timezone.now().strftime('%Y%m%d')}"
    
    invoice = Invoice.objects.create(
        order=order,
        invoice_number=invoice_number,
        status='unpaid',
        due_date=due_date
    )
    
    # Return order data
    serializer = OrderSerializer(order)
    return Response(serializer.data, status=status.HTTP_201_CREATED)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def update_order_status(request, order_id):
    """
    Update order status
    """
    try:
        if request.user.is_staff:
            order = Order.objects.get(id=order_id)
        else:
            order = Order.objects.get(id=order_id, user=request.user)
    except Order.DoesNotExist:
        return Response(
            {'error': 'Order not found'},
            status=status.HTTP_404_NOT_FOUND
        )
    
    status_value = request.data.get('status')
    if not status_value:
        return Response(
            {'error': 'Status not provided'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    # Validate status
    valid_statuses = [s[0] for s in Order.STATUS_CHOICES]
    if status_value not in valid_statuses:
        return Response(
            {'error': f'Invalid status. Valid values are: {", ".join(valid_statuses)}'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    # Update order status
    order.status = status_value
    order.save()
    
    # If order is cancelled, restore product stock
    if status_value == 'cancelled':
        for item in order.items.all():
            product = item.product
            product.stock += item.quantity
            product.save()
    
    serializer = OrderSerializer(order)
    return Response(serializer.data)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def update_invoice_status(request, invoice_id):
    """
    Update invoice status
    """
    try:
        if request.user.is_staff:
            invoice = Invoice.objects.get(id=invoice_id)
        else:
            invoice = Invoice.objects.get(id=invoice_id, order__user=request.user)
    except Invoice.DoesNotExist:
        return Response(
            {'error': 'Invoice not found'},
            status=status.HTTP_404_NOT_FOUND
        )
    
    status_value = request.data.get('status')
    if not status_value:
        return Response(
            {'error': 'Status not provided'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    # Validate status
    valid_statuses = [s[0] for s in Invoice.STATUS_CHOICES]
    if status_value not in valid_statuses:
        return Response(
            {'error': f'Invalid status. Valid values are: {", ".join(valid_statuses)}'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    # Update invoice status
    invoice.status = status_value
    
    # If paid, update payment date
    if status_value == 'paid':
        invoice.payment_date = timezone.now().date()
        invoice.payment_method = request.data.get('payment_method', '')
    
    invoice.save()
    
    serializer = InvoiceSerializer(invoice)
    return Response(serializer.data)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def product_search(request):
    """
    Search for products
    """
    query = request.query_params.get('q', '')
    category = request.query_params.get('category', None)
    
    products = Product.objects.filter(is_active=True)
    
    if query:
        products = products.filter(
            Q(name__icontains=query) | 
            Q(description__icontains=query)
        )
    
    if category:
        products = products.filter(category_id=category)
    
    serializer = ProductSerializer(products, many=True)
    return Response(serializer.data)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def order_details(request, order_id):
    """
    Get order details including items
    """
    try:
        if request.user.is_staff:
            order = Order.objects.get(id=order_id)
        else:
            order = Order.objects.get(id=order_id, user=request.user)
    except Order.DoesNotExist:
        return Response(
            {'error': 'Order not found'},
            status=status.HTTP_404_NOT_FOUND
        )
    
    serializer = OrderSerializer(order)
    return Response(serializer.data)

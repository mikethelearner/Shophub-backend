from rest_framework import generics, status, permissions
from rest_framework.response import Response
from rest_framework.views import APIView
from django.shortcuts import get_object_or_404
from .models import Order, OrderItem
from .serializers import (
    OrderSerializer, 
    OrderCreateSerializer, 
    OrderStatusUpdateSerializer,
    CancellationRequestSerializer,
    CancellationResponseSerializer,
    DeliveryConfirmationSerializer,
    AdminDeliveryMarkSerializer
)
from products.models import Product


class OrderListView(generics.ListAPIView):
    serializer_class = OrderSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return Order.objects.filter(user=self.request.user).order_by('-created_at')


class OrderDetailView(generics.RetrieveAPIView):
    serializer_class = OrderSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return Order.objects.filter(user=self.request.user)


class OrderCreateView(generics.CreateAPIView):
    serializer_class = OrderCreateSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def perform_create(self, serializer):
        serializer.save()


class OrderCancelView(generics.UpdateAPIView):
    serializer_class = OrderSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return Order.objects.filter(user=self.request.user)
    
    def update(self, request, *args, **kwargs):
        order = self.get_object()
        
        # Check if order can be cancelled
        if order.status not in ['pending', 'processing']:
            return Response(
                {"error": "Order cannot be cancelled at this stage"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        order.status = 'cancelled'
        order.save()
        
        serializer = self.get_serializer(order)
        return Response(serializer.data)


class OrderStatusUpdateView(generics.UpdateAPIView):
    serializer_class = OrderStatusUpdateSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return Order.objects.all()
    
    def update(self, request, *args, **kwargs):
        # Debug print
        print("OrderStatusUpdateView.update() - request.data:", request.data)
        print("OrderStatusUpdateView.update() - request.data type:", type(request.data))
        
        # Check if user is admin
        if not request.user.is_staff:
            return Response(
                {"error": "Only admin users can update order status"},
                status=status.HTTP_403_FORBIDDEN
            )
        
        try:
            # Get the order object
            order = self.get_object()
            print(f"OrderStatusUpdateView.update() - order before: id={order.id}, status={order.status}, total_amount={order.total_amount}")
            
            # Ensure we're only passing the status field to the serializer
            status_data = {'status': request.data.get('status')}
            print("OrderStatusUpdateView.update() - status_data:", status_data)
            
            serializer = self.get_serializer(order, data=status_data)
            serializer.is_valid(raise_exception=True)
            self.perform_update(serializer)
            
            # Refresh the order from the database
            order.refresh_from_db()
            print(f"OrderStatusUpdateView.update() - order after: id={order.id}, status={order.status}, total_amount={order.total_amount}")
            
            return Response(serializer.data)
        except Exception as e:
            print("OrderStatusUpdateView.update() - Exception:", str(e))
            return Response(
                {"error": str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )


class AdminOrderListView(generics.ListAPIView):
    serializer_class = OrderSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        # Check if user is admin
        if not self.request.user.is_staff:
            return Order.objects.none()
        
        # Filter by status if provided
        status_filter = self.request.query_params.get('status', None)
        queryset = Order.objects.all().order_by('-created_at')
        
        if status_filter:
            queryset = queryset.filter(status=status_filter)
            
        return queryset
    
    def list(self, request, *args, **kwargs):
        # Check if user is admin
        if not request.user.is_staff:
            return Response(
                {"error": "Only admin users can view all orders"},
                status=status.HTTP_403_FORBIDDEN
            )
        
        return super().list(request, *args, **kwargs)


class CancellationRequestView(generics.UpdateAPIView):
    """User requests cancellation of an order"""
    serializer_class = CancellationRequestSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return Order.objects.filter(user=self.request.user)
    
    def update(self, request, *args, **kwargs):
        # Debug print
        print(f"CancellationRequestView.update() - request.data: {request.data}")
        print(f"CancellationRequestView.update() - request.data type: {type(request.data)}")
        
        try:
            # Get the order
            instance = self.get_object()
            print(f"CancellationRequestView.update() - order before: id={instance.id}, status={instance.status}, total_amount={instance.total_amount}")
            
            # Create the serializer
            serializer = self.get_serializer(instance, data=request.data)
            serializer.is_valid(raise_exception=True)
            
            # Update the instance
            self.perform_update(serializer)
            
            # Refresh the order from the database
            instance.refresh_from_db()
            print(f"CancellationRequestView.update() - order after: id={instance.id}, status={instance.status}, total_amount={instance.total_amount}")
            
            return Response(serializer.data)
        except Exception as e:
            print(f"CancellationRequestView.update() - Exception: {str(e)}")
            return Response(
                {"error": str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )


class CancellationResponseView(generics.UpdateAPIView):
    """Admin approves or rejects a cancellation request"""
    serializer_class = CancellationResponseSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return Order.objects.all()
    
    def update(self, request, *args, **kwargs):
        # Debug print
        print(f"CancellationResponseView.update() - request.data: {request.data}")
        print(f"CancellationResponseView.update() - request.data type: {type(request.data)}")
        
        # Check if user is admin
        if not request.user.is_staff:
            return Response(
                {"error": "Only admin users can respond to cancellation requests"},
                status=status.HTTP_403_FORBIDDEN
            )
        
        try:
            # Get the order
            instance = self.get_object()
            print(f"CancellationResponseView.update() - order before: id={instance.id}, status={instance.status}, total_amount={instance.total_amount}")
            
            # Create the serializer
            serializer = self.get_serializer(instance, data=request.data)
            serializer.is_valid(raise_exception=True)
            
            # Update the instance
            self.perform_update(serializer)
            
            # Refresh the order from the database
            instance.refresh_from_db()
            print(f"CancellationResponseView.update() - order after: id={instance.id}, status={instance.status}, total_amount={instance.total_amount}")
            
            return Response(serializer.data)
        except Exception as e:
            print(f"CancellationResponseView.update() - Exception: {str(e)}")
            return Response(
                {"error": str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )


class DeliveryConfirmationView(generics.UpdateAPIView):
    """User confirms delivery of an order"""
    serializer_class = DeliveryConfirmationSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return Order.objects.filter(user=self.request.user)
    
    def update(self, request, *args, **kwargs):
        # Debug print
        print(f"DeliveryConfirmationView.update() - request.data: {request.data}")
        print(f"DeliveryConfirmationView.update() - request.data type: {type(request.data)}")
        
        try:
            # Get the order
            instance = self.get_object()
            print(f"DeliveryConfirmationView.update() - order before: id={instance.id}, status={instance.status}, total_amount={instance.total_amount}")
            
            # Create the serializer
            serializer = self.get_serializer(instance, data=request.data)
            serializer.is_valid(raise_exception=True)
            
            # Update the instance
            self.perform_update(serializer)
            
            # Refresh the order from the database
            instance.refresh_from_db()
            print(f"DeliveryConfirmationView.update() - order after: id={instance.id}, status={instance.status}, total_amount={instance.total_amount}")
            
            return Response(serializer.data)
        except Exception as e:
            print(f"DeliveryConfirmationView.update() - Exception: {str(e)}")
            return Response(
                {"error": str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )


class AdminDeliveryMarkView(generics.UpdateAPIView):
    """Admin marks an order as delivered after user confirmation"""
    serializer_class = AdminDeliveryMarkSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return Order.objects.all()
    
    def update(self, request, *args, **kwargs):
        # Debug print
        print(f"AdminDeliveryMarkView.update() - request.data: {request.data}")
        print(f"AdminDeliveryMarkView.update() - request.data type: {type(request.data)}")
        
        # Check if user is admin
        if not request.user.is_staff:
            return Response(
                {"error": "Only admin users can mark orders as delivered"},
                status=status.HTTP_403_FORBIDDEN
            )
        
        try:
            # Get the order
            instance = self.get_object()
            print(f"AdminDeliveryMarkView.update() - order before: id={instance.id}, status={instance.status}, total_amount={instance.total_amount}")
            
            # Create the serializer
            serializer = self.get_serializer(instance, data=request.data)
            serializer.is_valid(raise_exception=True)
            
            # Update the instance
            self.perform_update(serializer)
            
            # Refresh the order from the database
            instance.refresh_from_db()
            print(f"AdminDeliveryMarkView.update() - order after: id={instance.id}, status={instance.status}, total_amount={instance.total_amount}")
            
            return Response(serializer.data)
        except Exception as e:
            print(f"AdminDeliveryMarkView.update() - Exception: {str(e)}")
            return Response(
                {"error": str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )


class PendingCancellationsView(generics.ListAPIView):
    """List all orders with pending cancellation requests (admin only)"""
    serializer_class = OrderSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        # Check if user is admin
        if not self.request.user.is_staff:
            return Order.objects.none()
        
        return Order.objects.filter(status='cancel_requested').order_by('-cancellation_requested_at')
    
    def list(self, request, *args, **kwargs):
        # Check if user is admin
        if not request.user.is_staff:
            return Response(
                {"error": "Only admin users can view pending cancellations"},
                status=status.HTTP_403_FORBIDDEN
            )
        
        return super().list(request, *args, **kwargs)


class PendingDeliveryConfirmationsView(generics.ListAPIView):
    """List all orders with delivery confirmations pending admin review (admin only)"""
    serializer_class = OrderSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        # Check if user is admin
        if not self.request.user.is_staff:
            return Order.objects.none()
        
        return Order.objects.filter(status='delivery_confirmed').order_by('-delivery_confirmed_at')
    
    def list(self, request, *args, **kwargs):
        # Check if user is admin
        if not request.user.is_staff:
            return Response(
                {"error": "Only admin users can view pending delivery confirmations"},
                status=status.HTTP_403_FORBIDDEN
            )
        
        return super().list(request, *args, **kwargs) 
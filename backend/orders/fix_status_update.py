from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions
from django.shortcuts import get_object_or_404
from .models import Order
from django.utils import timezone


class FixedOrderStatusUpdateView(APIView):
    """
    A view that directly updates the order status without using a serializer.
    This avoids issues with decimal validation.
    """
    permission_classes = [permissions.IsAuthenticated]
    
    def put(self, request, pk):
        # Debug print
        print("FixedOrderStatusUpdateView.put() - request.data:", request.data)
        print("FixedOrderStatusUpdateView.put() - request.data type:", type(request.data))
        
        # Check if user is admin
        if not request.user.is_staff:
            return Response(
                {"error": "Only admin users can update order status"},
                status=status.HTTP_403_FORBIDDEN
            )
        
        try:
            # Get the order object
            order = get_object_or_404(Order, id=pk)
            print(f"FixedOrderStatusUpdateView.put() - order before: id={order.id}, status={order.status}, total_amount={order.total_amount}")
            
            # Get the new status
            new_status = request.data.get('status')
            if not new_status:
                return Response(
                    {"error": "Status field is required"},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Validate the status
            valid_statuses = dict(Order.STATUS_CHOICES).keys()
            if new_status not in valid_statuses:
                return Response(
                    {"error": f"Invalid status. Must be one of: {', '.join(valid_statuses)}"},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Check status transitions
            old_status = order.status
            if old_status == 'cancelled' and new_status != 'cancelled':
                return Response(
                    {"error": "Cannot change status of a cancelled order"},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            if old_status == 'delivered' and new_status not in ['delivered', 'cancelled']:
                return Response(
                    {"error": "A delivered order can only be cancelled"},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Update the status
            order.status = new_status
            order.save(update_fields=['status'])
            
            # Refresh the order from the database
            order.refresh_from_db()
            print(f"FixedOrderStatusUpdateView.put() - order after: id={order.id}, status={order.status}, total_amount={order.total_amount}")
            
            return Response({
                'id': order.id,
                'status': order.status
            })
            
        except Exception as e:
            print("FixedOrderStatusUpdateView.put() - Exception:", str(e))
            return Response(
                {"error": str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )


class FixedDeliveryConfirmationView(APIView):
    """
    A view that directly confirms delivery without using a serializer.
    This avoids issues with decimal validation.
    """
    permission_classes = [permissions.IsAuthenticated]
    
    def put(self, request, pk):
        # Debug print
        print("FixedDeliveryConfirmationView.put() - request.data:", request.data)
        print("FixedDeliveryConfirmationView.put() - request.data type:", type(request.data))
        
        try:
            # Get the order object
            order = get_object_or_404(Order, id=pk, user=request.user)
            print(f"FixedDeliveryConfirmationView.put() - order before: id={order.id}, status={order.status}, total_amount={order.total_amount}")
            
            # Get the delivery notes
            delivery_notes = request.data.get('delivery_notes', '')
            
            # Confirm delivery
            if order.status != 'shipped':
                return Response(
                    {"error": "Cannot confirm delivery for this order. Order must be in 'shipped' status."},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Update the order directly
            order.status = 'delivery_confirmed'
            order.delivery_confirmed_at = timezone.now()
            order.delivery_notes = delivery_notes
            
            # Only update the specific fields
            update_fields = ['status', 'delivery_confirmed_at', 'delivery_notes']
            order.save(update_fields=update_fields)
            
            # Refresh the order from the database
            order.refresh_from_db()
            print(f"FixedDeliveryConfirmationView.put() - order after: id={order.id}, status={order.status}, total_amount={order.total_amount}")
            
            return Response({
                'id': order.id,
                'status': order.status,
                'delivery_confirmed_at': order.delivery_confirmed_at,
                'delivery_notes': order.delivery_notes
            })
            
        except Exception as e:
            print("FixedDeliveryConfirmationView.put() - Exception:", str(e))
            return Response(
                {"error": str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )


class FixedCancellationRequestView(APIView):
    """
    A view that directly requests cancellation without using a serializer.
    This avoids issues with decimal validation.
    """
    permission_classes = [permissions.IsAuthenticated]
    
    def put(self, request, pk):
        # Debug print
        print("FixedCancellationRequestView.put() - request.data:", request.data)
        print("FixedCancellationRequestView.put() - request.data type:", type(request.data))
        
        try:
            # Get the order object
            order = get_object_or_404(Order, id=pk, user=request.user)
            print(f"FixedCancellationRequestView.put() - order before: id={order.id}, status={order.status}, total_amount={order.total_amount}")
            
            # Get the cancellation reason
            cancellation_reason = request.data.get('cancellation_reason', '')
            
            # Request cancellation
            if order.status not in ['pending', 'processing']:
                return Response(
                    {"error": "Cannot request cancellation for this order. Order must be in 'pending' or 'processing' status."},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Update the order directly
            order.status = 'cancel_requested'
            order.cancellation_requested_at = timezone.now()
            order.cancellation_reason = cancellation_reason
            
            # Only update the specific fields
            update_fields = ['status', 'cancellation_requested_at', 'cancellation_reason']
            order.save(update_fields=update_fields)
            
            # Refresh the order from the database
            order.refresh_from_db()
            print(f"FixedCancellationRequestView.put() - order after: id={order.id}, status={order.status}, total_amount={order.total_amount}")
            
            return Response({
                'id': order.id,
                'status': order.status,
                'cancellation_requested_at': order.cancellation_requested_at,
                'cancellation_reason': order.cancellation_reason
            })
            
        except Exception as e:
            print("FixedCancellationRequestView.put() - Exception:", str(e))
            return Response(
                {"error": str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )


class FixedCancellationResponseView(APIView):
    """
    A view that directly responds to cancellation requests without using a serializer.
    This avoids issues with decimal validation.
    """
    permission_classes = [permissions.IsAuthenticated]
    
    def put(self, request, pk):
        # Debug print
        print("FixedCancellationResponseView.put() - request.data:", request.data)
        print("FixedCancellationResponseView.put() - request.data type:", type(request.data))
        
        # Check if user is admin
        if not request.user.is_staff:
            return Response(
                {"error": "Only admin users can respond to cancellation requests"},
                status=status.HTTP_403_FORBIDDEN
            )
        
        try:
            # Get the order object
            order = get_object_or_404(Order, id=pk)
            print(f"FixedCancellationResponseView.put() - order before: id={order.id}, status={order.status}, total_amount={order.total_amount}")
            
            # Get the approval status
            approve = request.data.get('approve', False)
            
            # Check if order is in cancel_requested status
            if order.status != 'cancel_requested':
                return Response(
                    {"error": "Cannot respond to cancellation for this order. Order must be in 'cancel_requested' status."},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Update the order directly
            if approve:
                order.status = 'cancelled'
                order.cancellation_approved = True
                
                # Only update the specific fields
                update_fields = ['status', 'cancellation_approved']
                order.save(update_fields=update_fields)
                
                # Return stock to inventory
                for item in order.items.all():
                    product = item.product
                    product.stock += item.quantity
                    product.save(update_fields=['stock'])
            else:
                order.status = 'processing'
                order.cancellation_rejected = True
                
                # Only update the specific fields
                update_fields = ['status', 'cancellation_rejected']
                order.save(update_fields=update_fields)
            
            # Refresh the order from the database
            order.refresh_from_db()
            print(f"FixedCancellationResponseView.put() - order after: id={order.id}, status={order.status}, total_amount={order.total_amount}")
            
            return Response({
                'id': order.id,
                'status': order.status,
                'cancellation_approved': order.cancellation_approved,
                'cancellation_rejected': order.cancellation_rejected
            })
            
        except Exception as e:
            print("FixedCancellationResponseView.put() - Exception:", str(e))
            return Response(
                {"error": str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )


class FixedAdminDeliveryMarkView(APIView):
    """
    A view that directly marks an order as delivered without using a serializer.
    This avoids issues with decimal validation.
    """
    permission_classes = [permissions.IsAuthenticated]
    
    def put(self, request, pk):
        # Debug print
        print("FixedAdminDeliveryMarkView.put() - request.data:", request.data)
        print("FixedAdminDeliveryMarkView.put() - request.data type:", type(request.data))
        
        # Check if user is admin
        if not request.user.is_staff:
            return Response(
                {"error": "Only admin users can mark orders as delivered"},
                status=status.HTTP_403_FORBIDDEN
            )
        
        try:
            # Get the order object
            order = get_object_or_404(Order, id=pk)
            print(f"FixedAdminDeliveryMarkView.put() - order before: id={order.id}, status={order.status}, total_amount={order.total_amount}")
            
            # Check if order is in delivery_confirmed status
            if order.status != 'delivery_confirmed':
                return Response(
                    {"error": "Cannot mark as delivered for this order. Order must be in 'delivery_confirmed' status."},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Update the order directly
            order.status = 'delivered'
            order.delivered_at = timezone.now()
            
            # Only update the specific fields
            update_fields = ['status', 'delivered_at']
            order.save(update_fields=update_fields)
            
            # Refresh the order from the database
            order.refresh_from_db()
            print(f"FixedAdminDeliveryMarkView.put() - order after: id={order.id}, status={order.status}, total_amount={order.total_amount}")
            
            return Response({
                'id': order.id,
                'status': order.status,
                'delivered_at': order.delivered_at
            })
            
        except Exception as e:
            print("FixedAdminDeliveryMarkView.put() - Exception:", str(e))
            return Response(
                {"error": str(e)},
                status=status.HTTP_400_BAD_REQUEST
            ) 
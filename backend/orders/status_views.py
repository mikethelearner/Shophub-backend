from rest_framework import status, permissions
from rest_framework.response import Response
from rest_framework.views import APIView
from django.shortcuts import get_object_or_404
from .models import Order
from .serializers import OrderSerializer

class OrderStatusUpdateView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    
    def put(self, request, pk=None):
        # Debug print
        print("OrderStatusUpdateView.put() - request.data:", request.data)
        print("OrderStatusUpdateView.put() - request.data type:", type(request.data))
        
        # Check if user is admin
        if not request.user.is_staff:
            return Response(
                {"error": "Only admin users can update order status"},
                status=status.HTTP_403_FORBIDDEN
            )
        
        try:
            # Get the order
            order = get_object_or_404(Order, pk=pk)
            print(f"OrderStatusUpdateView.put() - order before: id={order.id}, status={order.status}, total_amount={order.total_amount}")
            
            # Get the status from request data
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
            print(f"OrderStatusUpdateView.put() - order after: id={order.id}, status={order.status}, total_amount={order.total_amount}")
            
            # Return the updated order
            serializer = OrderSerializer(order)
            return Response(serializer.data)
            
        except Exception as e:
            print("OrderStatusUpdateView.put() - Exception:", str(e))
            return Response(
                {"error": str(e)},
                status=status.HTTP_400_BAD_REQUEST
            ) 
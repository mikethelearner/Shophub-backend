from django.urls import path
from .views import (
    OrderListView, 
    OrderDetailView, 
    OrderCreateView, 
    OrderCancelView,
    AdminOrderListView,
    PendingCancellationsView,
    PendingDeliveryConfirmationsView
)
from .fix_status_update import (
    FixedOrderStatusUpdateView,
    FixedDeliveryConfirmationView,
    FixedCancellationRequestView,
    FixedCancellationResponseView,
    FixedAdminDeliveryMarkView
)

urlpatterns = [
    path('', OrderListView.as_view(), name='order-list'),
    path('create/', OrderCreateView.as_view(), name='order-create'),
    path('<int:pk>/', OrderDetailView.as_view(), name='order-detail'),
    path('<int:pk>/cancel/', OrderCancelView.as_view(), name='order-cancel'),
    path('<int:pk>/status/', FixedOrderStatusUpdateView.as_view(), name='order-status-update'),
    path('admin/', AdminOrderListView.as_view(), name='admin-order-list'),
    path('my-orders/', OrderListView.as_view(), name='my-orders'),
    path('my-orders/<int:pk>/', OrderDetailView.as_view(), name='my-order-detail'),
    
    # New endpoints for cancellation and delivery
    path('<int:pk>/request-cancellation/', FixedCancellationRequestView.as_view(), name='request-cancellation'),
    path('<int:pk>/respond-cancellation/', FixedCancellationResponseView.as_view(), name='respond-cancellation'),
    path('<int:pk>/confirm-delivery/', FixedDeliveryConfirmationView.as_view(), name='confirm-delivery'),
    path('<int:pk>/mark-delivered/', FixedAdminDeliveryMarkView.as_view(), name='mark-delivered'),
    
    # Admin views for pending actions
    path('admin/pending-cancellations/', PendingCancellationsView.as_view(), name='pending-cancellations'),
    path('admin/pending-deliveries/', PendingDeliveryConfirmationsView.as_view(), name='pending-deliveries'),
] 
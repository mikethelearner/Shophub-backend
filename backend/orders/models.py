from django.db import models
from django.utils import timezone


class Order(models.Model):
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('processing', 'Processing'),
        ('shipped', 'Shipped'),
        ('delivered', 'Delivered'),
        ('cancelled', 'Cancelled'),
        ('cancel_requested', 'Cancellation Requested'),
        ('delivery_confirmed', 'Delivery Confirmed'),
    )
    
    PAYMENT_STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
    )
    
    PAYMENT_METHOD_CHOICES = (
        ('cod', 'Cash on Delivery'),
        ('card', 'Credit/Debit Card'),
        ('paypal', 'PayPal'),
        ('other', 'Other'),
    )
    
    user = models.ForeignKey('users.User', on_delete=models.CASCADE)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    payment_status = models.CharField(max_length=20, choices=PAYMENT_STATUS_CHOICES, default='pending')
    payment_method = models.CharField(max_length=20, choices=PAYMENT_METHOD_CHOICES, default='cod')
    
    # Cancellation and delivery fields
    cancellation_reason = models.TextField(blank=True, null=True)
    cancellation_requested_at = models.DateTimeField(blank=True, null=True)
    cancellation_approved = models.BooleanField(default=False)
    cancellation_rejected = models.BooleanField(default=False)
    delivered_at = models.DateTimeField(blank=True, null=True)
    delivery_confirmed_at = models.DateTimeField(blank=True, null=True)
    delivery_notes = models.TextField(blank=True, null=True)
    
    # Shipping address
    shipping_street = models.CharField(max_length=255)
    shipping_city = models.CharField(max_length=100)
    shipping_state = models.CharField(max_length=100)
    shipping_zip_code = models.CharField(max_length=20)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"Order #{self.id} - {self.get_status_display()}"
    
    @property
    def shipping_address(self):
        return f"{self.shipping_street}, {self.shipping_city}, {self.shipping_state} {self.shipping_zip_code}"
    
    def request_cancellation(self, reason=None):
        """User requests cancellation"""
        if self.status in ['pending', 'processing']:
            self.status = 'cancel_requested'
            self.cancellation_requested_at = timezone.now()
            self.cancellation_reason = reason
            
            # Only update the specific fields
            update_fields = ['status', 'cancellation_requested_at', 'cancellation_reason']
            self.save(update_fields=update_fields)
            return True
        return False
    
    def approve_cancellation(self):
        """Admin approves cancellation request"""
        if self.status == 'cancel_requested':
            self.status = 'cancelled'
            self.cancellation_approved = True
            
            # Only update the specific fields
            update_fields = ['status', 'cancellation_approved']
            self.save(update_fields=update_fields)
            
            # Return stock to inventory
            for item in self.items.all():
                product = item.product
                product.stock += item.quantity
                product.save(update_fields=['stock'])
            
            return True
        return False
    
    def reject_cancellation(self):
        """Admin rejects cancellation request"""
        if self.status == 'cancel_requested':
            # Revert to previous status (usually processing)
            self.status = 'processing'
            self.cancellation_rejected = True
            
            # Only update the specific fields
            update_fields = ['status', 'cancellation_rejected']
            self.save(update_fields=update_fields)
            return True
        return False
    
    def confirm_delivery(self, notes=None):
        """User confirms delivery"""
        if self.status == 'shipped':
            self.status = 'delivery_confirmed'
            self.delivery_confirmed_at = timezone.now()
            
            # Only update the specific fields
            update_fields = ['status', 'delivery_confirmed_at']
            
            if notes:
                self.delivery_notes = notes
                update_fields.append('delivery_notes')
                
            self.save(update_fields=update_fields)
            return True
        return False
    
    def mark_delivered(self):
        """Admin marks as delivered after user confirmation"""
        if self.status == 'delivery_confirmed':
            self.status = 'delivered'
            self.delivered_at = timezone.now()
            
            # Only update the specific fields
            update_fields = ['status', 'delivered_at']
            self.save(update_fields=update_fields)
            return True
        return False


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey('products.Product', on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    
    def __str__(self):
        return f"{self.quantity} x {self.product.name} in Order #{self.order.id}"
    
    @property
    def total(self):
        try:
            # Convert price to float before multiplication to avoid Decimal128 issues
            price_float = float(self.price)
            return self.quantity * price_float
        except (TypeError, ValueError) as e:
            print(f"Error calculating total: {e}")
            return 0 
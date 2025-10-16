from rest_framework import serializers
from .models import Order, OrderItem
from products.serializers import ProductSerializer
from users.serializers import UserSerializer


class OrderItemSerializer(serializers.ModelSerializer):
    product = ProductSerializer(read_only=True)
    
    class Meta:
        model = OrderItem
        fields = ('id', 'product', 'quantity', 'price', 'total')
        read_only_fields = ('id', 'total')
    
    def to_representation(self, instance):
        representation = super().to_representation(instance)
        
        # Handle price field - ensure it's a float
        try:
            if 'price' in representation and representation['price'] is not None:
                representation['price'] = float(representation['price'])
        except (TypeError, ValueError) as e:
            print(f"Error converting price to float: {e}")
            representation['price'] = 0
        
        # Handle total field - calculate it directly here to avoid model property issues
        try:
            quantity = instance.quantity or 0
            price = float(instance.price) if instance.price else 0
            representation['total'] = quantity * price
        except (TypeError, ValueError) as e:
            print(f"Error calculating total in serializer: {e}")
            representation['total'] = 0
            
        return representation


class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True, read_only=True)
    user = UserSerializer(read_only=True)
    
    class Meta:
        model = Order
        fields = (
            'id', 'user', 'items', 'total_amount', 'status', 
            'payment_status', 'payment_method', 'shipping_address',
            'created_at', 'updated_at', 'cancellation_reason', 
            'cancellation_requested_at', 'cancellation_approved',
            'delivery_confirmed_at', 'delivery_notes'
        )
        read_only_fields = ('id', 'created_at', 'updated_at')


class OrderCreateSerializer(serializers.ModelSerializer):
    shipping_street = serializers.CharField(required=True)
    shipping_city = serializers.CharField(required=True)
    shipping_state = serializers.CharField(required=True)
    shipping_zip_code = serializers.CharField(required=True)
    cart_items = serializers.JSONField(required=True, write_only=True)
    
    class Meta:
        model = Order
        fields = (
            'payment_method', 'shipping_street', 'shipping_city', 
            'shipping_state', 'shipping_zip_code', 'cart_items'
        )
    
    def to_representation(self, instance):
        # Use the OrderSerializer for the response
        return OrderSerializer(instance, context=self.context).data
    
    def create(self, validated_data):
        # Debug: Log the validated data
        print("OrderCreateSerializer.create() - validated_data:", validated_data)
        
        user = self.context['request'].user
        cart_items = validated_data.pop('cart_items')
        
        # Debug: Log the cart items
        print("OrderCreateSerializer.create() - cart_items:", cart_items)
        
        if not cart_items:
            raise serializers.ValidationError("Your cart is empty.")
        
        # Calculate total amount from the provided cart items
        total_amount = 0
        for item in cart_items:
            product_id = item.get('id')
            quantity = item.get('quantity', 1)
            price = item.get('price', 0)
            
            # Convert price to float if it's a string
            if isinstance(price, str):
                try:
                    price = float(price)
                except (ValueError, TypeError):
                    print(f"Error converting price '{price}' to float")
                    price = 0
            
            # Debug: Log each item
            print(f"Processing item: id={product_id}, quantity={quantity}, price={price}")
            
            total_amount += price * quantity
        
        # Create order
        order = Order.objects.create(
            user=user,
            total_amount=total_amount,
            payment_method=validated_data.get('payment_method', 'cod'),
            shipping_street=validated_data.get('shipping_street'),
            shipping_city=validated_data.get('shipping_city'),
            shipping_state=validated_data.get('shipping_state'),
            shipping_zip_code=validated_data.get('shipping_zip_code')
        )
        
        # Create order items
        from products.models import Product
        
        for item in cart_items:
            product_id = item.get('id')
            quantity = item.get('quantity', 1)
            price = item.get('price', 0)
            
            # Convert price to float if it's a string
            if isinstance(price, str):
                try:
                    price = float(price)
                except (ValueError, TypeError):
                    print(f"Error converting price '{price}' to float")
                    price = 0
            
            try:
                product = Product.objects.get(id=product_id)
                
                OrderItem.objects.create(
                    order=order,
                    product=product,
                    quantity=quantity,
                    price=price
                )
                
                # Update product stock
                try:
                    current_stock = product.stock
                    if isinstance(current_stock, str):
                        current_stock = float(current_stock)
                    
                    # Ensure quantity is a number
                    if isinstance(quantity, str):
                        quantity = int(quantity)
                    
                    # Calculate new stock and ensure it's a float
                    new_stock = float(max(0, current_stock - quantity))
                    
                    # Update stock directly with raw query to avoid decimal conversion issues
                    from django.db import connection
                    with connection.cursor() as cursor:
                        cursor.execute(
                            "UPDATE products_product SET stock = %s WHERE id = %s",
                            [new_stock, product.id]
                        )
                except Exception as e:
                    print(f"Error updating product stock: {e}")
                    # Continue with order creation even if stock update fails
                
            except Product.DoesNotExist:
                # Debug: Log if product doesn't exist
                print(f"Product with id {product_id} does not exist")
                # If product doesn't exist, just skip it
                continue
        
        return order


class OrderStatusUpdateSerializer(serializers.Serializer):
    """
    A simplified serializer for order status updates that only handles the status field.
    This avoids issues with decimal validation for other fields.
    """
    status = serializers.CharField(required=True)
    
    def validate_status(self, value):
        valid_statuses = dict(Order.STATUS_CHOICES).keys()
        if value not in valid_statuses:
            raise serializers.ValidationError(f"Invalid status. Must be one of: {', '.join(valid_statuses)}")
        return value
    
    def update(self, instance, validated_data):
        old_status = instance.status
        new_status = validated_data.get('status')
        
        # Prevent certain status transitions
        if old_status == 'cancelled' and new_status != 'cancelled':
            raise serializers.ValidationError("Cannot change status of a cancelled order")
        
        if old_status == 'delivered' and new_status not in ['delivered', 'cancelled']:
            raise serializers.ValidationError("A delivered order can only be cancelled")
        
        # Only update the status field
        instance.status = new_status
        instance.save(update_fields=['status'])
        
        return instance
    
    def to_representation(self, instance):
        return {
            'id': instance.id,
            'status': instance.status
        }


class CancellationRequestSerializer(serializers.Serializer):
    """
    A simplified serializer for cancellation requests that only handles the cancellation_reason field.
    This avoids issues with decimal validation for other fields.
    """
    cancellation_reason = serializers.CharField(required=False, allow_blank=True)
    
    def update(self, instance, validated_data):
        # Debug print
        print(f"CancellationRequestSerializer.update() - validated_data: {validated_data}")
        print(f"CancellationRequestSerializer.update() - instance before: status={instance.status}, total_amount={instance.total_amount}")
        
        # Use the model method to request cancellation
        reason = validated_data.get('cancellation_reason', '')
        success = instance.request_cancellation(reason)
        
        if not success:
            raise serializers.ValidationError("Cannot request cancellation for this order")
        
        # Debug print
        print(f"CancellationRequestSerializer.update() - instance after: status={instance.status}, total_amount={instance.total_amount}")
        
        return instance
    
    def to_representation(self, instance):
        return {
            'id': instance.id,
            'status': instance.status,
            'cancellation_requested_at': instance.cancellation_requested_at,
            'cancellation_reason': instance.cancellation_reason
        }


class CancellationResponseSerializer(serializers.Serializer):
    """
    A simplified serializer for cancellation responses that only handles the approve field.
    This avoids issues with decimal validation for other fields.
    """
    approve = serializers.BooleanField(write_only=True)
    
    def update(self, instance, validated_data):
        # Debug print
        print(f"CancellationResponseSerializer.update() - validated_data: {validated_data}")
        print(f"CancellationResponseSerializer.update() - instance before: status={instance.status}, total_amount={instance.total_amount}")
        
        approve = validated_data.get('approve', False)
        
        if approve:
            success = instance.approve_cancellation()
        else:
            success = instance.reject_cancellation()
            
        if not success:
            raise serializers.ValidationError("Cannot process cancellation response for this order")
        
        # Debug print
        print(f"CancellationResponseSerializer.update() - instance after: status={instance.status}, total_amount={instance.total_amount}")
        
        return instance
    
    def to_representation(self, instance):
        return {
            'id': instance.id,
            'status': instance.status,
            'cancellation_approved': instance.cancellation_approved,
            'cancellation_rejected': instance.cancellation_rejected
        }


class DeliveryConfirmationSerializer(serializers.Serializer):
    """
    A simplified serializer for delivery confirmation that only handles the delivery_notes field.
    This avoids issues with decimal validation for other fields.
    """
    delivery_notes = serializers.CharField(required=False, allow_blank=True)
    
    def update(self, instance, validated_data):
        # Debug print
        print(f"DeliveryConfirmationSerializer.update() - validated_data: {validated_data}")
        print(f"DeliveryConfirmationSerializer.update() - instance before: status={instance.status}, total_amount={instance.total_amount}")
        
        notes = validated_data.get('delivery_notes', '')
        success = instance.confirm_delivery(notes)
        
        if not success:
            raise serializers.ValidationError("Cannot confirm delivery for this order. Order must be in 'shipped' status.")
        
        # Debug print
        print(f"DeliveryConfirmationSerializer.update() - instance after: status={instance.status}, total_amount={instance.total_amount}")
        
        return instance
    
    def to_representation(self, instance):
        return {
            'id': instance.id,
            'status': instance.status,
            'delivery_confirmed_at': instance.delivery_confirmed_at,
            'delivery_notes': instance.delivery_notes
        }


class AdminDeliveryMarkSerializer(serializers.Serializer):
    """
    A simplified serializer for admin delivery marking that doesn't require any fields.
    This avoids issues with decimal validation for other fields.
    """
    
    def update(self, instance, validated_data):
        # Debug print
        print(f"AdminDeliveryMarkSerializer.update() - instance before: status={instance.status}, total_amount={instance.total_amount}")
        
        success = instance.mark_delivered()
        
        if not success:
            raise serializers.ValidationError("Cannot mark as delivered for this order")
        
        # Debug print
        print(f"AdminDeliveryMarkSerializer.update() - instance after: status={instance.status}, total_amount={instance.total_amount}")
        
        return instance
    
    def to_representation(self, instance):
        return {
            'id': instance.id,
            'status': instance.status,
            'delivered_at': instance.delivered_at
        } 
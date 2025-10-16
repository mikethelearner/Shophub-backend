from rest_framework import serializers
from .models import Cart, CartItem
from products.models import Product
from products.serializers import ProductListSerializer


class CartItemSerializer(serializers.ModelSerializer):
    product = ProductListSerializer(read_only=True)
    product_id = serializers.IntegerField(write_only=True)
    total = serializers.SerializerMethodField()
    
    class Meta:
        model = CartItem
        fields = ('id', 'product', 'product_id', 'quantity', 'total')
    
    def get_total(self, obj):
        return obj.total
    
    def validate(self, data):
        try:
            product = Product.objects.get(id=data['product_id'])
            if data['quantity'] > product.stock:
                raise serializers.ValidationError(f"Only {product.stock} items available in stock.")
        except Product.DoesNotExist:
            raise serializers.ValidationError("Product not found.")
        
        return data
    
    def create(self, validated_data):
        product_id = validated_data.pop('product_id')
        product = Product.objects.get(id=product_id)
        cart = validated_data.get('cart')
        
        try:
            # Update existing item
            item = CartItem.objects.get(cart=cart, product=product)
            item.quantity += validated_data.get('quantity', 1)
            item.save()
        except CartItem.DoesNotExist:
            # Create new item
            item = CartItem.objects.create(
                cart=cart,
                product=product,
                **validated_data
            )
        
        return item


class CartSerializer(serializers.ModelSerializer):
    items = CartItemSerializer(many=True, read_only=True)
    total = serializers.SerializerMethodField()
    item_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Cart
        fields = ('id', 'items', 'total', 'item_count', 'created_at', 'updated_at')
    
    def get_total(self, obj):
        return obj.total
    
    def get_item_count(self, obj):
        return obj.item_count 
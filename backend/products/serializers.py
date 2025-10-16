from rest_framework import serializers
from .models import Product, ProductReview
from users.serializers import UserSerializer


class ProductReviewSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    
    class Meta:
        model = ProductReview
        fields = ('id', 'user', 'rating', 'comment', 'created_at')
        read_only_fields = ('id', 'created_at')


class ProductSerializer(serializers.ModelSerializer):
    reviews = ProductReviewSerializer(many=True, read_only=True)
    
    class Meta:
        model = Product
        fields = (
            'id', 'name', 'description', 'price', 'category', 
            'manufacturer', 'stock', 'image_url', 'rating', 
            'is_active', 'created_at', 'updated_at', 'reviews'
        )
        read_only_fields = ('id', 'created_at', 'updated_at')


# Add a dedicated serializer for image uploads only
class ProductImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ('id', 'image_url')
        read_only_fields = ('id',)
        extra_kwargs = {
            'image_url': {'required': True}
        }
    
    def validate(self, attrs):
        # Only validate the image_url field, ignore all other fields
        return {'image_url': attrs.get('image_url')}


class ProductListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ('id', 'name', 'description', 'price', 'category', 'image_url', 'rating', 'stock', 'manufacturer')


class AddProductReviewSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductReview
        fields = ('rating', 'comment')
    
    def create(self, validated_data):
        product_id = self.context['product_id']
        user = self.context['request'].user
        
        # Check if user already reviewed this product
        if ProductReview.objects.filter(product_id=product_id, user=user).exists():
            raise serializers.ValidationError("You have already reviewed this product.")
        
        return ProductReview.objects.create(
            product_id=product_id,
            user=user,
            **validated_data
        ) 
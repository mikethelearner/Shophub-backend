from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from .models import Cart, CartItem
from .serializers import CartSerializer, CartItemSerializer
from products.models import Product


class CartView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request):
        cart, created = Cart.objects.get_or_create(user=request.user)
        serializer = CartSerializer(cart)
        return Response(serializer.data)


class AddToCartView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request):
        product_id = request.data.get('product_id')
        quantity = int(request.data.get('quantity', 1))
        
        try:
            product = Product.objects.get(id=product_id)
        except Product.DoesNotExist:
            return Response(
                {"error": "Product not found"}, 
                status=status.HTTP_404_NOT_FOUND
            )
        
        if quantity <= 0:
            return Response(
                {"error": "Quantity must be greater than zero"}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        if quantity > product.stock:
            return Response(
                {"error": f"Only {product.stock} items available in stock"}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Get or create cart
        cart, created = Cart.objects.get_or_create(user=request.user)
        
        # Check if item already exists in cart
        try:
            cart_item = CartItem.objects.get(cart=cart, product=product)
            cart_item.quantity += quantity
            cart_item.save()
        except CartItem.DoesNotExist:
            cart_item = CartItem.objects.create(
                cart=cart,
                product=product,
                quantity=quantity
            )
        
        serializer = CartSerializer(cart)
        return Response(serializer.data)


class UpdateCartItemView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    
    def put(self, request, pk):
        try:
            cart_item = CartItem.objects.get(
                pk=pk, 
                cart__user=request.user
            )
        except CartItem.DoesNotExist:
            return Response(
                {"error": "Item not found in cart"}, 
                status=status.HTTP_404_NOT_FOUND
            )
        
        quantity = int(request.data.get('quantity', 1))
        
        if quantity <= 0:
            return Response(
                {"error": "Quantity must be greater than zero"}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        if quantity > cart_item.product.stock:
            return Response(
                {"error": f"Only {cart_item.product.stock} items available in stock"}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        cart_item.quantity = quantity
        cart_item.save()
        
        serializer = CartSerializer(cart_item.cart)
        return Response(serializer.data)


class RemoveFromCartView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    
    def delete(self, request, pk):
        try:
            cart_item = CartItem.objects.get(
                pk=pk, 
                cart__user=request.user
            )
        except CartItem.DoesNotExist:
            return Response(
                {"error": "Item not found in cart"}, 
                status=status.HTTP_404_NOT_FOUND
            )
        
        cart = cart_item.cart
        cart_item.delete()
        
        serializer = CartSerializer(cart)
        return Response(serializer.data)


class ClearCartView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    
    def delete(self, request):
        try:
            cart = Cart.objects.get(user=request.user)
            cart.items.all().delete()
            
            serializer = CartSerializer(cart)
            return Response(serializer.data)
        except Cart.DoesNotExist:
            return Response(
                {"error": "Cart not found"}, 
                status=status.HTTP_404_NOT_FOUND
            ) 
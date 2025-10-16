from rest_framework import generics, permissions, status, filters, viewsets
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from .models import Product, ProductReview
from .serializers import (
    ProductSerializer, 
    ProductListSerializer, 
    ProductReviewSerializer,
    AddProductReviewSerializer,
    ProductImageSerializer
)
from django.http import Http404
from rest_framework.decorators import action
from decimal import Decimal, InvalidOperation
from rest_framework.parsers import JSONParser, MultiPartParser, FormParser


class ProductListView(generics.ListAPIView):
    serializer_class = ProductListSerializer
    permission_classes = [permissions.AllowAny]
    # Remove filter backends as they don't work well with MongoDB
    # filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    # filterset_fields = ['category', 'manufacturer']
    # search_fields = ['name', 'description', 'manufacturer']
    # ordering_fields = ['price', 'rating', 'created_at']
    
    def get_queryset(self):
        # Get all products and manually filter them
        all_products = list(Product.objects.all())
        # Filter active products
        return [p for p in all_products if p.is_active]
    
    def list(self, request, *args, **kwargs):
        try:
            queryset = self.get_queryset()
            serializer = self.get_serializer(queryset, many=True)
            return Response(serializer.data)
        except Exception as e:
            return Response(
                {"error": "Error loading products", "detail": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


# Add ProductViewSet for admin operations
class ProductViewSet(viewsets.ModelViewSet):
    """
    A viewset for handling product CRUD operations.
    Only authenticated admin users can create, update, or delete products.
    """
    serializer_class = ProductSerializer
    queryset = Product.objects.all()
    parser_classes = [JSONParser, MultiPartParser, FormParser]
    
    def get_permissions(self):
        """
        Instantiates and returns the list of permissions that this view requires.
        """
        if self.action in ['create', 'update', 'partial_update', 'destroy', 'update_product', 'upload_image']:
            permission_classes = [permissions.IsAuthenticated]
        else:
            permission_classes = [permissions.AllowAny]
        return [permission() for permission in permission_classes]
    
    @action(detail=True, methods=['post'], parser_classes=[MultiPartParser, FormParser])
    def upload_image(self, request, pk=None):
        """
        Upload an image for a product.
        Only admin users can upload images.
        """
        try:
            # Check if user is admin
            if request.user.role != 'admin':
                return Response(
                    {"error": "Only admin users can upload product images"},
                    status=status.HTTP_403_FORBIDDEN
                )
            
            # Log the request data for debugging
            print(f"Image upload request data: {request.data}")
            print(f"Image upload request FILES: {request.FILES}")
            
            # Get the product instance
            product = self.get_object()
            
            # Check if an image was provided
            if 'image' not in request.FILES:
                return Response(
                    {"error": "No image file provided"},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Directly update the image field without using serializer
            try:
                # Save the previous image path for logging
                previous_image = product.image_url.name if product.image_url else None
                
                # Update the image directly
                product.image_url = request.FILES['image']
                product.save(update_fields=['image_url'])
                
                print(f"Image updated successfully. Previous: {previous_image}, New: {product.image_url.name}")
                
                # Return success response with image URL
                return Response({
                    "success": "Image uploaded successfully",
                    "data": {
                        "id": product.id,
                        "image_url": product.image_url.url if product.image_url else None
                    }
                }, status=status.HTTP_200_OK)
            except Exception as e:
                print(f"Error saving image: {str(e)}")
                return Response(
                    {"error": "Failed to save image", "detail": str(e)},
                    status=status.HTTP_400_BAD_REQUEST
                )
        except Exception as e:
            print(f"Unexpected error in upload_image: {str(e)}")
            return Response(
                {"error": "Error uploading image", "detail": str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
    
    @action(detail=True, methods=['post'], url_path='update-product')
    def update_product(self, request, pk=None):
        """
        Custom action to update a product with special handling for the price field.
        """
        try:
            # Check if user is admin
            if request.user.role != 'admin':
                return Response(
                    {"error": "Only admin users can update products"},
                    status=status.HTTP_403_FORBIDDEN
                )
            
            # Get the product instance
            product = self.get_object()
            
            # Extract data from request
            data = request.data.copy()
            
            # Print the full request data for debugging
            print("Update product request data:", data)
            print("Original product data:", {
                "name": product.name,
                "description": product.description,
                "price": product.price,
                "category": product.category,
                "stock": product.stock,
                "manufacturer": product.manufacturer,
                "rating": product.rating
            })
            
            # Handle price field explicitly
            if 'price' in data:
                try:
                    price_str = str(data['price']).strip()
                    # Convert to Decimal
                    price = Decimal(price_str)
                    # Format with 2 decimal places
                    data['price'] = price.quantize(Decimal('0.01'))
                    print(f"Processed price: {data['price']} (type: {type(data['price'])})")
                except (ValueError, TypeError, InvalidOperation) as e:
                    print(f"Price conversion error: {str(e)}")
                    return Response(
                        {"error": f"Invalid price format: {str(e)}"},
                        status=status.HTTP_400_BAD_REQUEST
                    )
            
            # Handle stock field
            if 'stock' in data:
                try:
                    stock = int(data['stock'])
                    data['stock'] = stock
                    print(f"Processed stock: {data['stock']} (type: {type(data['stock'])})")
                except (ValueError, TypeError) as e:
                    print(f"Stock conversion error: {str(e)}")
                    return Response(
                        {"error": f"Invalid stock format: {str(e)}"},
                        status=status.HTTP_400_BAD_REQUEST
                    )
            
            # Handle rating field - ensure it's a valid decimal
            if 'rating' not in data:
                # If rating is not provided, use the existing value
                data['rating'] = product.rating
            else:
                try:
                    rating_str = str(data['rating']).strip()
                    # Convert to Decimal with 1 decimal place
                    rating = Decimal(rating_str)
                    data['rating'] = rating.quantize(Decimal('0.1'))
                    print(f"Processed rating: {data['rating']} (type: {type(data['rating'])})")
                except (ValueError, TypeError, InvalidOperation) as e:
                    print(f"Rating conversion error: {str(e)}")
                    return Response(
                        {"error": f"Invalid rating format: {str(e)}"},
                        status=status.HTTP_400_BAD_REQUEST
                    )
            
            # Log other fields
            if 'description' in data:
                print(f"Description: '{data['description']}' (type: {type(data['description'])})")
            
            if 'manufacturer' in data:
                print(f"Manufacturer: '{data['manufacturer']}' (type: {type(data['manufacturer'])})")
            
            # Update the product
            serializer = self.get_serializer(product, data=data, partial=True)
            
            # Print validation errors if any
            if not serializer.is_valid():
                print("Serializer validation errors:", serializer.errors)
                return Response(
                    serializer.errors,
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            self.perform_update(serializer)
            
            # Log the updated product data
            updated_product = self.get_object()
            print("Updated product data:", {
                "name": updated_product.name,
                "description": updated_product.description,
                "price": updated_product.price,
                "category": updated_product.category,
                "stock": updated_product.stock,
                "manufacturer": updated_product.manufacturer,
                "rating": updated_product.rating
            })
            
            return Response(serializer.data)
        except Exception as e:
            print(f"Unexpected error in update_product: {str(e)}")
            return Response(
                {"error": "Error updating product", "detail": str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
    
    def create(self, request, *args, **kwargs):
        try:
            # Check if user is admin
            if request.user.role != 'admin':
                return Response(
                    {"error": "Only admin users can create products"},
                    status=status.HTTP_403_FORBIDDEN
                )
            
            # Handle price field
            if 'price' in request.data:
                try:
                    # Convert price to Decimal
                    price = request.data.get('price')
                    if isinstance(price, str):
                        price = Decimal(price)
                    request.data['price'] = price
                except (ValueError, TypeError, InvalidOperation) as e:
                    return Response(
                        {"error": f"Invalid price format: {str(e)}"},
                        status=status.HTTP_400_BAD_REQUEST
                    )
                
            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            self.perform_create(serializer)
            headers = self.get_success_headers(serializer.data)
            return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)
        except Exception as e:
            return Response(
                {"error": "Error creating product", "detail": str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
    
    def update(self, request, *args, **kwargs):
        try:
            # Check if user is admin
            if request.user.role != 'admin':
                return Response(
                    {"error": "Only admin users can update products"},
                    status=status.HTTP_403_FORBIDDEN
                )
            
            # Log the request data and content type for debugging
            print(f"Update request data: {request.data}")
            print(f"Update request content type: {request.content_type}")
            print(f"Update request FILES: {request.FILES}")
            
            # Get the instance
            instance = self.get_object()
            
            # Special handling for image uploads - redirect to the dedicated image upload endpoint
            if 'image' in request.FILES:
                print(f"Redirecting image upload to dedicated endpoint")
                return self.upload_image(request, pk=kwargs.get('pk'))
            
            # Handle price field
            if 'price' in request.data:
                try:
                    # Convert price to Decimal
                    price = request.data.get('price')
                    if isinstance(price, str):
                        price = Decimal(price)
                    request.data['price'] = price
                except Exception as e:
                    return Response(
                        {"error": f"Invalid price format: {str(e)}"},
                        status=status.HTTP_400_BAD_REQUEST
                    )
            
            # Update the instance
            serializer = self.get_serializer(instance, data=request.data, partial=kwargs.get('partial', False))
            
            if not serializer.is_valid():
                print(f"Serializer validation errors: {serializer.errors}")
                return Response(
                    serializer.errors,
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            self.perform_update(serializer)
            
            return Response(serializer.data)
        except Exception as e:
            print(f"Unexpected error in update: {str(e)}")
            return Response(
                {"error": "Error updating product", "detail": str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
    
    def destroy(self, request, *args, **kwargs):
        try:
            # Check if user is admin
            if request.user.role != 'admin':
                return Response(
                    {"error": "Only admin users can delete products"},
                    status=status.HTTP_403_FORBIDDEN
                )
                
            return super().destroy(request, *args, **kwargs)
        except Exception as e:
            return Response(
                {"error": "Error deleting product", "detail": str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )


class ProductDetailView(generics.RetrieveAPIView):
    serializer_class = ProductSerializer
    permission_classes = [permissions.AllowAny]
    
    def get_object(self):
        try:
            pk = self.kwargs.get('pk')
            return Product.objects.get(id=pk)
        except Product.DoesNotExist:
            raise Http404("Product not found")


class ProductReviewCreateView(generics.CreateAPIView):
    serializer_class = AddProductReviewSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['product_id'] = self.kwargs['pk']
        return context


class ProductReviewListView(generics.ListAPIView):
    serializer_class = ProductReviewSerializer
    permission_classes = [permissions.AllowAny]
    
    def get_queryset(self):
        return ProductReview.objects.filter(product_id=self.kwargs['pk'])


class ProductByCategoryView(generics.ListAPIView):
    serializer_class = ProductListSerializer
    permission_classes = [permissions.AllowAny]
    
    def get_queryset(self):
        category = self.kwargs['category']
        # Get all products and manually filter them
        all_products = list(Product.objects.all())
        # Filter by category and active status
        return [p for p in all_products if p.category == category and p.is_active] 
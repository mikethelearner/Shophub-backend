from django.urls import path
from rest_framework.routers import DefaultRouter
from .views import (
    ProductListView, 
    ProductDetailView, 
    ProductReviewCreateView,
    ProductReviewListView,
    ProductByCategoryView,
    ProductViewSet
)

# Create a router for the viewset
router = DefaultRouter()
# Register with an explicit prefix
router.register(r'products', ProductViewSet)

urlpatterns = [
    path('list/', ProductListView.as_view(), name='product-list'),
    path('detail/<int:pk>/', ProductDetailView.as_view(), name='product-detail'),
    path('<int:pk>/reviews/', ProductReviewListView.as_view(), name='product-reviews'),
    path('<int:pk>/reviews/create/', ProductReviewCreateView.as_view(), name='create-review'),
    path('category/<str:category>/', ProductByCategoryView.as_view(), name='products-by-category'),
]

# Add the router URLs
urlpatterns += router.urls 
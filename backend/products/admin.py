from django.contrib import admin
from .models import Product, ProductReview


class ProductReviewInline(admin.TabularInline):
    model = ProductReview
    extra = 0
    readonly_fields = ('user', 'rating', 'comment', 'created_at')
    can_delete = False


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'price', 'category', 'stock', 'rating', 'is_active')
    list_filter = ('category', 'is_active', 'manufacturer')
    search_fields = ('name', 'description', 'manufacturer')
    readonly_fields = ('created_at', 'updated_at')
    inlines = [ProductReviewInline]


@admin.register(ProductReview)
class ProductReviewAdmin(admin.ModelAdmin):
    list_display = ('product', 'user', 'rating', 'created_at')
    list_filter = ('rating', 'created_at')
    search_fields = ('product__name', 'user__email', 'comment')
    readonly_fields = ('created_at',) 
from django.contrib import admin
from .models import Cart, CartItem


class CartItemInline(admin.TabularInline):
    model = CartItem
    extra = 0


@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'item_count', 'total', 'created_at')
    search_fields = ('user__email', 'user__name')
    readonly_fields = ('created_at', 'updated_at')
    inlines = [CartItemInline] 
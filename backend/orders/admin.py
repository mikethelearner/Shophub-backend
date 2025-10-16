from django.contrib import admin
from .models import Order, OrderItem


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ('product', 'quantity', 'price', 'total')


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'total_amount', 'status', 'payment_status', 'created_at')
    list_filter = ('status', 'payment_status', 'payment_method', 'created_at')
    search_fields = ('user__email', 'user__name', 'shipping_street', 'shipping_city')
    readonly_fields = ('created_at', 'updated_at')
    inlines = [OrderItemInline]
    fieldsets = (
        ('Order Info', {
            'fields': ('user', 'total_amount', 'status', 'payment_status', 'payment_method')
        }),
        ('Shipping Address', {
            'fields': ('shipping_street', 'shipping_city', 'shipping_state', 'shipping_zip_code')
        }),
        ('Dates', {
            'fields': ('created_at', 'updated_at')
        }),
    ) 
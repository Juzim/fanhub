from django.contrib import admin
from .models import Product, Order, OrderItem


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ("name", "club", "price", "in_stock")
    list_filter = ("club", "in_stock")


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ("product_name", "size", "quantity", "unit_price", "total_price")
    can_delete = False


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ("id", "full_name", "phone", "status", "total_price", "created_at")
    list_filter = ("status",)
    inlines = [OrderItemInline]
    readonly_fields = ("user", "full_name", "phone", "address", "created_at")

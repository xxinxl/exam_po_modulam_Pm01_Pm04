from django.contrib import admin

from .models import Order, OrderStatus, PickupPoint


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "product_name", "quantity", "status", "pickup_point")
    list_filter = ("status", "pickup_point")
    search_fields = ("product_name", "user__username", "user__first_name", "user__last_name")


@admin.register(OrderStatus)
class OrderStatusAdmin(admin.ModelAdmin):
    search_fields = ("name",)


@admin.register(PickupPoint)
class PickupPointAdmin(admin.ModelAdmin):
    search_fields = ("address",)

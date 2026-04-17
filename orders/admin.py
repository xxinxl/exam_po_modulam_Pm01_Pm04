from .models import Order, OrderStatus, PickupPoint
from django.contrib import admin

admin.site.register(Order)
admin.site.register(OrderStatus)
admin.site.register(PickupPoint)
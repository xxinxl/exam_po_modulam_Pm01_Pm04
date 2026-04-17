from django.contrib.auth.models import User
from django.db import models


class OrderStatus(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name


class PickupPoint(models.Model):
    address = models.CharField(max_length=255)

    def __str__(self):
        return self.address


class Order(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    product_name = models.CharField(max_length=255)
    quantity = models.IntegerField(default=1)
    status = models.ForeignKey(OrderStatus, on_delete=models.CASCADE)
    pickup_point = models.ForeignKey(PickupPoint, on_delete=models.CASCADE)

    def __str__(self):
        return f"Заказ {self.id}"
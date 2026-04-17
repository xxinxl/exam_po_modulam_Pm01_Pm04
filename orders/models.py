from django.contrib.auth.models import User
from django.core.validators import MinValueValidator
from django.db import models


class OrderStatus(models.Model):
    name = models.CharField(max_length=100, unique=True, verbose_name="Статус")

    class Meta:
        verbose_name = "Статус заказа"
        verbose_name_plural = "Статусы заказов"
        ordering = ["name"]

    def __str__(self):
        return self.name


class PickupPoint(models.Model):
    address = models.CharField(max_length=255, unique=True, verbose_name="Адрес пункта выдачи")

    class Meta:
        verbose_name = "Пункт выдачи"
        verbose_name_plural = "Пункты выдачи"
        ordering = ["address"]

    def __str__(self):
        return self.address


class Order(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="orders",
        verbose_name="Клиент",
    )
    product_name = models.CharField(max_length=255, verbose_name="Товар")
    quantity = models.PositiveIntegerField(
        default=1,
        validators=[MinValueValidator(1)],
        verbose_name="Количество",
    )
    status = models.ForeignKey(OrderStatus, on_delete=models.PROTECT, verbose_name="Статус")
    pickup_point = models.ForeignKey(PickupPoint, on_delete=models.PROTECT, verbose_name="Пункт выдачи")

    class Meta:
        verbose_name = "Заказ"
        verbose_name_plural = "Заказы"
        ordering = ["-id"]

    def __str__(self):
        return f"Заказ #{self.id}"

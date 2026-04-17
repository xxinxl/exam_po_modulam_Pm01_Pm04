import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


def seed_reference_data(apps, schema_editor):
    Group = apps.get_model("auth", "Group")
    OrderStatus = apps.get_model("orders", "OrderStatus")
    PickupPoint = apps.get_model("orders", "PickupPoint")

    for group_name in ("Клиенты", "Менеджеры"):
        Group.objects.get_or_create(name=group_name)

    for status_name in ("Новый", "В обработке", "Готов к выдаче", "Выдан"):
        OrderStatus.objects.get_or_create(name=status_name)

    for address in ("ул. Ленина, 1", "пр. Мира, 10", "ул. Советская, 25"):
        PickupPoint.objects.get_or_create(address=address)


class Migration(migrations.Migration):
    dependencies = [
        ("orders", "0001_initial"),
    ]

    operations = [
        migrations.AlterField(
            model_name="orderstatus",
            name="name",
            field=models.CharField(max_length=100, unique=True, verbose_name="Статус"),
        ),
        migrations.AlterField(
            model_name="pickuppoint",
            name="address",
            field=models.CharField(max_length=255, unique=True, verbose_name="Адрес пункта выдачи"),
        ),
        migrations.AlterField(
            model_name="order",
            name="pickup_point",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.PROTECT,
                to="orders.pickuppoint",
                verbose_name="Пункт выдачи",
            ),
        ),
        migrations.AlterField(
            model_name="order",
            name="product_name",
            field=models.CharField(max_length=255, verbose_name="Товар"),
        ),
        migrations.AlterField(
            model_name="order",
            name="quantity",
            field=models.PositiveIntegerField(default=1, verbose_name="Количество"),
        ),
        migrations.AlterField(
            model_name="order",
            name="status",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.PROTECT,
                to="orders.orderstatus",
                verbose_name="Статус",
            ),
        ),
        migrations.AlterField(
            model_name="order",
            name="user",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="orders",
                to=settings.AUTH_USER_MODEL,
                verbose_name="Клиент",
            ),
        ),
        migrations.RunPython(seed_reference_data, migrations.RunPython.noop),
    ]

from django.contrib.auth.models import Group, User
from django.test import Client, TestCase
from django.urls import reverse

from accounts.roles import get_user_role
from products.models import Category, Manufacturer, Product, Supplier, Unit

from .models import Order, OrderStatus, PickupPoint


class OrderAccessTests(TestCase):
    def setUp(self):
        self.http = Client()

        self.client_group, _ = Group.objects.get_or_create(name="Клиенты")
        self.manager_group, _ = Group.objects.get_or_create(name="Менеджеры")

        self.client_user = User.objects.create_user(username="client", password="testpass123")
        self.client_user.groups.add(self.client_group)

        self.other_client = User.objects.create_user(username="other_client", password="testpass123")
        self.other_client.groups.add(self.client_group)

        self.manager_user = User.objects.create_user(username="manager", password="testpass123")
        self.manager_user.groups.add(self.manager_group)

        self.admin_user = User.objects.create_superuser(
            username="admin",
            password="testpass123",
            email="admin@example.com",
        )

        self.status, _ = OrderStatus.objects.get_or_create(name="Новый")
        self.pickup_point, _ = PickupPoint.objects.get_or_create(address="ул. Ленина, 1")

        category = Category.objects.create(name="Двигатели")
        manufacturer = Manufacturer.objects.create(name="Bosch")
        supplier = Supplier.objects.create(name="ЭлектроПоставка")
        unit = Unit.objects.create(name="штука", abbreviation="шт")

        self.product = Product.objects.create(
            name="Стартер",
            category=category,
            description="Тестовый товар",
            manufacturer=manufacturer,
            supplier=supplier,
            price="1500.00",
            unit=unit,
            quantity=10,
            discount="0.00",
        )

        self.client_order = Order.objects.create(
            user=self.client_user,
            product_name=self.product.name,
            quantity=2,
            status=self.status,
            pickup_point=self.pickup_point,
        )
        self.other_order = Order.objects.create(
            user=self.other_client,
            product_name="Генератор",
            quantity=1,
            status=self.status,
            pickup_point=self.pickup_point,
        )

    def test_get_user_role_returns_expected_values(self):
        anonymous_user = type("AnonymousUser", (), {"is_authenticated": False})()

        self.assertEqual(get_user_role(anonymous_user), "guest")
        self.assertEqual(get_user_role(self.client_user), "client")
        self.assertEqual(get_user_role(self.manager_user), "manager")
        self.assertEqual(get_user_role(self.admin_user), "admin")

    def test_client_sees_only_own_orders(self):
        self.http.login(username="client", password="testpass123")

        response = self.http.get(reverse("orders:order_list"))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(list(response.context["orders"]), [self.client_order])

    def test_manager_sees_all_orders(self):
        self.http.login(username="manager", password="testpass123")

        response = self.http.get(reverse("orders:order_list"))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(list(response.context["orders"]), [self.other_order, self.client_order])

    def test_client_can_create_order_without_selecting_user_or_status(self):
        self.http.login(username="client", password="testpass123")

        response = self.http.post(
            reverse("orders:order_create"),
            data={
                "product": self.product.pk,
                "quantity": 3,
                "pickup_point": self.pickup_point.pk,
            },
        )

        self.assertRedirects(response, reverse("orders:order_list"))
        created_order = Order.objects.latest("id")
        self.assertEqual(created_order.user, self.client_user)
        self.assertEqual(created_order.status, self.status)
        self.assertEqual(created_order.product_name, self.product.name)

    def test_client_cannot_open_product_create_page(self):
        self.http.login(username="client", password="testpass123")

        response = self.http.get(reverse("products:product_create"))

        self.assertRedirects(response, reverse("products:product_list"))

    def test_client_cannot_edit_foreign_order(self):
        self.http.login(username="client", password="testpass123")

        response = self.http.get(reverse("orders:order_update", args=[self.other_order.pk]))

        self.assertEqual(response.status_code, 404)

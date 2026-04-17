from django import forms
from django.contrib.auth.models import User

from accounts.roles import get_user_role
from products.models import Product

from .models import Order, OrderStatus


class OrderForm(forms.ModelForm):
    product = forms.ModelChoiceField(
        queryset=Product.objects.none(),
        label="Товар",
        widget=forms.Select(attrs={"class": "form-select"}),
    )

    class Meta:
        model = Order
        fields = ["user", "product", "quantity", "status", "pickup_point"]
        widgets = {
            "user": forms.Select(attrs={"class": "form-select"}),
            "quantity": forms.NumberInput(attrs={"class": "form-control", "min": 1}),
            "status": forms.Select(attrs={"class": "form-select"}),
            "pickup_point": forms.Select(attrs={"class": "form-select"}),
        }

    def __init__(self, *args, user=None, **kwargs):
        self.current_user = user
        super().__init__(*args, **kwargs)

        self.fields["product"].queryset = Product.objects.order_by("name")
        self.fields["user"].queryset = User.objects.filter(is_active=True, is_superuser=False).order_by("username")

        if self.instance.pk and self.instance.product_name:
            selected_product = Product.objects.filter(name=self.instance.product_name).first()
            if selected_product:
                self.fields["product"].initial = selected_product.pk

        if get_user_role(user) == "client":
            self.fields.pop("user")
            self.fields.pop("status")

    def clean(self):
        cleaned_data = super().clean()
        product = cleaned_data.get("product")
        quantity = cleaned_data.get("quantity")
        role = get_user_role(self.current_user)

        if role == "client" and not self.instance.pk and not OrderStatus.objects.exists():
            raise forms.ValidationError("В системе не настроены статусы заказов. Обратитесь к администратору.")

        if product and product.quantity <= 0:
            self.add_error("product", "Выбранный товар отсутствует на складе.")

        if product and quantity and quantity > product.quantity:
            self.add_error("quantity", "Нельзя заказать больше, чем есть на складе.")

        return cleaned_data

    def save(self, commit=True):
        order = super().save(commit=False)
        product = self.cleaned_data["product"]

        order.product_name = product.name

        if get_user_role(self.current_user) == "client":
            order.user = self.current_user
            if not order.status_id:
                order.status = OrderStatus.objects.order_by("id").first()

        if commit:
            order.save()

        return order

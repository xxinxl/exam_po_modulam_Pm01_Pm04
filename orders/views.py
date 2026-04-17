from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect, render

from accounts.roles import get_user_role, role_required

from .forms import OrderForm
from .models import Order


def get_order_queryset(user):
    orders = Order.objects.select_related("user", "status", "pickup_point")
    role = get_user_role(user)

    if role in {"manager", "admin"}:
        return orders

    if role == "client":
        return orders.filter(user=user)

    return orders.none()


@role_required("client", "manager", "admin")
def order_list(request):
    return render(
        request,
        "orders/order_list.html",
        {
            "orders": get_order_queryset(request.user),
            "user_role": get_user_role(request.user),
        },
    )


@role_required("client", "manager", "admin")
def order_create(request):
    if request.method == "POST":
        form = OrderForm(request.POST, user=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, "Заказ успешно создан.")
            return redirect("orders:order_list")
    else:
        form = OrderForm(user=request.user)

    return render(
        request,
        "orders/order_form.html",
        {
            "form": form,
            "title": "Создать заказ",
            "submit_label": "Сохранить",
            "user_role": get_user_role(request.user),
        },
    )


@role_required("client", "manager", "admin")
def order_update(request, pk):
    order = get_object_or_404(get_order_queryset(request.user), pk=pk)

    if request.method == "POST":
        form = OrderForm(request.POST, instance=order, user=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, "Заказ успешно обновлен.")
            return redirect("orders:order_list")
    else:
        form = OrderForm(instance=order, user=request.user)

    return render(
        request,
        "orders/order_form.html",
        {
            "form": form,
            "title": f"Редактировать заказ #{order.id}",
            "submit_label": "Обновить",
            "order": order,
            "user_role": get_user_role(request.user),
        },
    )


@role_required("client", "manager", "admin")
def order_delete(request, pk):
    order = get_object_or_404(get_order_queryset(request.user), pk=pk)

    if request.method == "POST":
        order.delete()
        messages.success(request, "Заказ успешно удален.")
        return redirect("orders:order_list")

    return render(
        request,
        "orders/order_confirm_delete.html",
        {
            "order": order,
            "user_role": get_user_role(request.user),
        },
    )

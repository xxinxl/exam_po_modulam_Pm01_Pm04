from functools import wraps

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect


def get_user_role(user):
    if not user or not user.is_authenticated:
        return "guest"

    if user.is_superuser:
        return "admin"

    if user.groups.filter(name="Менеджеры").exists():
        return "manager"

    if user.groups.filter(name="Клиенты").exists():
        return "client"

    return "guest"


def role_required(*allowed_roles, redirect_to="products:product_list"):
    def decorator(view_func):
        @login_required
        @wraps(view_func)
        def wrapped_view(request, *args, **kwargs):
            if get_user_role(request.user) not in allowed_roles:
                messages.error(request, "У вас нет прав для выполнения этого действия.")
                return redirect(redirect_to)

            return view_func(request, *args, **kwargs)

        return wrapped_view

    return decorator

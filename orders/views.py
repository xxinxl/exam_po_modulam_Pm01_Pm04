from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden
from .models import Order
from .forms import OrderForm


def get_user_role(user):
    if user.is_superuser:
        return 'admin'
    if user.groups.filter(name='Менеджеры').exists():
        return 'manager'
    if user.groups.filter(name='Клиенты').exists():
        return 'client'
    return 'guest'


@login_required
def order_list(request):
    role = get_user_role(request.user)

    if role == 'manager' or role == 'admin':
        orders = Order.objects.all()
    elif role == 'client':
        orders = Order.objects.filter(user=request.user)
    else:
        return HttpResponseForbidden()

    return render(request, 'orders/order_list.html', {'orders': orders})


@login_required
def order_create(request):
    if request.method == 'POST':
        form = OrderForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('order_list')
    else:
        form = OrderForm()

    return render(request, 'orders/order_form.html', {'form': form})
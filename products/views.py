from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render

from accounts.roles import get_user_role, role_required

from .forms import ProductForm
from .models import Product, Supplier


def product_list(request):
    user_role = get_user_role(request.user)
    products = Product.objects.select_related("category", "manufacturer", "supplier", "unit")

    if user_role == "admin":
        search_query = request.GET.get("search", "").strip()
        supplier_filter = request.GET.get("supplier", "").strip()
        sort_by = request.GET.get("sort", "name")

        if search_query:
            products = products.filter(
                Q(name__icontains=search_query)
                | Q(description__icontains=search_query)
                | Q(category__name__icontains=search_query)
                | Q(manufacturer__name__icontains=search_query)
                | Q(supplier__name__icontains=search_query)
                | Q(unit__name__icontains=search_query)
            )

        if supplier_filter:
            products = products.filter(supplier__id=supplier_filter)

        if sort_by == "quantity_asc":
            products = products.order_by("quantity", "name")
        elif sort_by == "quantity_desc":
            products = products.order_by("-quantity", "name")
        else:
            products = products.order_by("name")

        suppliers = Supplier.objects.all()
    else:
        search_query = ""
        supplier_filter = ""
        sort_by = "name"
        suppliers = None
        products = products.order_by("name")

    paginator = Paginator(products, 10)
    page_obj = paginator.get_page(request.GET.get("page"))

    return render(
        request,
        "products/product_list.html",
        {
            "page_obj": page_obj,
            "user_role": user_role,
            "suppliers": suppliers,
            "search_query": search_query,
            "supplier_filter": supplier_filter,
            "sort_by": sort_by,
        },
    )


@role_required("admin")
def product_create(request):
    if request.method == "POST":
        form = ProductForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, "Электрозапчасть успешно создана.")
            return redirect("products:product_list")
    else:
        form = ProductForm()

    return render(
        request,
        "products/product_form.html",
        {
            "form": form,
            "title": "Добавить электрозапчасть",
            "user_role": get_user_role(request.user),
        },
    )


@role_required("admin")
def product_update(request, pk):
    product = get_object_or_404(Product, pk=pk)

    if request.method == "POST":
        form = ProductForm(request.POST, request.FILES, instance=product)
        if form.is_valid():
            if "image" in request.FILES and product.image:
                product.image.delete()
            form.save()
            messages.success(request, "Электрозапчасть успешно обновлена.")
            return redirect("products:product_list")
    else:
        form = ProductForm(instance=product)

    return render(
        request,
        "products/product_form.html",
        {
            "form": form,
            "product": product,
            "title": "Редактировать электрозапчасть",
            "user_role": get_user_role(request.user),
        },
    )


@role_required("admin")
def product_delete(request, pk):
    product = get_object_or_404(Product, pk=pk)

    if request.method == "POST":
        if product.image:
            product.image.delete()
        product.delete()
        messages.success(request, "Электрозапчасть успешно удалена.")
        return redirect("products:product_list")

    return render(
        request,
        "products/product_confirm_delete.html",
        {
            "product": product,
            "user_role": get_user_role(request.user),
        },
    )

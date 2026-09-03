from decimal import Decimal

from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages

from .models import Product, Order, OrderItem, SIZE_CHOICES
from .cart import Cart


def product_list(request):
    products = Product.objects.select_related("club").filter(in_stock=True)
    return render(request, "merch/list.html", {"products": products})


def product_detail(request, pk):
    product = get_object_or_404(Product.objects.select_related("club"), pk=pk)
    return render(request, "merch/detail.html", {"product": product, "sizes": SIZE_CHOICES})


@login_required
def cart_add(request, pk):
    if request.method != "POST":
        return redirect("merch:detail", pk=pk)
    product = get_object_or_404(Product, pk=pk)
    size = request.POST.get("size") or SIZE_CHOICES[2]  # по умолчанию "L"
    quantity = max(1, int(request.POST.get("quantity", 1) or 1))
    Cart(request).add(product, size, quantity)
    messages.success(request, f"«{product.name}» ({size}) добавлен в корзину.")
    return redirect("merch:cart")


@login_required
def cart_remove(request, key):
    if request.method == "POST":
        Cart(request).remove(key)
    return redirect("merch:cart")


@login_required
def cart_view(request):
    cart = Cart(request)
    return render(request, "merch/cart.html", {"cart": cart, "total": cart.get_total_price()})


@login_required
def checkout(request):
    cart = Cart(request)
    if len(cart) == 0:
        return redirect("merch:cart")

    if request.method == "POST":
        order = Order.objects.create(
            user=request.user,
            full_name=request.POST.get("full_name", "").strip() or request.user.username,
            phone=request.POST.get("phone", "").strip(),
            address=request.POST.get("address", "").strip(),
        )
        for item in cart:
            OrderItem.objects.create(
                order=order,
                product=item["product"],
                product_name=item["product"].name,
                size=item["size"],
                quantity=item["quantity"],
                unit_price=item["unit_price"],
            )
        cart.clear()
        from apps.core.models import Notification
        Notification.objects.create(
            user=request.user, notif_type="order",
            title=f"Заказ №{order.pk} принят",
            body=f"На сумму {order.total_price} ₸. Менеджер свяжется для подтверждения.",
            link=f"/merch/order/{order.pk}/success/",
        )
        return redirect("merch:order_success", pk=order.pk)

    return render(request, "merch/checkout.html", {"cart": cart, "total": cart.get_total_price()})


@login_required
def order_success(request, pk):
    order = get_object_or_404(Order, pk=pk, user=request.user)
    return render(request, "merch/order_success.html", {"order": order})

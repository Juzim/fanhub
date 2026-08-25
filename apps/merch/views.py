from django.shortcuts import render
from .models import Product


def product_list(request):
    products = Product.objects.select_related("club").filter(in_stock=True)
    return render(request, "merch/list.html", {"products": products})

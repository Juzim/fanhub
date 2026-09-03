"""
Корзина на сессиях Django — без отдельной модели в БД. Стандартный подход
для витрины без реальной оплаты: содержимое живёт в session пользователя,
а реальная запись в БД (Order/OrderItem) создаётся только на шаге
оформления заказа (см. views.checkout).
"""
from decimal import Decimal

from .models import Product

CART_SESSION_KEY = "cart"


class Cart:
    def __init__(self, request):
        self.session = request.session
        cart = self.session.get(CART_SESSION_KEY)
        if cart is None:
            cart = self.session[CART_SESSION_KEY] = {}
        self.cart = cart

    def add(self, product, size, quantity=1):
        key = f"{product.id}:{size}"
        if key in self.cart:
            self.cart[key]["quantity"] += quantity
        else:
            self.cart[key] = {
                "product_id": product.id,
                "size": size,
                "quantity": quantity,
                "price": str(product.price),
            }
        self._save()

    def remove(self, key):
        if key in self.cart:
            del self.cart[key]
            self._save()

    def update_quantity(self, key, quantity):
        if key in self.cart and quantity > 0:
            self.cart[key]["quantity"] = quantity
            self._save()
        elif key in self.cart:
            self.remove(key)

    def clear(self):
        self.session[CART_SESSION_KEY] = {}
        self._save()

    def _save(self):
        self.session.modified = True

    def __iter__(self):
        product_ids = [item["product_id"] for item in self.cart.values()]
        products = {p.id: p for p in Product.objects.filter(id__in=product_ids)}
        for key, raw in self.cart.items():
            item = dict(raw)
            item["key"] = key
            item["product"] = products.get(raw["product_id"])
            item["unit_price"] = Decimal(raw["price"])
            item["total_price"] = Decimal(raw["price"]) * raw["quantity"]
            if item["product"] is not None:
                yield item

    def __len__(self):
        return sum(item["quantity"] for item in self.cart.values())

    def get_total_price(self):
        return sum((Decimal(item["price"]) * item["quantity"] for item in self.cart.values()), Decimal("0"))

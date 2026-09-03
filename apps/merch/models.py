from django.db import models
from apps.clubs.models import Club

# Размеры, доступные для любого товара одежды. Не выносим в БД —
# для витрины этого достаточно, у всех джерси одинаковая сетка размеров.
SIZE_CHOICES = ["S", "M", "L", "XL", "XXL"]


class Product(models.Model):
    club = models.ForeignKey(Club, on_delete=models.CASCADE, related_name="products")
    name = models.CharField("Название", max_length=150)
    description = models.TextField("Описание", blank=True)
    price = models.DecimalField("Цена (₸)", max_digits=10, decimal_places=2)
    image = models.ImageField(
        "Фото (загружено через админку)", upload_to="merch/", blank=True, null=True,
        help_text="Приоритетнее image_static, если заполнено",
    )
    image_static = models.CharField(
        "Путь к фото в static/", max_length=200, blank=True,
        help_text="Например: img/merch/aktobe.jpg — так подключены реальные фото джерси",
    )
    in_stock = models.BooleanField("В наличии", default=True)

    class Meta:
        verbose_name = "Товар"
        verbose_name_plural = "Мерч"

    def __str__(self):
        return f"{self.name} — {self.club.name}"


class Order(models.Model):
    """Заказ без онлайн-оплаты: витрина полностью рабочая (корзина, размеры,
    оформление), но вместо оплаты — заявка с контактами, как в модели
    'звонок менеджера подтвердит заказ'. Реальный платёжный шлюз сюда
    не подключён по просьбе заказчика — эта модель просто фиксирует заявку."""

    STATUS_CHOICES = [
        ("new", "Новый"),
        ("confirmed", "Подтверждён"),
        ("cancelled", "Отменён"),
    ]

    user = models.ForeignKey(
        "accounts.User", on_delete=models.SET_NULL, null=True, blank=True, related_name="orders"
    )
    full_name = models.CharField("Имя", max_length=150)
    phone = models.CharField("Телефон", max_length=30)
    address = models.CharField("Адрес доставки", max_length=250, blank=True)
    status = models.CharField("Статус", max_length=12, choices=STATUS_CHOICES, default="new")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Заказ"
        verbose_name_plural = "Заказы"
        ordering = ["-created_at"]

    @property
    def total_price(self):
        return sum((item.total_price for item in self.items.all()), 0)

    def __str__(self):
        return f"Заказ №{self.pk} — {self.full_name}"


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="items")
    product = models.ForeignKey(Product, on_delete=models.SET_NULL, null=True, blank=True)
    # Снапшот названия/цены на момент заказа — переживает удаление/изменение товара
    product_name = models.CharField("Товар", max_length=150)
    size = models.CharField("Размер", max_length=6)
    quantity = models.PositiveIntegerField("Количество", default=1)
    unit_price = models.DecimalField("Цена за штуку (₸)", max_digits=10, decimal_places=2)

    class Meta:
        verbose_name = "Позиция заказа"
        verbose_name_plural = "Позиции заказа"

    @property
    def total_price(self):
        return self.unit_price * self.quantity

    def __str__(self):
        return f"{self.product_name} ({self.size}) × {self.quantity}"

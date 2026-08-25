from django.db import models
from apps.clubs.models import Club


class Product(models.Model):
    club = models.ForeignKey(Club, on_delete=models.CASCADE, related_name="products")
    name = models.CharField("Название", max_length=150)
    price = models.DecimalField("Цена (₸)", max_digits=10, decimal_places=2)
    image = models.ImageField("Фото", upload_to="merch/", blank=True, null=True)
    in_stock = models.BooleanField("В наличии", default=True)

    class Meta:
        verbose_name = "Товар"
        verbose_name_plural = "Мерч"

    def __str__(self):
        return f"{self.name} — {self.club.name}"

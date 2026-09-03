from django.db import models


class Notification(models.Model):
    TYPE_CHOICES = [
        ("match_result", "Результат матча"),
        ("level_up", "Новый уровень"),
        ("new_content", "Новый материал"),
        ("order", "Заказ"),
    ]

    user = models.ForeignKey(
        "accounts.User", on_delete=models.CASCADE, related_name="notifications"
    )
    notif_type = models.CharField("Тип", max_length=20, choices=TYPE_CHOICES)
    title = models.CharField("Заголовок", max_length=150)
    body = models.CharField("Текст", max_length=250, blank=True)
    link = models.CharField("Ссылка", max_length=250, blank=True)
    is_read = models.BooleanField("Прочитано", default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "Уведомление"
        verbose_name_plural = "Уведомления"

    def __str__(self):
        return f"{self.user} — {self.title}"

from django.db import models
from apps.clubs.models import Club


class Article(models.Model):
    club = models.ForeignKey(Club, on_delete=models.CASCADE, related_name="articles", null=True, blank=True)
    title = models.CharField("Заголовок", max_length=250)
    summary = models.TextField("Краткое описание", max_length=400)
    body = models.TextField("Текст новости", blank=True)
    image = models.ImageField("Изображение", upload_to="news/", blank=True, null=True)
    published_at = models.DateTimeField("Дата публикации", auto_now_add=True)
    source_url = models.URLField("Ссылка на источник", blank=True)

    class Meta:
        verbose_name = "Новость"
        verbose_name_plural = "Новости"
        ordering = ["-published_at"]

    def __str__(self):
        return self.title

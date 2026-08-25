from django.db import models
from apps.clubs.models import Club


class Video(models.Model):
    CATEGORY_CHOICES = [
        ("review", "Обзоры матчей"),
        ("highlights", "Highlights"),
        ("interview", "Интервью"),
        ("team", "Команды"),
        ("player", "Игроки"),
        ("league", "Премьер-лига"),
    ]

    club = models.ForeignKey(Club, on_delete=models.CASCADE, related_name="videos", null=True, blank=True)
    title = models.CharField("Название", max_length=250)
    category = models.CharField("Категория", max_length=20, choices=CATEGORY_CHOICES, default="review")
    youtube_id = models.CharField(
        "YouTube ID", max_length=20, blank=True,
        help_text="Идентификатор видео из ссылки youtube.com/watch?v=<ID> — если известен точно",
    )
    external_url = models.URLField(
        "Внешняя ссылка", blank=True,
        help_text=(
            "Ссылка на реальный источник (официальный YouTube-канал, статья с видеообзором), "
            "используется, когда точный youtube_id для встраивания не подтверждён"
        ),
    )
    duration_seconds = models.PositiveIntegerField("Длительность (сек)", default=0)
    published_at = models.DateTimeField("Опубликовано", auto_now_add=True)

    class Meta:
        verbose_name = "Видео"
        verbose_name_plural = "Видео"
        ordering = ["-published_at"]

    def __str__(self):
        return self.title

    @property
    def embed_url(self):
        return f"https://www.youtube.com/embed/{self.youtube_id}" if self.youtube_id else None

    @property
    def thumbnail_url(self):
        """Официальное превью-изображение YouTube для этого видео — тот же
        URL, что использует сам YouTube в предпросмотре ссылок/embed'ах,
        не копия чужого фото. None, если youtube_id не указан (тогда
        в шаблоне используется fallback-иконка)."""
        return f"https://img.youtube.com/vi/{self.youtube_id}/hqdefault.jpg" if self.youtube_id else None

    @property
    def watch_url(self):
        """Куда вести пользователя: точное embed-видео, иначе — внешний источник."""
        if self.youtube_id:
            return f"https://www.youtube.com/watch?v={self.youtube_id}"
        return self.external_url

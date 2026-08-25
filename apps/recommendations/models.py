from django.db import models

# Вес взаимодействия — насколько сильно оно говорит об интересе к клубу.
# Используется как "неявный рейтинг" (implicit rating) для Collaborative Filtering.
INTERACTION_WEIGHTS = {
    "club_view": 1.0,
    "news_read": 2.0,
    "video_watch": 3.0,
    "like": 4.0,
    "match_interest": 3.0,
    "favorite_club_set": 6.0,
}


class Interaction(models.Model):
    TYPE_CHOICES = [
        ("club_view", "Просмотр клуба"),
        ("news_read", "Прочитана новость"),
        ("video_watch", "Просмотрено видео"),
        ("like", "Лайк"),
        ("match_interest", "Интерес к матчу"),
        ("favorite_club_set", "Выбор любимого клуба"),
    ]

    user = models.ForeignKey("accounts.User", on_delete=models.CASCADE, related_name="interactions")
    interaction_type = models.CharField("Тип", max_length=20, choices=TYPE_CHOICES)
    club = models.ForeignKey("clubs.Club", on_delete=models.CASCADE, related_name="interactions")
    article = models.ForeignKey("news.Article", on_delete=models.SET_NULL, null=True, blank=True)
    video = models.ForeignKey("videos.Video", on_delete=models.SET_NULL, null=True, blank=True)
    match = models.ForeignKey("matches.Match", on_delete=models.SET_NULL, null=True, blank=True)
    weight = models.FloatField(
        "Вес", default=0.0,
        help_text="Автоматически подставляется по типу взаимодействия при сохранении, если не задан явно",
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Взаимодействие"
        verbose_name_plural = "История взаимодействий"
        indexes = [models.Index(fields=["user", "club"])]

    def save(self, *args, **kwargs):
        if not self.weight:
            self.weight = INTERACTION_WEIGHTS.get(self.interaction_type, 1.0)
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.user} · {self.get_interaction_type_display()} · {self.club}"

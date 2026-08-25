from django.db import models
from apps.clubs.models import Club


class Match(models.Model):
    STATUS_CHOICES = [
        ("scheduled", "Предстоящий"),
        ("live", "Идёт сейчас"),
        ("finished", "Завершён"),
    ]

    home_club = models.ForeignKey(Club, on_delete=models.CASCADE, related_name="home_matches")
    away_club = models.ForeignKey(Club, on_delete=models.CASCADE, related_name="away_matches")
    kickoff_at = models.DateTimeField("Дата и время")
    tournament = models.CharField("Турнир", max_length=120, default="Казахстанская Премьер-лига")
    status = models.CharField("Статус", max_length=12, choices=STATUS_CHOICES, default="scheduled")
    home_score = models.PositiveIntegerField("Голы (хозяева)", null=True, blank=True)
    away_score = models.PositiveIntegerField("Голы (гости)", null=True, blank=True)

    class Meta:
        verbose_name = "Матч"
        verbose_name_plural = "Матчи"
        ordering = ["kickoff_at"]

    def __str__(self):
        return f"{self.home_club} — {self.away_club} ({self.kickoff_at:%d.%m.%Y})"

    @property
    def score_display(self):
        if self.home_score is None or self.away_score is None:
            return None
        return f"{self.home_score}:{self.away_score}"

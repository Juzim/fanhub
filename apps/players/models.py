from django.db import models
from apps.clubs.models import Club


class Player(models.Model):
    POSITION_CHOICES = [
        ("GK", "Вратарь"),
        ("DF", "Защитник"),
        ("MF", "Полузащитник"),
        ("FW", "Нападающий"),
    ]

    club = models.ForeignKey(Club, on_delete=models.CASCADE, related_name="players")
    full_name = models.CharField("Имя игрока", max_length=150)
    position = models.CharField("Позиция", max_length=2, choices=POSITION_CHOICES)
    photo = models.ImageField("Фото", upload_to="players/", blank=True, null=True)
    matches_played = models.PositiveIntegerField("Матчи", default=0)
    goals = models.PositiveIntegerField("Голы", default=0)
    assists = models.PositiveIntegerField("Ассисты", default=0)
    rating = models.DecimalField("Рейтинг", max_digits=3, decimal_places=1, default=0)

    class Meta:
        verbose_name = "Игрок"
        verbose_name_plural = "Игроки"
        ordering = ["-rating"]

    def __str__(self):
        return f"{self.full_name} ({self.club.short_name or self.club.name})"


class FavoritePlayer(models.Model):
    """M2M через явную модель, чтобы удобно логировать взаимодействие для рекомендаций."""

    user = models.ForeignKey("accounts.User", on_delete=models.CASCADE, related_name="favorite_players")
    player = models.ForeignKey(Player, on_delete=models.CASCADE, related_name="fans")
    added_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("user", "player")
        verbose_name = "Любимый игрок"
        verbose_name_plural = "Любимые игроки"

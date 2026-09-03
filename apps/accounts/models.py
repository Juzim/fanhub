from django.contrib.auth.models import AbstractUser
from django.db import models

# XP, необходимый для перехода на следующий уровень.
# Формула прогрессивная: чем выше уровень, тем больше XP нужно.
# level_threshold(n) = BASE_XP_STEP * n  -> совпадает с примером в ТЗ
# (уровень 15 → следующий порог 5000 XP смотрится правдоподобно при BASE_XP_STEP ~ 333,
# но для читаемости в интерфейсе используем круглый шаг).
BASE_XP_STEP = 250

# Множитель, переводящий "вес взаимодействия" (см. recommendations.models.INTERACTION_WEIGHTS,
# там значения 1.0–6.0) в реальные очки опыта. Без множителя прогресс был бы
# незаметным — 1 XP за клик выглядит бессмысленно на шкале уровней.
XP_PER_WEIGHT_POINT = 10


class User(AbstractUser):
    favorite_club = models.ForeignKey(
        "clubs.Club", on_delete=models.SET_NULL, null=True, blank=True,
        related_name="fans", verbose_name="Любимый клуб",
    )
    avatar = models.ImageField("Аватар", upload_to="avatars/", blank=True, null=True)
    xp = models.PositiveIntegerField("Опыт (XP)", default=0)
    fan_title = models.CharField(
        "Титул болельщика", max_length=80, blank=True,
        help_text="Необязательно — если не задано, генерируется автоматически по клубу",
    )

    class Meta:
        verbose_name = "Пользователь"
        verbose_name_plural = "Пользователи"

    @property
    def display_title(self):
        """Титул для интерфейса: ручной fan_title в приоритете,
        иначе — автоматически по названию любимого клуба."""
        if self.fan_title:
            return self.fan_title
        if self.favorite_club:
            return f"Болельщик «{self.favorite_club.name}»"
        return "Болельщик FAN-HUB"

    @property
    def level(self):
        # уровень растёт медленнее с каждым шагом (накопительный порог)
        total = 0
        lvl = 1
        step = BASE_XP_STEP
        while total + step <= self.xp:
            total += step
            step += BASE_XP_STEP // 4
            lvl += 1
        return lvl

    @property
    def level_progress(self):
        """Возвращает (текущий_xp_в_уровне, xp_для_след_уровня)."""
        total = 0
        step = BASE_XP_STEP
        while total + step <= self.xp:
            total += step
            step += BASE_XP_STEP // 4
        return self.xp - total, step

    def add_xp(self, amount):
        if amount <= 0:
            return
        old_level = self.level
        self.xp = models.F("xp") + amount
        self.save(update_fields=["xp"])
        self.refresh_from_db(fields=["xp"])
        if self.level > old_level:
            from apps.core.models import Notification
            Notification.objects.create(
                user=self, notif_type="level_up",
                title=f"Новый уровень! LVL {self.level}",
                body=f"Вы достигли {self.level} уровня болельщика — {self.display_title}.",
                link="/accounts/profile/",
            )

    def change_favorite_club(self, club):
        """Смена любимого клуба — ключевой сценарий демо (Шаг 8-9 ТЗ)."""
        self.favorite_club = club
        self.save(update_fields=["favorite_club"])
        # смена клуба — тоже взаимодействие: логируем его (даёт XP и
        # учитывается в рекомендательной системе) и сбрасываем кэш
        # рекомендаций, чтобы дашборд сразу перестроился под новый клуб.
        from apps.recommendations.services import log_interaction
        log_interaction(self, "favorite_club_set", club=club)

    def __str__(self):
        return self.username

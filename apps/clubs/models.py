from django.db import models


class Club(models.Model):
    """Клуб Казахстанской Премьер-лиги."""

    name = models.CharField("Название", max_length=120, unique=True)
    short_name = models.CharField("Короткое название", max_length=20, blank=True)
    city = models.CharField("Город", max_length=80)
    founded_year = models.PositiveIntegerField("Год основания", null=True, blank=True)
    slogan = models.CharField("Слоган", max_length=200, blank=True)
    crest = models.ImageField(
        "Эмблема (загружена через админку)", upload_to="clubs/crests/", blank=True, null=True,
        help_text="Приоритетнее crest_static, если заполнено",
    )
    crest_static = models.CharField(
        "Путь к эмблеме в static/", max_length=200, blank=True,
        help_text="Например: img/clubs/aktobe.png — так подключены официальные логотипы КПЛ",
    )
    primary_color = models.CharField(
        "Основной цвет (hex)", max_length=7, default="#3B7CFF",
        help_text="Используется для акцентов клуба в интерфейсе, если логотип не загружен",
    )
    official_site = models.URLField("Официальный сайт", blank=True)

    class Meta:
        verbose_name = "Клуб"
        verbose_name_plural = "Клубы"
        ordering = ["name"]

    def __str__(self):
        return self.name


class Standing(models.Model):
    """Строка турнирной таблицы клуба в конкретном сезоне."""

    club = models.OneToOneField(Club, on_delete=models.CASCADE, related_name="standing")
    season = models.CharField("Сезон", max_length=20, default="2026")
    played = models.PositiveIntegerField("Игры", default=0)
    wins = models.PositiveIntegerField("Победы", default=0)
    draws = models.PositiveIntegerField("Ничьи", default=0)
    losses = models.PositiveIntegerField("Поражения", default=0)
    goals_for = models.PositiveIntegerField("Забито", default=0)
    goals_against = models.PositiveIntegerField("Пропущено", default=0)

    class Meta:
        verbose_name = "Строка турнирной таблицы"
        verbose_name_plural = "Турнирная таблица"
        # points — вычисляемое свойство, а не поле БД, поэтому сортировка
        # по очкам делается в Python (см. views.club_list)

    @property
    def points(self):
        return self.wins * 3 + self.draws

    @property
    def goal_difference(self):
        return self.goals_for - self.goals_against

    def __str__(self):
        return f"{self.club.name} — {self.points} очков"

from django.apps import AppConfig


class CoreConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.core"
    verbose_name = "Ядро (дашборд, аналитика)"

    def ready(self):
        import apps.core.signals  # noqa: F401 — регистрирует обработчики уведомлений

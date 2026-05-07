from django.apps import AppConfig


class IaConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "ia"
    verbose_name = "IA"

    def ready(self):
        import ia.signals  # noqa: F401

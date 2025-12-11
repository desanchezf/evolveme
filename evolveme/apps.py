# ruff: noqa

from django.apps import AppConfig


class EvolvemeConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "evolveme"

    def ready(self):
        import evolveme.signals

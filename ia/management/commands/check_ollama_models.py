"""
Comprobar estado de los modelos Ollama (descargado, digest) y marcar si hay actualización disponible.
Ejecutar diariamente (Celery Beat: check_ollama_models_task a las 03:00 UTC) o con cron.
"""
from django.core.management.base import BaseCommand
from django.utils import timezone

from ia.models import OllamaModelConfig
from ia.services import check_model_on_server


class Command(BaseCommand):
    help = "Comprueba el estado (descargado/digest) de cada modelo Ollama y actualiza update_available."

    def handle(self, *args, **options):
        now = timezone.now()
        updated = 0
        for config in OllamaModelConfig.objects.select_related("server").all():
            if not config.server.enabled:
                continue
            downloaded, digest = check_model_on_server(
                config.server, config.model_name
            )
            changed = (
                config.downloaded != downloaded
                or config.digest != digest
                or config.last_checked_at is None
            )
            config.downloaded = downloaded
            config.digest = digest
            config.last_checked_at = now
            config.update_available = not downloaded or (digest and config.digest != digest)
            config.save(update_fields=[
                "downloaded", "digest", "last_checked_at", "update_available", "updated_at"
            ])
            if changed:
                updated += 1
            self.stdout.write(
                f"  {config.model_name}: downloaded={downloaded} digest={digest[:12] if digest else '-'}..."
            )
        self.stdout.write(self.style.SUCCESS(f"Comprobados. {updated} actualizados."))

"""
Tareas Celery para la app IA.
"""
from django.core.management import call_command
from celery import shared_task


@shared_task
def check_ollama_models_task():
    """Ejecuta check_ollama_models (estado y actualizaciones de modelos Ollama)."""
    call_command("check_ollama_models")


@shared_task(bind=True, max_retries=2)
def pull_ollama_model_task(self, config_pk: int) -> dict:
    """
    Descarga o actualiza un modelo Ollama en segundo plano.
    Lanzar desde el admin o directamente:
        pull_ollama_model_task.delay(config_pk)
    """
    from django.utils import timezone
    from ia.models import OllamaModelConfig
    from ia.services import check_model_on_server, pull_model_on_server

    try:
        config = (
            OllamaModelConfig.objects
            .select_related("server")
            .get(pk=config_pk)
        )
    except OllamaModelConfig.DoesNotExist:
        return {"ok": False, "error": f"OllamaModelConfig pk={config_pk} no encontrado."}

    if not config.server.enabled:
        return {"ok": False, "error": "El servidor Ollama está deshabilitado."}

    ok, err = pull_model_on_server(config.server, config.model_name)
    if ok:
        downloaded, digest = check_model_on_server(
            config.server, config.model_name
        )
        config.downloaded = downloaded
        config.digest = digest
        config.last_checked_at = timezone.now()
        config.update_available = False
        config.save(update_fields=[
            "downloaded", "digest", "last_checked_at",
            "update_available", "updated_at",
        ])
        return {"ok": True, "model": config.model_name}
    else:
        try:
            raise self.retry(countdown=60, exc=Exception(err))
        except Exception:
            return {"ok": False, "error": err}

"""
Configuración de Celery para el proyecto.
La comprobación de modelos Ollama está programada para ejecutarse una vez al día.
"""
from celery import Celery
from celery.schedules import crontab

app = Celery("project")
app.config_from_object("django.conf:settings", namespace="CELERY")
app.autodiscover_tasks()

# Comprobar modelos Ollama una vez al día a las 03:00 (UTC)
app.conf.beat_schedule = {
    "check-ollama-models-daily": {
        "task": "ia.tasks.check_ollama_models_task",
        "schedule": crontab(hour=3, minute=0),
    },
}

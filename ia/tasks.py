"""
Tareas Celery para la app IA.
"""
from django.core.management import call_command
from celery import shared_task


@shared_task
def check_ollama_models_task():
    """Ejecuta el comando check_ollama_models (estado y actualizaciones de modelos Ollama)."""
    call_command("check_ollama_models")

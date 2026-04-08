"""
Descarga o actualiza modelos Ollama desde la línea de comandos.
Uso:
    python manage.py pull_ollama_model llama3.1:8b
    python manage.py pull_ollama_model llama3.1:8b qwen3:8b      # varios modelos
    python manage.py pull_ollama_model --server "local" llama3.1:8b
    python manage.py pull_ollama_model --all                      # todos los configurados
"""
from django.core.management.base import BaseCommand, CommandError
from django.utils import timezone

from ia.models import OllamaModelConfig, OllamaServer
from ia.services import check_model_on_server, pull_model_on_server


class Command(BaseCommand):
    help = "Descarga o actualiza modelos Ollama (equivalente a 'ollama pull')."

    def add_arguments(self, parser):
        parser.add_argument(
            "models",
            nargs="*",
            metavar="MODEL",
            help="Nombre(s) del modelo, p.ej. llama3.1:8b qwen3:8b",
        )
        parser.add_argument(
            "--server",
            dest="server_name",
            default=None,
            help="Nombre del servidor Ollama (por defecto: primero habilitado).",
        )
        parser.add_argument(
            "--all",
            action="store_true",
            dest="pull_all",
            help="Descarga todos los modelos configurados en OllamaModelConfig.",
        )

    def handle(self, *args, **options):
        server_name = options["server_name"]
        pull_all = options["pull_all"]
        model_names = options["models"]

        if not pull_all and not model_names:
            raise CommandError(
                "Especifica al menos un nombre de modelo o usa --all. "
                "Ejemplo: python manage.py pull_ollama_model llama3.1:8b"
            )

        # Resolver servidor
        if server_name:
            try:
                server = OllamaServer.objects.get(name=server_name, enabled=True)
            except OllamaServer.DoesNotExist:
                raise CommandError(f"Servidor '{server_name}' no encontrado o deshabilitado.")
        else:
            server = OllamaServer.objects.filter(enabled=True).first()
            if not server:
                raise CommandError("No hay ningún servidor Ollama habilitado en la base de datos.")

        self.stdout.write(f"Servidor: {server.name} ({server.base_url})")

        # Construir lista de modelos a descargar
        if pull_all:
            configs = list(OllamaModelConfig.objects.filter(server=server).order_by("model_name"))
            if not configs:
                self.stdout.write(self.style.WARNING("No hay modelos configurados para este servidor."))
                return
            targets = [(cfg.model_name, cfg) for cfg in configs]
        else:
            targets = [(name, None) for name in model_names]

        errors = []
        for model_name, config in targets:
            self.stdout.write(f"  Descargando '{model_name}'... ", ending="")
            ok, err = pull_model_on_server(server, model_name)
            if ok:
                self.stdout.write(self.style.SUCCESS("OK"))
                # Actualizar el registro OllamaModelConfig si existe
                if config is None:
                    config = OllamaModelConfig.objects.filter(
                        server=server, model_name=model_name
                    ).first()
                if config:
                    downloaded, digest = check_model_on_server(server, model_name)
                    config.downloaded = downloaded
                    config.digest = digest
                    config.last_checked_at = timezone.now()
                    config.update_available = False
                    config.save(update_fields=[
                        "downloaded", "digest", "last_checked_at", "update_available", "updated_at"
                    ])
            else:
                self.stdout.write(self.style.ERROR(f"ERROR: {err}"))
                errors.append(model_name)

        if errors:
            raise CommandError(f"Fallaron los siguientes modelos: {', '.join(errors)}")
        self.stdout.write(self.style.SUCCESS("Descarga completada."))

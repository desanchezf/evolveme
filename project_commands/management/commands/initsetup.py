import os

from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from django.core.management.base import BaseCommand


PROMPTS_DIR = os.path.join(settings.BASE_DIR, "prompts")

PROMPT_FILES = [
    {"name": "gym", "filename": "gym.txt"},
    {"name": "nutrition", "filename": "nutrition.txt"},
    {"name": "product_extraction", "filename": "product_response.txt"},
]

OLLAMA_MODELS = [
    {
        "model_name": "llama3.2-vision:11b",
        "alias": "llama3.2 vision 11b",
        "proposito": "OCR",
        "description": "Modelo de visión para extracción de datos desde imágenes.",
    },
    {
        "model_name": "qwen3:8b",
        "alias": "qwen3 8b",
        "proposito": "Chat",
        "description": "Modelo de chat avanzado (requiere ~5.5 GiB RAM).",
    },
    {
        "model_name": "qwen3:1.7b",
        "alias": "qwen3 1.7b",
        "proposito": "Chat",
        "description": "Modelo de chat por defecto, razonamiento del nutricionista (~1.4 GiB RAM).",
        "is_default": True,
    },
]


class Command(BaseCommand):
    def handle(self, *args, **kwargs):
        created_superuser, error_superuser = self.create_superuser()
        self.setup_ollama_models()
        self.setup_prompts()
        # created_groups, error_groups = self.create_groups_and_permissions()

        if not error_superuser:
            self.stdout.write(self.style.SUCCESS("Superuser created successfully ✅"))
        else:
            self.stdout.write(self.style.WARNING(f"Superuser already exists ❌ ({error_superuser})"))

        # if not error_groups:
        #     self.stdout.write(self.style.SUCCESS("Groups created successfully ✅"))
        # else:
        #     self.stdout.write(self.style.WARNING(f"Groups already exist ❌ ({error_groups})"))

    def setup_ollama_models(self):
        try:
            from ia.models import OllamaModelConfig, OllamaServer
            server, _ = OllamaServer.objects.get_or_create(
                name="local",
                defaults={"base_url": "http://ollama:11434", "enabled": True},
            )
            for entry in OLLAMA_MODELS:
                OllamaModelConfig.objects.get_or_create(
                    server=server,
                    model_name=entry["model_name"],
                    defaults={
                        "alias": entry.get("alias", entry["model_name"]),
                        "proposito": entry.get("proposito", ""),
                        "description": entry.get("description", ""),
                        "is_default": entry.get("is_default", False),
                    },
                )
            self.stdout.write(self.style.SUCCESS("Ollama models configured ✅"))
        except Exception as e:
            self.stdout.write(self.style.WARNING(f"Ollama model setup skipped: {e}"))

    def setup_prompts(self):
        try:
            from ia.models import Promtps

            loaded = []
            for entry in PROMPT_FILES:
                path = os.path.join(PROMPTS_DIR, entry["filename"])
                if not os.path.exists(path):
                    self.stdout.write(self.style.WARNING(f"Prompt file not found: {path}"))
                    continue
                with open(path, "r", encoding="utf-8") as f:
                    content = f.read().strip()
                if not content:
                    continue
                obj, created = Promtps.objects.update_or_create(
                    name=entry["name"],
                    defaults={"prompt": content},
                )
                loaded.append(entry["name"])
            self.stdout.write(self.style.SUCCESS(f"Prompts loaded ✅: {', '.join(loaded)}"))
        except Exception as e:
            self.stdout.write(self.style.WARNING(f"Prompt setup skipped: {e}"))

    def create_superuser(self):
        try:
            User = get_user_model()
            if not User.objects.filter(username="admin").exists():
                User.objects.create_superuser(
                    "admin",  # USERNAME
                    "admin@sanbox.org",  # MAIL
                    "admin",  # PASS
                )
                return True, None
            return False, "Usuario ya existe"
        except Exception as e:
            return False, str(e)

    def create_groups_and_permissions(self):
        try:
            for group in settings.ADMIN_GROUPS:
                Group.objects.get_or_create(name=group)

            role_permissions = settings.ROLE_PERMISSIONS

            for role_permission, permissions in role_permissions.items():
                role, created = Group.objects.get_or_create(name=role_permission)
                for item in permissions:
                    content_type = ContentType.objects.get(app_label=item["app_label"], model=item["model"])
                    for permission in item["permissions"]:
                        # NOTE: If it exists, it is not added (there is no error)
                        role.permissions.add(
                            Permission.objects.get(
                                codename=f"{permission}_{item['model']}",
                                content_type=content_type,
                            )
                        )
            role.save()
            return True, None
        except Exception as e:
            return False, str(e)

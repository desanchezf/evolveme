import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("ia", "0002_ollamamodelconfig_pull_progress"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="UserModelPrompt",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("prompt_text", models.TextField(verbose_name="Prompt de sistema")),
                ("generated_at", models.DateTimeField(auto_now=True, verbose_name="Generado el")),
                (
                    "model_config",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="user_prompts",
                        to="ia.ollamamodelconfig",
                        verbose_name="Modelo",
                    ),
                ),
                (
                    "user",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="ia_prompts",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
            options={
                "verbose_name": "Prompt de usuario",
                "verbose_name_plural": "Prompts de usuario",
                "unique_together": {("user", "model_config")},
            },
        ),
    ]

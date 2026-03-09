# Generated manually: proposito, estado (downloaded), digest, last_checked_at, update_available

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("ia", "0002_ollamaserver_chatsession_chatmessage_and_more"),
    ]

    operations = [
        migrations.AddField(
            model_name="ollamamodelconfig",
            name="proposito",
            field=models.CharField(
                blank=True,
                help_text="Uso del modelo (p. ej. 'OCR', 'Razonamiento del nutricionista', 'Chat').",
                max_length=255,
                verbose_name="Propósito",
            ),
        ),
        migrations.AddField(
            model_name="ollamamodelconfig",
            name="downloaded",
            field=models.BooleanField(
                default=False,
                help_text="Si el modelo está actualmente descargado en el servidor Ollama.",
                verbose_name="Descargado",
            ),
        ),
        migrations.AddField(
            model_name="ollamamodelconfig",
            name="digest",
            field=models.CharField(
                blank=True,
                help_text="Digest del modelo en Ollama (para detectar actualizaciones).",
                max_length=64,
                verbose_name="Digest",
            ),
        ),
        migrations.AddField(
            model_name="ollamamodelconfig",
            name="last_checked_at",
            field=models.DateTimeField(
                blank=True,
                null=True,
                verbose_name="Última comprobación",
            ),
        ),
        migrations.AddField(
            model_name="ollamamodelconfig",
            name="update_available",
            field=models.BooleanField(
                default=False,
                help_text="Hay una versión nueva disponible o el modelo no está descargado.",
                verbose_name="Actualización disponible",
            ),
        ),
    ]

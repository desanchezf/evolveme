# Generated manually for workout_image

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("cardio", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="cardiosession",
            name="workout_image",
            field=models.ImageField(
                blank=True,
                help_text="Opcional. Sube una captura o foto del entrenamiento para extraer datos con IA.",
                null=True,
                upload_to="cardio/%Y/%m/",
                verbose_name="Imagen del entrenamiento",
            ),
        ),
    ]

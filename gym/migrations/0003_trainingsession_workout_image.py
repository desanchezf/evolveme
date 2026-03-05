# Generated manually for workout_image on TrainingSession

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("gym", "0002_alter_routine_duration"),
    ]

    operations = [
        migrations.AddField(
            model_name="trainingsession",
            name="workout_image",
            field=models.ImageField(
                blank=True,
                help_text="Opcional. Sube una captura o foto del entrenamiento para extraer datos con IA.",
                null=True,
                upload_to="gym/%Y/%m/",
                verbose_name="Imagen del entrenamiento",
            ),
        ),
    ]

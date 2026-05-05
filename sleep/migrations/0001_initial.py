import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="SleepRecord",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("date", models.DateField(verbose_name="Fecha")),
                ("sleep_start", models.DateTimeField(blank=True, null=True, verbose_name="Inicio del sueño")),
                ("sleep_end", models.DateTimeField(blank=True, null=True, verbose_name="Fin del sueño")),
                ("total_sleep_time", models.DurationField(blank=True, null=True, verbose_name="Tiempo total dormido")),
                ("awake_time", models.DurationField(blank=True, null=True, verbose_name="Tiempo despierto")),
                ("rem_time", models.DurationField(blank=True, null=True, verbose_name="Sueño REM")),
                ("core_time", models.DurationField(blank=True, null=True, verbose_name="Sueño Core (ligero)")),
                ("deep_time", models.DurationField(blank=True, null=True, verbose_name="Sueño profundo")),
                ("notes", models.TextField(blank=True, null=True, verbose_name="Notas")),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                (
                    "user",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="sleep_records",
                        to=settings.AUTH_USER_MODEL,
                        verbose_name="Usuario",
                    ),
                ),
            ],
            options={
                "verbose_name": "Registro de sueño",
                "verbose_name_plural": "Registros de sueño",
                "ordering": ["-date", "-sleep_start"],
                "unique_together": {("user", "date")},
            },
        ),
    ]

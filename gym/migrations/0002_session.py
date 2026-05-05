import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


def migrate_sessions_forward(apps, schema_editor):
    CardioSession = apps.get_model("gym", "CardioSession")
    TrainingSession = apps.get_model("gym", "TrainingSession")
    Session = apps.get_model("gym", "Session")

    for cs in CardioSession.objects.select_related("exercise", "user").all():
        name = cs.exercise.name if cs.exercise else "Outdoor Walk"
        Session.objects.create(
            user=cs.user,
            name=name,
            session_start=cs.session_start,
            session_end=cs.session_end,
            date=cs.date,
            location=cs.location,
            workout_time=cs.workout_time,
            distance=cs.distance,
            avg_speed=cs.avg_speed,
            active_calories=cs.active_calories,
            total_calories=cs.total_calories,
            elevation_gain=cs.elevation_gain,
            average_heart_rate=cs.average_heart_rate,
        )

    for ts in TrainingSession.objects.select_related("user", "routine").all():
        date = ts.session_date.date() if ts.session_date else None
        if not date:
            continue
        Session.objects.create(
            user=ts.user,
            name="Musculation",
            routine=ts.routine,
            session_start=ts.session_date,
            date=date,
            location=ts.location,
            workout_time=ts.workout_time,
            active_calories=ts.active_kilocalories,
            total_calories=ts.total_kilocalories,
            average_heart_rate=ts.avg_heart_rate,
        )


class Migration(migrations.Migration):

    dependencies = [
        ("gym", "0001_initial"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="Session",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("name", models.CharField(
                    choices=[
                        ("Outdoor Walk", "Caminar exterior"),
                        ("Indoor Walk", "Caminar cinta"),
                        ("Outdoor Cycle", "Bicicleta exterior"),
                        ("Indoor Cycle", "Bicicleta estática"),
                        ("Elliptical", "Elíptica"),
                        ("Musculation", "Musculación"),
                    ],
                    max_length=255,
                    verbose_name="Categoría",
                )),
                ("session_start", models.DateTimeField(blank=True, null=True, verbose_name="Inicio")),
                ("session_end", models.DateTimeField(blank=True, null=True, verbose_name="Fin")),
                ("date", models.DateField(verbose_name="Fecha")),
                ("location", models.CharField(blank=True, max_length=255, null=True, verbose_name="Ubicación")),
                ("workout_time", models.DurationField(blank=True, null=True, verbose_name="Duración")),
                ("distance", models.FloatField(blank=True, null=True, verbose_name="Distancia (km)")),
                ("avg_speed", models.FloatField(blank=True, null=True, verbose_name="Velocidad media (km/h)")),
                ("active_calories", models.IntegerField(blank=True, null=True, verbose_name="Kcal activas")),
                ("total_calories", models.IntegerField(blank=True, null=True, verbose_name="Kcal totales")),
                ("elevation_gain", models.IntegerField(blank=True, null=True, verbose_name="Desnivel (m)")),
                ("average_heart_rate", models.IntegerField(blank=True, null=True, verbose_name="FC media (bpm)")),
                ("workout_image", models.ImageField(
                    blank=True,
                    help_text="Opcional. Sube una captura para extraer datos con IA.",
                    null=True,
                    upload_to="sessions/%Y/%m/",
                    verbose_name="Imagen",
                )),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("user", models.ForeignKey(
                    blank=True,
                    null=True,
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name="sessions",
                    to=settings.AUTH_USER_MODEL,
                    verbose_name="Usuario",
                )),
                ("routine", models.ForeignKey(
                    blank=True,
                    null=True,
                    on_delete=django.db.models.deletion.SET_NULL,
                    related_name="unified_sessions",
                    to="gym.routine",
                    verbose_name="Rutina",
                )),
            ],
            options={
                "verbose_name": "Sesión",
                "verbose_name_plural": "Sesiones",
                "ordering": ["-date", "-session_start"],
            },
        ),
        migrations.RunPython(
            code=migrate_sessions_forward,
            reverse_code=migrations.RunPython.noop,
        ),
    ]

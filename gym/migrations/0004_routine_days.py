import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("gym", "0003_routine_classification_fields"),
    ]

    operations = [
        migrations.CreateModel(
            name="RoutineDay",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("day_number", models.PositiveSmallIntegerField(verbose_name="Número de día")),
                ("name", models.CharField(
                    help_text="Ej: Push + calistenia de empuje, Descanso",
                    max_length=255,
                    verbose_name="Enfoque del día",
                )),
                ("is_rest", models.BooleanField(default=False, verbose_name="Día de descanso")),
                ("routine", models.ForeignKey(
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name="days",
                    to="gym.routine",
                    verbose_name="Rutina",
                )),
            ],
            options={
                "verbose_name": "Día de rutina",
                "verbose_name_plural": "Días de rutina",
                "ordering": ["day_number"],
                "unique_together": {("routine", "day_number")},
            },
        ),
        migrations.CreateModel(
            name="RoutineDayExercise",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("exercise_name", models.CharField(
                    help_text="Nombre libre. Puede incluir prefijo de categoría (ej: Core: Plancha)",
                    max_length=255,
                    verbose_name="Nombre del ejercicio",
                )),
                ("sets_reps", models.CharField(
                    blank=True,
                    default="",
                    help_text="Ej: 4x8-10, 3x30-45s, 3x12",
                    max_length=50,
                    verbose_name="Series × Reps",
                )),
                ("notes", models.CharField(blank=True, max_length=255, null=True, verbose_name="Notas")),
                ("order", models.PositiveSmallIntegerField(default=0, verbose_name="Orden")),
                ("day", models.ForeignKey(
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name="exercises",
                    to="gym.routineday",
                    verbose_name="Día",
                )),
                ("exercise", models.ForeignKey(
                    blank=True,
                    null=True,
                    on_delete=django.db.models.deletion.SET_NULL,
                    related_name="routine_day_exercises",
                    to="gym.musculationexercise",
                    verbose_name="Ejercicio (biblioteca)",
                )),
            ],
            options={
                "verbose_name": "Ejercicio del día",
                "verbose_name_plural": "Ejercicios del día",
                "ordering": ["order"],
            },
        ),
    ]

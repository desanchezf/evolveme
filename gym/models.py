from django.db import models
from django.contrib.auth.models import User


from gym.enums import BodyPartChoices


# Ejercicios de Musculación
class MusculationExercise(models.Model):
    name = models.CharField(max_length=255, verbose_name="Nombre del ejercicio")
    description = models.TextField(null=True, blank=True, verbose_name="Descripción")
    body_part = models.CharField(
        max_length=255,
        choices=BodyPartChoices.choices(),
        null=True,
        blank=True,
        verbose_name="Parte del cuerpo",
    )
    sets = models.IntegerField(null=False, blank=False, verbose_name="Series")
    reps = models.IntegerField(null=False, blank=False, verbose_name="Repeticiones")
    image_base64 = models.TextField(null=True, blank=True, verbose_name="Imagen")

    class Meta:
        verbose_name = "Ejercicio de musculación"
        verbose_name_plural = "Ejercicios de musculación"

    def __str__(self):
        return self.name


class MusculationRecord(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="musculation_records",
        verbose_name="Usuario",
    )
    exercise = models.ForeignKey(
        MusculationExercise,
        on_delete=models.CASCADE,
        related_name="records",
        verbose_name="Ejercicio",
    )
    sets = models.IntegerField(null=False, blank=False, verbose_name="Series")
    reps = models.IntegerField(null=False, blank=False, verbose_name="Repeticiones")
    weight = models.IntegerField(null=False, blank=False, verbose_name="Peso (kg)")
    tbi = models.BooleanField(null=False, blank=False, verbose_name="To be improved")
    observation = models.TextField(null=True, blank=True, verbose_name="Observación")
    record_date = models.DateTimeField(
        null=True, blank=True, verbose_name="Fecha de registro"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Registro de ejercicio de musculación"


class Routine(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="routines",
        verbose_name="Usuario",
    )
    exercises = models.ManyToManyField(
        MusculationExercise, related_name="routines", verbose_name="Ejercicios"
    )
    start_date = models.DateTimeField(
        null=True, blank=True, verbose_name="Fecha de inicio"
    )
    end_date = models.DateTimeField(null=True, blank=True, verbose_name="Fecha de fin")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Rutina"
        verbose_name_plural = "Rutinas"
        ordering = ["-start_date"]

    def __str__(self):
        return f"{self.user} - {self.start_date} - {self.end_date}"


class TrainingSession(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="training_sessions",
        verbose_name="Usuario",
    )
    routine = models.ForeignKey(
        Routine,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="sessions",
        verbose_name="Rutina",
    )
    session_date = models.DateTimeField(
        null=True, blank=True, verbose_name="Fecha y hora de la sesión"
    )
    location = models.CharField(
        max_length=255, verbose_name="Ubicación", null=True, blank=True
    )
    workout_time = models.DurationField(
        null=True, blank=True, verbose_name="Duración de la sesión"
    )
    active_kilocalories = models.IntegerField(
        null=True, blank=True, verbose_name="Kcal activas"
    )
    total_kilocalories = models.IntegerField(
        null=True, blank=True, verbose_name="Kcal totales"
    )
    avg_heart_rate = models.IntegerField(
        null=True, blank=True, verbose_name="FC media (BPM)"
    )

    class Meta:
        verbose_name = "Sesión de entrenamiento"
        verbose_name_plural = "Sesiones de entrenamiento"

    def __str__(self):
        return f"{self.user} - {self.session_date}"

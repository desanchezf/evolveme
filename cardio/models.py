from django.contrib.auth.models import User
from django.db import models

from cardio.enums import CardioExerciseChoices


class CardioSession(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="cardio_sessions",
        verbose_name="Usuario",
    )
    name = models.CharField(
        max_length=255,
        verbose_name="Nombre del ejercicio",
    )
    exercise_type = models.CharField(
        max_length=255,
        verbose_name="Tipo de ejercicio",
        choices=CardioExerciseChoices.choices(),
        null=True,
        blank=True,
    )
    session_start = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="Fecha y hora de inicio",
    )
    session_end = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="Fecha y hora de fin",
    )
    date = models.DateField(
        verbose_name="Fecha",
    )
    location = models.CharField(
        max_length=255,
        null=True,
        blank=True,
        verbose_name="Ubicación",
    )
    workout_time = models.DurationField(
        null=True,
        blank=True,
        verbose_name="Duración del entrenamiento",
    )
    distance = models.FloatField(
        null=True,
        blank=True,
        verbose_name="Distancia (km)",
    )
    avg_speed = models.FloatField(
        null=True,
        blank=True,
        verbose_name="Velocidad promedio (km/h)",
    )
    active_calories = models.IntegerField(
        null=True,
        blank=True,
        verbose_name="Calorías activas (kcal)",
    )
    total_calories = models.IntegerField(
        null=True,
        blank=True,
        verbose_name="Calorías totales (kcal)",
    )
    elevation_gain = models.IntegerField(
        null=True,
        blank=True,
        verbose_name="Ganancia de elevación (m)",
    )
    average_heart_rate = models.IntegerField(
        null=True,
        blank=True,
        verbose_name="Frecuencia cardíaca promedio (bpm)",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Sesión de cardio"
        verbose_name_plural = "Sesiones de cardio"
        ordering = ["-date", "-session_start"]

    def __str__(self):
        return f"{self.user.username} - {self.name} - {self.date}"

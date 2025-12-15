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
    date = models.DateField(
        verbose_name="Fecha",
    )
    workout_time = models.IntegerField(
        verbose_name="Tiempo de entrenamiento (minutos)",
    )
    distance = models.FloatField(
        null=True,
        blank=True,
        verbose_name="Distancia (km)",
    )
    active_calories = models.IntegerField(
        null=True,
        blank=True,
        verbose_name="Calorías activas",
    )
    total_calories = models.IntegerField(
        null=True,
        blank=True,
        verbose_name="Calorías totales",
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
    avg_speed = models.FloatField(
        null=True,
        blank=True,
        verbose_name="Velocidad promedio (km/h)",
    )

    class Meta:
        verbose_name = "Sesión de cardio"
        verbose_name_plural = "Sesiones de cardio"
        ordering = ["-date", "-workout_time"]

    def __str__(self):
        return f"{self.user.username} - {self.name} - {self.date}"

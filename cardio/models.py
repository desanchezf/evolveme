from django.contrib.auth.models import User
from django.db import models

from cardio.enums import CardioExerciseNameChoices


class CardioExercise(models.Model):
    name = models.CharField(
        max_length=255,
        verbose_name="Nombre del ejercicio",
        choices=CardioExerciseNameChoices.choices(),
    )
    description = models.TextField(null=True, blank=True, verbose_name="Descripción")
    image_base64 = models.TextField(null=True, blank=True, verbose_name="Imagen")

    class Meta:
        verbose_name = "Ejercicio de cardio"
        verbose_name_plural = "Ejercicios de cardio"

    def __str__(self):
        """Devuelve el nombre del ejercicio en español"""
        return self.get_name_display() or self.name


class CardioSession(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="cardio_sessions",
        verbose_name="Usuario",
    )
    exercise = models.ForeignKey(
        CardioExercise,
        on_delete=models.CASCADE,
        related_name="sessions",
        verbose_name="Ejercicio",
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
        if self.exercise:
            return f"{self.user.username} - {self.exercise.name} - {self.date}"
        return f"{self.user.username} - Sin ejercicio - {self.date}"

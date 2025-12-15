from django.db import models
from django.contrib.auth.models import User

from cardio.models import CardioExercise
from gym.enums import BodyPartChoices


# Musculation Exercise
class MusculationExercise(models.Model):
    id = models.CharField(
        primary_key=True, max_length=255, verbose_name="ID del ejercicio"
    )
    name = models.CharField(max_length=255, verbose_name="Nombre del ejercicio")
    description = models.TextField(null=True, blank=True, verbose_name="Descripción")
    body_part = models.CharField(
        max_length=255,
        choices=BodyPartChoices.choices(),
        null=True,
        blank=True,
        verbose_name="Parte del cuerpo",
    )
    observation = models.TextField(null=True, blank=True, verbose_name="Observación")
    image_base64 = models.TextField(null=True, blank=True, verbose_name="Imagen")

    class Meta:
        verbose_name = "Ejercicio de musculación"
        verbose_name_plural = "Ejercicios de musculación"

    def __str__(self):
        return self.name


class ExerciseSet(models.Model):
    exercise = models.ForeignKey(
        MusculationExercise,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        verbose_name="Ejercicio",
    )
    weight = models.IntegerField(null=False, blank=False, verbose_name="Peso (kg)")
    reps = models.IntegerField(null=False, blank=False, verbose_name="Repeticiones")
    sets = models.IntegerField(null=False, blank=False, verbose_name="Series")
    tbi = models.BooleanField(
        null=False,
        blank=False,
        verbose_name="To be improved",
    )

    class Meta:
        verbose_name = "Set de ejercicio"
        verbose_name_plural = "Sets de ejercicios"


# Entrenamiento
class TrainingSession(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        verbose_name="Usuario",
    )
    musculation = models.ManyToManyField(
        ExerciseSet, blank=True, verbose_name="Ejercicios de musculación"
    )
    cardio = models.ForeignKey(
        CardioExercise,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        verbose_name="Actividad de cardio",
    )
    date = models.DateField(verbose_name="Fecha")
    observation = models.TextField(null=True, blank=True, verbose_name="Observación")

    class Meta:
        verbose_name = "Sesión de entrenamiento"
        verbose_name_plural = "Sesiones de entrenamiento"

    def __str__(self):
        return f"{self.user.username} - {self.date}"




class Routine(models.Model):
    name = models.CharField(max_length=255, verbose_name="Nombre de la rutina")
    start_date = models.DateField(
        null=False, blank=False, verbose_name="Fecha de inicio"
    )
    end_date = models.DateField(null=False, blank=False, verbose_name="Fecha de fin")
    exercises = models.ManyToManyField(MusculationExercise, verbose_name="Ejercicios")

    class Meta:
        verbose_name = "Rutina"
        verbose_name_plural = "Rutinas"

    def __str__(self):
        return f"{self.start_date} - {self.end_date}"


# Ejercicios de Musculación
class MusculationExercise(models.Model):
    id = models.CharField(
        primary_key=True, max_length=255, verbose_name="ID del ejercicio"
    )
    name = models.CharField(max_length=255, verbose_name="Nombre del ejercicio")
    description = models.TextField(null=True, blank=True, verbose_name="Descripción")
    body_part = models.CharField(
        max_length=255,
        choices=BodyPartChoices.choices(),
        null=True,
        blank=True,
        verbose_name="Parte del cuerpo",
    )
    observation = models.TextField(null=True, blank=True, verbose_name="Observación")
    image_base64 = models.TextField(null=True, blank=True, verbose_name="Imagen")

    class Meta:
        verbose_name = "Ejercicio de musculación"
        verbose_name_plural = "Ejercicios de musculación"

    def __str__(self):
        return self.name

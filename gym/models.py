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
    weight = models.IntegerField(null=False, blank=False, verbose_name="Peso (kg)")
    tbi = models.BooleanField(null=False, blank=False, verbose_name="To be improved")
    observation = models.TextField(null=True, blank=True, verbose_name="Observación")
    image_base64 = models.TextField(null=True, blank=True, verbose_name="Imagen")

    class Meta:
        verbose_name = "Ejercicio de musculación"
        verbose_name_plural = "Ejercicios de musculación"

    def __str__(self):
        return self.name

class Routine():
    Exercises = models.ManyToManyField(MusculationExercise, verbose_name="Ejercicios")

class TrainingSession(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        verbose_name="Usuario",
    )
    exercises = models.ManyToManyField(MusculationExercise, verbose_name="Ejercicios")

class
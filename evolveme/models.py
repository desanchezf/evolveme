# ruff: noqa: E501
from django.contrib.auth.models import User
from django.db import models

from evolveme.enums import (BodyPartChoices, CardioExerciseChoices,
                            GenderChoices, MealTypeChoices, ObjectiveChoices)


class GymUserProfile(models.Model):
    user = models.OneToOneField(
        User, on_delete=models.CASCADE, related_name="profile", verbose_name="Usuario"
    )
    birth_date = models.DateField(
        null=True,
        verbose_name="Fecha de nacimiento",
    )
    gender = models.CharField(
        max_length=10,
        choices=GenderChoices.choices(),
        null=True,
        blank=True,
        verbose_name="Género",
    )
    height = models.FloatField(
        null=True,
        blank=True,
        verbose_name="Altura (cm)",
    )
    objective = models.CharField(
        max_length=255,
        choices=ObjectiveChoices.choices(),
        null=True,
        blank=True,
        verbose_name="Objetivo",
    )

    class Meta:
        verbose_name = "Información del usuario"
        verbose_name_plural = "Información de los usuarios"

    def __str__(self):
        return self.user.username


# Medidas
class Measure(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="measures",
        verbose_name="Usuario",
    )
    date = models.DateField(verbose_name="Fecha")
    weight = models.FloatField(null=True, blank=True, verbose_name="Peso (kg)")
    arm = models.FloatField(null=True, blank=True, verbose_name="Brazo (cm)")
    chest = models.FloatField(null=True, blank=True, verbose_name="Pecho (cm)")
    waist = models.FloatField(null=True, blank=True, verbose_name="Cintura (cm)")
    leg = models.FloatField(null=True, blank=True, verbose_name="Pierna (cm)")
    fat_perc = models.FloatField(
        null=True, blank=True, verbose_name="Porcentaje de masa grasa (Kg)"
    )
    muscle_mass = models.FloatField(
        null=True, blank=True, verbose_name="Masa muscular (Kg)"
    )

    class Meta:
        verbose_name = "Medida"
        verbose_name_plural = "Medidas"

    def __str__(self):
        return f"{self.user.username} - {self.date}"


# Cardio Exercise
class CardioExercise(models.Model):
    name = models.CharField(
        max_length=255,
        choices=CardioExerciseChoices.choices(),
        verbose_name="Tipo de actividad",
    )
    workout_time = models.IntegerField(
        null=False, blank=False, verbose_name="Duración (min)"
    )
    distance = models.FloatField(null=False, blank=False, verbose_name="Distancia (km)")
    active_calories = models.IntegerField(
        null=False, blank=False, verbose_name="Calorías activas"
    )
    total_calories = models.IntegerField(
        null=False, blank=False, verbose_name="Calorías totales"
    )
    elevation_gain = models.IntegerField(
        null=False, blank=False, verbose_name="Elevación (m)"
    )
    average_heart_rate = models.IntegerField(
        null=False, blank=False, verbose_name="Frecuencia cardíaca promedio (bpm)"
    )
    avg_speed = models.FloatField(
        null=False, blank=False, verbose_name="Velocidad promedio (km/h)"
    )

    class Meta:
        verbose_name = "Actividad de cardio"
        verbose_name_plural = "Actividades de cardio"

    def __str__(self):
        return self.name


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


# Nutrición
class Diet(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="Usuario")
    date = models.DateTimeField(verbose_name="Fecha")
    meal_type = models.CharField(
        max_length=255,
        choices=MealTypeChoices.choices(),
        null=True,
        blank=True,
        verbose_name="Tipo de comida",
    )
    food = models.TextField(null=True, blank=True, verbose_name="Comida")
    quantity = models.IntegerField(null=True, blank=True, verbose_name="Cantidad")
    calories = models.IntegerField(
        null=True, blank=True, verbose_name="Calorías (kcal)"
    )

    class Meta:
        verbose_name = "Dieta"
        verbose_name_plural = "Dietas"

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

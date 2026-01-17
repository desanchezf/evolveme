# ruff: noqa: E501
from django.contrib.auth.models import User
from django.db import models

from evolveme.enums import GenderChoices, ObjectiveChoices
from gym.models import Routine


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
    active_routine = models.ForeignKey(
        Routine,
        on_delete=models.SET_NULL,
        related_name="active_routine",
        verbose_name="Rutina activa",
        null=True,
        blank=True,
    )
    start_date = models.DateField(null=True, blank=True, verbose_name="Fecha de inicio")
    end_date = models.DateField(null=True, blank=True, verbose_name="Fecha de fin")
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
        null=True, blank=True, verbose_name="Porcentaje de masa grasa (%)"
    )
    muscle_mass = models.FloatField(
        null=True, blank=True, verbose_name="Masa muscular (kg)"
    )
    # Composición corporal
    bmi = models.FloatField(
        null=True, blank=True, verbose_name="Índice de masa corporal (BMI)"
    )
    body_water_mass = models.FloatField(
        null=True, blank=True, verbose_name="Masa de agua corporal (kg)"
    )
    body_water_percentage = models.FloatField(
        null=True, blank=True, verbose_name="Porcentaje de agua corporal (%)"
    )
    fat_mass = models.FloatField(null=True, blank=True, verbose_name="Masa grasa (kg)")
    bone_mineral_content = models.FloatField(
        null=True, blank=True, verbose_name="Contenido mineral óseo (kg)"
    )
    bone_mineral_percentage = models.FloatField(
        null=True, blank=True, verbose_name="Porcentaje de mineral óseo (%)"
    )
    protein_mass = models.FloatField(
        null=True, blank=True, verbose_name="Masa proteica (kg)"
    )
    protein_percentage = models.FloatField(
        null=True, blank=True, verbose_name="Porcentaje de proteína (%)"
    )
    muscle_percentage = models.FloatField(
        null=True, blank=True, verbose_name="Porcentaje muscular (%)"
    )
    skeletal_muscle_mass = models.FloatField(
        null=True, blank=True, verbose_name="Masa muscular esquelética (kg)"
    )
    visceral_fat_rating = models.FloatField(
        null=True, blank=True, verbose_name="Calificación de grasa visceral"
    )
    basal_metabolic_rate = models.FloatField(
        null=True, blank=True, verbose_name="Tasa metabólica basal (Kcal)"
    )
    waist_to_hip_ratio = models.FloatField(
        null=True, blank=True, verbose_name="Ratio cintura-cadera"
    )
    body_age = models.IntegerField(
        null=True, blank=True, verbose_name="Edad corporal (años)"
    )
    fat_free_body_weight = models.FloatField(
        null=True, blank=True, verbose_name="Peso corporal libre de grasa (kg)"
    )

    class Meta:
        verbose_name = "Medida"
        verbose_name_plural = "Medidas"

    def __str__(self):
        return f"{self.user.username} - {self.date}"

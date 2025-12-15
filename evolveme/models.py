# ruff: noqa: E501
from django.contrib.auth.models import User
from django.db import models

from evolveme.enums import GenderChoices, ObjectiveChoices
from gym.enums import BodyPartChoices


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



from django.utils.translation import gettext_lazy as _


class GenderChoices(str):
    Male = "M"
    Female = "F"
    Other = "O"

    values = (
        (Male, _("Masculino")),
        (Female, _("Femenino")),
        (Other, _("Otro")),
    )

    @classmethod
    def choices(cls):
        return cls.values


class ObjectiveChoices(str):
    LoseWeight = "lose_weight"
    GainMuscle = "gain_muscle"
    GainWeight = "gain_weight"
    ImproveHealth = "improve_health"
    ImprovePerformance = "improve_performance"

    values = (
        (LoseWeight, _("Perder peso")),
        (GainMuscle, _("Ganar músculo")),
        (GainWeight, _("Ganar peso")),
        (ImproveHealth, _("Mejorar la salud")),
        (ImprovePerformance, _("Mejorar el rendimiento")),
    )

    @classmethod
    def choices(cls):
        return ObjectiveChoices.values

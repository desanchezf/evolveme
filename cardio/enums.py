from django.utils.translation import gettext_lazy as _


class CardioExerciseNameChoices(str):
    """Enum para los nombres de ejercicios de cardio"""

    Outdoor_Walk = "Outdoor Walk"
    Indoor_Walk = "Indoor Walk"
    Outdoor_Cycle = "Outdoor Cycle"
    Indoor_Cycle = "Indoor Cycle"
    Elliptical = "Elliptical"

    values = (
        (Outdoor_Walk, _("Caminar exterior")),
        (Indoor_Walk, _("Caminar cinta")),
        (Outdoor_Cycle, _("Bicicleta exterior")),
        (Indoor_Cycle, _("Bicicleta estática")),
        (Elliptical, _("Elíptica")),
    )

    @classmethod
    def choices(cls):
        return CardioExerciseNameChoices.values

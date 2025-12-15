from django.utils.translation import gettext_lazy as _


class CardioExerciseChoices(str):
    Walking_Outside = "walking_outside"
    Walking_Treadmill = "walking_treadmill"
    Cycling_Outside = "cycling_outside"
    Cycling_Treadmill = "cycling_treadmill"
    Elliptical_Treadmill = "elliptical_treadmill"

    values = (
        (Walking_Outside, _("Caminar exterior")),
        (Walking_Treadmill, _("Caminar cinta")),
        (Cycling_Outside, _("Bicicleta exterior")),
        (Cycling_Treadmill, _("Bicicleta cinta")),
        (Elliptical_Treadmill, _("Elíptica cinta")),
    )

    @classmethod
    def choices(cls):
        return CardioExerciseChoices.values

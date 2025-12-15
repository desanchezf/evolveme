from django.utils.translation import gettext_lazy as _


class MealTypeChoices(str):
    Breakfast = "breakfast"
    Lunch = "lunch"
    Snack = "snack"
    Dinner = "dinner"
    Nibble = "nibble"

    values = (
        (Breakfast, _("Desayuno")),
        (Lunch, _("Almuerzo")),
        (Snack, _("Snack")),
        (Dinner, _("Cena")),
        (Nibble, _("Picoteo")),
    )

    @classmethod
    def choices(cls):
        return MealTypeChoices.values

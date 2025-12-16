from django.utils.translation import gettext_lazy as _


class BodyPartChoices(str):
    Chest = "chest"
    Core = "core"
    Back = "back"
    Legs = "legs"
    Arms = "arms"
    Shoulders = "shoulders"
    Abs = "abs"
    Forearms = "forearms"

    values = (
        (Chest, _("Pecho")),
        (Back, _("Espalda")),
        (Legs, _("Piernas")),
        (Arms, _("Brazos")),
        (Shoulders, _("Hombros")),
        (Abs, _("Abdomen")),
        (Forearms, _("Antebrazos")),
        (Core, _("Zona media")),
    )

    @classmethod
    def choices(cls):
        return BodyPartChoices.values

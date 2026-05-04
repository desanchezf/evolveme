from django.utils.translation import gettext_lazy as _


class CardioExerciseNameChoices(str):
    Outdoor_Walk = "Outdoor Walk"
    Indoor_Walk = "Indoor Walk"
    Outdoor_Cycle = "Outdoor Cycle"
    Indoor_Cycle = "Indoor Cycle"
    Elliptical = "Elliptical"
    Musculation = "Musculation"

    values = (
        (Outdoor_Walk, _("Caminar exterior")),
        (Indoor_Walk, _("Caminar cinta")),
        (Outdoor_Cycle, _("Bicicleta exterior")),
        (Indoor_Cycle, _("Bicicleta estática")),
        (Elliptical, _("Elíptica")),
        (Musculation, _("Musculación")),
    )

    @classmethod
    def choices(cls):
        return CardioExerciseNameChoices.values


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


class ExerciseTypesChoices(str):
    Push = "push"
    Pull = "pull"
    Legs = "legs"
    Core = "core"
    FullBody = "full_body"
    LowerBody = "lower_body"
    UpperBody = "upper_body"
    Abs = "abs"
    Forearms = "forearms"

    values = (
        (Push, _("Push")),
        (Pull, _("Pull")),
        (Legs, _("Piernas")),
        (Core, _("Core")),
        (FullBody, _("Cuerpo completo")),
        (LowerBody, _("Parte inferior")),
        (UpperBody, _("Parte superior")),
        (Abs, _("Abdomen")),
        (Forearms, _("Antebrazos")),
    )

    @classmethod
    def choices(cls):
        return ExerciseTypesChoices.values


class UnitChoices(str):
    reps = "reps"
    seconds = "seconds"

    values = (
        (reps, _("Repeticiones")),
        (seconds, _("Segundos")),
    )

    @classmethod
    def choices(cls):
        return UnitChoices.values

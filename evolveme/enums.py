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


class BodyPartChoices(str):
    Chest = "chest"
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
    )

    @classmethod
    def choices(cls):
        return BodyPartChoices.values


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

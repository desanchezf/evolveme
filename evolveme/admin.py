from django.contrib import admin
from unfold.admin import ModelAdmin as UnfoldModelAdmin

from evolveme.models import (CardioExercise, Diet, ExerciseSet, GymUserProfile,
                             Measure, MusculationExercise, Routine,
                             TrainingSession)


@admin.register(GymUserProfile)
class GymUserProfileAdmin(UnfoldModelAdmin):
    list_display = ("user", "birth_date", "gender", "height", "objective")
    search_fields = ("user__username",)
    list_filter = ("gender", "objective")


@admin.register(CardioExercise)
class CardioAdmin(UnfoldModelAdmin):
    list_display = (
        "name",
        "workout_time",
        "active_calories",
        "total_calories",
        "distance"
    )
    search_fields = ("name",)
    list_filter = ("name",)


@admin.register(ExerciseSet)
class ExerciseSetAdmin(UnfoldModelAdmin):
    list_display = ["exercise", "weight", "reps", "sets"]
    search_fields = ("exercise__name",)
    list_filter = ("exercise__body_part",)


@admin.register(MusculationExercise)
class MusculationExerciseAdmin(UnfoldModelAdmin):
    list_display = ("name", "body_part", "description", "observation")
    search_fields = ("name", "body_part")
    list_filter = ("body_part",)


@admin.register(TrainingSession)
class TrainingSessionAdmin(UnfoldModelAdmin):
    list_display = ("user", "date", "observation")
    search_fields = ("user__username",)
    list_filter = ("date",)


@admin.register(Diet)
class DietAdmin(UnfoldModelAdmin):
    list_display = ("user", "date", "meal_type", "food", "quantity", "calories")
    search_fields = ("user__username", "meal_type", "food")
    list_filter = ("meal_type", "date")


@admin.register(Measure)
class MeasureAdmin(UnfoldModelAdmin):
    list_display = ("user", "date", "weight", "arm", "chest", "waist", "leg")
    search_fields = ("user__username",)
    list_filter = ("date",)


@admin.register(Routine)
class RoutineAdmin(UnfoldModelAdmin):
    list_display = ("name", "start_date", "end_date")
    search_fields = ("name",)
    list_filter = ("start_date", "end_date")

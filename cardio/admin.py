from django.contrib import admin
from unfold.admin import ModelAdmin as UnfoldModelAdmin

from cardio.models import CardioExercise, CardioSession


@admin.register(CardioExercise)
class CardioExerciseAdmin(UnfoldModelAdmin):
    list_display = (
        "name",
        "workout_time",
        "active_calories",
        "total_calories",
        "distance"
    )
    search_fields = ("name",)
    list_filter = ("name",)


@admin.register(CardioSession)
class CardioSessionAdmin(UnfoldModelAdmin):
    list_display = (
        "user",
        "name",
        "date",
        "workout_time",
        "distance",
        "active_calories",
        "total_calories",
        "average_heart_rate",
    )
    search_fields = ("user__username", "name")
    list_filter = ("name", "date")
    date_hierarchy = "date"

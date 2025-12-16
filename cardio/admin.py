from django.contrib import admin
from unfold.admin import ModelAdmin as UnfoldModelAdmin

from cardio.models import CardioSession


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
        "avg_speed",
        "elevation_gain",
    )
    list_filter = ("name", "date", "user")
    search_fields = ("user__username", "user__email", "name")
    date_hierarchy = "date"
    ordering = ("-date", "-workout_time")
    fieldsets = (
        (
            "Información básica",
            {
                "fields": ("user", "name", "date"),
            },
        ),
        (
            "Datos del entrenamiento",
            {
                "fields": (
                    "workout_time",
                    "distance",
                    "avg_speed",
                    "elevation_gain",
                ),
            },
        ),
        (
            "Calorías",
            {
                "fields": ("active_calories", "total_calories"),
            },
        ),
        (
            "Frecuencia cardíaca",
            {
                "fields": ("average_heart_rate",),
            },
        ),
    )

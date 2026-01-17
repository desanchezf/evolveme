from django.contrib import admin
from unfold.admin import ModelAdmin as UnfoldModelAdmin

from cardio.models import CardioSession
from cardio.forms import CardioSessionAdminForm


@admin.register(CardioSession)
class CardioSessionAdmin(UnfoldModelAdmin):
    form = CardioSessionAdminForm
    list_display = (
        "user",
        "exercise_type",
        "date",
        "session_start",
        "session_end",
        "location",
        "workout_time",
        "distance",
        "avg_speed",
        "active_calories",
        "total_calories",
        "elevation_gain",
        "average_heart_rate",
    )
    list_filter = ("exercise_type", "name", "date", "user", "location")
    search_fields = ("user__username", "user__email", "name", "location")
    date_hierarchy = "date"
    ordering = ("-date", "-session_start")
    fieldsets = (
        (
            "Información básica",
            {
                "fields": ("user", "name", "exercise_type", "date"),
            },
        ),
        (
            "Fecha y hora",
            {
                "fields": ("session_start", "session_end"),
            },
        ),
        (
            "Ubicación",
            {
                "fields": ("location",),
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

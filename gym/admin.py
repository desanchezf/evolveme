from django.contrib import admin
from unfold.admin import ModelAdmin as UnfoldModelAdmin

from gym.models import (
    MusculationExercise,
    MusculationRecord,
    Routine,
    TrainingSession,
)


@admin.register(MusculationExercise)
class MusculationExerciseAdmin(UnfoldModelAdmin):
    list_display = ("name", "body_part")
    list_filter = ("body_part",)
    search_fields = ("name", "description")
    fieldsets = (
        (
            "Información básica",
            {
                "fields": ("name", "description", "body_part"),
            },
        ),
        (
            "Imagen",
            {
                "fields": ("image_base64",),
            },
        ),
    )


@admin.register(MusculationRecord)
class MusculationRecordAdmin(UnfoldModelAdmin):
    list_display = (
        "user",
        "exercise",
        "sets",
        "reps",
        "weight",
        "tbi",
        "record_date",
    )
    list_filter = ("tbi", "record_date", "exercise", "user")
    search_fields = (
        "user__username",
        "user__email",
        "exercise__name",
        "observation",
    )
    date_hierarchy = "record_date"
    ordering = ("-record_date", "-created_at")
    fieldsets = (
        (
            "Información básica",
            {
                "fields": ("user", "exercise", "record_date"),
            },
        ),
        (
            "Datos del ejercicio",
            {
                "fields": ("sets", "reps", "weight", "tbi"),
            },
        ),
        (
            "Observaciones",
            {
                "fields": ("observation",),
            },
        ),
    )


@admin.register(Routine)
class RoutineAdmin(UnfoldModelAdmin):
    list_display = ("user", "start_date", "end_date", "created_at")
    list_filter = ("start_date", "end_date", "user")
    search_fields = ("user__username", "user__email")
    date_hierarchy = "start_date"
    ordering = ("-start_date",)
    filter_horizontal = ("Exercises",)
    fieldsets = (
        (
            "Información básica",
            {
                "fields": ("user", "start_date", "end_date"),
            },
        ),
        (
            "Ejercicios",
            {
                "fields": ("Exercises",),
            },
        ),
    )


@admin.register(TrainingSession)
class TrainingSessionAdmin(UnfoldModelAdmin):
    list_display = (
        "user",
        "routine",
        "session_date",
        "location",
        "workout_time",
        "active_kilocalories",
        "total_kilocalories",
        "avg_heart_rate",
    )
    list_filter = ("routine", "session_date", "user", "location")
    search_fields = (
        "user__username",
        "user__email",
        "location",
        "routine__id",
    )
    date_hierarchy = "session_date"
    ordering = ("-session_date",)
    fieldsets = (
        (
            "Información básica",
            {
                "fields": ("user", "routine", "session_date", "location"),
            },
        ),
        (
            "Datos del entrenamiento",
            {
                "fields": ("workout_time",),
            },
        ),
        (
            "Calorías",
            {
                "fields": ("active_kilocalories", "total_kilocalories"),
            },
        ),
        (
            "Frecuencia cardíaca",
            {
                "fields": ("avg_heart_rate",),
            },
        ),
    )

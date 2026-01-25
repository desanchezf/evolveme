from django.contrib import admin
from django.urls import path
from django.utils.safestring import mark_safe
from unfold.admin import ModelAdmin as UnfoldModelAdmin

from gym.models import (
    MusculationExercise,
    MusculationRecord,
    Routine,
    TrainingSession,
)
from gym.views import MusculationRecordFormsetView, RoutineJSONView
from gym.forms import (
    RoutineAdminForm,
    TrainingSessionAdminForm,
    MusculationRecordAdminForm,
)


@admin.register(MusculationExercise)
class MusculationExerciseAdmin(UnfoldModelAdmin):
    list_display = ("name", "body_part", "sets", "reps", "formatted_unit")
    list_filter = ("body_part", "unit")
    search_fields = ("name", "description")

    def formatted_unit(self, obj):
        """Muestra la unidad formateada"""
        return obj.get_unit_display() if obj.unit else "-"

    formatted_unit.short_description = "Unidad"
    formatted_unit.admin_order_field = "unit"

    fieldsets = (
        (
            "Información básica",
            {
                "fields": ("name", "description", "body_part"),
            },
        ),
        (
            "Series y repeticiones",
            {
                "fields": ("sets", "reps", "unit"),
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
    form = MusculationRecordAdminForm
    list_display = (
        "user",
        "exercise",
        "sets",
        "reps",
        "weight",
        "tbi",
        "formatted_record_date",
    )

    def formatted_record_date(self, obj):
        """Formatea la fecha de registro como DD/MM/YYYY HH:MM:SS"""
        if obj.record_date:
            return obj.record_date.strftime("%d/%m/%Y %H:%M:%S")
        return "-"

    formatted_record_date.short_description = "Fecha de registro"
    formatted_record_date.admin_order_field = "record_date"
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

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path(
                "add-formset/",
                self.admin_site.admin_view(MusculationRecordFormsetView.as_view()),
                name="gym_musculationrecord_add_formset",
            ),
        ]
        return custom_urls + urls

    def changelist_view(self, request, extra_context=None):
        extra_context = extra_context or {}
        extra_context["add_formset_url"] = "admin:gym_musculationrecord_add_formset"
        return super().changelist_view(request, extra_context=extra_context)


@admin.register(Routine)
class RoutineAdmin(UnfoldModelAdmin):
    form = RoutineAdminForm
    list_display = ("user", "formatted_exercise_types", "formatted_duration", "formatted_created_at")

    def formatted_exercise_types(self, obj):
        """Formatea los tipos de ejercicios como lista con viñetas"""
        if obj.exercise_types and isinstance(obj.exercise_types, list):
            # Crear lista con viñetas, cada elemento en una línea nueva
            items = [f"- {item}" for item in obj.exercise_types]
            return mark_safe("<br>".join(items))
        return "-"

    formatted_exercise_types.short_description = "Tipos de ejercicios"
    formatted_exercise_types.admin_order_field = "exercise_types"

    def formatted_duration(self, obj):
        """Formatea la duración en semanas"""
        if obj.duration:
            return f"{obj.duration} semana{'s' if obj.duration != 1 else ''}"
        return "-"

    formatted_duration.short_description = "Duración de la rutina"
    formatted_duration.admin_order_field = "duration"

    def formatted_created_at(self, obj):
        """Formatea la fecha de creación como DD/MM/YYYY HH:MM:SS"""
        if obj.created_at:
            return obj.created_at.strftime("%d/%m/%Y %H:%M:%S")
        return "-"

    formatted_created_at.short_description = "Fecha de creación"
    formatted_created_at.admin_order_field = "created_at"
    list_filter = ("created_at", "user")
    search_fields = ("user__username", "user__email")
    date_hierarchy = "created_at"
    ordering = ("-created_at",)
    filter_horizontal = ("exercises",)
    fieldsets = (
        (
            "Información básica",
            {
                "fields": ("user", "duration"),
            },
        ),
        (
            "Tipos de ejercicios",
            {
                "fields": ("exercise_types",),
                "description": "Selecciona los tipos de ejercicios para esta rutina",
            },
        ),
        (
            "Calentamiento",
            {
                "fields": ("warmup", "warmup_duration"),
            },
        ),
        (
            "Ejercicios",
            {
                "fields": ("exercises",),
            },
        ),
    )

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path(
                "generate-from-json/",
                self.admin_site.admin_view(RoutineJSONView.as_view()),
                name="gym_routine_generate_from_json",
            ),
        ]
        return custom_urls + urls

    def changelist_view(self, request, extra_context=None):
        extra_context = extra_context or {}
        extra_context["generate_json_url"] = "admin:gym_routine_generate_from_json"
        return super().changelist_view(request, extra_context=extra_context)


@admin.register(TrainingSession)
class TrainingSessionAdmin(UnfoldModelAdmin):
    form = TrainingSessionAdminForm
    list_display = (
        "user",
        "routine",
        "formatted_session_date",
        "location",
        "workout_time",
        "active_kilocalories",
        "total_kilocalories",
        "avg_heart_rate",
    )

    def formatted_session_date(self, obj):
        """Formatea la fecha de sesión como DD/MM/YYYY HH:MM:SS"""
        if obj.session_date:
            return obj.session_date.strftime("%d/%m/%Y %H:%M:%S")
        return "-"

    formatted_session_date.short_description = "Fecha y hora de la sesión"
    formatted_session_date.admin_order_field = "session_date"
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

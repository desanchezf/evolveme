from django.contrib import admin
from django.urls import path
from import_export.admin import ImportExportModelAdmin
from django.utils.safestring import mark_safe

from gym.models import (
    CardioExercise,
    CardioSession,
    MusculationExercise,
    MusculationRecord,
    Routine,
    RoutineDay,
    RoutineDayExercise,
    Session,
    TrainingSession,
)
from gym.views import MusculationRecordFormsetView, RoutineJSONView
from gym.forms import (
    CardioSessionAdminForm,
    RoutineAdminForm,
    TrainingSessionAdminForm,
    MusculationRecordAdminForm,
)


@admin.register(CardioExercise)
class CardioExerciseAdmin(ImportExportModelAdmin):
    list_display = ("formatted_name",)
    search_fields = ("name", "description")

    def formatted_name(self, obj):
        return obj.get_name_display() or obj.name

    formatted_name.short_description = "Nombre"
    formatted_name.admin_order_field = "name"
    fieldsets = (
        ("Información básica", {"fields": ("name", "description")}),
        ("Imagen", {"fields": ("image_base64",)}),
    )


@admin.register(CardioSession)
class CardioSessionAdmin(ImportExportModelAdmin):
    form = CardioSessionAdminForm
    list_display = (
        "user",
        "formatted_exercise",
        "formatted_date",
        "formatted_session_start",
        "formatted_session_end",
        "location",
        "workout_time",
        "distance",
        "avg_speed",
        "active_calories",
        "total_calories",
        "elevation_gain",
        "average_heart_rate",
    )

    def formatted_exercise(self, obj):
        if obj.exercise:
            return obj.exercise.get_name_display() or obj.exercise.name
        return "-"

    formatted_exercise.short_description = "Ejercicio"
    formatted_exercise.admin_order_field = "exercise__name"

    def formatted_date(self, obj):
        return obj.date.strftime("%d/%m/%Y") if obj.date else "-"

    formatted_date.short_description = "Fecha"
    formatted_date.admin_order_field = "date"

    def formatted_session_start(self, obj):
        return obj.session_start.strftime("%d/%m/%Y %H:%M:%S") if obj.session_start else "-"

    formatted_session_start.short_description = "Fecha y hora de inicio"
    formatted_session_start.admin_order_field = "session_start"

    def formatted_session_end(self, obj):
        return obj.session_end.strftime("%d/%m/%Y %H:%M:%S") if obj.session_end else "-"

    formatted_session_end.short_description = "Fecha y hora de fin"
    formatted_session_end.admin_order_field = "session_end"

    list_filter = ("exercise", "date", "user", "location")
    search_fields = ("user__username", "user__email", "exercise__name", "location")
    date_hierarchy = "date"
    ordering = ("-date", "-session_start")
    fieldsets = (
        ("Información básica", {"fields": ("user", "exercise", "date")}),
        ("Fecha y hora", {"fields": ("session_start", "session_end")}),
        ("Ubicación", {"fields": ("location",)}),
        (
            "Datos del entrenamiento",
            {"fields": ("workout_time", "distance", "avg_speed", "elevation_gain")},
        ),
        ("Calorías", {"fields": ("active_calories", "total_calories")}),
        ("Frecuencia cardíaca", {"fields": ("average_heart_rate",)}),
        ("Imagen del entrenamiento", {"fields": ("workout_image",)}),
    )


@admin.register(MusculationExercise)
class MusculationExerciseAdmin(ImportExportModelAdmin):
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
class MusculationRecordAdmin(ImportExportModelAdmin):
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


class RoutineDayExerciseInline(admin.TabularInline):
    model = RoutineDayExercise
    extra = 1
    fields = ("order", "exercise_name", "sets_reps", "notes", "exercise")
    ordering = ("order",)


class RoutineDayInline(admin.TabularInline):
    model = RoutineDay
    extra = 0
    fields = ("day_number", "name", "is_rest")
    ordering = ("day_number",)
    show_change_link = True


@admin.register(RoutineDay)
class RoutineDayAdmin(admin.ModelAdmin):
    list_display = ("routine", "day_number", "name", "is_rest")
    list_filter = ("routine", "is_rest")
    ordering = ("routine", "day_number")
    inlines = [RoutineDayExerciseInline]


@admin.register(Routine)
class RoutineAdmin(ImportExportModelAdmin):
    form = RoutineAdminForm
    inlines = [RoutineDayInline]
    list_display = (
        "user",
        "formatted_weekly_structure",
        "formatted_training_focus",
        "formatted_exercise_types",
        "formatted_duration",
        "formatted_created_at",
    )

    def formatted_exercise_types(self, obj):
        """Formatea los tipos de ejercicios como lista con viñetas"""
        if obj.exercise_types and isinstance(obj.exercise_types, list):
            # Crear lista con viñetas, cada elemento en una línea nueva
            items = [f"- {item}" for item in obj.exercise_types]
            return mark_safe("<br>".join(items))
        return "-"

    formatted_exercise_types.short_description = "Tipos de ejercicios"
    formatted_exercise_types.admin_order_field = "exercise_types"

    def formatted_weekly_structure(self, obj):
        return obj.get_weekly_structure_display() if obj.weekly_structure else "-"

    formatted_weekly_structure.short_description = "Estructura temporal"
    formatted_weekly_structure.admin_order_field = "weekly_structure"

    def formatted_training_focus(self, obj):
        return obj.get_training_focus_display() if obj.training_focus else "-"

    formatted_training_focus.short_description = "Enfoque"
    formatted_training_focus.admin_order_field = "training_focus"

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
    list_filter = ("created_at", "user", "weekly_structure", "training_focus")
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
            "Clasificación",
            {
                "fields": ("weekly_structure", "training_focus", "intensity_techniques"),
                "description": "Define estructura semanal, enfoque y técnicas de intensidad.",
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
class TrainingSessionAdmin(ImportExportModelAdmin):
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
        (
            "Imagen del entrenamiento",
            {
                "fields": ("workout_image",),
            },
        ),
    )


@admin.register(Session)
class SessionAdmin(ImportExportModelAdmin):
    list_display = (
        "user",
        "name",
        "date",
        "formatted_session_start",
        "location",
        "workout_time",
        "active_calories",
        "total_calories",
        "average_heart_rate",
    )

    def formatted_session_start(self, obj):
        return obj.session_start.strftime("%d/%m/%Y %H:%M") if obj.session_start else "-"

    formatted_session_start.short_description = "Inicio"
    formatted_session_start.admin_order_field = "session_start"

    list_filter = ("name", "date", "user")
    search_fields = ("user__username", "user__email", "location")
    date_hierarchy = "date"
    ordering = ("-date", "-session_start")
    fieldsets = (
        ("Información básica", {"fields": ("user", "name", "routine", "date")}),
        ("Fecha y hora", {"fields": ("session_start", "session_end")}),
        ("Ubicación", {"fields": ("location",)}),
        ("Datos", {"fields": ("workout_time", "distance", "avg_speed", "elevation_gain")}),
        ("Calorías", {"fields": ("active_calories", "total_calories")}),
        ("Frecuencia cardíaca", {"fields": ("average_heart_rate",)}),
        ("Imagen", {"fields": ("workout_image",)}),
    )

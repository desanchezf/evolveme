from django.contrib import admin
from import_export.admin import ImportExportModelAdmin

from cardio.models import CardioExercise, CardioSession
from cardio.forms import CardioSessionAdminForm


@admin.register(CardioExercise)
class CardioExerciseAdmin(ImportExportModelAdmin):
    list_display = ("formatted_name",)
    search_fields = ("name", "description")

    def formatted_name(self, obj):
        """Muestra el nombre del ejercicio en español"""
        return obj.get_name_display() or obj.name

    formatted_name.short_description = "Nombre"
    formatted_name.admin_order_field = "name"
    fieldsets = (
        (
            "Información básica",
            {
                "fields": ("name", "description"),
            },
        ),
        (
            "Imagen",
            {
                "fields": ("image_base64",),
            },
        ),
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
        """Muestra el nombre del ejercicio en español"""
        if obj.exercise:
            return obj.exercise.get_name_display() or obj.exercise.name
        return "-"

    formatted_exercise.short_description = "Ejercicio"
    formatted_exercise.admin_order_field = "exercise__name"

    def formatted_date(self, obj):
        """Formatea la fecha como DD/MM/YYYY"""
        if obj.date:
            return obj.date.strftime("%d/%m/%Y")
        return "-"

    formatted_date.short_description = "Fecha"
    formatted_date.admin_order_field = "date"

    def formatted_session_start(self, obj):
        """Formatea la fecha y hora de inicio como DD/MM/YYYY HH:MM:SS"""
        if obj.session_start:
            return obj.session_start.strftime("%d/%m/%Y %H:%M:%S")
        return "-"

    formatted_session_start.short_description = "Fecha y hora de inicio"
    formatted_session_start.admin_order_field = "session_start"

    def formatted_session_end(self, obj):
        """Formatea la fecha y hora de fin como DD/MM/YYYY HH:MM:SS"""
        if obj.session_end:
            return obj.session_end.strftime("%d/%m/%Y %H:%M:%S")
        return "-"

    formatted_session_end.short_description = "Fecha y hora de fin"
    formatted_session_end.admin_order_field = "session_end"
    list_filter = ("exercise", "date", "user", "location")
    search_fields = (
        "user__username",
        "user__email",
        "exercise__name",
        "location",
    )
    date_hierarchy = "date"
    ordering = ("-date", "-session_start")
    fieldsets = (
        (
            "Información básica",
            {
                "fields": ("user", "exercise", "date"),
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
        (
            "Imagen del entrenamiento",
            {
                "fields": ("workout_image",),
            },
        ),
    )

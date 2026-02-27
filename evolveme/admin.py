from django.contrib import admin
from unfold.admin import ModelAdmin as UnfoldModelAdmin

from evolveme.models import GymUserProfile, Measure
from evolveme.forms import GymUserProfileAdminForm, MeasureAdminForm


@admin.register(GymUserProfile)
class GymUserProfileAdmin(UnfoldModelAdmin):
    form = GymUserProfileAdminForm
    list_display = (
        "user",
        "formatted_birth_date",
        "gender",
        "height",
        "objective",
        "active_routine",
        "formatted_start_date",
        "formatted_end_date",
    )

    def formatted_birth_date(self, obj):
        """Formatea la fecha de nacimiento como DD/MM/YYYY"""
        if obj.birth_date:
            return obj.birth_date.strftime("%d/%m/%Y")
        return "-"

    formatted_birth_date.short_description = "Fecha de nacimiento"
    formatted_birth_date.admin_order_field = "birth_date"

    def formatted_start_date(self, obj):
        """Formatea la fecha de inicio como DD/MM/YYYY"""
        if obj.start_date:
            return obj.start_date.strftime("%d/%m/%Y")
        return "-"

    formatted_start_date.short_description = "Fecha de inicio"
    formatted_start_date.admin_order_field = "start_date"

    def formatted_end_date(self, obj):
        """Formatea la fecha de fin como DD/MM/YYYY"""
        if obj.end_date:
            return obj.end_date.strftime("%d/%m/%Y")
        return "-"

    formatted_end_date.short_description = "Fecha de fin"
    formatted_end_date.admin_order_field = "end_date"
    search_fields = (
        "user__username",
        "user__email",
        "user__first_name",
        "user__last_name",
    )
    list_filter = ("gender", "objective", "active_routine", "start_date", "end_date")
    date_hierarchy = "birth_date"
    ordering = ("-birth_date",)
    fieldsets = (
        (
            "Usuario",
            {
                "fields": ("user",),
            },
        ),
        (
            "Información personal",
            {
                "fields": ("birth_date", "gender", "height"),
            },
        ),
        (
            "Objetivos",
            {
                "fields": ("objective",),
            },
        ),
        (
            "Rutina activa",
            {
                "fields": ("active_routine", "start_date", "end_date"),
            },
        ),
    )


@admin.register(Measure)
class MeasureAdmin(UnfoldModelAdmin):
    form = MeasureAdminForm
    list_display = (
        "user",
        "formatted_date",
        "weight",
        "arm",
        "arm_relaxed",
        "chest",
        "waist",
        "leg",
        "leg_relaxed",
        "bmi",
        "fat_perc",
        "muscle_mass",
        "body_water_percentage",
        "visceral_fat_rating",
    )

    def formatted_date(self, obj):
        """Formatea la fecha como DD/MM/YYYY"""
        if obj.date:
            return obj.date.strftime("%d/%m/%Y")
        return "-"

    formatted_date.short_description = "Fecha"
    formatted_date.admin_order_field = "date"
    search_fields = (
        "user__username",
        "user__email",
        "user__first_name",
        "user__last_name",
    )
    list_filter = ("date", "user")
    date_hierarchy = "date"
    ordering = ("-date", "-user")
    fieldsets = (
        (
            "Información básica",
            {
                "fields": ("user", "date"),
            },
        ),
        (
            "Medidas corporales",
            {
                "fields": (
                    "weight",
                    "chest",
                    "waist",
                ),
            },
        ),
        (
            "Medidas de brazo",
            {
                "fields": (
                    "arm",
                    "arm_relaxed",
                ),
            },
        ),
        (
            "Medidas de pierna",
            {
                "fields": (
                    "leg",
                    "leg_relaxed",
                ),
            },
        ),
        (
            "Composición corporal básica",
            {
                "fields": (
                    "bmi",
                    "fat_perc",
                    "fat_mass",
                    "muscle_mass",
                    "muscle_percentage",
                    "skeletal_muscle_mass",
                ),
            },
        ),
        (
            "Agua y minerales",
            {
                "fields": (
                    "body_water_mass",
                    "body_water_percentage",
                    "bone_mineral_content",
                    "bone_mineral_percentage",
                ),
            },
        ),
        (
            "Proteína y otros",
            {
                "fields": (
                    "protein_mass",
                    "protein_percentage",
                    "fat_free_body_weight",
                ),
            },
        ),
        (
            "Métricas avanzadas",
            {
                "fields": (
                    "visceral_fat_rating",
                    "basal_metabolic_rate",
                    "waist_to_hip_ratio",
                    "body_age",
                ),
            },
        ),
    )

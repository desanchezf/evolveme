from django.contrib import admin
from unfold.admin import ModelAdmin as UnfoldModelAdmin

from evolveme.models import GymUserProfile, Measure


@admin.register(GymUserProfile)
class GymUserProfileAdmin(UnfoldModelAdmin):
    list_display = ("user", "birth_date", "gender", "height", "objective")
    search_fields = (
        "user__username",
        "user__email",
        "user__first_name",
        "user__last_name",
    )
    list_filter = ("gender", "objective")
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
    )


@admin.register(Measure)
class MeasureAdmin(UnfoldModelAdmin):
    list_display = (
        "user",
        "date",
        "weight",
        "bmi",
        "fat_perc",
        "muscle_mass",
        "body_water_percentage",
        "visceral_fat_rating",
    )
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
                    "arm",
                    "chest",
                    "waist",
                    "leg",
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

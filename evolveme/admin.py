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
        "arm",
        "chest",
        "waist",
        "leg",
        "fat_perc",
        "muscle_mass",
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
            "Composición corporal",
            {
                "fields": (
                    "fat_perc",
                    "muscle_mass",
                ),
            },
        ),
    )

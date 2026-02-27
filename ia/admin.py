from django.contrib import admin

from ia.models import Promtps


@admin.register(Promtps)
class PromtpsAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "created_at",
        "updated_at",
    )
    list_filter = ("created_at", "updated_at")
    search_fields = ("name", "prompt")
    date_hierarchy = "created_at"
    ordering = ("-created_at",)
    fieldsets = (
        (
            "Información básica",
            {
                "fields": ("name",),
            },
        ),
        (
            "Contenido",
            {
                "fields": ("prompt",),
            },
        ),
        (
            "Información del sistema",
            {
                "fields": ("created_at", "updated_at"),
                "classes": ("collapse",),
            },
        ),
    )
    readonly_fields = ("created_at", "updated_at")

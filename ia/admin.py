from django.contrib import admin

from ia.models import (
    ChatMessage,
    ChatSession,
    OllamaModelConfig,
    OllamaServer,
    Promtps,
)


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


@admin.register(OllamaServer)
class OllamaServerAdmin(admin.ModelAdmin):
    list_display = ("name", "base_url", "enabled", "created_at")
    list_filter = ("enabled",)
    search_fields = ("name", "base_url")
    ordering = ("name",)
    fieldsets = (
        (
            "Configuración",
            {"fields": ("name", "base_url", "enabled", "api_key")},
        ),
        (
            "Sistema",
            {"fields": ("created_at", "updated_at"), "classes": ("collapse",)},
        ),
    )
    readonly_fields = ("created_at", "updated_at")


@admin.register(OllamaModelConfig)
class OllamaModelConfigAdmin(admin.ModelAdmin):
    list_display = ("alias", "server", "model_name", "is_default", "deprecated", "created_at")
    list_filter = ("server", "is_default", "deprecated")
    search_fields = ("alias", "model_name")
    ordering = ("server", "alias")
    raw_id_fields = ("server",)
    fieldsets = (
        (
            "Servidor y modelo",
            {"fields": ("server", "model_name", "alias", "description")},
        ),
        (
            "Parámetros de inferencia",
            {"fields": ("temperature", "top_p", "max_tokens")},
        ),
        (
            "Uso",
            {"fields": ("is_default", "deprecated", "deprecated_at")},
        ),
        (
            "Sistema",
            {"fields": ("created_at", "updated_at"), "classes": ("collapse",)},
        ),
    )
    readonly_fields = ("created_at", "updated_at")


class ChatMessageInline(admin.TabularInline):
    model = ChatMessage
    extra = 0
    readonly_fields = ("created_at",)
    ordering = ("created_at",)


@admin.register(ChatSession)
class ChatSessionAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "model_key", "created_at", "updated_at")
    list_filter = ("created_at", "updated_at")
    search_fields = ("user__username", "model_key")
    ordering = ("-updated_at",)
    inlines = [ChatMessageInline]
    readonly_fields = ("created_at", "updated_at")


@admin.register(ChatMessage)
class ChatMessageAdmin(admin.ModelAdmin):
    list_display = ("id", "session", "role", "content_preview", "created_at")
    list_filter = ("role",)
    search_fields = ("content",)
    ordering = ("session", "created_at")
    raw_id_fields = ("session",)
    readonly_fields = ("created_at",)

    def content_preview(self, obj):
        return (obj.content[:60] + "...") if len(obj.content) > 60 else obj.content

    content_preview.short_description = "Contenido"

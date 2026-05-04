from django.contrib import admin
from django.urls import reverse
from import_export.admin import ImportExportModelAdmin
from django.utils.html import format_html
from django.utils.translation import gettext_lazy as _

from ia.models import (
    ChatMessage,
    ChatSession,
    OllamaModelConfig,
    OllamaServer,
    Promtps,
)


@admin.register(Promtps)
class PromtpsAdmin(ImportExportModelAdmin):
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
class OllamaServerAdmin(ImportExportModelAdmin):
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
class OllamaModelConfigAdmin(ImportExportModelAdmin):
    list_display = (
        "alias",
        "server",
        "model_name",
        "proposito",
        "is_default",
        "deprecated",
        "downloaded",
        "update_available",
        "pull_action",
        "created_at",
    )
    list_filter = ("server", "is_default", "deprecated", "downloaded", "update_available")
    search_fields = ("alias", "model_name", "proposito")
    ordering = ("server", "alias")
    raw_id_fields = ("server",)
    readonly_fields = (
        "created_at",
        "updated_at",
        "downloaded",
        "digest",
        "last_checked_at",
        "update_available",
    )
    fieldsets = (
        (
            "Servidor y modelo",
            {"fields": ("server", "model_name", "alias", "proposito", "description")},
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
            _("Estado"),
            {
                "fields": ("downloaded", "digest", "last_checked_at", "update_available"),
                "description": _("Actualizado por la tarea en segundo plano y al pulsar Actualizar."),
            },
        ),
        (
            "Sistema",
            {"fields": ("created_at", "updated_at"), "classes": ("collapse",)},
        ),
    )

    @admin.action(description=_("Descargar/actualizar modelos seleccionados"))
    def download_models(self, request, queryset):
        from django.utils import timezone
        from ia.services import check_model_on_server, pull_model_on_server

        ok_count = 0
        fail_count = 0
        for config in queryset:
            ok, err = pull_model_on_server(config.server, config.model_name)
            if ok:
                downloaded, digest = check_model_on_server(config.server, config.model_name)
                config.downloaded = downloaded
                config.digest = digest
                config.last_checked_at = timezone.now()
                config.update_available = not downloaded
                config.save(update_fields=[
                    "downloaded", "digest", "last_checked_at",
                    "update_available", "updated_at",
                ])
                ok_count += 1
            else:
                fail_count += 1
                self.message_user(
                    request,
                    f"Error al descargar '{config.model_name}': {err}",
                    level="error",
                )
        if ok_count:
            self.message_user(
                request,
                f"{ok_count} modelo(s) descargado(s) o actualizados correctamente.",
            )

    actions = ["download_models"]

    def pull_action(self, obj):
        url = reverse("ia:ollama_model_pull", args=[obj.pk])
        if not obj.downloaded:
            label = _("Descargar")
        elif obj.update_available:
            label = _("Actualizar")
        else:
            return "—"
        return format_html('<a class="button" href="{}">{}</a>', url, label)

    pull_action.short_description = _("Acción")


class ChatMessageInline(admin.TabularInline):
    model = ChatMessage
    extra = 0
    readonly_fields = ("created_at",)
    ordering = ("created_at",)


@admin.register(ChatSession)
class ChatSessionAdmin(ImportExportModelAdmin):
    list_display = ("id", "user", "model_key", "created_at", "updated_at")
    list_filter = ("created_at", "updated_at")
    search_fields = ("user__username", "model_key")
    ordering = ("-updated_at",)
    inlines = [ChatMessageInline]
    readonly_fields = ("created_at", "updated_at")


@admin.register(ChatMessage)
class ChatMessageAdmin(ImportExportModelAdmin):
    list_display = ("id", "session", "role", "content_preview", "created_at")
    list_filter = ("role",)
    search_fields = ("content",)
    ordering = ("session", "created_at")
    raw_id_fields = ("session",)
    readonly_fields = ("created_at",)

    def content_preview(self, obj):
        return (obj.content[:60] + "...") if len(obj.content) > 60 else obj.content

    content_preview.short_description = "Contenido"

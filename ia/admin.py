from django.contrib import admin
from django.urls import reverse
from import_export.admin import ImportExportModelAdmin
from django.utils.html import format_html, mark_safe
from django.utils.translation import gettext_lazy as _

from ia.models import (
    ChatMessage,
    ChatSession,
    OllamaModelConfig,
    OllamaServer,
    Promtps,
    UserModelPrompt,
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
        "downloaded_display",
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
        "pull_progress",
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
                "fields": (
                    "downloaded", "digest", "last_checked_at",
                    "update_available", "pull_progress",
                ),
                "description": _("Actualizado automáticamente al descargar o actualizar."),
            },
        ),
        (
            "Sistema",
            {"fields": ("created_at", "updated_at"), "classes": ("collapse",)},
        ),
    )

    @admin.action(description=_("Descargar/actualizar modelos seleccionados en segundo plano"))
    def download_models(self, request, queryset):
        import threading
        from django.utils import timezone
        from django.db import connection

        started = []
        for config in queryset.filter(pull_progress__isnull=True):
            config.__class__.objects.filter(pk=config.pk).update(pull_progress=0)
            pk = config.pk
            server = config.server
            model_name = config.model_name

            def do_pull(pk=pk, server=server, model_name=model_name):
                connection.close()
                from ia.models import OllamaModelConfig as M
                from ia.services import check_model_on_server, pull_model_on_server

                def on_progress(pct):
                    M.objects.filter(pk=pk).update(pull_progress=pct)

                ok, _err = pull_model_on_server(server, model_name, progress_callback=on_progress)
                if ok:
                    downloaded, digest = check_model_on_server(server, model_name)
                    M.objects.filter(pk=pk).update(
                        downloaded=downloaded,
                        digest=digest,
                        last_checked_at=timezone.now(),
                        update_available=not downloaded,
                        pull_progress=None,
                    )
                else:
                    M.objects.filter(pk=pk).update(pull_progress=None)

            threading.Thread(target=do_pull, daemon=True).start()
            started.append(model_name)

        if started:
            self.message_user(
                request,
                f"Descarga iniciada en segundo plano para: {', '.join(started)}. "
                "La página se actualizará automáticamente.",
            )
        else:
            self.message_user(request, "No hay modelos nuevos para descargar.", level="warning")

    @admin.action(description=_("Borrar modelos seleccionados del servidor Ollama"))
    def delete_models(self, request, queryset):
        from ia.services import delete_model_on_server

        ok_count = 0
        for config in queryset.filter(downloaded=True):
            ok, err = delete_model_on_server(config.server, config.model_name)
            if ok:
                config.__class__.objects.filter(pk=config.pk).update(
                    downloaded=False, digest="", update_available=False
                )
                ok_count += 1
            else:
                self.message_user(
                    request,
                    f"Error al borrar '{config.model_name}': {err}",
                    level="error",
                )
        if ok_count:
            self.message_user(
                request,
                f"{ok_count} modelo(s) eliminado(s) del servidor correctamente.",
            )

    actions = ["download_models", "delete_models"]

    class Media:
        css = {"all": ("ia/admin_pull_progress.css",)}
        js = ("ia/admin_pull_progress.js",)

    def downloaded_display(self, obj):
        if obj.pull_progress is not None:
            progress_url = reverse("ia:ollama_model_pull_progress", args=[obj.pk])
            return format_html(
                '<div data-pull-pk="{pk}" data-progress-url="{url}" class="pull-bar-container">'
                '<div class="pull-bar-track"><div class="pull-bar-fill" style="width:{pct}%"></div></div>'
                '<span class="pull-bar-label">{pct}%</span>'
                "</div>",
                pk=obj.pk,
                url=progress_url,
                pct=obj.pull_progress,
            )
        if obj.downloaded:
            return mark_safe('<span style="color:#28a745;font-weight:600">&#10003; Sí</span>')
        return mark_safe('<span style="color:#dc3545">&#10007; No</span>')

    downloaded_display.short_description = _("Descargado")
    downloaded_display.allow_tags = True

    def pull_action(self, obj):
        if obj.pull_progress is not None:
            return mark_safe('<span class="text-muted">Descargando…</span>')

        buttons = []
        start_url = reverse("ia:ollama_model_pull_start", args=[obj.pk])
        progress_url = reverse("ia:ollama_model_pull_progress", args=[obj.pk])

        if not obj.downloaded:
            buttons.append(format_html(
                '<button class="button pull-btn" data-start-url="{}" data-progress-url="{}" data-pk="{}">{}</button>',
                start_url, progress_url, obj.pk, _("Descargar"),
            ))
        else:
            if obj.update_available:
                buttons.append(format_html(
                    '<button class="button pull-btn" data-start-url="{}" data-progress-url="{}" data-pk="{}">{}</button>',
                    start_url, progress_url, obj.pk, _("Actualizar"),
                ))
            delete_url = reverse("ia:ollama_model_delete", args=[obj.pk])
            buttons.append(format_html(
                '<button class="button pull-btn pull-btn--danger" data-delete-url="{}">{}</button>',
                delete_url, _("Borrar"),
            ))

        if not buttons:
            return "—"
        return mark_safe(" ".join(str(b) for b in buttons))

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


@admin.register(UserModelPrompt)
class UserModelPromptAdmin(admin.ModelAdmin):
    list_display = ("user", "model_config", "generated_at")
    list_filter = ("model_config",)
    search_fields = ("user__username",)
    ordering = ("user", "model_config")
    readonly_fields = ("generated_at", "prompt_text")

    @admin.action(description=_("Regenerar prompt para los usuarios seleccionados"))
    def regenerate_prompts(self, request, queryset):
        from ia.services import build_user_prompt

        count = 0
        for obj in queryset:
            obj.prompt_text = build_user_prompt(obj.user)
            obj.save(update_fields=["prompt_text", "generated_at"])
            count += 1
        self.message_user(request, f"{count} prompt(s) regenerado(s) correctamente.")

    actions = ["regenerate_prompts"]

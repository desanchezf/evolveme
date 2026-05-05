import json
import threading

from django.contrib.admin.views.decorators import staff_member_required
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_http_methods

from ia.models import ChatMessage, ChatSession, OllamaModelConfig
from ia.services import (
    chat_with_ollama,
    check_model_on_server,
    is_model_downloaded,
    pull_model_on_server,
)
from project.admin_context import with_admin_context


@login_required
def chat_view(request):
    """Vista de la ventana de chat con IA. Carga o crea una sesión y sus mensajes."""
    session = (
        ChatSession.objects.filter(user=request.user)
        .order_by("-updated_at")
        .first()
    )
    if not session:
        session = ChatSession.objects.create(user=request.user)
    chat_messages = list(session.messages.all().order_by("created_at"))
    return render(
        request,
        "ia/chat.html",
        with_admin_context(request, {
            "chat_session": session,
            "chat_messages": chat_messages,
            "chat_available": is_model_downloaded("qwen3:1.7b"),
        }),
    )


@login_required
@require_http_methods(["POST"])
def chat_send_view(request):
    """Recibe un mensaje del usuario, lo guarda y devuelve la respuesta del asistente (por ahora placeholder)."""
    try:
        data = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse({"error": "JSON inválido"}, status=400)
    content = (data.get("content") or "").strip()
    session_id = data.get("session_id")
    model_key = "qwen3:1.7b"
    if not content:
        return JsonResponse({"error": "Mensaje vacío"}, status=400)
    if session_id:
        session = get_object_or_404(
            ChatSession, pk=session_id, user=request.user
        )
    else:
        session = ChatSession.objects.create(user=request.user)
        session_id = session.pk
    if model_key:
        session.model_key = model_key
        session.save(update_fields=["model_key", "updated_at"])
    ChatMessage.objects.create(
        session=session, role=ChatMessage.ROLE_USER, content=content
    )

    assistant_content, err = chat_with_ollama(session, model_key)
    is_error = bool(err)

    if err:
        if err == "timeout":
            assistant_content = "El servidor Ollama tardó demasiado en responder. Inténtalo de nuevo."
        elif err == "connection":
            assistant_content = "No se pudo conectar con el servidor Ollama. Comprueba que esté en ejecución."
        elif err.startswith("model_not_found:"):
            model_name = err.split(":", 1)[1]
            assistant_content = (
                f"El modelo «{model_name}» no está descargado en el servidor Ollama. "
                "Descárgalo desde el panel de Modelos Ollama."
            )
            OllamaModelConfig.objects.filter(model_name=model_name).update(downloaded=False)
        else:
            assistant_content = "El servidor Ollama devolvió un error inesperado. Inténtalo de nuevo."

    if not assistant_content:
        assistant_content = "El modelo no devolvió ninguna respuesta."
        is_error = True

    ChatMessage.objects.create(
        session=session,
        role=ChatMessage.ROLE_ASSISTANT,
        content=assistant_content,
    )
    return JsonResponse({
        "content": assistant_content,
        "session_id": session.pk,
        "is_error": is_error,
    })


@staff_member_required
def ollama_model_pull_view(request, pk):
    """GET: confirmación. POST: lanza descarga/actualización del modelo Ollama."""
    from django.utils import timezone
    from django.template.response import TemplateResponse

    config = get_object_or_404(OllamaModelConfig, pk=pk)

    if request.method != "POST":
        return TemplateResponse(
            request,
            "admin/ia/ollamamodelconfig/confirm_pull.html",
            {"config": config, "opts": OllamaModelConfig._meta},
        )

    ok, err = pull_model_on_server(config.server, config.model_name)
    if ok:
        downloaded, digest = check_model_on_server(config.server, config.model_name)
        config.downloaded = downloaded
        config.digest = digest
        config.last_checked_at = timezone.now()
        config.update_available = not downloaded
        config.save(update_fields=[
            "downloaded", "digest", "last_checked_at", "update_available", "updated_at"
        ])
        messages.success(
            request,
            f"Modelo '{config.model_name}' descargado o actualizado correctamente.",
        )
    else:
        messages.error(request, f"Error al actualizar el modelo: {err}")
    return redirect("admin:ia_ollamamodelconfig_changelist")


@staff_member_required
@require_http_methods(["POST"])
def ollama_model_delete_view(request, pk):
    """Elimina el modelo del servidor Ollama y actualiza el registro."""
    from ia.services import delete_model_on_server

    config = get_object_or_404(OllamaModelConfig, pk=pk)
    ok, err = delete_model_on_server(config.server, config.model_name)
    if ok:
        OllamaModelConfig.objects.filter(pk=pk).update(
            downloaded=False, digest="", update_available=False
        )
        return JsonResponse({"deleted": True})
    return JsonResponse({"deleted": False, "error": err}, status=500)


@staff_member_required
@require_http_methods(["POST"])
def ollama_model_pull_start_view(request, pk):
    """Inicia la descarga en segundo plano y devuelve JSON inmediatamente."""
    from django.utils import timezone
    from django.db import connection

    config = get_object_or_404(OllamaModelConfig, pk=pk)

    if config.pull_progress is not None:
        return JsonResponse({"started": False, "reason": "already_running"})

    OllamaModelConfig.objects.filter(pk=pk).update(pull_progress=0)

    server_id = config.server_id
    model_name = config.model_name

    def do_pull():
        connection.close()
        from ia.models import OllamaModelConfig as M
        from ia.services import check_model_on_server, pull_model_on_server

        server_obj = M.objects.select_related("server").get(pk=pk).server

        def on_progress(pct):
            M.objects.filter(pk=pk).update(pull_progress=pct)

        ok, _err = pull_model_on_server(server_obj, model_name, progress_callback=on_progress)
        if ok:
            downloaded, digest = check_model_on_server(server_obj, model_name)
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
    return JsonResponse({"started": True})


@staff_member_required
def ollama_model_pull_progress_view(request, pk):
    """Devuelve JSON con el progreso actual de descarga de un modelo."""
    config = get_object_or_404(OllamaModelConfig, pk=pk)
    return JsonResponse({
        "progress": config.pull_progress,
        "downloaded": config.downloaded,
    })

import json

from django.contrib.admin.views.decorators import staff_member_required
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_http_methods

from ia.models import ChatMessage, ChatSession, OllamaModelConfig
from ia.services import chat_with_ollama, check_model_on_server, pull_model_on_server


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
    messages = list(session.messages.all().order_by("created_at"))
    return render(
        request,
        "ia/chat.html",
        {"chat_session": session, "chat_messages": messages},
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
    model_key = (data.get("model_key") or "").strip()
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
    if err:
        assistant_content = f"No se pudo obtener respuesta del modelo: {err}"
    if not assistant_content:
        assistant_content = "El modelo no devolvió ninguna respuesta."

    ChatMessage.objects.create(
        session=session,
        role=ChatMessage.ROLE_ASSISTANT,
        content=assistant_content,
    )
    return JsonResponse({"content": assistant_content, "session_id": session.pk})


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

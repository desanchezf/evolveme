import json

from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, render
from django.views.decorators.http import require_http_methods

from ia.models import ChatMessage, ChatSession
from ia.services import chat_with_ollama


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

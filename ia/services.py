"""
Servicio para el CHAT con IA. Usa un modelo de lenguaje (p. ej. qwen3:8b).
Para extracción de datos desde imágenes (Cardio, Entrenamiento, Producto)
se usa otro modelo de visión (llama3.2-vision:11b) en cardio/gym/nutrition services.
"""
try:
    import requests
except ImportError:
    requests = None


def _get_ollama_server():
    """Devuelve el primer servidor Ollama habilitado, o None."""
    from ia.models import OllamaServer
    return OllamaServer.objects.filter(enabled=True).first()


def chat_with_ollama(session, model_key):
    """
    Envía el historial de la sesión (incluido el último mensaje del usuario ya guardado)
    a Ollama y devuelve el contenido de la respuesta del asistente.
    session: ChatSession con .messages (queryset ordenado por created_at).
    model_key: nombre del modelo de CHAT en Ollama (p. ej. "qwen3:8b"). No usar modelo de visión aquí.
    Devuelve (content, error). Si error no es None, content puede ser un mensaje de fallback.
    """
    if not requests:
        return None, "Falta la dependencia 'requests'."

    server = _get_ollama_server()
    if not server:
        return None, "No hay ningún servidor Ollama configurado o habilitado."

    model = (model_key or "qwen3:8b").strip() or "qwen3:8b"

    # El historial ya incluye el mensaje del usuario recién guardado en la vista
    messages = [
        {"role": msg.role, "content": msg.content or ""}
        for msg in session.messages.all().order_by("created_at")
    ]

    url = f"{server.base_url.rstrip('/')}/api/chat"
    payload = {
        "model": model,
        "messages": messages,
        "stream": False,
    }
    headers = {}
    if server.api_key:
        headers["Authorization"] = f"Bearer {server.api_key}"

    try:
        resp = requests.post(url, json=payload, headers=headers or None, timeout=120)
        resp.raise_for_status()
        data = resp.json()
        message = data.get("message")
        if message and isinstance(message.get("content"), str):
            return message["content"].strip(), None
        return None, "La respuesta de Ollama no incluyó contenido."
    except requests.exceptions.Timeout:
        return None, "El servidor Ollama tardó demasiado en responder."
    except requests.exceptions.ConnectionError:
        return None, "No se pudo conectar con el servidor Ollama. Comprueba que esté en ejecución."
    except requests.exceptions.HTTPError as e:
        return None, f"Error del servidor Ollama: {e.response.status_code if e.response else str(e)}"
    except Exception as e:
        return None, str(e)


def fetch_ollama_tags(server):
    """GET /api/tags del servidor. Devuelve (data, error)."""
    if not requests:
        return None, "Falta 'requests'."
    url = f"{server.base_url.rstrip('/')}/api/tags"
    headers = {}
    if server.api_key:
        headers["Authorization"] = f"Bearer {server.api_key}"
    try:
        resp = requests.get(url, headers=headers or None, timeout=15)
        resp.raise_for_status()
        return resp.json(), None
    except Exception as e:
        return None, str(e)


def check_model_on_server(server, model_name):
    """
    Comprueba si el modelo está en el servidor y devuelve su digest.
    Devuelve (downloaded: bool, digest: str).
    """
    data, err = fetch_ollama_tags(server)
    if err:
        return False, ""
    models = data.get("models") or []
    for m in models:
        name = m.get("name") or m.get("model") or ""
        if name == model_name or name.startswith(model_name + ":"):
            return True, (m.get("digest") or "")[:64]
    return False, ""


def pull_model_on_server(server, model_name):
    """Lanza la descarga del modelo en Ollama (POST /api/pull). Devuelve (ok, error)."""
    if not requests:
        return False, "Falta 'requests'."
    url = f"{server.base_url.rstrip('/')}/api/pull"
    headers = {}
    if server.api_key:
        headers["Authorization"] = f"Bearer {server.api_key}"
    try:
        resp = requests.post(
            url, json={"name": model_name}, headers=headers or None, timeout=300
        )
        resp.raise_for_status()
        return True, None
    except Exception as e:
        return False, str(e)

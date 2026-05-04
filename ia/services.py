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
        return None, "timeout"
    except requests.exceptions.ConnectionError:
        return None, "connection"
    except requests.exceptions.HTTPError as e:
        code = getattr(e.response, "status_code", None)
        if code is None:
            raw = str(e)
            if "404" in raw:
                code = 404
            elif "500" in raw:
                code = 500
        if code == 404:
            return None, f"model_not_found:{model}"
        return None, f"http_error:{code or str(e)}"
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


def is_model_downloaded(model_name):
    """Devuelve True si el modelo está marcado como descargado en algún servidor habilitado."""
    from ia.models import OllamaModelConfig
    return OllamaModelConfig.objects.filter(
        model_name=model_name,
        downloaded=True,
        server__enabled=True,
    ).exists()


def pull_model_on_server(server, model_name, progress_callback=None):
    """
    Descarga el modelo en Ollama (POST /api/pull) con streaming de progreso.
    progress_callback(pct: int) se llama con 0-100 durante la descarga.
    Devuelve (ok, error).
    """
    import json as _json

    if not requests:
        return False, "Falta 'requests'."
    url = f"{server.base_url.rstrip('/')}/api/pull"
    headers = {}
    if server.api_key:
        headers["Authorization"] = f"Bearer {server.api_key}"
    try:
        resp = requests.post(
            url,
            json={"name": model_name, "stream": True},
            headers=headers or None,
            stream=True,
            timeout=600,
        )
        resp.raise_for_status()

        status_pct = {
            "pulling manifest": 2,
            "verifying sha256 digest": 92,
            "writing manifest": 96,
            "removing any unused layers": 98,
            "success": 100,
        }

        for raw_line in resp.iter_lines():
            if not raw_line:
                continue
            try:
                data = _json.loads(raw_line)
            except ValueError:
                continue
            status = data.get("status", "")
            total = data.get("total")
            completed = data.get("completed")
            if total and completed:
                pct = max(5, min(90, int(completed / total * 85) + 5))
            elif status in status_pct:
                pct = status_pct[status]
            else:
                continue
            if progress_callback:
                progress_callback(pct)

        return True, None
    except Exception as e:
        return False, str(e)

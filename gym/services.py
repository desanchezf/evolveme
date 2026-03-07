"""
Servicio de extracción de datos de sesión de entrenamiento desde una imagen usando LLM con visión.
"""
import base64
import json
import re
from datetime import timedelta

try:
    import requests
except ImportError:
    requests = None

# Modelo solo para IMÁGENES (OCR/detección). El chat usa otro modelo (qwen3:8b) en ia/services.
VISION_MODEL = "llama3.2-vision:11b"  # ollama pull llama3.2-vision:11b


def _get_ollama_server():
    """Devuelve el primer servidor Ollama habilitado, o None."""
    from ia.models import OllamaServer
    return OllamaServer.objects.filter(enabled=True).first()


def _encode_image(file) -> str:
    """Lee el archivo de imagen y devuelve base64."""
    file.seek(0)
    return base64.b64encode(file.read()).decode("utf-8")


def _parse_llm_json(response_text: str) -> dict:
    """Extrae un objeto JSON del texto de respuesta (puede venir en markdown)."""
    text = (response_text or "").strip()
    match = re.search(r"```(?:json)?\s*([\s\S]*?)\s*```", text)
    if match:
        text = match.group(1).strip()
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        return {}


def extract_training_session_data_from_image(image_files) -> dict:
    """
    Envía una o varias imágenes al LLM con visión (Ollama) y devuelve un diccionario
    con los campos que se puedan mapear al modelo TrainingSession.
    image_files: archivo único o lista de archivos.
    Si no hay servidor/configuración o falla la llamada, devuelve {}.
    """
    if not requests:
        return {}

    server = _get_ollama_server()
    if not server:
        return {}

    if not hasattr(image_files, "__iter__") or isinstance(image_files, (str, bytes)):
        image_files = [image_files]
    images_b64 = []
    for f in image_files:
        try:
            images_b64.append(_encode_image(f))
            f.seek(0)
        except Exception:
            pass
    if not images_b64:
        return {}

    prompt = (
        "Analiza esta(s) imagen(es) de una sesión de entrenamiento (captura de reloj, app de fitness, etc.). "
        "Devuelve ÚNICAMENTE un JSON válido, sin texto adicional ni markdown, con estas claves "
        "(usa null para lo que no detectes): "
        "session_date (ISO 8601, p.ej. 2025-02-27T10:30:00), location (texto), "
        "workout_time_seconds (número entero), active_kilocalories (número entero), "
        "total_kilocalories (número entero), avg_heart_rate (número entero)."
    )

    url = f"{server.base_url.rstrip('/')}/api/generate"
    payload = {
        "model": VISION_MODEL,
        "prompt": prompt,
        "images": images_b64,
        "stream": False,
    }
    headers = {}
    if server.api_key:
        headers["Authorization"] = f"Bearer {server.api_key}"

    try:
        resp = requests.post(url, json=payload, headers=headers or None, timeout=60)
        resp.raise_for_status()
        data = resp.json()
        response_text = data.get("response") or ""
        raw = _parse_llm_json(response_text)
    except Exception:
        return {}

    result = {}
    if raw.get("session_date"):
        result["session_date"] = raw["session_date"]
    if raw.get("location"):
        result["location"] = str(raw["location"])[:255]
    if raw.get("workout_time_seconds") is not None:
        result["workout_time"] = timedelta(seconds=int(raw["workout_time_seconds"]))
    if raw.get("active_kilocalories") is not None:
        result["active_kilocalories"] = int(raw["active_kilocalories"])
    if raw.get("total_kilocalories") is not None:
        result["total_kilocalories"] = int(raw["total_kilocalories"])
    if raw.get("avg_heart_rate") is not None:
        result["avg_heart_rate"] = int(raw["avg_heart_rate"])

    return result

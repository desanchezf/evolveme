"""
Servicio de extracción de datos de sesión de cardio desde una imagen usando LLM con visión.
"""
import base64
import json
import re
from datetime import timedelta

try:
    import requests
except ImportError:
    requests = None

# Modelo de visión por defecto en Ollama (debe estar instalado: ollama pull llava)
DEFAULT_VISION_MODEL = "llava"


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
    # Quitar posibles bloques ```json ... ```
    match = re.search(r"```(?:json)?\s*([\s\S]*?)\s*```", text)
    if match:
        text = match.group(1).strip()
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        return {}


def extract_cardio_data_from_image(image_files) -> dict:
    """
    Envía una o varias imágenes al LLM con visión (Ollama) y devuelve un diccionario
    con los campos que se puedan mapear al modelo CardioSession.
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
        "Analiza esta(s) imagen(es) de un entrenamiento de cardio (captura de reloj, app de fitness, etc.). "
        "Devuelve ÚNICAMENTE un JSON válido, sin texto adicional ni markdown, con estas claves "
        "(usa null para lo que no detectes): "
        "date (YYYY-MM-DD), exercise (uno de: Outdoor Walk, Indoor Walk, Outdoor Cycle, Indoor Cycle, Elliptical), "
        "workout_time_seconds (número entero), distance_km (número), avg_speed_kmh (número), "
        "active_calories (número entero), total_calories (número entero), elevation_gain_m (número entero), "
        "average_heart_rate (número entero), location (texto)."
    )

    url = f"{server.base_url.rstrip('/')}/api/generate"
    payload = {
        "model": DEFAULT_VISION_MODEL,
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

    # Mapear al formato que usa el formulario / modelo
    result = {}
    if raw.get("date"):
        result["date"] = raw["date"]
    if raw.get("exercise") in (
        "Outdoor Walk", "Indoor Walk", "Outdoor Cycle", "Indoor Cycle", "Elliptical"
    ):
        from cardio.models import CardioExercise
        ex = CardioExercise.objects.filter(name=raw["exercise"]).first()
        if ex:
            result["exercise"] = ex.pk
    if raw.get("workout_time_seconds") is not None:
        result["workout_time"] = timedelta(seconds=int(raw["workout_time_seconds"]))
    if raw.get("distance_km") is not None:
        result["distance"] = float(raw["distance_km"])
    if raw.get("avg_speed_kmh") is not None:
        result["avg_speed"] = float(raw["avg_speed_kmh"])
    if raw.get("active_calories") is not None:
        result["active_calories"] = int(raw["active_calories"])
    if raw.get("total_calories") is not None:
        result["total_calories"] = int(raw["total_calories"])
    if raw.get("elevation_gain_m") is not None:
        result["elevation_gain"] = int(raw["elevation_gain_m"])
    if raw.get("average_heart_rate") is not None:
        result["average_heart_rate"] = int(raw["average_heart_rate"])
    if raw.get("location"):
        result["location"] = str(raw["location"])[:255]

    return result

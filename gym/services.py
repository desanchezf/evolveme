"""
Servicios de extracción de datos desde imágenes usando LLM con visión (Ollama).
Cubre sesiones de entrenamiento (musculación) y sesiones de cardio.
"""
import base64
import json
import re
from datetime import timedelta

try:
    import requests
except ImportError:
    requests = None

# Modelo de visión para OCR/detección en imágenes.
VISION_MODEL = "llama3.2-vision:11b"  # ollama pull llama3.2-vision:11b


def _get_ollama_server():
    from ia.models import OllamaServer
    return OllamaServer.objects.filter(enabled=True).first()


def _encode_image(file) -> str:
    file.seek(0)
    return base64.b64encode(file.read()).decode("utf-8")


def _parse_llm_json(response_text: str) -> dict:
    text = (response_text or "").strip()
    match = re.search(r"```(?:json)?\s*([\s\S]*?)\s*```", text)
    if match:
        text = match.group(1).strip()
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        return {}


def _call_ollama(server, prompt: str, images_b64: list) -> dict:
    url = f"{server.base_url.rstrip('/')}/api/generate"
    payload = {"model": VISION_MODEL, "prompt": prompt, "images": images_b64, "stream": False}
    headers = {"Authorization": f"Bearer {server.api_key}"} if server.api_key else {}
    try:
        resp = requests.post(url, json=payload, headers=headers or None, timeout=60)
        resp.raise_for_status()
        return _parse_llm_json(resp.json().get("response") or "")
    except Exception:
        return {}


def _encode_files(image_files) -> list:
    if not hasattr(image_files, "__iter__") or isinstance(image_files, (str, bytes)):
        image_files = [image_files]
    images_b64 = []
    for f in image_files:
        try:
            images_b64.append(_encode_image(f))
            f.seek(0)
        except Exception:
            pass
    return images_b64


def extract_cardio_data_from_image(image_files) -> dict:
    """
    Envía imágenes al LLM con visión y devuelve campos mapeados a CardioSession.
    Devuelve {} si no hay servidor o falla la llamada.
    """
    if not requests:
        return {}
    server = _get_ollama_server()
    if not server:
        return {}
    images_b64 = _encode_files(image_files)
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
    raw = _call_ollama(server, prompt, images_b64)

    result = {}
    if raw.get("date"):
        result["date"] = raw["date"]
    if raw.get("exercise") in ("Outdoor Walk", "Indoor Walk", "Outdoor Cycle", "Indoor Cycle", "Elliptical"):
        from gym.models import CardioExercise
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


def extract_session_data_from_image(image_files) -> dict:
    """
    Envía imágenes al LLM con visión y devuelve campos mapeados a Session.
    Devuelve {} si no hay servidor o falla la llamada.
    """
    if not requests:
        return {}
    server = _get_ollama_server()
    if not server:
        return {}
    images_b64 = _encode_files(image_files)
    if not images_b64:
        return {}

    prompt = (
        "Analiza esta(s) imagen(es) de una sesión de entrenamiento o cardio "
        "(captura de reloj, app de fitness, etc.). "
        "Devuelve ÚNICAMENTE un JSON válido, sin texto adicional ni markdown, con estas claves "
        "(usa null para lo que no detectes): "
        "date (YYYY-MM-DD), session_start (ISO 8601), session_end (ISO 8601), "
        "name (uno de: Outdoor Walk, Indoor Walk, Outdoor Cycle, Indoor Cycle, Elliptical, Musculation), "
        "location (texto), workout_time_seconds (número entero), "
        "distance_km (número), avg_speed_kmh (número), "
        "active_calories (número entero), total_calories (número entero), "
        "elevation_gain_m (número entero), average_heart_rate (número entero)."
    )
    raw = _call_ollama(server, prompt, images_b64)

    valid_names = {
        "Outdoor Walk", "Indoor Walk", "Outdoor Cycle",
        "Indoor Cycle", "Elliptical", "Musculation",
    }
    result = {}
    if raw.get("date"):
        result["date"] = raw["date"]
    if raw.get("session_start"):
        result["session_start"] = raw["session_start"]
    if raw.get("session_end"):
        result["session_end"] = raw["session_end"]
    if raw.get("name") in valid_names:
        result["name"] = raw["name"]
    if raw.get("location"):
        result["location"] = str(raw["location"])[:255]
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
    return result


def extract_training_session_data_from_image(image_files) -> dict:
    """
    Envía imágenes al LLM con visión y devuelve campos mapeados a TrainingSession.
    Devuelve {} si no hay servidor o falla la llamada.
    """
    if not requests:
        return {}
    server = _get_ollama_server()
    if not server:
        return {}
    images_b64 = _encode_files(image_files)
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
    raw = _call_ollama(server, prompt, images_b64)

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

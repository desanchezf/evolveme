from gym.services import (
    _call_ollama,
    _encode_files,
    _get_ollama_server,
)

try:
    import requests
except ImportError:
    requests = None


def extract_sleep_data_from_image(image_files) -> dict:
    """
    Envía imágenes al LLM con visión y devuelve campos mapeados a SleepRecord.
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
        "Analiza esta(s) imagen(es) de datos de sueño (captura de Apple Health, Garmin, Fitbit, "
        "Whoop, Samsung Health, Oura Ring u otra app de sueño). "
        "Devuelve ÚNICAMENTE un JSON válido, sin texto adicional ni markdown, con estas claves "
        "(usa null para lo que no detectes): "
        "date (YYYY-MM-DD), "
        "sleep_start (ISO 8601, p. ej. 2026-04-23T02:10:00), "
        "sleep_end (ISO 8601, p. ej. 2026-04-23T08:05:00), "
        "total_sleep_seconds (número entero, tiempo TOTAL dormido sin contar tiempo despierto), "
        "awake_seconds (número entero, tiempo despierto durante la noche), "
        "rem_seconds (número entero, tiempo en fase REM), "
        "core_seconds (número entero, tiempo en sueño ligero/Core), "
        "deep_seconds (número entero, tiempo en sueño profundo/Deep). "
        "Si la app muestra los tiempos en horas y minutos, conviértelos a segundos."
    )
    raw = _call_ollama(server, prompt, images_b64)

    from datetime import timedelta

    result = {}
    if raw.get("date"):
        result["date"] = raw["date"]
    if raw.get("sleep_start"):
        result["sleep_start"] = raw["sleep_start"]
    if raw.get("sleep_end"):
        result["sleep_end"] = raw["sleep_end"]
    if raw.get("total_sleep_seconds") is not None:
        result["total_sleep_time"] = timedelta(seconds=int(raw["total_sleep_seconds"]))
    if raw.get("awake_seconds") is not None:
        result["awake_time"] = timedelta(seconds=int(raw["awake_seconds"]))
    if raw.get("rem_seconds") is not None:
        result["rem_time"] = timedelta(seconds=int(raw["rem_seconds"]))
    if raw.get("core_seconds") is not None:
        result["core_time"] = timedelta(seconds=int(raw["core_seconds"]))
    if raw.get("deep_seconds") is not None:
        result["deep_time"] = timedelta(seconds=int(raw["deep_seconds"]))
    return result

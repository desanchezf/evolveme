"""
Servicio de extracción de datos de medidas corporales desde una imagen
usando LLM con visión (Ollama). Mismo patrón que gym/services.py.
"""
import base64
import json
import re

try:
    import requests
except ImportError:
    requests = None

VISION_MODEL = "llama3.2-vision:11b"


def _get_ollama_server():
    """Devuelve el primer servidor Ollama habilitado, o None."""
    from ia.models import OllamaServer
    return OllamaServer.objects.filter(enabled=True).first()


def _encode_image(file) -> str:
    """Lee el archivo de imagen y devuelve base64."""
    file.seek(0)
    return base64.b64encode(file.read()).decode("utf-8")


def _parse_llm_json(response_text: str) -> dict:
    """Extrae un objeto JSON del texto (puede venir en markdown)."""
    text = (response_text or "").strip()
    match = re.search(r"```(?:json)?\s*([\s\S]*?)\s*```", text)
    if match:
        text = match.group(1).strip()
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        return {}


def extract_measure_data_from_image(image_files) -> dict:
    """
    Envía una o varias imágenes de báscula/app de composición corporal
    al LLM con visión y devuelve un diccionario con los campos que se
    puedan mapear al modelo Measure.

    image_files: archivo único o lista de archivos.
    Devuelve {} si no hay servidor o falla la llamada.
    """
    if not requests:
        return {}

    server = _get_ollama_server()
    if not server:
        return {}

    if not hasattr(image_files, "__iter__") or isinstance(
        image_files, (str, bytes)
    ):
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
        "Analiza esta(s) imagen(es) de una báscula inteligente o app de "
        "composición corporal. Devuelve ÚNICAMENTE un JSON válido, sin texto "
        "adicional ni markdown, con estas claves (usa null para lo que no "
        "detectes): "
        "date (ISO 8601, p.ej. 2025-04-08), "
        "weight (número decimal, kg), "
        "fat_perc (porcentaje de grasa corporal, decimal), "
        "muscle_mass (masa muscular kg, decimal), "
        "bmi (índice de masa corporal, decimal), "
        "body_water_mass (masa de agua kg, decimal), "
        "body_water_percentage (porcentaje de agua, decimal), "
        "fat_mass (masa grasa kg, decimal), "
        "bone_mineral_content (contenido mineral óseo kg, decimal), "
        "protein_mass (masa proteica kg, decimal), "
        "muscle_percentage (porcentaje muscular, decimal), "
        "skeletal_muscle_mass (masa muscular esquelética kg, decimal), "
        "visceral_fat_rating (calificación grasa visceral, decimal), "
        "basal_metabolic_rate (tasa metabólica basal kcal, decimal), "
        "body_age (edad corporal años, entero)."
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
        resp = requests.post(
            url, json=payload, headers=headers or None, timeout=60
        )
        resp.raise_for_status()
        raw = _parse_llm_json(resp.json().get("response") or "")
    except Exception:
        return {}

    float_fields = [
        "weight", "fat_perc", "muscle_mass", "bmi",
        "body_water_mass", "body_water_percentage", "fat_mass",
        "bone_mineral_content", "protein_mass", "muscle_percentage",
        "skeletal_muscle_mass", "visceral_fat_rating", "basal_metabolic_rate",
    ]
    result = {}
    if raw.get("date"):
        result["date"] = raw["date"]
    for field in float_fields:
        if raw.get(field) is not None:
            try:
                result[field] = float(raw[field])
            except (TypeError, ValueError):
                pass
    if raw.get("body_age") is not None:
        try:
            result["body_age"] = int(raw["body_age"])
        except (TypeError, ValueError):
            pass

    return result

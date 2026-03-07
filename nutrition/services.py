"""
Servicio de extracción de datos de producto desde una o varias imágenes (etiquetado nutricional) usando LLM con visión.
"""
import base64
import json
import re

try:
    import requests
except ImportError:
    requests = None

# Modelo solo para IMÁGENES (OCR/etiquetado). El chat usa otro modelo (qwen3:8b) en ia/services.
VISION_MODEL = "llama3.2-vision:11b"  # ollama pull llama3.2-vision:11b

# Valores válidos para market (nutrition.enums.MarketChoices)
VALID_MARKETS = {"mercadona", "carrefour", "lidl", "alcampo", "other"}


def _get_ollama_server():
    """Devuelve el primer servidor Ollama habilitado, o None."""
    from ia.models import OllamaServer
    return OllamaServer.objects.filter(enabled=True).first()


def _encode_image(file) -> str:
    """Lee el archivo de imagen y devuelve base64. Reposiciona el archivo al inicio después."""
    file.seek(0)
    data = base64.b64encode(file.read()).decode("utf-8")
    file.seek(0)
    return data


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


def extract_product_data_from_images(image_files) -> dict:
    """
    Envía una o varias imágenes al LLM con visión (Ollama) y devuelve un diccionario
    con los campos que se puedan mapear al modelo Product.
    image_files: lista de archivos de imagen (p. ej. fotos del etiquetado nutricional).
    Si no hay servidor o falla la llamada, devuelve {}.
    """
    if not requests or not image_files:
        return {}

    server = _get_ollama_server()
    if not server:
        return {}

    images_b64 = []
    for f in image_files:
        try:
            images_b64.append(_encode_image(f))
        except Exception:
            pass
    if not images_b64:
        return {}

    prompt = (
        "Analiza esta(s) imagen(es) de un producto alimenticio (etiquetado nutricional, envase, etc.). "
        "Devuelve ÚNICAMENTE un JSON válido, sin texto adicional ni markdown, con estas claves "
        "(usa null para lo que no detectes): "
        "name (nombre del producto), description (breve descripción), barcode (código de barras si aparece), "
        "market (uno de: mercadona, carrefour, lidl, alcampo, other), "
        "calories_per_100g (número), protein_per_100g (número), carbs_per_100g (número), fat_per_100g (número). "
        "Todos los valores nutricionales deben ser por 100g."
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
        resp = requests.post(url, json=payload, headers=headers or None, timeout=90)
        resp.raise_for_status()
        data = resp.json()
        response_text = data.get("response") or ""
        raw = _parse_llm_json(response_text)
    except Exception:
        return {}

    result = {}
    if raw.get("name"):
        result["name"] = str(raw["name"])[:255]
    if raw.get("description") is not None:
        result["description"] = str(raw["description"])
    if raw.get("barcode"):
        result["barcode"] = str(raw["barcode"])[:255]
    if raw.get("market") and str(raw["market"]).lower() in VALID_MARKETS:
        result["market"] = str(raw["market"]).lower()
    if raw.get("calories_per_100g") is not None:
        try:
            result["calories_per_100g"] = float(raw["calories_per_100g"])
        except (TypeError, ValueError):
            pass
    if raw.get("protein_per_100g") is not None:
        try:
            result["protein_per_100g"] = float(raw["protein_per_100g"])
        except (TypeError, ValueError):
            pass
    if raw.get("carbs_per_100g") is not None:
        try:
            result["carbs_per_100g"] = float(raw["carbs_per_100g"])
        except (TypeError, ValueError):
            pass
    if raw.get("fat_per_100g") is not None:
        try:
            result["fat_per_100g"] = float(raw["fat_per_100g"])
        except (TypeError, ValueError):
            pass

    return result

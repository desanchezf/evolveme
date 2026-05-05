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

_FALLBACK_PROMPT = (
    "Analiza esta(s) imagen(es) de un producto alimenticio (etiquetado nutricional, envase, etc.). "
    "Devuelve ÚNICAMENTE un JSON válido con la clave 'product' conteniendo: "
    "name, description, barcode, market (mercadona/carrefour/lidl/alcampo/other), "
    "energy_kj_per_100g, calories_per_100g, protein_per_100g, carbs_per_100g, fat_per_100g, "
    "saturated_fat_per_100g, monounsaturated_fat_per_100g, polyunsaturated_fat_per_100g, "
    "sugars_per_100g, polyols_per_100g, fiber_per_100g, salt_per_100g, "
    "omega3_epa_dha_per_100g, thiamine_b1_per_100g, phosphorus_per_100g, "
    "magnesium_per_100g, iron_per_100g, zinc_per_100g, stock (yes/no/buy). "
    "Usa null para los valores no detectables. Todos los valores nutricionales por 100g."
)

_NUMERIC_FIELDS = [
    "energy_kj_per_100g",
    "calories_per_100g",
    "protein_per_100g",
    "carbs_per_100g",
    "fat_per_100g",
    "saturated_fat_per_100g",
    "monounsaturated_fat_per_100g",
    "polyunsaturated_fat_per_100g",
    "sugars_per_100g",
    "polyols_per_100g",
    "fiber_per_100g",
    "salt_per_100g",
    "omega3_epa_dha_per_100g",
    "thiamine_b1_per_100g",
    "phosphorus_per_100g",
    "magnesium_per_100g",
    "iron_per_100g",
    "zinc_per_100g",
]


def _get_ollama_server():
    from ia.models import OllamaServer
    return OllamaServer.objects.filter(enabled=True).first()


def _get_extraction_prompt() -> str:
    try:
        from ia.models import Promtps
        p = Promtps.objects.filter(name="product_extraction").first()
        if p and p.prompt:
            return p.prompt
    except Exception:
        pass
    return _FALLBACK_PROMPT


def _encode_image(file) -> str:
    file.seek(0)
    data = base64.b64encode(file.read()).decode("utf-8")
    file.seek(0)
    return data


def _parse_llm_json(response_text: str) -> dict:
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

    prompt = _get_extraction_prompt()

    url = f"{server.base_url.rstrip('/')}/api/generate"
    payload = {"model": VISION_MODEL, "prompt": prompt, "images": images_b64, "stream": False}
    headers = {}
    if server.api_key:
        headers["Authorization"] = f"Bearer {server.api_key}"

    try:
        resp = requests.post(url, json=payload, headers=headers or None, timeout=90)
        resp.raise_for_status()
        raw_full = _parse_llm_json(resp.json().get("response") or "")
    except Exception:
        return {}

    # El modelo devuelve {"product": {...}} o {"error": "..."}
    if raw_full.get("error"):
        return {}
    raw = raw_full.get("product") or raw_full  # tolerar respuesta plana

    result = {}
    if raw.get("name"):
        result["name"] = str(raw["name"])[:255]
    if raw.get("description") is not None:
        result["description"] = str(raw["description"])
    if raw.get("barcode"):
        result["barcode"] = str(raw["barcode"])[:255]
    if raw.get("market") and str(raw["market"]).lower() in VALID_MARKETS:
        result["market"] = str(raw["market"]).lower()
    if raw.get("stock") in ("yes", "no", "buy"):
        result["stock"] = raw["stock"]

    for field in _NUMERIC_FIELDS:
        val = raw.get(field)
        if val is not None:
            try:
                result[field] = float(val)
            except (TypeError, ValueError):
                pass

    return result

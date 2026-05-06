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


def build_user_prompt(user):
    """
    Genera el texto del prompt de sistema con los datos actuales del usuario:
    - Perfil completo
    - Últimas 2 medidas
    - Sesiones de entrenamiento y cardio del último mes
    - Rutina activa completa
    - Dieta de la última semana
    """
    from datetime import timedelta
    from django.utils import timezone

    now = timezone.now()
    today = now.date()
    month_ago = now - timedelta(days=30)
    week_ago = today - timedelta(days=7)

    lines = [
        "Eres el asistente de fitness y nutrición de EvolveMe. "
        "Responde siempre en español de forma concisa y personalizada. "
        "Usa los datos del usuario para dar respuestas contextualizadas. "
        "REGLA ESTRICTA: si el usuario pregunta sobre gimnasio, entrenamiento, rutinas o ejercicios, "
        "responde ÚNICAMENTE sobre ese tema sin incluir ningún consejo de alimentación ni nutrición. "
        "Si el usuario pregunta sobre alimentación, dieta o nutrición, responde ÚNICAMENTE sobre ese "
        "tema sin incluir ningún consejo de gimnasio ni entrenamiento. "
        "Usa formato Markdown en tus respuestas: encabezados (##), listas (-), negrita (**texto**) y tablas cuando ayuden a la claridad.",
        "",
    ]

    # ── PERFIL COMPLETO ──────────────────────────────────────────────────────
    profile = None
    try:
        from evolveme.models import GymUserProfile
        profile = GymUserProfile.objects.select_related("active_routine").get(user=user)
        lines.append("## PERFIL")
        lines.append(f"Usuario: {user.get_full_name() or user.username}")
        if profile.birth_date:
            lines.append(f"Fecha nacimiento: {profile.birth_date}")
        if profile.gender:
            lines.append(f"Género: {profile.gender}")
        if profile.height:
            lines.append(f"Altura: {profile.height} cm")
        if profile.objective:
            lines.append(f"Objetivo: {profile.objective}")
        if profile.start_date:
            lines.append(f"Inicio programa: {profile.start_date}")
        if profile.end_date:
            lines.append(f"Fin programa: {profile.end_date}")
    except Exception:
        pass

    # ── ÚLTIMAS 2 MEDIDAS ────────────────────────────────────────────────────
    try:
        from evolveme.models import Measure
        measures = list(Measure.objects.filter(user=user).order_by("-date")[:2])
        if measures:
            lines += ["", "## ÚLTIMAS MEDIDAS"]
            for m in measures:
                parts = [str(m.date)]
                if m.weight:
                    parts.append(f"peso {m.weight} kg")
                if m.fat_perc:
                    parts.append(f"grasa {m.fat_perc}%")
                if m.muscle_mass:
                    parts.append(f"músculo {m.muscle_mass} kg")
                if m.waist:
                    parts.append(f"cintura {m.waist} cm")
                if m.bmi:
                    parts.append(f"IMC {m.bmi}")
                if m.basal_metabolic_rate:
                    parts.append(f"TMB {m.basal_metabolic_rate} kcal")
                lines.append("- " + " | ".join(parts))
    except Exception:
        pass

    # ── RUTINA ACTIVA COMPLETA ───────────────────────────────────────────────
    try:
        from gym.models import Routine
        routine = getattr(profile, "active_routine", None)
        if not routine:
            routine = Routine.objects.filter(user=user).order_by("-created_at").first()
        if routine:
            lines += ["", "## RUTINA ACTIVA"]
            if routine.start_date:
                lines.append(f"Inicio: {routine.start_date}")
            if routine.end_date:
                lines.append(f"Fin: {routine.end_date}")
            if routine.duration:
                lines.append(f"Duración: {routine.duration} semanas")
            if routine.weekly_structure:
                lines.append(f"Estructura semanal: {routine.get_weekly_structure_display()}")
            if routine.training_focus:
                lines.append(f"Enfoque: {routine.get_training_focus_display()}")
            if routine.intensity_techniques:
                techniques = (
                    routine.intensity_techniques
                    if isinstance(routine.intensity_techniques, list)
                    else []
                )
                if techniques:
                    lines.append(f"Técnicas de intensidad: {', '.join(techniques)}")
            if routine.exercise_types:
                types = routine.exercise_types if isinstance(routine.exercise_types, list) else []
                lines.append(f"Tipos: {', '.join(types)}")
            if routine.warmup:
                lines.append(f"Calentamiento: {routine.warmup.name}")
            exercises = list(routine.exercises.all())
            if exercises:
                lines.append("Ejercicios:")
                for ex in exercises:
                    ex_line = f"  · {ex.name}"
                    if ex.body_part:
                        ex_line += f" ({ex.body_part})"
                    if ex.sets and ex.reps:
                        ex_line += f" — {ex.sets}×{ex.reps}"
                        if ex.unit:
                            ex_line += f" {ex.unit}"
                    lines.append(ex_line)
    except Exception:
        pass

    # ── SESIONES (último mes) ────────────────────────────────────────────────
    try:
        from gym.models import Session
        sessions = list(
            Session.objects.filter(user=user, date__gte=month_ago.date())
            .order_by("-date", "-session_start")
        )
        if sessions:
            lines += ["", "## SESIONES (último mes)"]
            for s in sessions:
                parts = [str(s.date), s.get_name_display()]
                if s.workout_time:
                    mins = int(s.workout_time.total_seconds() // 60)
                    parts.append(f"{mins} min")
                if s.distance:
                    parts.append(f"{s.distance} km")
                if s.active_calories:
                    parts.append(f"{s.active_calories} kcal")
                if s.average_heart_rate:
                    parts.append(f"FC {s.average_heart_rate} ppm")
                lines.append("- " + " | ".join(parts))
    except Exception:
        pass

    # ── DIETA ÚLTIMA SEMANA ──────────────────────────────────────────────────
    try:
        from nutrition.models import DailyDiet
        diets = list(
            DailyDiet.objects.filter(user=user, date__gte=week_ago)
            .prefetch_related("products__product")
            .order_by("-date")
        )
        if diets:
            lines += ["", "## DIETA (última semana)"]
            for diet in diets:
                lines.append(f"- {diet.date}:")
                for pq in diet.products.select_related("product").all():
                    if not pq.product:
                        continue
                    item = f"  · {pq.product.name}: {pq.quantity} {pq.unit}".strip()
                    if pq.product.calories_per_100g and pq.quantity:
                        kcal = round(pq.product.calories_per_100g * pq.quantity / 100)
                        item += f" (~{kcal} kcal)"
                    lines.append(item)
    except Exception:
        pass

    # ── BASE DE CONOCIMIENTO (gym + nutrition) ───────────────────────────────
    try:
        from ia.models import Promtps
        for name in ("gym", "nutrition"):
            p = Promtps.objects.filter(name=name).first()
            if p and p.prompt:
                lines += ["", f"## BASE DE CONOCIMIENTO: {name.upper()}", p.prompt]
    except Exception:
        pass

    return "\n".join(lines)


def get_or_build_user_prompt(user, model_name):
    """
    Devuelve el texto del prompt almacenado para user + model_name.
    Si no existe, lo genera y lo guarda.
    Devuelve None si no hay OllamaModelConfig para ese modelo.
    """
    from ia.models import OllamaModelConfig, UserModelPrompt
    try:
        model_config = OllamaModelConfig.objects.get(model_name=model_name)
    except OllamaModelConfig.DoesNotExist:
        return None

    prompt_text = build_user_prompt(user)
    obj, _ = UserModelPrompt.objects.update_or_create(
        user=user,
        model_config=model_config,
        defaults={"prompt_text": prompt_text},
    )
    return obj.prompt_text


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

    system_prompt = get_or_build_user_prompt(session.user, model)
    messages = []
    if system_prompt:
        messages.append({"role": "system", "content": system_prompt})
    messages.extend(
        {"role": msg.role, "content": msg.content or ""}
        for msg in session.messages.all().order_by("created_at")
    )

    url = f"{server.base_url.rstrip('/')}/api/chat"
    payload = {
        "model": model,
        "messages": messages,
        "stream": False,
        "think": False,
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


def delete_model_on_server(server, model_name):
    """Elimina el modelo del servidor Ollama (DELETE /api/delete). Devuelve (ok, error)."""
    if not requests:
        return False, "Falta 'requests'."
    url = f"{server.base_url.rstrip('/')}/api/delete"
    headers = {}
    if server.api_key:
        headers["Authorization"] = f"Bearer {server.api_key}"
    try:
        resp = requests.delete(
            url, json={"name": model_name}, headers=headers or None, timeout=30
        )
        resp.raise_for_status()
        return True, None
    except Exception as e:
        return False, str(e)

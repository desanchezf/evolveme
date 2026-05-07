"""
Señales Django que regeneran el prompt de sistema del usuario en UserModelPrompt
cada vez que cambia cualquier dato relevante para build_user_prompt.
"""
from django.db.models.signals import post_delete, post_save
from django.dispatch import receiver


def _refresh_prompt(user):
    """Reconstruye y guarda el prompt para todas las configuraciones activas del usuario."""
    if user is None:
        return
    from ia.models import OllamaModelConfig, UserModelPrompt
    from ia.services import build_user_prompt

    prompt_text = build_user_prompt(user)
    for model_config in OllamaModelConfig.objects.filter(downloaded=True):
        UserModelPrompt.objects.update_or_create(
            user=user,
            model_config=model_config,
            defaults={"prompt_text": prompt_text},
        )


# ── EVOLVEME ─────────────────────────────────────────────────────────────────

@receiver(post_save, sender="evolveme.GymUserProfile")
def on_profile_save(sender, instance, **kwargs):
    _refresh_prompt(instance.user)


@receiver(post_save, sender="evolveme.Measure")
@receiver(post_delete, sender="evolveme.Measure")
def on_measure_change(sender, instance, **kwargs):
    _refresh_prompt(instance.user)


# ── GYM ──────────────────────────────────────────────────────────────────────

@receiver(post_save, sender="gym.Routine")
@receiver(post_delete, sender="gym.Routine")
def on_routine_change(sender, instance, **kwargs):
    _refresh_prompt(instance.user)


@receiver(post_save, sender="gym.Session")
@receiver(post_delete, sender="gym.Session")
def on_session_change(sender, instance, **kwargs):
    _refresh_prompt(instance.user)


@receiver(post_save, sender="gym.CardioSession")
@receiver(post_delete, sender="gym.CardioSession")
def on_cardio_session_change(sender, instance, **kwargs):
    _refresh_prompt(instance.user)


@receiver(post_save, sender="gym.TrainingSession")
@receiver(post_delete, sender="gym.TrainingSession")
def on_training_session_change(sender, instance, **kwargs):
    _refresh_prompt(instance.user)


@receiver(post_save, sender="gym.MusculationRecord")
@receiver(post_delete, sender="gym.MusculationRecord")
def on_musculation_record_change(sender, instance, **kwargs):
    _refresh_prompt(instance.user)


# ── SLEEP ─────────────────────────────────────────────────────────────────────

@receiver(post_save, sender="sleep.SleepRecord")
@receiver(post_delete, sender="sleep.SleepRecord")
def on_sleep_record_change(sender, instance, **kwargs):
    _refresh_prompt(instance.user)


# ── NUTRITION ─────────────────────────────────────────────────────────────────

@receiver(post_save, sender="nutrition.DailyDiet")
@receiver(post_delete, sender="nutrition.DailyDiet")
def on_daily_diet_change(sender, instance, **kwargs):
    _refresh_prompt(instance.user)


@receiver(post_save, sender="nutrition.MealMetrics")
@receiver(post_delete, sender="nutrition.MealMetrics")
def on_meal_metrics_change(sender, instance, **kwargs):
    try:
        user = instance.daily_diet.user
    except Exception:
        return
    _refresh_prompt(user)


# ── IA (base de conocimiento) ─────────────────────────────────────────────────

@receiver(post_save, sender="ia.Promtps")
def on_knowledge_base_change(sender, instance, **kwargs):
    from django.contrib.auth import get_user_model
    User = get_user_model()
    for user in User.objects.filter(is_active=True):
        _refresh_prompt(user)

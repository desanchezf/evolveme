import json
from datetime import date, timedelta

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Avg, Count, Max, Sum
from django.db.models.functions import TruncWeek
from django.http import JsonResponse
from django.shortcuts import redirect, render
from django.views.generic import TemplateView

from evolveme.forms import GymUserProfileForm, MeasureForm
from evolveme.models import Measure, MeasureImage
from evolveme.services import extract_measure_data_from_image
from ia.services import is_model_downloaded
from project.admin_context import with_admin_context


class IndexView(LoginRequiredMixin, TemplateView):
    """Vista para la página principal con tarjetas de acceso"""

    template_name = "evolveme/index.html"

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx.update(with_admin_context(self.request))
        return ctx


@login_required
def dashboard_view(request):
    """Dashboard de hitos, evolución personal y rankings de plataforma."""
    from gym.models import Session, MusculationRecord
    from sleep.models import SleepRecord
    from nutrition.models import MealMetrics

    user = request.user
    today = date.today()
    month_start = today.replace(day=1)
    thirty_days_ago = today - timedelta(days=30)
    fourteen_days_ago = today - timedelta(days=14)
    seven_days_ago = today - timedelta(days=7)
    eight_weeks_ago = today - timedelta(weeks=8)

    # ── KPI ─────────────────────────────────────────────────────────────────
    monthly_kcal = Session.objects.filter(
        user=user, date__gte=month_start
    ).aggregate(t=Sum("active_calories"))["t"] or 0

    monthly_sessions = Session.objects.filter(user=user, date__gte=month_start).count()

    monthly_workout_min = round(sum(
        s.workout_time.total_seconds()
        for s in Session.objects.filter(user=user, date__gte=month_start)
        if s.workout_time
    ) / 60)

    # Racha de días activos consecutivos
    active_dates = (
        set(Session.objects.filter(user=user).values_list("date", flat=True)) |
        set(MusculationRecord.objects.filter(user=user, record_date__isnull=False)
            .values_list("record_date__date", flat=True))
    )
    streak, check = 0, today if today in active_dates else today - timedelta(days=1)
    while check in active_dates:
        streak += 1
        check -= timedelta(days=1)

    # Sueño promedio (última semana)
    sleep_week = list(SleepRecord.objects.filter(user=user, date__gte=seven_days_ago))
    sleep_avg_h = 0.0
    if sleep_week:
        total_s = sum(s.total_sleep_time.total_seconds() for s in sleep_week if s.total_sleep_time)
        sleep_avg_h = round(total_s / len(sleep_week) / 3600, 1)

    # Cambio de peso
    measures_w = list(Measure.objects.filter(user=user, weight__isnull=False).order_by("-date")[:2])
    weight_change = None
    current_weight = measures_w[0].weight if measures_w else None
    if len(measures_w) >= 2:
        weight_change = round(measures_w[0].weight - measures_w[1].weight, 1)

    # ── Charts: Calorías activas por semana ──────────────────────────────────
    wk_qs = (
        Session.objects.filter(user=user, date__gte=eight_weeks_ago)
        .annotate(week=TruncWeek("date"))
        .values("week").annotate(t=Sum("active_calories")).order_by("week")
    )
    weekly = {"labels": [i["week"].strftime("%d/%m") for i in wk_qs],
              "data": [i["t"] or 0 for i in wk_qs]}

    # ── Charts: Tipos de sesión (doughnut) ───────────────────────────────────
    st_qs = (
        Session.objects.filter(user=user, date__gte=thirty_days_ago)
        .values("name").annotate(c=Count("id"))
    )
    session_types = {"labels": [i["name"] for i in st_qs], "data": [i["c"] for i in st_qs]}

    # ── Charts: Evolución de peso ─────────────────────────────────────────────
    wt_qs = list(Measure.objects.filter(user=user, weight__isnull=False).order_by("-date")[:15])[::-1]
    weight_chart = {"labels": [m.date.strftime("%d/%m/%y") for m in wt_qs],
                    "data": [m.weight for m in wt_qs]}

    # ── Charts: Composición corporal ─────────────────────────────────────────
    bc_qs = list(Measure.objects.filter(user=user).exclude(fat_perc=None).order_by("-date")[:12])[::-1]
    body_comp = {"labels": [m.date.strftime("%d/%m/%y") for m in bc_qs],
                 "fat": [m.fat_perc for m in bc_qs],
                 "muscle": [m.muscle_mass for m in bc_qs]}

    # ── Charts: Sueño por noche ───────────────────────────────────────────────
    sl_qs = list(SleepRecord.objects.filter(user=user).order_by("-date")[:14])[::-1]
    sleep_nights = {
        "labels": [s.date.strftime("%d/%m") for s in sl_qs],
        "data": [round(s.total_sleep_time.total_seconds() / 3600, 1) if s.total_sleep_time else 0 for s in sl_qs],
    }

    # ── Charts: Fases de sueño promedio (doughnut) ───────────────────────────
    sl_30 = list(SleepRecord.objects.filter(user=user, date__gte=thirty_days_ago))
    n = len(sl_30)

    def _avg_phase(attr):
        vals = [getattr(s, attr).total_seconds() for s in sl_30 if getattr(s, attr)]
        return round(sum(vals) / n / 60) if vals else 0

    sleep_phases = {
        "labels": ["Despierto", "REM", "Core", "Profundo"],
        "data": [_avg_phase("awake_time"), _avg_phase("rem_time"),
                 _avg_phase("core_time"), _avg_phase("deep_time")] if n else [0, 0, 0, 0],
    }

    # ── Charts: Calorías nutrición (últimas 2 semanas) ───────────────────────
    nut_qs = (
        MealMetrics.objects.filter(daily_diet__user=user, daily_diet__date__gte=fourteen_days_ago)
        .select_related("daily_diet").order_by("daily_diet__date")
    )
    nutrition_kcal = {
        "labels": [m.daily_diet.date.strftime("%d/%m") for m in nut_qs],
        "data": [round(m.calories) for m in nut_qs],
    }

    # ── Charts: Macros promedio 30 días (doughnut) ───────────────────────────
    mac_qs = list(MealMetrics.objects.filter(daily_diet__user=user, daily_diet__date__gte=thirty_days_ago))
    nm = len(mac_qs)
    macros = {
        "labels": ["Proteína (g)", "Carbos (g)", "Grasas (g)"],
        "data": [round(sum(m.protein for m in mac_qs) / nm, 1),
                 round(sum(m.carbs for m in mac_qs) / nm, 1),
                 round(sum(m.fat for m in mac_qs) / nm, 1)] if nm else [0, 0, 0],
    }

    # ── Charts: Records personales (horizontal bar) ───────────────────────────
    pr_qs = (
        MusculationRecord.objects.filter(user=user)
        .values("exercise__name").annotate(max_w=Max("weight")).order_by("-max_w")[:10]
    )
    prs = {"labels": [i["exercise__name"] for i in pr_qs],
           "data": [i["max_w"] for i in pr_qs]}

    # ── Rankings de plataforma ────────────────────────────────────────────────
    # 1. Kcal quemadas este mes
    rank_kcal = list(
        Session.objects.filter(date__gte=month_start)
        .values("user__username").annotate(t=Sum("active_calories")).order_by("-t")[:10]
    )
    # 2. Sesiones este mes
    rank_sessions = list(
        Session.objects.filter(date__gte=month_start)
        .values("user__username").annotate(c=Count("id")).order_by("-c")[:10]
    )
    # 3. Levantamiento máximo (PR absoluto por usuario)
    rank_lifts = list(
        MusculationRecord.objects.values("user__username")
        .annotate(max_w=Max("weight")).order_by("-max_w")[:10]
    )
    # 4. Sueño promedio (último mes)
    rank_sleep_raw = list(
        SleepRecord.objects.filter(date__gte=thirty_days_ago)
        .values("user__username", "total_sleep_time")
    )
    sleep_by_user = {}
    for row in rank_sleep_raw:
        uname = row["user__username"]
        td = row["total_sleep_time"]
        if td:
            sleep_by_user.setdefault(uname, []).append(td.total_seconds())
    rank_sleep = sorted(
        [{"user__username": u, "avg_h": round(sum(v) / len(v) / 3600, 1)}
         for u, v in sleep_by_user.items()],
        key=lambda x: x["avg_h"], reverse=True
    )[:10]

    charts = {
        "weekly": weekly,
        "session_types": session_types,
        "weight": weight_chart,
        "body_comp": body_comp,
        "sleep_nights": sleep_nights,
        "sleep_phases": sleep_phases,
        "nutrition_kcal": nutrition_kcal,
        "macros": macros,
        "prs": prs,
    }

    ctx = {
        "kpi": {
            "monthly_kcal": monthly_kcal,
            "monthly_sessions": monthly_sessions,
            "monthly_workout_min": monthly_workout_min,
            "streak": streak,
            "sleep_avg_h": sleep_avg_h,
            "weight_change": weight_change,
            "current_weight": current_weight,
        },
        "rankings": {
            "kcal": rank_kcal,
            "sessions": rank_sessions,
            "lifts": rank_lifts,
            "sleep": rank_sleep,
        },
        "current_username": user.username,
        "charts_json": json.dumps(charts),
    }
    return render(request, "evolveme/dashboard.html", with_admin_context(request, ctx))


@login_required
def profile_form_view(request):
    """Vista pública para editar el perfil del usuario."""
    from evolveme.models import GymUserProfile
    is_staff = getattr(request.user, "is_staff", False)

    profile, _ = GymUserProfile.objects.get_or_create(user=request.user)

    if request.method == "POST":
        form = GymUserProfileForm(request.POST, instance=profile, user=request.user)
        if form.is_valid():
            instance = form.save(commit=False)
            if not is_staff:
                instance.user = request.user
            instance.save()
            messages.success(request, "Perfil actualizado correctamente.")
            return redirect("evolveme:profile_form")
    else:
        form = GymUserProfileForm(instance=profile, user=request.user)

    return render(request, "evolveme/profile_form.html", with_admin_context(request, {
        "form": form,
    }))


@login_required
def measure_form_view(request):
    """Vista para el formulario de medidas corporales."""
    if request.method == "POST":
        image_files = request.FILES.getlist("measure_images")
        form = MeasureForm(request.POST, user=request.user)
        if form.is_valid():
            measure = form.save()
            for f in image_files:
                f.seek(0)
                MeasureImage.objects.create(measure=measure, image=f)
            messages.success(request, "Medidas guardadas correctamente.")
            return redirect("evolveme:measure_form")
    else:
        form = MeasureForm(user=request.user)

    return render(
        request,
        "evolveme/measure_form.html",
        with_admin_context(request, {
            "form": form,
            "vision_available": is_model_downloaded("llama3.2-vision:11b"),
        }),
    )


@login_required
def measure_analyze_view(request):
    """AJAX: analiza imágenes de báscula y devuelve campos extraídos."""
    if request.method != "POST":
        return JsonResponse({"error": "Método no permitido."}, status=405)
    image_files = request.FILES.getlist("measure_images")
    if not image_files:
        return JsonResponse({"error": "No se recibieron imágenes."}, status=400)

    extracted = extract_measure_data_from_image(image_files)
    if not extracted:
        return JsonResponse({"error": "No se pudieron extraer datos."}, status=422)

    result = {
        k: (str(v) if not isinstance(v, (str, int, float, bool, type(None))) else v)
        for k, v in extracted.items()
    }
    return JsonResponse({"data": result})

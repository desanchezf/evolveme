import json
from datetime import datetime

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.contrib.auth.models import User
from django.shortcuts import redirect, render
from django.urls import reverse_lazy
from django.utils import timezone
from django.views.generic import FormView

from ia.services import is_model_downloaded
from gym.forms import (
    MusculationRecordFormSet,
    MusculationRecordFormsetHelper,
    MusculationRecordPublicForm,
    RoutineJSONForm,
    RoutinePublicForm,
    SessionModelForm,
    TrainingSessionForm,
)
from gym.models import MusculationExercise, MusculationRecord, Routine, RoutineDay, RoutineDayExercise
from evolveme.models import GymUserProfile
from project.admin_context import with_admin_context


class MusculationRecordFormsetView(PermissionRequiredMixin, FormView):
    """Vista para crear múltiples registros de musculación"""

    permission_required = ("gym.add_musculationrecord",)
    form_class = TrainingSessionForm
    success_url = reverse_lazy("admin:gym_musculationrecord_changelist")
    template_name = "gym/musculation_record_formset.html"

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        # Obtener usuario de la sesión si está autenticado
        if self.request.user.is_authenticated:
            kwargs["user"] = self.request.user
        return kwargs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Inicializar formset
        if self.request.method == "POST":
            formset = MusculationRecordFormSet(self.request.POST, prefix="records")
        else:
            formset = MusculationRecordFormSet(
                queryset=MusculationRecord.objects.none(), prefix="records"
            )

        context.update(
            {
                "formset": formset,
                "formset_helper": MusculationRecordFormsetHelper(),
            }
        )
        return context

    def form_valid(self, form):
        formset = MusculationRecordFormSet(self.request.POST, prefix="records")

        if formset.is_valid():
            user = form.cleaned_data["user"]
            record_date = form.cleaned_data["record_date"]

            # Guardar todos los registros
            instances = formset.save(commit=False)
            for instance in instances:
                instance.user = user
                instance.record_date = record_date
                instance.save()

            # Eliminar los marcados para borrar
            for obj in formset.deleted_objects:
                obj.delete()

            messages.success(
                self.request,
                f"Se han guardado {len(instances)} registro(s) de entrenamiento correctamente.",
            )
            return super().form_valid(form)
        else:
            # Si el formset no es válido, volver a mostrar el formulario
            return self.form_invalid(form)

    def form_invalid(self, form):
        messages.error(self.request, "Por favor, corrige los errores en el formulario.")
        return super().form_invalid(form)


class RoutineJSONView(PermissionRequiredMixin, FormView):
    """Vista para generar rutina desde JSON"""

    permission_required = ("gym.add_routine",)
    form_class = RoutineJSONForm
    success_url = reverse_lazy("admin:gym_routine_changelist")
    template_name = "gym/routine_json_form.html"

    def parse_date(self, date_str):
        """Parsea fecha en formato DD/MM/YYYY HH:MM"""
        try:
            return datetime.strptime(date_str, "%d/%m/%Y %H:%M")
        except ValueError:
            try:
                return datetime.strptime(date_str, "%d/%m/%Y")
            except ValueError:
                return None

    def form_valid(self, form):
        json_data = form.cleaned_data["json_data"]

        try:
            data = json.loads(json_data)
        except json.JSONDecodeError as e:
            messages.error(self.request, f"Error al parsear JSON: {str(e)}")
            return self.form_invalid(form)

        # Validar campos requeridos
        if "user" not in data:
            messages.error(self.request, "El JSON debe contener el campo 'user'")
            return self.form_invalid(form)

        # Obtener usuario
        try:
            user = User.objects.get(username=data["user"])
        except User.DoesNotExist:
            messages.error(
                self.request, f"Usuario '{data['user']}' no encontrado en el sistema"
            )
            return self.form_invalid(form)

        # Parsear duración si está presente (en semanas)
        duration = None
        if "duration" in data:
            try:
                duration = int(data["duration"])
                if duration <= 0:
                    raise ValueError("La duración debe ser un número positivo")
            except (ValueError, TypeError):
                messages.error(
                    self.request,
                    "Formato de duración incorrecto. Debe ser un número entero positivo (semanas)",
                )
                return self.form_invalid(form)

        # Crear rutina
        routine = Routine.objects.create(
            user=user,
            duration=duration,
            warmup=data.get("warmup", ""),
            exercise_types=data.get("exercise_types", []),
            weekly_structure=data.get("weekly_structure") or None,
            training_focus=data.get("training_focus") or None,
            intensity_techniques=data.get("intensity_techniques", []),
        )

        # Actualizar perfil del usuario con start_date y end_date si están presentes
        profile, _ = GymUserProfile.objects.get_or_create(user=user)

        if "start_date" in data:
            start_date = self.parse_date(data["start_date"])
            if start_date:
                if timezone.is_naive(start_date):
                    start_date = timezone.make_aware(start_date)
                profile.start_date = start_date.date()

        if "end_date" in data:
            end_date = self.parse_date(data["end_date"])
            if end_date:
                if timezone.is_naive(end_date):
                    end_date = timezone.make_aware(end_date)
                profile.end_date = end_date.date()

        if not profile.active_routine:
            profile.active_routine = routine

        profile.save()

        # Procesar días y ejercicios
        routine_data = data.get("routine", {})
        days_created = 0
        exercises_added = 0

        for i, (day_key, day_data) in enumerate(routine_data.items(), start=1):
            # Soporte formato nuevo {"name": ..., "exercises": [...]}
            # y formato legacy (lista directa de ejercicios)
            if isinstance(day_data, dict):
                day_name = day_data.get("name", day_key)
                is_rest = bool(day_data.get("is_rest", False))
                exercises_list = day_data.get("exercises", [])
            elif isinstance(day_data, list):
                day_name = day_key.replace("_", " ").capitalize()
                is_rest = False
                exercises_list = day_data
            else:
                continue

            # Extraer número de día del key (day_1 → 1) o usar índice
            try:
                day_number = int(day_key.split("_")[-1])
            except (ValueError, IndexError):
                day_number = i

            routine_day = RoutineDay.objects.create(
                routine=routine,
                day_number=day_number,
                name=day_name,
                is_rest=is_rest,
            )
            days_created += 1

            if is_rest or not isinstance(exercises_list, list):
                continue

            for order, exercise_data in enumerate(exercises_list):
                if not isinstance(exercise_data, dict):
                    continue
                ex_name = exercise_data.get("name", "").strip()
                if not ex_name:
                    continue

                # Intentar vincular con la biblioteca
                library_ex, _ = MusculationExercise.objects.get_or_create(
                    name=ex_name,
                    defaults={
                        "description": exercise_data.get("description", ""),
                        "body_part": exercise_data.get("body_part") or None,
                        "sets": exercise_data.get("sets", 0),
                        "reps": exercise_data.get("reps", 0),
                    },
                )
                routine.exercises.add(library_ex)

                RoutineDayExercise.objects.create(
                    day=routine_day,
                    exercise=library_ex,
                    exercise_name=ex_name,
                    sets_reps=exercise_data.get("sets_reps", ""),
                    notes=exercise_data.get("notes") or None,
                    order=order,
                )
                exercises_added += 1

        messages.success(
            self.request,
            f"Rutina creada correctamente. "
            f"{days_created} día(s) creado(s), "
            f"{exercises_added} ejercicio(s) añadido(s).",
        )
        return super().form_valid(form)


@login_required
def routine_form_view(request):
    """Vista pública para crear una rutina de entrenamiento."""
    is_staff = getattr(request.user, "is_staff", False)

    if request.method == "POST":
        form = RoutinePublicForm(request.POST, user=request.user, is_staff=is_staff)
        if form.is_valid():
            instance = form.save(commit=False)
            if not is_staff:
                instance.user = request.user
            instance.save()
            messages.success(request, "Rutina creada correctamente.")
            return redirect("gym:routine_form")
    else:
        form = RoutinePublicForm(user=request.user, is_staff=is_staff)

    return render(request, "gym/routine_form.html", with_admin_context(request, {
        "form": form,
    }))


@login_required
def musculation_record_form_view(request):
    """Vista para el formulario de registros de musculación"""
    if request.method == "POST":
        form = MusculationRecordPublicForm(request.POST, user=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, "Registro de musculación guardado correctamente.")
            return redirect("gym:musculation_record_form")
    else:
        form = MusculationRecordPublicForm(user=request.user)

    return render(request, "gym/musculation_record_form.html", with_admin_context(request, {"form": form}))


@login_required
def cardio_session_form_view(request):
    """Redirección al formulario unificado de sesión."""
    return redirect("gym:session_form")


@login_required
def cardio_analyze_view(request):
    """AJAX: analiza imágenes de cardio y devuelve campos extraídos."""
    from django.http import JsonResponse
    from gym.services import extract_cardio_data_from_image

    if request.method != "POST":
        return JsonResponse({"error": "Método no permitido."}, status=405)
    image_files = request.FILES.getlist("workout_images")
    if not image_files:
        return JsonResponse({"error": "No se recibieron imágenes."}, status=400)

    extracted = extract_cardio_data_from_image(image_files)
    if not extracted:
        return JsonResponse({"error": "No se pudieron extraer datos."}, status=422)

    result = {}
    for k, v in extracted.items():
        if hasattr(v, "total_seconds"):
            s = int(v.total_seconds())
            result[k] = f"{s // 3600:02d}:{(s % 3600) // 60:02d}:{s % 60:02d}"
        elif not isinstance(v, (str, int, float, bool, type(None))):
            result[k] = str(v)
        else:
            result[k] = v
    return JsonResponse({"data": result})


@login_required
def training_session_form_view(request):
    """Redirección al formulario unificado de sesión."""
    return redirect("gym:session_form")


@login_required
def session_form_view(request):
    """Vista unificada para registrar sesiones de entrenamiento o cardio."""
    is_staff = getattr(request.user, "is_staff", False)

    if request.method == "POST":
        form = SessionModelForm(
            request.POST, request.FILES,
            user=request.user, is_staff=is_staff,
        )
        if form.is_valid():
            instance = form.save(commit=False)
            if not is_staff:
                instance.user = request.user
            instance.save()
            messages.success(request, "Sesión guardada correctamente.")
            return redirect("gym:session_form")
    else:
        form = SessionModelForm(user=request.user, is_staff=is_staff)

    return render(request, "gym/session_form.html", with_admin_context(request, {
        "form": form,
        "vision_available": is_model_downloaded("llama3.2-vision:11b"),
    }))


@login_required
def session_analyze_view(request):
    """AJAX: analiza imágenes de sesión y devuelve campos extraídos."""
    from django.http import JsonResponse
    from gym.services import extract_session_data_from_image

    if request.method != "POST":
        return JsonResponse({"error": "Método no permitido."}, status=405)
    image_files = request.FILES.getlist("workout_images")
    if not image_files:
        return JsonResponse({"error": "No se recibieron imágenes."}, status=400)

    extracted = extract_session_data_from_image(image_files)
    if not extracted:
        return JsonResponse({"error": "No se pudieron extraer datos."}, status=422)

    result = {}
    for k, v in extracted.items():
        if hasattr(v, "total_seconds"):
            s = int(v.total_seconds())
            result[k] = f"{s // 3600:02d}:{(s % 3600) // 60:02d}:{s % 60:02d}"
        elif not isinstance(v, (str, int, float, bool, type(None))):
            result[k] = str(v)
        else:
            result[k] = v
    return JsonResponse({"data": result})


@login_required
def training_analyze_view(request):
    """AJAX: analiza imágenes de entrenamiento y devuelve campos extraídos."""
    from django.http import JsonResponse
    from gym.services import extract_training_session_data_from_image

    if request.method != "POST":
        return JsonResponse({"error": "Método no permitido."}, status=405)
    image_files = request.FILES.getlist("workout_images")
    if not image_files:
        return JsonResponse({"error": "No se recibieron imágenes."}, status=400)

    extracted = extract_training_session_data_from_image(image_files)
    if not extracted:
        return JsonResponse({"error": "No se pudieron extraer datos."}, status=422)

    result = {}
    for k, v in extracted.items():
        if hasattr(v, "total_seconds"):
            s = int(v.total_seconds())
            result[k] = f"{s // 3600:02d}:{(s % 3600) // 60:02d}:{s % 60:02d}"
        elif not isinstance(v, (str, int, float, bool, type(None))):
            result[k] = str(v)
        else:
            result[k] = v
    return JsonResponse({"data": result})

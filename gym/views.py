import json
from datetime import datetime

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.shortcuts import redirect, render
from django.urls import reverse_lazy
from django.utils import timezone
from django.views.generic import FormView
from unfold.views import UnfoldModelAdminViewMixin

from gym.forms import (
    MusculationRecordFormSet,
    MusculationRecordFormsetHelper,
    MusculationRecordPublicForm,
    RoutineJSONForm,
    TrainingSessionForm,
    TrainingSessionModelForm,
)
from gym.models import MusculationExercise, MusculationRecord, Routine


class MusculationRecordFormsetView(UnfoldModelAdminViewMixin, FormView):
    """Vista para crear múltiples registros de musculación"""

    title = "Registrar Entrenamiento de Musculación"
    form_class = TrainingSessionForm
    success_url = reverse_lazy("admin:gym_musculationrecord_changelist")
    permission_required = ("gym.add_musculationrecord",)
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


class RoutineJSONView(UnfoldModelAdminViewMixin, FormView):
    """Vista para generar rutina desde JSON"""

    title = "Generar Rutina desde JSON"
    form_class = RoutineJSONForm
    success_url = reverse_lazy("admin:gym_routine_changelist")
    permission_required = ("gym.add_routine",)
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
        )

        # Actualizar perfil del usuario con start_date y end_date si están presentes
        from evolveme.models import GymUserProfile

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

        # Procesar ejercicios por día
        routine_data = data.get("routine", {})
        exercises_created = 0
        exercises_added = 0

        for day_key, exercises_list in routine_data.items():
            if not isinstance(exercises_list, list):
                continue

            for exercise_data in exercises_list:
                if not isinstance(exercise_data, dict):
                    continue

                # Obtener o crear ejercicio
                exercise_name = exercise_data.get("name", "").strip()
                if not exercise_name:
                    continue

                exercise, created = MusculationExercise.objects.get_or_create(
                    name=exercise_name,
                    defaults={
                        "description": exercise_data.get("description", ""),
                        "body_part": exercise_data.get("body_part") or None,
                        "sets": exercise_data.get("sets", 0),
                        "reps": exercise_data.get("reps", 0),
                    },
                )

                if created:
                    exercises_created += 1

                # Añadir ejercicio a la rutina
                routine.exercises.add(exercise)
                exercises_added += 1

        messages.success(
            self.request,
            f"Rutina creada correctamente. "
            f"{exercises_created} ejercicio(s) nuevo(s) creado(s), "
            f"{exercises_added} ejercicio(s) añadido(s) a la rutina.",
        )
        return super().form_valid(form)


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

    return render(request, "gym/musculation_record_form.html", {"form": form})


@login_required
def training_session_form_view(request):
    """Vista para el formulario de sesiones de entrenamiento"""
    if request.method == "POST":
        form = TrainingSessionModelForm(request.POST, user=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, "Sesión de entrenamiento guardada correctamente.")
            return redirect("gym:training_session_form")
    else:
        form = TrainingSessionModelForm(user=request.user)

    return render(request, "gym/training_session_form.html", {"form": form})

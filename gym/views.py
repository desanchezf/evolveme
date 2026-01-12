from django.contrib import messages
from django.urls import reverse_lazy
from django.utils import timezone
from django.views.generic import FormView
from unfold.views import UnfoldModelAdminViewMixin

from gym.forms import (
    MusculationRecordFormSet,
    MusculationRecordFormsetHelper,
    TrainingSessionForm,
)
from gym.models import MusculationRecord


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
            formset = MusculationRecordFormSet(
                self.request.POST, prefix="records"
            )
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
        formset = MusculationRecordFormSet(
            self.request.POST, prefix="records"
        )

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
        messages.error(
            self.request, "Por favor, corrige los errores en el formulario."
        )
        return super().form_invalid(form)

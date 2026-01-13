from django import forms
from django.forms import modelformset_factory
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Row, Column
from unfold.widgets import (
    UnfoldAdminTextInputWidget,
    UnfoldAdminSelectWidget,
)

from gym.models import MusculationRecord, MusculationExercise


class MusculationRecordForm(forms.ModelForm):
    """Formulario para un registro de ejercicio de musculación"""

    class Meta:
        model = MusculationRecord
        fields = ["exercise", "sets", "reps", "weight", "tbi", "observation"]
        widgets = {
            "exercise": UnfoldAdminSelectWidget(),
            "sets": UnfoldAdminTextInputWidget(),
            "reps": UnfoldAdminTextInputWidget(),
            "weight": UnfoldAdminTextInputWidget(),
            "tbi": forms.CheckboxInput(attrs={"class": "form-check-input"}),
            "observation": forms.Textarea(attrs={"rows": 2, "class": "form-control"}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Filtrar ejercicios si es necesario
        self.fields["exercise"].queryset = MusculationExercise.objects.all()
        self.fields["exercise"].empty_label = "Selecciona un ejercicio"


class MusculationRecordFormsetHelper(FormHelper):
    """Helper para el formset de registros de musculación"""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.template = "unfold_crispy/layout/table_inline_formset.html"
        self.form_id = "musculation-record-formset"
        self.form_add = True
        self.attrs = {
            "novalidate": "novalidate",
        }
        self.layout = Layout(
            Row(
                Column("exercise", css_class="w-1/3"),
                Column("sets", css_class="w-1/6"),
                Column("reps", css_class="w-1/6"),
                Column("weight", css_class="w-1/6"),
                Column("tbi", css_class="w-1/12"),
            ),
            Row("observation"),
        )


# Formset factory
MusculationRecordFormSet = modelformset_factory(
    MusculationRecord,
    form=MusculationRecordForm,
    extra=1,
    can_delete=True,
    min_num=1,
    validate_min=True,
)


class TrainingSessionForm(forms.Form):
    """Formulario para la sesión de entrenamiento (usuario y fecha)"""

    user = forms.ModelChoiceField(
        queryset=None,
        required=True,
        widget=UnfoldAdminSelectWidget(),
        label="Usuario",
    )
    record_date = forms.DateTimeField(
        required=True,
        widget=forms.DateTimeInput(attrs={"type": "datetime-local", "class": "form-control"}),
        label="Fecha y hora del entrenamiento",
    )

    def __init__(self, *args, **kwargs):
        user = kwargs.pop("user", None)
        super().__init__(*args, **kwargs)
        from django.contrib.auth.models import User

        self.fields["user"].queryset = User.objects.all()
        if user:
            self.fields["user"].initial = user
            self.fields["user"].widget.attrs["readonly"] = True


class RoutineJSONForm(forms.Form):
    """Formulario para generar rutina desde JSON"""

    json_data = forms.CharField(
        widget=forms.Textarea(
            attrs={
                "rows": 20,
                "class": "form-control",
                "placeholder": 'Pega aquí el JSON generado por la IA. Ejemplo:\n{\n  "user": "david",\n  "start_date": "01/01/2026 08:00",\n  "end_date": "01/02/2026 08:00",\n  "warmup": "Calentamiento...",\n  "exercise_types": ["push", "pull"],\n  "routine": {...}\n}',
            }
        ),
        label="JSON de la Rutina",
        help_text="Pega el JSON generado por la IA siguiendo el formato de gym_response.txt",
        required=True,
    )

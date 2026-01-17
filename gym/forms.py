from django import forms
from django.contrib.auth.models import User
from django.forms import modelformset_factory
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Row, Column
from unfold.widgets import (
    UnfoldAdminTextInputWidget,
    UnfoldAdminSelectWidget,
)

from gym.models import (
    MusculationRecord,
    MusculationExercise,
    Routine,
    TrainingSession,
)
from gym.widgets import ExerciseTypesCheckboxWidget


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


class MusculationRecordAdminForm(forms.ModelForm):
    """Formulario personalizado para el admin de MusculationRecord"""

    class Meta:
        model = MusculationRecord
        fields = "__all__"
        widgets = {
            "record_date": forms.DateTimeInput(
                attrs={
                    "type": "datetime-local",
                    "class": "form-control",
                    "placeholder": "YYYY-MM-DDTHH:MM",
                }
            ),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Configurar widget de fecha/hora
        self.fields["record_date"].widget = forms.DateTimeInput(
            attrs={
                "type": "datetime-local",
                "class": "form-control",
                "placeholder": "YYYY-MM-DDTHH:MM",
            }
        )

        # Formatear el valor inicial si existe
        if self.instance and self.instance.pk:
            if self.instance.record_date:
                self.fields["record_date"].initial = self.instance.record_date.strftime(
                    "%Y-%m-%dT%H:%M"
                )


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
        widget=forms.DateTimeInput(
            attrs={"type": "datetime-local", "class": "form-control"}
        ),
        label="Fecha y hora del entrenamiento",
    )

    def __init__(self, *args, **kwargs):
        user = kwargs.pop("user", None)
        super().__init__(*args, **kwargs)

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
                "placeholder": 'Pega aquí el JSON generado por la IA. Ejemplo:\n{\n  "user": "david",\n  "duration": "1 12:30:00",\n  "warmup": "Calentamiento...",\n  "exercise_types": ["push", "pull"],\n  "routine": {...}\n}',
            }
        ),
        label="JSON de la Rutina",
        help_text="Pega el JSON generado por la IA siguiendo el formato de gym_response.txt. "
        "Opcionalmente puedes incluir 'start_date' y 'end_date' para actualizar el perfil del usuario.",
        required=True,
    )


class RoutineAdminForm(forms.ModelForm):
    """Formulario personalizado para el admin de Routine que maneja exercise_types"""

    class Meta:
        model = Routine
        fields = "__all__"
        widgets = {
            "exercise_types": ExerciseTypesCheckboxWidget(),
            "duration": forms.TextInput(
                attrs={
                    "type": "text",
                    "class": "form-control",
                    "placeholder": "DD HH:MM:SS o HH:MM:SS (ej: 1 12:30:00)",
                }
            ),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Asegurar que el widget esté configurado
        self.fields["exercise_types"].widget = ExerciseTypesCheckboxWidget()

        # Asegurar que el valor inicial del campo sea una lista si existe
        if self.instance and self.instance.pk:
            if (
                hasattr(self.instance, "exercise_types")
                and self.instance.exercise_types
            ):
                # El valor ya debería ser una lista desde el modelo
                # Pero asegurémonos de que el campo lo maneje correctamente
                if not isinstance(self.instance.exercise_types, list):
                    # Si por alguna razón no es una lista, convertirla
                    import json

                    if isinstance(self.instance.exercise_types, str):
                        try:
                            self.instance.exercise_types = json.loads(
                                self.instance.exercise_types
                            )
                        except (json.JSONDecodeError, ValueError):
                            self.instance.exercise_types = []

        # Configurar widget de duración
        self.fields["duration"].widget = forms.TextInput(
            attrs={
                "type": "text",
                "class": "form-control",
                "placeholder": "DD HH:MM:SS o HH:MM:SS (ej: 1 12:30:00)",
            }
        )
        self.fields["duration"].help_text = (
            "Formato: DD HH:MM:SS o HH:MM:SS. "
            "Ejemplo: '1 12:30:00' (1 día, 12 horas, 30 minutos) o '02:30:00' (2 horas, 30 minutos)"
        )

    def clean_exercise_types(self):
        """Limpia y valida los tipos de ejercicios seleccionados"""
        # El widget devuelve directamente una lista desde value_from_datadict
        data = self.cleaned_data.get("exercise_types", [])

        # Asegurar que sea una lista
        if not isinstance(data, list):
            data = []

        return data


class TrainingSessionAdminForm(forms.ModelForm):
    """Formulario personalizado para el admin de TrainingSession"""

    class Meta:
        model = TrainingSession
        fields = "__all__"
        widgets = {
            "session_date": forms.DateTimeInput(
                attrs={
                    "type": "datetime-local",
                    "class": "form-control",
                    "placeholder": "YYYY-MM-DDTHH:MM",
                }
            ),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Configurar widget de fecha/hora
        self.fields["session_date"].widget = forms.DateTimeInput(
            attrs={
                "type": "datetime-local",
                "class": "form-control",
                "placeholder": "YYYY-MM-DDTHH:MM",
            }
        )

        # Formatear el valor inicial si existe
        if self.instance and self.instance.pk:
            if self.instance.session_date:
                self.fields[
                    "session_date"
                ].initial = self.instance.session_date.strftime("%Y-%m-%dT%H:%M")

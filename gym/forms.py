from django import forms
from django.contrib.auth.models import User
from django.forms import modelformset_factory
from django.utils.dateparse import parse_duration
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Row, Column, Submit
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
        self.helper = FormHelper()
        self.helper.layout = Layout(
            Row(Column("exercise", css_class="w-full")),
            Row(
                Column("sets", css_class="w-1/3"),
                Column("reps", css_class="w-1/3"),
                Column("weight", css_class="w-1/3"),
            ),
            Row(Column("tbi", css_class="w-full")),
            Row(Column("observation", css_class="w-full")),
        )


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
        self.helper = FormHelper()
        self.helper.layout = Layout(
            Row(
                Column("user", css_class="w-1/2"),
                Column("record_date", css_class="w-1/2"),
            ),
        )


class RoutineJSONForm(forms.Form):
    """Formulario para generar rutina desde JSON"""

    json_data = forms.CharField(
        widget=forms.Textarea(
            attrs={
                "rows": 20,
                "class": "form-control",
                "placeholder": 'Pega aquí el JSON generado por la IA. Ejemplo:\n{\n  "user": "david",\n  "duration": 4,\n  "warmup": "Calentamiento...",\n  "exercise_types": ["push", "pull"],\n  "routine": {...}\n}',
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
            "duration": forms.NumberInput(
                attrs={
                    "type": "number",
                    "class": "form-control",
                    "placeholder": "Número de semanas (ej: 4)",
                    "min": "1",
                    "step": "1",
                }
            ),
            "warmup_duration": forms.TextInput(
                attrs={
                    "type": "text",
                    "class": "form-control",
                    "placeholder": "HH:MM (ej: 00:15)",
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

        # Configurar widget de duración (en semanas)
        self.fields["duration"].widget = forms.NumberInput(
            attrs={
                "type": "number",
                "class": "form-control",
                "placeholder": "Número de semanas (ej: 4)",
                "min": "1",
                "step": "1",
            }
        )
        self.fields["duration"].help_text = (
            "Duración de la rutina en semanas. "
            "Ejemplo: '4' (4 semanas) o '8' (8 semanas)"
        )

        # Configurar widget de duración de calentamiento
        if "warmup_duration" in self.fields:
            self.fields["warmup_duration"].widget = forms.TextInput(
                attrs={
                    "type": "text",
                    "class": "form-control",
                    "placeholder": "HH:MM (ej: 00:15)",
                }
            )
            self.fields["warmup_duration"].help_text = (
                "Formato: HH:MM (solo horas y minutos, los segundos se establecen en 0). "
                "Ejemplo: '00:15' (15 minutos) o '00:30' (30 minutos)"
            )

    def clean_exercise_types(self):
        """Limpia y valida los tipos de ejercicios seleccionados"""
        # El widget devuelve directamente una lista desde value_from_datadict
        data = self.cleaned_data.get("exercise_types", [])

        # Asegurar que sea una lista
        if not isinstance(data, list):
            data = []

        return data

    def clean_warmup_duration(self):
        """Limpia y valida warmup_duration, convirtiendo HH:MM a HH:MM:00"""
        warmup_duration = self.cleaned_data.get("warmup_duration")
        
        if not warmup_duration:
            return None
        
        # Si ya es un timedelta, devolverlo directamente
        if hasattr(warmup_duration, 'total_seconds'):
            return warmup_duration
        
        # Si es una cadena, procesarla
        if isinstance(warmup_duration, str):
            warmup_duration = warmup_duration.strip()
            
            # Si está vacío, devolver None
            if not warmup_duration:
                return None
            
            # Si ya tiene formato HH:MM:SS, parsearlo directamente
            if warmup_duration.count(':') == 2:
                parsed = parse_duration(warmup_duration)
                if parsed:
                    return parsed
            
            # Si tiene formato HH:MM, agregar :00 para los segundos
            elif warmup_duration.count(':') == 1:
                try:
                    # Validar formato HH:MM
                    parts = warmup_duration.split(':')
                    if len(parts) == 2:
                        hours = int(parts[0])
                        minutes = int(parts[1])
                        # Convertir a formato HH:MM:00 y parsear
                        formatted = f"{hours:02d}:{minutes:02d}:00"
                        parsed = parse_duration(formatted)
                        if parsed:
                            return parsed
                except (ValueError, IndexError):
                    pass
            
            # Intentar parsear como está (por si acaso)
            parsed = parse_duration(warmup_duration)
            if parsed:
                return parsed
        
        # Si no se pudo parsear, devolver el valor original
        return warmup_duration


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


class TrainingSessionModelForm(forms.ModelForm):
    """Formulario público para registrar sesiones de entrenamiento"""

    class Meta:
        model = TrainingSession
        fields = [
            "user",
            "routine",
            "session_date",
            "location",
            "workout_time",
            "active_kilocalories",
            "total_kilocalories",
            "avg_heart_rate",
        ]
        widgets = {
            "user": forms.Select(attrs={"class": "form-control"}),
            "routine": forms.Select(attrs={"class": "form-control"}),
            "session_date": forms.DateTimeInput(
                attrs={
                    "type": "datetime-local",
                    "class": "form-control",
                    "placeholder": "YYYY-MM-DDTHH:MM",
                }
            ),
            "location": forms.TextInput(attrs={"class": "form-control"}),
            "workout_time": forms.TextInput(
                attrs={"class": "form-control", "placeholder": "HH:MM:SS"}
            ),
            "active_kilocalories": forms.NumberInput(attrs={"class": "form-control"}),
            "total_kilocalories": forms.NumberInput(attrs={"class": "form-control"}),
            "avg_heart_rate": forms.NumberInput(attrs={"class": "form-control"}),
        }

    def __init__(self, *args, **kwargs):
        user = kwargs.pop("user", None)
        super().__init__(*args, **kwargs)
        self.fields["user"].queryset = User.objects.all()
        self.fields["routine"].queryset = Routine.objects.all()
        if user:
            self.fields["user"].initial = user
        self.helper = FormHelper()
        self.helper.layout = Layout(
            Row(
                Column("user", css_class="w-1/2"), Column("routine", css_class="w-1/2")
            ),
            Row(Column("session_date", css_class="w-full")),
            Row(Column("location", css_class="w-full")),
            Row(Column("workout_time", css_class="w-1/3")),
            Row(
                Column("active_kilocalories", css_class="w-1/3"),
                Column("total_kilocalories", css_class="w-1/3"),
                Column("avg_heart_rate", css_class="w-1/3"),
            ),
            Submit("submit", "Guardar Sesión", css_class="btn btn-primary"),
        )


class MusculationRecordPublicForm(forms.ModelForm):
    """Formulario público para registrar un ejercicio de musculación"""

    class Meta:
        model = MusculationRecord
        fields = [
            "user",
            "exercise",
            "sets",
            "reps",
            "weight",
            "tbi",
            "observation",
            "record_date",
        ]
        widgets = {
            "user": forms.Select(attrs={"class": "form-control"}),
            "exercise": forms.Select(attrs={"class": "form-control"}),
            "sets": forms.NumberInput(attrs={"class": "form-control"}),
            "reps": forms.NumberInput(attrs={"class": "form-control"}),
            "weight": forms.NumberInput(attrs={"class": "form-control", "step": "0.1"}),
            "tbi": forms.CheckboxInput(attrs={"class": "form-check-input"}),
            "observation": forms.Textarea(attrs={"rows": 3, "class": "form-control"}),
            "record_date": forms.DateTimeInput(
                attrs={
                    "type": "datetime-local",
                    "class": "form-control",
                    "placeholder": "YYYY-MM-DDTHH:MM",
                }
            ),
        }

    def __init__(self, *args, **kwargs):
        user = kwargs.pop("user", None)
        super().__init__(*args, **kwargs)
        self.fields["user"].queryset = User.objects.all()
        self.fields["exercise"].queryset = MusculationExercise.objects.all()
        if user:
            self.fields["user"].initial = user
        self.helper = FormHelper()
        self.helper.layout = Layout(
            Row(
                Column("user", css_class="w-1/2"),
                Column("record_date", css_class="w-1/2"),
            ),
            Row(Column("exercise", css_class="w-full")),
            Row(
                Column("sets", css_class="w-1/3"),
                Column("reps", css_class="w-1/3"),
                Column("weight", css_class="w-1/3"),
            ),
            Row(Column("tbi", css_class="w-full")),
            Row(Column("observation", css_class="w-full")),
            Submit("submit", "Guardar Registro", css_class="btn btn-primary"),
        )

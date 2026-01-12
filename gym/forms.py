from django import forms
from django.forms import modelformset_factory
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Row, Column
from unfold.widgets import (
    UnfoldAdminTextInputWidget,
    UnfoldAdminSelectWidget,
    UnfoldAdminDateInputWidget,
    UnfoldAdminCheckboxInputWidget,
    UnfoldAdminTextareaWidget,
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
            "tbi": UnfoldAdminCheckboxInputWidget(),
            "observation": UnfoldAdminTextareaWidget(attrs={"rows": 2}),
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
        widget=UnfoldAdminDateInputWidget(),
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

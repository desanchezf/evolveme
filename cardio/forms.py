from django import forms
from django.contrib.auth.models import User
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Row, Column

from cardio.models import CardioExercise, CardioSession


class CardioSessionAdminForm(forms.ModelForm):
    """Formulario personalizado para el admin de CardioSession"""

    class Meta:
        model = CardioSession
        fields = "__all__"
        widgets = {
            "date": forms.DateInput(
                attrs={
                    "type": "date",
                    "class": "form-control",
                    "placeholder": "YYYY-MM-DD",
                }
            ),
            "session_start": forms.DateTimeInput(
                attrs={
                    "type": "datetime-local",
                    "class": "form-control",
                    "placeholder": "YYYY-MM-DDTHH:MM",
                }
            ),
            "session_end": forms.DateTimeInput(
                attrs={
                    "type": "datetime-local",
                    "class": "form-control",
                    "placeholder": "YYYY-MM-DDTHH:MM",
                }
            ),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Configurar widgets de fecha
        self.fields["date"].widget = forms.DateInput(
            attrs={
                "type": "date",
                "class": "form-control",
                "placeholder": "YYYY-MM-DD",
            }
        )
        self.fields["session_start"].widget = forms.DateTimeInput(
            attrs={
                "type": "datetime-local",
                "class": "form-control",
                "placeholder": "YYYY-MM-DDTHH:MM",
            }
        )
        self.fields["session_end"].widget = forms.DateTimeInput(
            attrs={
                "type": "datetime-local",
                "class": "form-control",
                "placeholder": "YYYY-MM-DDTHH:MM",
            }
        )

        # Formatear valores iniciales si existen
        if self.instance and self.instance.pk:
            if self.instance.date:
                self.fields["date"].initial = self.instance.date.strftime("%Y-%m-%d")
            if self.instance.session_start:
                self.fields[
                    "session_start"
                ].initial = self.instance.session_start.strftime("%Y-%m-%dT%H:%M")
                if self.instance.session_end:
                    self.fields[
                        "session_end"
                    ].initial = self.instance.session_end.strftime("%Y-%m-%dT%H:%M")


class CardioSessionForm(forms.ModelForm):
    """Formulario público para registrar sesiones de cardio"""

    class Meta:
        model = CardioSession
        fields = [
            "user",
            "exercise",
            "date",
            "session_start",
            "session_end",
            "location",
            "workout_time",
            "distance",
            "avg_speed",
            "active_calories",
            "total_calories",
            "elevation_gain",
            "average_heart_rate",
        ]
        widgets = {
            "user": forms.Select(attrs={"class": "form-control"}),
            "exercise": forms.Select(attrs={"class": "form-control"}),
            "date": forms.DateInput(
                attrs={
                    "type": "date",
                    "class": "form-control",
                    "placeholder": "YYYY-MM-DD",
                }
            ),
            "session_start": forms.DateTimeInput(
                attrs={
                    "type": "datetime-local",
                    "class": "form-control",
                    "placeholder": "YYYY-MM-DDTHH:MM",
                }
            ),
            "session_end": forms.DateTimeInput(
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
            "distance": forms.NumberInput(
                attrs={"class": "form-control", "step": "0.01"}
            ),
            "avg_speed": forms.NumberInput(
                attrs={"class": "form-control", "step": "0.01"}
            ),
            "active_calories": forms.NumberInput(attrs={"class": "form-control"}),
            "total_calories": forms.NumberInput(attrs={"class": "form-control"}),
            "elevation_gain": forms.NumberInput(attrs={"class": "form-control"}),
            "average_heart_rate": forms.NumberInput(attrs={"class": "form-control"}),
        }

    def __init__(self, *args, **kwargs):
        user = kwargs.pop("user", None)
        super().__init__(*args, **kwargs)
        self.fields["user"].queryset = User.objects.all()
        self.fields["exercise"].queryset = CardioExercise.objects.all()
        if user:
            self.fields["user"].initial = user
        self.helper = FormHelper()
        self.helper.layout = Layout(
            Row(
                Column("user", css_class="col-md-6"),
                Column("exercise", css_class="col-md-6"),
                css_class="mb-3",
            ),
            Row(Column("date", css_class="col-12"), css_class="mb-3"),
            Row(
                Column("session_start", css_class="col-md-6"),
                Column("session_end", css_class="col-md-6"),
                css_class="mb-3",
            ),
            Row(Column("location", css_class="col-12"), css_class="mb-3"),
            Row(
                Column("workout_time", css_class="col-md-4"),
                Column("distance", css_class="col-md-4"),
                Column("avg_speed", css_class="col-md-4"),
                css_class="mb-3",
            ),
            Row(
                Column("active_calories", css_class="col-md-6"),
                Column("total_calories", css_class="col-md-6"),
                css_class="mb-3",
            ),
            Row(
                Column("elevation_gain", css_class="col-md-6"),
                Column("average_heart_rate", css_class="col-md-6"),
                css_class="mb-3",
            ),
        )

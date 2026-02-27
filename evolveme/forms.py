from django import forms
from django.contrib.auth.models import User
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Row, Column, Submit

from evolveme.models import GymUserProfile, Measure


class GymUserProfileAdminForm(forms.ModelForm):
    """Formulario personalizado para el admin de GymUserProfile"""

    class Meta:
        model = GymUserProfile
        fields = "__all__"
        widgets = {
            "birth_date": forms.DateInput(
                attrs={
                    "type": "date",
                    "class": "form-control",
                    "placeholder": "YYYY-MM-DD",
                }
            ),
            "start_date": forms.DateInput(
                attrs={
                    "type": "date",
                    "class": "form-control",
                    "placeholder": "YYYY-MM-DD",
                }
            ),
            "end_date": forms.DateInput(
                attrs={
                    "type": "date",
                    "class": "form-control",
                    "placeholder": "YYYY-MM-DD",
                }
            ),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Configurar widgets de fecha
        self.fields["birth_date"].widget = forms.DateInput(
            attrs={
                "type": "date",
                "class": "form-control",
                "placeholder": "YYYY-MM-DD",
            }
        )
        self.fields["start_date"].widget = forms.DateInput(
            attrs={
                "type": "date",
                "class": "form-control",
                "placeholder": "YYYY-MM-DD",
            }
        )
        self.fields["end_date"].widget = forms.DateInput(
            attrs={
                "type": "date",
                "class": "form-control",
                "placeholder": "YYYY-MM-DD",
            }
        )

        # Formatear el valor inicial si existe
        if self.instance and self.instance.pk:
            if self.instance.birth_date:
                self.fields["birth_date"].initial = self.instance.birth_date.strftime(
                    "%Y-%m-%d"
                )
            if self.instance.start_date:
                self.fields["start_date"].initial = self.instance.start_date.strftime(
                    "%Y-%m-%d"
                )
            if self.instance.end_date:
                self.fields["end_date"].initial = self.instance.end_date.strftime(
                    "%Y-%m-%d"
                )


class MeasureAdminForm(forms.ModelForm):
    """Formulario personalizado para el admin de Measure"""

    class Meta:
        model = Measure
        fields = "__all__"
        widgets = {
            "date": forms.DateInput(
                attrs={
                    "type": "date",
                    "class": "form-control",
                    "placeholder": "YYYY-MM-DD",
                }
            ),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Configurar widget de fecha
        self.fields["date"].widget = forms.DateInput(
            attrs={
                "type": "date",
                "class": "form-control",
                "placeholder": "YYYY-MM-DD",
            }
        )

        # Formatear el valor inicial si existe
        if self.instance and self.instance.pk:
            if self.instance.date:
                self.fields["date"].initial = self.instance.date.strftime("%Y-%m-%d")


class MeasureForm(forms.ModelForm):
    """Formulario público para registrar medidas corporales"""

    class Meta:
        model = Measure
        fields = [
            "user",
            "date",
            "weight",
            "arm",
            "arm_relaxed",
            "chest",
            "waist",
            "leg",
            "leg_relaxed",
        ]
        widgets = {
            "user": forms.Select(attrs={"class": "form-control"}),
            "date": forms.DateInput(
                attrs={
                    "type": "date",
                    "class": "form-control",
                    "placeholder": "YYYY-MM-DD",
                }
            ),
            "weight": forms.NumberInput(attrs={"class": "form-control", "step": "0.1"}),
            "arm": forms.NumberInput(attrs={"class": "form-control", "step": "0.1"}),
            "arm_relaxed": forms.NumberInput(
                attrs={"class": "form-control", "step": "0.1"}
            ),
            "chest": forms.NumberInput(attrs={"class": "form-control", "step": "0.1"}),
            "waist": forms.NumberInput(attrs={"class": "form-control", "step": "0.1"}),
            "leg": forms.NumberInput(attrs={"class": "form-control", "step": "0.1"}),
            "leg_relaxed": forms.NumberInput(
                attrs={"class": "form-control", "step": "0.1"}
            ),
        }

    def __init__(self, *args, **kwargs):
        user = kwargs.pop("user", None)
        super().__init__(*args, **kwargs)
        self.fields["user"].queryset = User.objects.all()
        if user:
            self.fields["user"].initial = user
        self.helper = FormHelper()
        self.helper.layout = Layout(
            Row(Column("user", css_class="w-1/2"), Column("date", css_class="w-1/2")),
            Row(Column("weight", css_class="w-full")),
            Row(
                Column("arm", css_class="w-1/2"),
                Column("arm_relaxed", css_class="w-1/2"),
            ),
            Row(Column("chest", css_class="w-full")),
            Row(Column("waist", css_class="w-full")),
            Row(
                Column("leg", css_class="w-1/2"),
                Column("leg_relaxed", css_class="w-1/2"),
            ),
            Submit("submit", "Guardar Medidas", css_class="btn btn-primary"),
        )

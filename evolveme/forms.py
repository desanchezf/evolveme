from django import forms
from django.contrib.auth.models import User
from crispy_forms.helper import FormHelper

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


class GymUserProfileForm(forms.ModelForm):
    """Formulario público para editar el perfil del usuario."""

    class Meta:
        model = GymUserProfile
        fields = ["user", "birth_date", "gender", "height", "objective", "active_routine", "start_date", "end_date"]
        widgets = {
            "user": forms.Select(attrs={"class": "form-select"}),
            "birth_date": forms.DateInput(attrs={"type": "date", "class": "form-control"}),
            "gender": forms.Select(attrs={"class": "form-select"}),
            "height": forms.NumberInput(attrs={"class": "form-control", "step": "0.1"}),
            "objective": forms.Select(attrs={"class": "form-select"}),
            "active_routine": forms.Select(attrs={"class": "form-select"}),
            "start_date": forms.DateInput(attrs={"type": "date", "class": "form-control"}),
            "end_date": forms.DateInput(attrs={"type": "date", "class": "form-control"}),
        }

    def __init__(self, *args, **kwargs):
        user = kwargs.pop("user", None)
        super().__init__(*args, **kwargs)
        from gym.models import Routine
        self.fields["user"].queryset = User.objects.all()
        self.fields["active_routine"].queryset = Routine.objects.all()
        self.fields["active_routine"].required = False
        if user:
            self.fields["user"].initial = user
            self.fields["active_routine"].queryset = Routine.objects.filter(user=user)
        self.helper = FormHelper()
        self.helper.form_tag = False


_NUM1 = {"class": "form-control", "step": "0.1"}
_NUM01 = {"class": "form-control", "step": "0.01"}


class MeasureForm(forms.ModelForm):
    """Formulario público para registrar medidas corporales."""

    class Meta:
        model = Measure
        fields = [
            "user", "date",
            # Báscula inteligente
            "weight", "fat_perc", "muscle_mass", "bmi",
            "body_water_mass", "body_water_percentage", "fat_mass",
            "bone_mineral_content", "protein_mass", "muscle_percentage",
            "skeletal_muscle_mass", "visceral_fat_rating",
            "basal_metabolic_rate", "body_age",
            # Perímetros
            "waist", "chest", "arm", "arm_relaxed", "leg", "leg_relaxed",
        ]
        widgets = {
            "user": forms.Select(attrs={"class": "form-select"}),
            "date": forms.DateInput(
                attrs={"type": "date", "class": "form-control"}
            ),
            "weight": forms.NumberInput(attrs=_NUM1),
            "fat_perc": forms.NumberInput(attrs=_NUM1),
            "muscle_mass": forms.NumberInput(attrs=_NUM1),
            "bmi": forms.NumberInput(attrs=_NUM01),
            "body_water_mass": forms.NumberInput(attrs=_NUM1),
            "body_water_percentage": forms.NumberInput(attrs=_NUM1),
            "fat_mass": forms.NumberInput(attrs=_NUM1),
            "bone_mineral_content": forms.NumberInput(attrs=_NUM01),
            "protein_mass": forms.NumberInput(attrs=_NUM1),
            "muscle_percentage": forms.NumberInput(attrs=_NUM1),
            "skeletal_muscle_mass": forms.NumberInput(attrs=_NUM1),
            "visceral_fat_rating": forms.NumberInput(attrs=_NUM01),
            "basal_metabolic_rate": forms.NumberInput(attrs=_NUM1),
            "body_age": forms.NumberInput(attrs={"class": "form-control"}),
            "waist": forms.NumberInput(attrs=_NUM1),
            "chest": forms.NumberInput(attrs=_NUM1),
            "arm": forms.NumberInput(attrs=_NUM1),
            "arm_relaxed": forms.NumberInput(attrs=_NUM1),
            "leg": forms.NumberInput(attrs=_NUM1),
            "leg_relaxed": forms.NumberInput(attrs=_NUM1),
        }

    def __init__(self, *args, **kwargs):
        user = kwargs.pop("user", None)
        super().__init__(*args, **kwargs)
        self.fields["user"].queryset = User.objects.all()
        if user:
            self.fields["user"].initial = user
        self.helper = FormHelper()
        self.helper.form_tag = False

from django import forms

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

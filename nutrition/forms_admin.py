from django import forms

from nutrition.models import DailyDiet


class DailyDietAdminForm(forms.ModelForm):
    """Formulario personalizado para el admin de DailyDiet"""

    class Meta:
        model = DailyDiet
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

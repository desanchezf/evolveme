from django import forms

from cardio.models import CardioSession


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
                self.fields["session_start"].initial = (
                    self.instance.session_start.strftime("%Y-%m-%dT%H:%M")
                )
            if self.instance.session_end:
                self.fields["session_end"].initial = (
                    self.instance.session_end.strftime("%Y-%m-%dT%H:%M")
                )

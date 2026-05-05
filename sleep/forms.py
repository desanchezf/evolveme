from django import forms
from django.contrib.auth.models import User
from crispy_forms.helper import FormHelper

from sleep.models import SleepRecord


class SleepRecordForm(forms.ModelForm):
    class Meta:
        model = SleepRecord
        fields = [
            "user",
            "date",
            "sleep_start",
            "sleep_end",
            "total_sleep_time",
            "awake_time",
            "rem_time",
            "core_time",
            "deep_time",
            "notes",
        ]
        widgets = {
            "user": forms.Select(attrs={"class": "form-control"}),
            "date": forms.DateInput(attrs={"type": "date", "class": "form-control"}),
            "sleep_start": forms.DateTimeInput(
                attrs={"type": "datetime-local", "class": "form-control"}
            ),
            "sleep_end": forms.DateTimeInput(
                attrs={"type": "datetime-local", "class": "form-control"}
            ),
            "total_sleep_time": forms.TextInput(
                attrs={"class": "form-control", "placeholder": "HH:MM:SS"}
            ),
            "awake_time": forms.TextInput(
                attrs={"class": "form-control", "placeholder": "HH:MM:SS"}
            ),
            "rem_time": forms.TextInput(
                attrs={"class": "form-control", "placeholder": "HH:MM:SS"}
            ),
            "core_time": forms.TextInput(
                attrs={"class": "form-control", "placeholder": "HH:MM:SS"}
            ),
            "deep_time": forms.TextInput(
                attrs={"class": "form-control", "placeholder": "HH:MM:SS"}
            ),
            "notes": forms.Textarea(attrs={"rows": 3, "class": "form-control"}),
        }

    def __init__(self, *args, **kwargs):
        user = kwargs.pop("user", None)
        super().__init__(*args, **kwargs)
        self.fields["user"].queryset = User.objects.all()
        if user:
            self.fields["user"].initial = user
        self.helper = FormHelper()
        self.helper.form_tag = False

from django import forms
from django.forms import modelformset_factory
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Row, Column, Submit
from unfold.widgets import (
    UnfoldAdminTextInputWidget,
    UnfoldAdminSelectWidget,
)

from nutrition.models import DailyDiet, ProductQuantity, Product


class ProductQuantityForm(forms.ModelForm):
    """Formulario para cantidad de producto"""

    class Meta:
        model = ProductQuantity
        fields = ["product", "quantity", "unit"]
        widgets = {
            "product": UnfoldAdminSelectWidget(),
            "quantity": UnfoldAdminTextInputWidget(),
            "unit": UnfoldAdminTextInputWidget(),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["product"].queryset = Product.objects.all()
        self.fields["product"].empty_label = "Selecciona un producto"
        self.fields["unit"].initial = "g"  # Unidad por defecto


class ProductQuantityFormsetHelper(FormHelper):
    """Helper para el formset de productos"""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.template = "unfold_crispy/layout/table_inline_formset.html"
        self.form_id = "product-quantity-formset"
        self.form_add = True
        self.attrs = {
            "novalidate": "novalidate",
        }
        self.layout = Layout(
            Row(
                Column("product", css_class="w-1/2"),
                Column("quantity", css_class="w-1/4"),
                Column("unit", css_class="w-1/4"),
            ),
        )


# Formset factory
ProductQuantityFormSet = modelformset_factory(
    ProductQuantity,
    form=ProductQuantityForm,
    extra=1,
    can_delete=True,
    min_num=1,
    validate_min=True,
)


class DailyDietForm(forms.Form):
    """Formulario para la dieta diaria (usuario y fecha)"""

    user = forms.ModelChoiceField(
        queryset=None,
        required=True,
        widget=UnfoldAdminSelectWidget(),
        label="Usuario",
    )
    date = forms.DateField(
        required=True,
        widget=forms.DateInput(attrs={"type": "date", "class": "form-control"}),
        label="Fecha",
    )

    def __init__(self, *args, **kwargs):
        user = kwargs.pop("user", None)
        super().__init__(*args, **kwargs)
        from django.contrib.auth.models import User

        self.fields["user"].queryset = User.objects.all()
        if user:
            self.fields["user"].initial = user
            self.fields["user"].widget.attrs["readonly"] = True


class DietJSONForm(forms.Form):
    """Formulario para generar dieta semanal desde JSON"""

    json_data = forms.CharField(
        widget=forms.Textarea(
            attrs={
                "rows": 20,
                "class": "form-control",
                "placeholder": 'Pega aquí el JSON generado por la IA. Ejemplo:\n{\n  "user": "david",\n  "week_start_date": "01/01/2026",\n  "diet": {\n    "monday": {...},\n    "tuesday": {...}\n  }\n}',
            }
        ),
        label="JSON de la Dieta Semanal",
        help_text="Pega el JSON generado por la IA siguiendo el formato de nutrition_response.txt",
        required=True,
    )


class ProductForm(forms.ModelForm):
    """Formulario público para registrar productos"""

    class Meta:
        model = Product
        fields = [
            "name",
            "description",
            "barcode",
            "market",
            "calories_per_100g",
            "protein_per_100g",
            "carbs_per_100g",
            "fat_per_100g",
        ]
        widgets = {
            "name": forms.TextInput(attrs={"class": "form-control"}),
            "description": forms.Textarea(attrs={"rows": 3, "class": "form-control"}),
            "barcode": forms.TextInput(attrs={"class": "form-control"}),
            "market": forms.Select(attrs={"class": "form-control"}),
            "calories_per_100g": forms.NumberInput(attrs={"class": "form-control", "step": "0.01"}),
            "protein_per_100g": forms.NumberInput(attrs={"class": "form-control", "step": "0.01"}),
            "carbs_per_100g": forms.NumberInput(attrs={"class": "form-control", "step": "0.01"}),
            "fat_per_100g": forms.NumberInput(attrs={"class": "form-control", "step": "0.01"}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            Row(Column("name", css_class="w-full")),
            Row(Column("description", css_class="w-full")),
            Row(
                Column("barcode", css_class="w-1/2"),
                Column("market", css_class="w-1/2"),
            ),
            Row(
                Column("calories_per_100g", css_class="w-1/4"),
                Column("protein_per_100g", css_class="w-1/4"),
                Column("carbs_per_100g", css_class="w-1/4"),
                Column("fat_per_100g", css_class="w-1/4"),
            ),
            Submit("submit", "Guardar Producto", css_class="btn btn-primary"),
        )

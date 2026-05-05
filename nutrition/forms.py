from django import forms
from django.forms import modelformset_factory
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Row, Column

from nutrition.models import DailyDiet, ProductQuantity, Product


class ProductQuantityForm(forms.ModelForm):
    """Formulario para cantidad de producto"""

    class Meta:
        model = ProductQuantity
        fields = ["product", "quantity", "unit"]
        widgets = {
            "product": forms.Select(attrs={"class": "form-select"}),
            "quantity": forms.NumberInput(attrs={"class": "form-control"}),
            "unit": forms.TextInput(attrs={"class": "form-control"}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["product"].queryset = Product.objects.all()
        self.fields["product"].empty_label = "Selecciona un producto"
        self.fields["unit"].initial = "g"  # Unidad por defecto


class ProductQuantityFormsetHelper(FormHelper):
    """Helper para el formset de productos: Producto en una fila, Cantidad y Unidad en la siguiente."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.form_tag = False
        self.form_id = "product-quantity-formset"
        self.form_add = True
        self.attrs = {
            "novalidate": "novalidate",
        }
        self.layout = Layout(
            Row(Column("product", css_class="col-12"), css_class="mb-2"),
            Row(
                Column("quantity", css_class="col-md-4"),
                Column("unit", css_class="col-md-4"),
                css_class="mb-3",
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
        widget=forms.Select(attrs={"class": "form-select"}),
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

        self.helper = FormHelper()
        self.helper.form_tag = False
        self.helper.layout = Layout(
            Row(
                Column("user", css_class="col-md-6"),
                Column("date", css_class="col-md-6"),
                css_class="mb-3",
            ),
        )


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


_NUM = {"class": "form-control", "step": "0.01"}


class ProductForm(forms.ModelForm):
    """Formulario público para registrar productos."""

    class Meta:
        model = Product
        fields = [
            "name", "description", "barcode", "market", "stock",
            "energy_kj_per_100g",
            "calories_per_100g", "protein_per_100g", "carbs_per_100g", "fat_per_100g",
            "saturated_fat_per_100g", "sugars_per_100g", "fiber_per_100g", "salt_per_100g",
            "monounsaturated_fat_per_100g", "polyunsaturated_fat_per_100g",
            "polyols_per_100g", "omega3_epa_dha_per_100g",
            "thiamine_b1_per_100g", "phosphorus_per_100g",
            "magnesium_per_100g", "iron_per_100g", "zinc_per_100g",
        ]
        widgets = {
            "name": forms.TextInput(attrs={"class": "form-control", "id": "id_name"}),
            "description": forms.Textarea(attrs={"rows": 2, "class": "form-control"}),
            "barcode": forms.TextInput(attrs={"class": "form-control"}),
            "market": forms.Select(attrs={"class": "form-select"}),
            "stock": forms.Select(attrs={"class": "form-select"}),
            "energy_kj_per_100g": forms.NumberInput(attrs=_NUM),
            "calories_per_100g": forms.NumberInput(attrs=_NUM),
            "protein_per_100g": forms.NumberInput(attrs=_NUM),
            "carbs_per_100g": forms.NumberInput(attrs=_NUM),
            "fat_per_100g": forms.NumberInput(attrs=_NUM),
            "saturated_fat_per_100g": forms.NumberInput(attrs=_NUM),
            "sugars_per_100g": forms.NumberInput(attrs=_NUM),
            "fiber_per_100g": forms.NumberInput(attrs=_NUM),
            "salt_per_100g": forms.NumberInput(attrs=_NUM),
            "monounsaturated_fat_per_100g": forms.NumberInput(attrs=_NUM),
            "polyunsaturated_fat_per_100g": forms.NumberInput(attrs=_NUM),
            "polyols_per_100g": forms.NumberInput(attrs=_NUM),
            "omega3_epa_dha_per_100g": forms.NumberInput(attrs=_NUM),
            "thiamine_b1_per_100g": forms.NumberInput(attrs=_NUM),
            "phosphorus_per_100g": forms.NumberInput(attrs=_NUM),
            "magnesium_per_100g": forms.NumberInput(attrs=_NUM),
            "iron_per_100g": forms.NumberInput(attrs=_NUM),
            "zinc_per_100g": forms.NumberInput(attrs=_NUM),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_tag = False

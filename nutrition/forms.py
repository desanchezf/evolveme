from django import forms
from django.forms import modelformset_factory
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Row, Column
from unfold.widgets import (
    UnfoldAdminTextInputWidget,
    UnfoldAdminSelectWidget,
    UnfoldAdminDateInputWidget,
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
        widget=UnfoldAdminDateInputWidget(),
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

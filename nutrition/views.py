from django.contrib import messages
from django.urls import reverse_lazy
from django.views.generic import FormView
from unfold.views import UnfoldModelAdminViewMixin

from nutrition.forms import (
    DailyDietForm,
    ProductQuantityFormSet,
    ProductQuantityFormsetHelper,
)
from nutrition.models import DailyDiet, ProductQuantity


class DailyDietFormsetView(UnfoldModelAdminViewMixin, FormView):
    """Vista para crear/editar dieta diaria con múltiples productos"""

    title = "Registrar Dieta Diaria"
    form_class = DailyDietForm
    success_url = reverse_lazy("admin:nutrition_dailydiet_changelist")
    permission_required = ("nutrition.add_dailydiet",)
    template_name = "nutrition/daily_diet_formset.html"

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        # Obtener usuario de la sesión si está autenticado
        if self.request.user.is_authenticated:
            kwargs["user"] = self.request.user
        return kwargs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Inicializar formset
        if self.request.method == "POST":
            formset = ProductQuantityFormSet(
                self.request.POST, prefix="products"
            )
        else:
            formset = ProductQuantityFormSet(
                queryset=ProductQuantity.objects.none(), prefix="products"
            )

        context.update(
            {
                "formset": formset,
                "formset_helper": ProductQuantityFormsetHelper(),
            }
        )
        return context

    def form_valid(self, form):
        formset = ProductQuantityFormSet(
            self.request.POST, prefix="products"
        )

        if formset.is_valid():
            user = form.cleaned_data["user"]
            date = form.cleaned_data["date"]

            # Obtener o crear DailyDiet
            daily_diet, created = DailyDiet.objects.get_or_create(
                user=user, date=date
            )

            # Guardar todos los productos
            instances = formset.save(commit=False)
            for instance in instances:
                instance.save()
                daily_diet.products.add(instance)

            # Eliminar los marcados para borrar
            for obj in formset.deleted_objects:
                daily_diet.products.remove(obj)
                obj.delete()

            messages.success(
                self.request,
                f"Dieta del {date} guardada correctamente con {len(instances)} producto(s).",
            )
            return super().form_valid(form)
        else:
            return self.form_invalid(form)

    def form_invalid(self, form):
        messages.error(
            self.request, "Por favor, corrige los errores en el formulario."
        )
        return super().form_invalid(form)

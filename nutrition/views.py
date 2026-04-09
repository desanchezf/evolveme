import json
from datetime import datetime

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.contrib.auth.models import User
from django.shortcuts import redirect, render
from django.urls import reverse_lazy
from django.views.generic import FormView

from nutrition.forms import (
    DailyDietForm,
    DietJSONForm,
    ProductForm,
    ProductQuantityFormSet,
    ProductQuantityFormsetHelper,
)
from nutrition.models import DailyDiet, Product, ProductImage, ProductQuantity
from project.admin_context import with_admin_context


class DailyDietFormsetView(PermissionRequiredMixin, FormView):
    """Vista para crear/editar dieta diaria con múltiples productos"""

    permission_required = ("nutrition.add_dailydiet",)
    form_class = DailyDietForm
    success_url = reverse_lazy("admin:nutrition_dailydiet_changelist")
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
            formset = ProductQuantityFormSet(self.request.POST, prefix="products")
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
        formset = ProductQuantityFormSet(self.request.POST, prefix="products")

        if formset.is_valid():
            user = form.cleaned_data["user"]
            date = form.cleaned_data["date"]

            # Obtener o crear DailyDiet
            daily_diet, created = DailyDiet.objects.get_or_create(user=user, date=date)

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
        messages.error(self.request, "Por favor, corrige los errores en el formulario.")
        return super().form_invalid(form)


class DietJSONView(PermissionRequiredMixin, FormView):
    """Vista para generar dieta semanal desde JSON"""

    permission_required = ("nutrition.add_dailydiet",)
    form_class = DietJSONForm
    success_url = reverse_lazy("admin:nutrition_dailydiet_changelist")
    template_name = "nutrition/diet_json_form.html"

    def parse_date(self, date_str):
        """Parsea fecha en formato DD/MM/YYYY"""
        try:
            return datetime.strptime(date_str, "%d/%m/%Y").date()
        except ValueError:
            return None

    def form_valid(self, form):
        json_data = form.cleaned_data["json_data"]

        try:
            data = json.loads(json_data)
        except json.JSONDecodeError as e:
            messages.error(self.request, f"Error al parsear JSON: {str(e)}")
            return self.form_invalid(form)

        # Validar campos requeridos
        if "user" not in data:
            messages.error(self.request, "El JSON debe contener el campo 'user'")
            return self.form_invalid(form)

        if "diet" not in data:
            messages.error(self.request, "El JSON debe contener el campo 'diet'")
            return self.form_invalid(form)

        # Obtener usuario
        try:
            user = User.objects.get(username=data["user"])
        except User.DoesNotExist:
            messages.error(
                self.request, f"Usuario '{data['user']}' no encontrado en el sistema"
            )
            return self.form_invalid(form)

        # Procesar dieta por días
        diet_data = data.get("diet", {})
        days_created = 0
        products_added = 0
        products_not_found = []

        day_mapping = {
            "monday": "lunes",
            "tuesday": "martes",
            "wednesday": "miércoles",
            "thursday": "jueves",
            "friday": "viernes",
            "saturday": "sábado",
            "sunday": "domingo",
        }

        for day_key, day_data in diet_data.items():
            if not isinstance(day_data, dict):
                continue

            # Obtener fecha del día
            date_str = day_data.get("date", "")
            if not date_str:
                continue

            date = self.parse_date(date_str)
            if not date:
                messages.warning(
                    self.request,
                    f"Fecha inválida para {day_mapping.get(day_key, day_key)}: {date_str}",
                )
                continue

            # Obtener o crear DailyDiet
            daily_diet, created = DailyDiet.objects.get_or_create(user=user, date=date)
            if created:
                days_created += 1

            # Procesar comidas del día
            meals = ["breakfast", "mid_morning", "lunch", "snack", "dinner"]
            for meal in meals:
                meal_products = day_data.get(meal, [])
                if not isinstance(meal_products, list):
                    continue

                for product_data in meal_products:
                    if not isinstance(product_data, dict):
                        continue

                    product_name = product_data.get("product_name", "").strip()
                    if not product_name:
                        continue

                    # Buscar producto por nombre (case-insensitive)
                    try:
                        product = Product.objects.get(name__iexact=product_name)
                    except Product.DoesNotExist:
                        products_not_found.append(product_name)
                        continue
                    except Product.MultipleObjectsReturned:
                        # Si hay múltiples, tomar el primero
                        product = Product.objects.filter(
                            name__iexact=product_name
                        ).first()

                    # Crear ProductQuantity
                    quantity = product_data.get("quantity", 0)
                    unit = product_data.get("unit", "g")

                    product_quantity = ProductQuantity.objects.create(
                        product=product, quantity=quantity, unit=unit
                    )

                    # Añadir a la dieta
                    daily_diet.products.add(product_quantity)
                    products_added += 1

        # Mensajes de resultado
        success_msg = (
            f"Dieta semanal creada correctamente. "
            f"{days_created} día(s) nuevo(s) creado(s), "
            f"{products_added} producto(s) añadido(s)."
        )

        if products_not_found:
            success_msg += (
                f" Productos no encontrados: {', '.join(set(products_not_found))}"
            )

        messages.success(self.request, success_msg)
        return super().form_valid(form)


@login_required
def product_form_view(request):
    """Vista para el formulario de productos. Permite subir una o varias imágenes para extraer datos con IA."""
    from nutrition.services import extract_product_data_from_images

    if request.method == "POST":
        post_data = request.POST.copy()
        image_files = request.FILES.getlist("product_images")
        if image_files:
            extracted = extract_product_data_from_images(image_files)
            for key, value in extracted.items():
                if key not in post_data or not str(post_data.get(key)).strip():
                    post_data[key] = value

        form = ProductForm(post_data, request.FILES)
        if form.is_valid():
            product = form.save()
            for img_file in image_files:
                ProductImage.objects.create(product=product, image=img_file)
            messages.success(request, "Producto guardado correctamente.")
            return redirect("nutrition:product_form")
    else:
        form = ProductForm()

    return render(request, "nutrition/product_form.html", with_admin_context(request, {"form": form}))


@login_required
def daily_diet_form_view(request):
    """Vista para el formulario de dieta diaria"""
    if request.method == "POST":
        form = DailyDietForm(request.POST, user=request.user)
        formset = ProductQuantityFormSet(request.POST, prefix="products")
        if form.is_valid() and formset.is_valid():
            user = form.cleaned_data["user"]
            date = form.cleaned_data["date"]

            # Obtener o crear DailyDiet
            daily_diet, created = DailyDiet.objects.get_or_create(user=user, date=date)

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
                request,
                f"Dieta del {date} guardada correctamente con {len(instances)} producto(s).",
            )
            return redirect("nutrition:daily_diet_form")
    else:
        form = DailyDietForm(user=request.user)
        formset = ProductQuantityFormSet(queryset=None, prefix="products")

    return render(
        request,
        "nutrition/daily_diet_form.html",
        with_admin_context(request, {
            "form": form,
            "formset": formset,
            "formset_helper": ProductQuantityFormsetHelper(),
        }),
    )

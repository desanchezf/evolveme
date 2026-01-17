from django.contrib import admin
from django.urls import path
from unfold.admin import ModelAdmin as UnfoldModelAdmin

from nutrition.models import DailyDiet, MealMetrics, Product, ProductQuantity
from nutrition.views import DailyDietFormsetView, DietJSONView
from nutrition.forms_admin import DailyDietAdminForm


@admin.register(Product)
class ProductsAdmin(UnfoldModelAdmin):
    list_display = (
        "name",
        "barcode",
        "market",
        "energy_kj_per_100g",
        "calories_per_100g",
        "protein_per_100g",
        "carbs_per_100g",
        "fat_per_100g",
        "stock",
        "created_at",
    )
    list_filter = ("stock", "market", "created_at")
    search_fields = ("name", "description", "barcode")
    date_hierarchy = "created_at"
    ordering = ("-created_at",)
    fieldsets = (
        (
            "Información básica",
            {
                "fields": (
                    "name",
                    "description",
                    "barcode",
                    "market",
                    "stock",
                ),
            },
        ),
        (
            "Valor energético",
            {
                "fields": (
                    "energy_kj_per_100g",
                    "calories_per_100g",
                ),
            },
        ),
        (
            "Macronutrientes",
            {
                "fields": (
                    "protein_per_100g",
                    "carbs_per_100g",
                    "fat_per_100g",
                ),
            },
        ),
        (
            "Grasas detalladas",
            {
                "fields": (
                    "saturated_fat_per_100g",
                    "monounsaturated_fat_per_100g",
                    "polyunsaturated_fat_per_100g",
                    "omega3_epa_dha_per_100g",
                ),
            },
        ),
        (
            "Carbohidratos detallados",
            {
                "fields": (
                    "sugars_per_100g",
                    "polyols_per_100g",
                    "fiber_per_100g",
                ),
            },
        ),
        (
            "Otros nutrientes",
            {
                "fields": (
                    "salt_per_100g",
                ),
            },
        ),
        (
            "Micronutrientes",
            {
                "fields": (
                    "thiamine_b1_per_100g",
                    "phosphorus_per_100g",
                    "magnesium_per_100g",
                    "iron_per_100g",
                    "zinc_per_100g",
                ),
            },
        ),
        (
            "Información del sistema",
            {
                "fields": (
                    "created_at",
                    "updated_at",
                ),
                "classes": ("collapse",),
            },
        ),
    )
    readonly_fields = ("created_at", "updated_at")


@admin.register(ProductQuantity)
class ProductQuantityAdmin(UnfoldModelAdmin):
    list_display = ("product", "quantity", "unit", "created_at")
    list_filter = ("product", "unit", "created_at")
    search_fields = ("product__name", "product__description")
    date_hierarchy = "created_at"
    ordering = ("-created_at",)
    fieldsets = (
        (
            "Información básica",
            {
                "fields": ("product", "quantity", "unit"),
            },
        ),
    )


@admin.register(DailyDiet)
class DailyDietAdmin(UnfoldModelAdmin):
    form = DailyDietAdminForm
    list_display = ("user", "date", "created_at")
    list_filter = ("date", "user")
    search_fields = ("user__username", "user__email")
    date_hierarchy = "date"
    ordering = ("-date",)
    filter_horizontal = ("products",)
    fieldsets = (
        (
            "Información básica",
            {
                "fields": ("user", "date"),
            },
        ),
        (
            "Productos y cantidades",
            {
                "fields": ("products",),
            },
        ),
    )

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path(
                "add-formset/",
                self.admin_site.admin_view(DailyDietFormsetView.as_view()),
                name="nutrition_dailydiet_add_formset",
            ),
            path(
                "generate-from-json/",
                self.admin_site.admin_view(DietJSONView.as_view()),
                name="nutrition_dailydiet_generate_from_json",
            ),
        ]
        return custom_urls + urls

    def changelist_view(self, request, extra_context=None):
        extra_context = extra_context or {}
        extra_context["add_formset_url"] = "admin:nutrition_dailydiet_add_formset"
        extra_context["generate_json_url"] = "admin:nutrition_dailydiet_generate_from_json"
        return super().changelist_view(request, extra_context=extra_context)


@admin.register(MealMetrics)
class MealMetricsAdmin(UnfoldModelAdmin):
    list_display = (
        "daily_diet",
        "calories",
        "protein",
        "carbs",
        "fat",
        "created_at",
    )
    list_filter = ("daily_diet", "created_at")
    search_fields = ("daily_diet__id",)
    date_hierarchy = "created_at"
    ordering = ("-created_at",)
    fieldsets = (
        (
            "Información básica",
            {
                "fields": ("daily_diet",),
            },
        ),
        (
            "Métricas nutricionales",
            {
                "fields": ("calories", "protein", "carbs", "fat"),
            },
        ),
    )

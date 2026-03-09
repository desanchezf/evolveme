from django.contrib import admin
from django.urls import path
from import_export.admin import ImportExportModelAdmin

from nutrition.models import DailyDiet, MealMetrics, Product, ProductImage, ProductQuantity
from nutrition.views import DailyDietFormsetView, DietJSONView
from nutrition.forms_admin import DailyDietAdminForm


class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 0
    readonly_fields = ("created_at",)


@admin.register(Product)
class ProductsAdmin(ImportExportModelAdmin):
    inlines = [ProductImageInline]
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
        "formatted_created_at",
    )

    def formatted_created_at(self, obj):
        """Formatea la fecha de creación como DD/MM/YYYY HH:MM:SS"""
        if obj.created_at:
            return obj.created_at.strftime("%d/%m/%Y %H:%M:%S")
        return "-"

    formatted_created_at.short_description = "Fecha de creación"
    formatted_created_at.admin_order_field = "created_at"
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
class ProductQuantityAdmin(ImportExportModelAdmin):
    list_display = ("product", "quantity", "unit", "formatted_created_at")

    def formatted_created_at(self, obj):
        """Formatea la fecha de creación como DD/MM/YYYY HH:MM:SS"""
        if obj.created_at:
            return obj.created_at.strftime("%d/%m/%Y %H:%M:%S")
        return "-"

    formatted_created_at.short_description = "Fecha de creación"
    formatted_created_at.admin_order_field = "created_at"
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
class DailyDietAdmin(ImportExportModelAdmin):
    form = DailyDietAdminForm
    list_display = ("user", "formatted_date", "formatted_created_at")

    def formatted_date(self, obj):
        """Formatea la fecha como DD/MM/YYYY"""
        if obj.date:
            return obj.date.strftime("%d/%m/%Y")
        return "-"

    formatted_date.short_description = "Fecha"
    formatted_date.admin_order_field = "date"

    def formatted_created_at(self, obj):
        """Formatea la fecha de creación como DD/MM/YYYY HH:MM:SS"""
        if obj.created_at:
            return obj.created_at.strftime("%d/%m/%Y %H:%M:%S")
        return "-"

    formatted_created_at.short_description = "Fecha de creación"
    formatted_created_at.admin_order_field = "created_at"
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
class MealMetricsAdmin(ImportExportModelAdmin):
    list_display = (
        "daily_diet",
        "calories",
        "protein",
        "carbs",
        "fat",
        "formatted_created_at",
    )

    def formatted_created_at(self, obj):
        """Formatea la fecha de creación como DD/MM/YYYY HH:MM:SS"""
        if obj.created_at:
            return obj.created_at.strftime("%d/%m/%Y %H:%M:%S")
        return "-"

    formatted_created_at.short_description = "Fecha de creación"
    formatted_created_at.admin_order_field = "created_at"
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

from django.contrib import admin
from unfold.admin import ModelAdmin as UnfoldModelAdmin

from food.models import DailyDiet, MealMetrics, Product, ProductQuantity


@admin.register(Product)
class ProductsAdmin(UnfoldModelAdmin):
    list_display = (
        "name",
        "market",
        "calories_per_100g",
        "protein_per_100g",
        "carbs_per_100g",
        "fat_per_100g",
        "stock",
    )
    list_filter = ("stock", "market")
    search_fields = ("name", "description")
    fieldsets = (
        (
            "Información básica",
            {
                "fields": ("name", "description", "market", "stock"),
            },
        ),
        (
            "Valores nutricionales básicos",
            {
                "fields": (
                    "calories_per_100g",
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
                ),
            },
        ),
        (
            "Carbohidratos detallados",
            {
                "fields": (
                    "sugars_per_100g",
                    "polyols_per_100g",
                ),
            },
        ),
        (
            "Otros nutrientes",
            {
                "fields": (
                    "fiber_per_100g",
                    "salt_per_100g",
                ),
            },
        ),
    )


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

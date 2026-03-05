from django.contrib.auth.models import User
from django.db import models
from nutrition.enums import StockChoices, MarketChoices

# Products -> productos de la tienda
# Supplements -> suplementos
# DailyMeal -> Conjunto de productos y suplementos que ingieren en un dia
# Diet -> Conjunto de DailyMeals que conforman una dieta
# ProductStock -> Stock de productos


# Products -> productos de la tienda
class Product(models.Model):
    name = models.CharField(max_length=255, verbose_name="Nombre")
    description = models.TextField(verbose_name="Descripción", blank=True)
    barcode = models.CharField(
        max_length=255,
        verbose_name="Código de barras",
        null=True,
        blank=True,
    )
    market = models.CharField(
        max_length=255,
        verbose_name="Mercado",
        blank=True,
        choices=MarketChoices.choices(),
    )
    energy_kj_per_100g = models.FloatField(
        default=0,
        null=True,
        blank=True,
        verbose_name="Valor energético por 100g (kJ)",
    )
    calories_per_100g = models.FloatField(default=0, verbose_name="Calorías por 100g")
    protein_per_100g = models.FloatField(
        default=0, verbose_name="Proteínas por 100g (g)"
    )
    carbs_per_100g = models.FloatField(
        default=0, verbose_name="Carbohidratos por 100g (g)"
    )
    fat_per_100g = models.FloatField(default=0, verbose_name="Grasas por 100g (g)")
    saturated_fat_per_100g = models.FloatField(
        default=0,
        null=True,
        blank=True,
        verbose_name="Grasas saturadas por 100g (g)",
    )
    monounsaturated_fat_per_100g = models.FloatField(
        default=0,
        null=True,
        blank=True,
        verbose_name="Grasas monoinsaturadas por 100g (g)",
    )
    polyunsaturated_fat_per_100g = models.FloatField(
        default=0,
        null=True,
        blank=True,
        verbose_name="Grasas poliinsaturadas por 100g (g)",
    )
    sugars_per_100g = models.FloatField(
        default=0,
        null=True,
        blank=True,
        verbose_name="Azúcares por 100g (g)",
    )
    polyols_per_100g = models.FloatField(
        default=0,
        null=True,
        blank=True,
        verbose_name="Polialcoholes por 100g (g)",
    )
    fiber_per_100g = models.FloatField(
        default=0,
        null=True,
        blank=True,
        verbose_name="Fibra alimentaria por 100g (g)",
    )
    salt_per_100g = models.FloatField(
        default=0,
        null=True,
        blank=True,
        verbose_name="Sal por 100g (g)",
    )
    omega3_epa_dha_per_100g = models.FloatField(
        default=0,
        null=True,
        blank=True,
        verbose_name="Omega-3 (EPA+DHA) por 100g (g)",
    )
    # Micronutrientes
    thiamine_b1_per_100g = models.FloatField(
        default=0,
        null=True,
        blank=True,
        verbose_name="Tiamina B1 por 100g (mg)",
    )
    phosphorus_per_100g = models.FloatField(
        default=0,
        null=True,
        blank=True,
        verbose_name="Fósforo por 100g (mg)",
    )
    magnesium_per_100g = models.FloatField(
        default=0,
        null=True,
        blank=True,
        verbose_name="Magnesio por 100g (mg)",
    )
    iron_per_100g = models.FloatField(
        default=0,
        null=True,
        blank=True,
        verbose_name="Hierro por 100g (mg)",
    )
    zinc_per_100g = models.FloatField(
        default=0,
        null=True,
        blank=True,
        verbose_name="Zinc por 100g (mg)",
    )
    stock = models.CharField(
        max_length=10,
        choices=StockChoices.choices(),
        default=StockChoices.No,
        verbose_name="Stock",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Producto"
        verbose_name_plural = "Productos"
        db_table = "food_products"

    def __str__(self):
        return self.name


class ProductImage(models.Model):
    """Imagen(es) del producto (etiquetado, envase, etc.) para extracción con IA o referencia."""

    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name="images",
        verbose_name="Producto",
    )
    image = models.ImageField(
        upload_to="nutrition/products/%Y/%m/",
        verbose_name="Imagen",
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Imagen de producto"
        verbose_name_plural = "Imágenes de producto"
        ordering = ["created_at"]

    def __str__(self):
        return f"Imagen de {self.product.name}"


class ProductQuantity(models.Model):
    product = models.ForeignKey(
        Product, on_delete=models.CASCADE, verbose_name="Producto"
    )
    quantity = models.FloatField(default=0, verbose_name="Cantidad")
    unit = models.CharField(max_length=255, verbose_name="Unidad", blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Cantidad de producto"
        verbose_name_plural = "Cantidades de productos"

    def __str__(self):
        return f"{self.product.name} - {self.quantity} {self.unit}"


class DailyDiet(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        verbose_name="Usuario",
        help_text="Usuario al que se asigna la dieta (opcional)",
    )
    date = models.DateField(verbose_name="Fecha")
    products = models.ManyToManyField(
        ProductQuantity, verbose_name="Productos y cantidad ingerida"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Dieta diaria"
        verbose_name_plural = "Dietas diarias"
        ordering = ["-date"]

    def __str__(self):
        return f"Dieta del {self.date} - {self.user.username if self.user else 'Sin usuario'}"


class MealMetrics(models.Model):
    daily_diet = models.ForeignKey(
        DailyDiet, on_delete=models.CASCADE, verbose_name="Dieta diaria"
    )
    calories = models.FloatField(default=0, verbose_name="Calorías")
    protein = models.FloatField(default=0, verbose_name="Proteínas")
    carbs = models.FloatField(default=0, verbose_name="Carbohidratos")
    fat = models.FloatField(default=0, verbose_name="Grasas")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Métricas de comida"
        verbose_name_plural = "Métricas de comida"

    def __str__(self):
        return f"{self.daily_diet} - {self.calories} kcal"

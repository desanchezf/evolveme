from django.contrib.auth.models import User
from django.db import models

# Products -> productos de la tienda
# Supplements -> suplementos
# DailyMeal -> Conjunto de productos y suplementos que ingieren en un dia
# Diet -> Conjunto de DailyMeals que conforman una dieta
# ProductStock -> Stock de productos


# Products -> productos de la tienda
class Products(models.Model):
    name = models.CharField(max_length=255, verbose_name="Nombre")
    description = models.TextField(verbose_name="Descripción", blank=True)
    calories_per_100g = models.FloatField(default=0, verbose_name="Calorías por 100g")
    protein_per_100g = models.FloatField(
        default=0, verbose_name="Proteínas por 100g (g)"
    )
    carbs_per_100g = models.FloatField(
        default=0, verbose_name="Carbohidratos por 100g (g)"
    )
    fat_per_100g = models.FloatField(default=0, verbose_name="Grasas por 100g (g)")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Producto"
        verbose_name_plural = "Productos"

    def __str__(self):
        return self.name


# Supplements -> suplementos
class Supplements(models.Model):
    name = models.CharField(max_length=255, verbose_name="Nombre")
    description = models.TextField(verbose_name="Descripción", blank=True)
    unit = models.CharField(
        max_length=50,
        default="unidad",
        verbose_name="Unidad",
        help_text="Ej: pastilla, cucharada, gramo",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Suplemento"
        verbose_name_plural = "Suplementos"

    def __str__(self):
        return self.name


# ProductStock -> Stock de productos
class ProductStock(models.Model):
    product = models.OneToOneField(
        Products,
        on_delete=models.CASCADE,
        related_name="stock",
        verbose_name="Producto",
    )
    quantity = models.FloatField(
        default=0,
        verbose_name="Cantidad",
        help_text="Cantidad disponible en stock",
    )
    unit = models.CharField(
        max_length=50,
        default="kg",
        verbose_name="Unidad",
        help_text="Unidad de medida del stock (kg, unidades, etc.)",
    )
    min_quantity = models.FloatField(
        default=0,
        verbose_name="Cantidad mínima",
        help_text="Cantidad mínima antes de reponer",
    )
    updated_at = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Stock de producto"
        verbose_name_plural = "Stock de productos"

    def __str__(self):
        return f"{self.product.name} - {self.quantity} {self.unit}"

    @property
    def is_low_stock(self):
        """Indica si el stock está por debajo del mínimo"""
        return self.quantity <= self.min_quantity


# Diet -> Conjunto de DailyMeals que conforman una dieta
class Diet(models.Model):
    name = models.CharField(max_length=255, verbose_name="Nombre de la dieta")
    diet_type = models.CharField(
        max_length=255, verbose_name="Tipo de dieta", blank=True
    )
    from_date = models.DateField(verbose_name="Fecha de inicio")
    to_date = models.DateField(verbose_name="Fecha de fin")
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        verbose_name="Usuario",
        help_text="Usuario al que se asigna la dieta (opcional)",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Dieta"
        verbose_name_plural = "Dietas"
        ordering = ["-from_date"]

    def __str__(self):
        return f"{self.name} ({self.from_date} - {self.to_date})"

    @property
    def duration_days(self):
        """Calcula la duración de la dieta en días"""
        return (self.to_date - self.from_date).days + 1


# DailyMeal -> Conjunto de productos y suplementos que ingieren en un dia
class DailyMeal(models.Model):
    date = models.DateField(verbose_name="Fecha")
    diet = models.ForeignKey(
        Diet,
        on_delete=models.CASCADE,
        related_name="daily_meals",
        null=True,
        blank=True,
        verbose_name="Dieta",
        help_text="Dieta a la que pertenece este día (opcional)",
    )
    day_number = models.IntegerField(
        null=True,
        blank=True,
        verbose_name="Número de día",
        help_text="Número del día en la dieta (1-14)",
    )
    notes = models.TextField(blank=True, verbose_name="Notas")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Comida diaria"
        verbose_name_plural = "Comidas diarias"
        ordering = ["date", "day_number"]

    def __str__(self):
        if self.diet:
            day_str = f"Día {self.day_number or '?'}"
            return f"{self.diet.name} - {day_str} ({self.date})"
        return f"Comida del {self.date}"

    @property
    def total_calories(self):
        """Calcula el total de calorías del día"""
        products_calories = sum(
            item.calories for item in self.daily_meal_products.all()
        )
        return products_calories


class DailyMealProduct(models.Model):
    """Producto incluido en una comida diaria"""

    daily_meal = models.ForeignKey(
        DailyMeal,
        on_delete=models.CASCADE,
        related_name="daily_meal_products",
        verbose_name="Comida diaria",
    )
    product = models.ForeignKey(
        Products, on_delete=models.CASCADE, verbose_name="Producto"
    )
    quantity_grams = models.FloatField(
        verbose_name="Cantidad (gramos)",
        help_text="Cantidad del producto en gramos",
    )
    calories = models.FloatField(
        verbose_name="Calorías",
        null=True,
        blank=True,
        help_text="Calorías totales (se calcula automáticamente)",
    )
    notes = models.TextField(blank=True, verbose_name="Notas")

    class Meta:
        verbose_name = "Producto de comida diaria"
        verbose_name_plural = "Productos de comida diaria"

    def __str__(self):
        qty_str = f"({self.quantity_grams}g)"
        return f"{self.daily_meal} - {self.product.name} {qty_str}"

    def save(self, *args, **kwargs):
        """Calcula las calorías automáticamente"""
        if not self.calories and self.product.calories_per_100g:
            self.calories = (self.product.calories_per_100g * self.quantity_grams) / 100
        super().save(*args, **kwargs)


class DailyMealSupplement(models.Model):
    """Suplemento incluido en una comida diaria"""

    daily_meal = models.ForeignKey(
        DailyMeal,
        on_delete=models.CASCADE,
        related_name="daily_meal_supplements",
        verbose_name="Comida diaria",
    )
    supplement = models.ForeignKey(
        Supplements, on_delete=models.CASCADE, verbose_name="Suplemento"
    )
    quantity = models.FloatField(verbose_name="Cantidad")
    notes = models.TextField(blank=True, verbose_name="Notas")

    class Meta:
        verbose_name = "Suplemento de comida diaria"
        verbose_name_plural = "Suplementos de comida diaria"

    def __str__(self):
        unit_str = f"{self.quantity} {self.supplement.unit}"
        return f"{self.daily_meal} - {self.supplement.name} ({unit_str})"

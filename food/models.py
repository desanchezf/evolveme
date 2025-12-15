from django.contrib.auth.models import User
from django.db import models

from food.enums import MealTypeChoices


# Create your models here.
class Food(models.Model):
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
        verbose_name = "Alimento"
        verbose_name_plural = "Alimentos"

    def __str__(self):
        return self.name


class Supplement(models.Model):
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


class Diet(models.Model):
    """Dieta completa generada por IA para 2 semanas (14 días)"""

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


class DietDay(models.Model):
    """Un día específico de la dieta (día 1, día 2, etc.)"""

    diet = models.ForeignKey(
        Diet, on_delete=models.CASCADE, related_name="days", verbose_name="Dieta"
    )
    day_number = models.IntegerField(
        verbose_name="Número de día",
        help_text="Día de la dieta (1-14 para 2 semanas)",
    )
    date = models.DateField(
        verbose_name="Fecha",
        help_text="Fecha específica de este día",
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Día de la dieta"
        verbose_name_plural = "Días de la dieta"
        ordering = ["diet", "day_number"]
        unique_together = [["diet", "day_number"]]

    def __str__(self):
        return f"{self.diet.name} - Día {self.day_number} ({self.date})"


class Meal(models.Model):
    """Una comida del día (desayuno, almuerzo, cena, etc.)"""

    diet_day = models.ForeignKey(
        DietDay,
        on_delete=models.CASCADE,
        related_name="meals",
        verbose_name="Día de la dieta",
    )
    meal_type = models.CharField(
        max_length=50,
        choices=MealTypeChoices.choices(),
        verbose_name="Tipo de comida",
    )
    order = models.IntegerField(
        default=0,
        verbose_name="Orden",
        help_text="Orden de la comida en el día (para ordenar)",
    )
    notes = models.TextField(
        blank=True,
        verbose_name="Notas",
        help_text="Notas adicionales sobre la comida",
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Comida"
        verbose_name_plural = "Comidas"
        ordering = ["diet_day", "order", "meal_type"]

    def __str__(self):
        return f"{self.diet_day} - {self.get_meal_type_display()}"

    @property
    def total_calories(self):
        """Calcula el total de calorías de la comida"""
        return sum(meal_food.calories for meal_food in self.foods.all())


class MealFood(models.Model):
    """Alimento incluido en una comida con su cantidad"""

    meal = models.ForeignKey(
        Meal,
        on_delete=models.CASCADE,
        related_name="foods",
        verbose_name="Comida",
    )
    food = models.ForeignKey(Food, on_delete=models.CASCADE, verbose_name="Alimento")
    quantity_grams = models.FloatField(
        verbose_name="Cantidad (gramos)",
        help_text="Cantidad del alimento en gramos",
    )
    calories = models.FloatField(
        verbose_name="Calorías",
        help_text="Calorías totales para esta cantidad",
        null=True,
        blank=True,
    )
    notes = models.TextField(
        blank=True,
        verbose_name="Notas",
        help_text="Notas sobre este alimento",
    )

    class Meta:
        verbose_name = "Alimento de la comida"
        verbose_name_plural = "Alimentos de la comida"
        ordering = ["meal", "food"]

    def __str__(self):
        return f"{self.meal} - {self.food.name} ({self.quantity_grams}g)"

    def save(self, *args, **kwargs):
        """Calcula las calorías automáticamente si no se proporcionan"""
        if not self.calories and self.food.calories_per_100g:
            self.calories = (self.food.calories_per_100g * self.quantity_grams) / 100
        super().save(*args, **kwargs)


class MealSupplement(models.Model):
    """Suplemento incluido en una comida"""

    meal = models.ForeignKey(
        Meal,
        on_delete=models.CASCADE,
        related_name="supplements",
        verbose_name="Comida",
    )
    supplement = models.ForeignKey(
        Supplement, on_delete=models.CASCADE, verbose_name="Suplemento"
    )
    quantity = models.FloatField(verbose_name="Cantidad")
    notes = models.TextField(
        blank=True,
        verbose_name="Notas",
        help_text="Notas sobre este suplemento",
    )

    class Meta:
        verbose_name = "Suplemento de la comida"
        verbose_name_plural = "Suplementos de la comida"
        ordering = ["meal", "supplement"]

    def __str__(self):
        return f"{self.meal} - {self.supplement.name} ({self.quantity} {self.supplement.unit})"


class EatenFood(models.Model):
    """Registro de alimentos realmente consumidos por el usuario"""

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="eaten_foods",
        verbose_name="Usuario",
    )
    meal = models.ForeignKey(
        Meal,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name="Comida planificada",
        help_text="Comida de la dieta que se estaba siguiendo (opcional)",
    )
    food = models.ForeignKey(Food, on_delete=models.CASCADE, verbose_name="Alimento")
    quantity_grams = models.FloatField(verbose_name="Cantidad consumida (gramos)")
    calories = models.FloatField(
        verbose_name="Calorías",
        null=True,
        blank=True,
        help_text="Calorías consumidas (se calcula automáticamente)",
    )
    date = models.DateField(verbose_name="Fecha de consumo")
    meal_type = models.CharField(
        max_length=50,
        choices=MealTypeChoices.choices(),
        verbose_name="Tipo de comida",
        help_text="Tipo de comida en la que se consumió",
    )
    notes = models.TextField(blank=True, verbose_name="Notas")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Alimento consumido"
        verbose_name_plural = "Alimentos consumidos"
        ordering = ["-date", "-created_at"]

    def __str__(self):
        return f"{self.user.username} - {self.food.name} ({self.date})"

    def save(self, *args, **kwargs):
        """Calcula las calorías automáticamente si no se proporcionan"""
        if not self.calories and self.food.calories_per_100g:
            self.calories = (self.food.calories_per_100g * self.quantity_grams) / 100
        super().save(*args, **kwargs)


class EatenSupplement(models.Model):
    """Registro de suplementos realmente consumidos por el usuario"""

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="eaten_supplements",
        verbose_name="Usuario",
    )
    meal = models.ForeignKey(
        Meal,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name="Comida planificada",
        help_text="Comida de la dieta que se estaba siguiendo (opcional)",
    )
    supplement = models.ForeignKey(
        Supplement, on_delete=models.CASCADE, verbose_name="Suplemento"
    )
    quantity = models.FloatField(verbose_name="Cantidad consumida")
    date = models.DateField(verbose_name="Fecha de consumo")
    meal_type = models.CharField(
        max_length=50,
        choices=MealTypeChoices.choices(),
        null=True,
        blank=True,
        verbose_name="Tipo de comida",
        help_text="Tipo de comida en la que se consumió (opcional)",
    )
    notes = models.TextField(blank=True, verbose_name="Notas")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Suplemento consumido"
        verbose_name_plural = "Suplementos consumidos"
        ordering = ["-date", "-created_at"]

    def __str__(self):
        return f"{self.user.username} - {self.supplement.name} ({self.date})"

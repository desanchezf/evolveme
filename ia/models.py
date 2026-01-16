from django.db import models

# Create your models here.


class LLMClient(models.Model):
    name = models.CharField(max_length=255, verbose_name="Nombre")
    url = models.URLField(verbose_name="URL")
    api_key = models.CharField(max_length=255, verbose_name="API Key")
    status = models.BooleanField(default=True, verbose_name="Estado")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Cliente de LLM"
        verbose_name_plural = "Clientes de LLM"


class Promtps(models.Model):
    name = models.CharField(max_length=255, verbose_name="Nombre")
    prompt = models.TextField(verbose_name="Descripción")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Prompt"
        verbose_name_plural = "Prompts"

    def __str__(self):
        return self.name


class GymLLMResponse(models.Model):
    response = models.TextField(verbose_name="Respuesta")
    stored = models.BooleanField(default=False, verbose_name="Almacenado")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Respuesta del modelo"
        verbose_name_plural = "Respuestas del modelo"

    def __str__(self):
        return self.response


class NutritionLLMResponse(models.Model):
    response = models.TextField(verbose_name="Respuesta")
    stored = models.BooleanField(default=False, verbose_name="Almacenado")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Respuesta del modelo"
        verbose_name_plural = "Respuestas del modelo"

    def __str__(self):
        return self.response


class ProductLLMResponse(models.Model):
    products = models.JSONField(verbose_name="Productos")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Respuesta del modelo"
        verbose_name_plural = "Respuestas del modelo"

    def __str__(self):
        return self.products

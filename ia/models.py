from django.conf import settings
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


# --- Conexión con Ollama ---


class OllamaServer(models.Model):
    """
    Configuración de un servidor Ollama.
    Permite soportar varios hosts/instancias (local o remotas).
    """

    name = models.CharField(max_length=100, unique=True)
    base_url = models.URLField(
        help_text="URL base del servidor Ollama, p.ej. http://localhost:11434",
    )
    enabled = models.BooleanField(default=True)
    api_key = models.CharField(
        max_length=255,
        blank=True,
        help_text="Opcional, por si el servidor requiere API key",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Servidor Ollama"
        verbose_name_plural = "Servidores Ollama"

    def __str__(self) -> str:
        return self.name


class OllamaModelConfig(models.Model):
    """
    Configuración de un modelo concreto servido vía Ollama.
    """

    server = models.ForeignKey(
        OllamaServer,
        on_delete=models.CASCADE,
        related_name="models",
    )
    model_name = models.CharField(
        max_length=100,
        help_text="Nombre tal y como lo expone Ollama (ej. 'llama3', 'qwen2.5', etc.)",
    )
    temperature = models.FloatField(default=0.7)
    top_p = models.FloatField(default=0.9)
    max_tokens = models.PositiveIntegerField(default=512)
    alias = models.CharField(
        max_length=100,
        help_text="Nombre lógico en la app (p.ej. 'asistente_pronosticos')",
    )
    description = models.TextField(blank=True)
    is_default = models.BooleanField(
        default=False,
        help_text="Si es el modelo por defecto para este servidor/uso",
    )
    deprecated = models.BooleanField(
        default=False,
        help_text="Marcar como deprecado (no recomendado para uso nuevo).",
    )
    deprecated_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text="Fecha de deprecación (opcional).",
    )
    proposito = models.CharField(
        max_length=255,
        blank=True,
        verbose_name="Propósito",
        help_text="Uso del modelo (p. ej. 'OCR', 'Razonamiento del nutricionista', 'Chat').",
    )
    downloaded = models.BooleanField(
        default=False,
        verbose_name="Descargado",
        help_text="Si el modelo está actualmente descargado en el servidor Ollama.",
    )
    digest = models.CharField(
        max_length=64,
        blank=True,
        verbose_name="Digest",
        help_text="Digest del modelo en Ollama (para detectar actualizaciones).",
    )
    last_checked_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="Última comprobación",
    )
    update_available = models.BooleanField(
        default=False,
        verbose_name="Actualización disponible",
        help_text="Hay una versión nueva disponible o el modelo no está descargado.",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Modelo Ollama"
        verbose_name_plural = "Modelos Ollama"
        unique_together = ("server", "model_name")

    @property
    def is_deprecated(self) -> bool:
        """True si el modelo está marcado como deprecado o tiene fecha de deprecación."""
        return self.deprecated or self.deprecated_at is not None

    def __str__(self) -> str:
        return f"{self.alias} ({self.server.name}:{self.model_name})"


class ChatSession(models.Model):
    """
    Sesión de conversación de un usuario con un modelo Ollama.
    Agrupa mensajes en un mismo hilo.
    """

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="ia_chat_sessions",
    )
    model_key = models.CharField(
        max_length=200,
        blank=True,
        help_text="Clave del modelo usado, p.ej. 'local|llama3.1:8b-q4_K_M'",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Sesión de chat"
        verbose_name_plural = "Sesiones de chat"
        ordering = ["-updated_at"]

    def __str__(self) -> str:
        return f"Sesión {self.pk} ({self.user}, {self.updated_at})"


class ChatMessage(models.Model):
    """
    Un mensaje dentro de una sesión de chat (usuario o asistente).
    """

    ROLE_USER = "user"
    ROLE_ASSISTANT = "assistant"
    ROLE_CHOICES = [(ROLE_USER, "Usuario"), (ROLE_ASSISTANT, "Asistente")]

    session = models.ForeignKey(
        ChatSession,
        on_delete=models.CASCADE,
        related_name="messages",
    )
    role = models.CharField(max_length=20, choices=ROLE_CHOICES)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Mensaje de chat"
        verbose_name_plural = "Mensajes de chat"
        ordering = ["created_at"]

    def __str__(self) -> str:
        return f"{self.role}: {self.content[:50]}..."

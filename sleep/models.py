from django.db import models
from django.contrib.auth.models import User


class SleepRecord(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="sleep_records",
        verbose_name="Usuario",
    )
    date = models.DateField(verbose_name="Fecha")
    sleep_start = models.DateTimeField(
        null=True, blank=True, verbose_name="Inicio del sueño"
    )
    sleep_end = models.DateTimeField(
        null=True, blank=True, verbose_name="Fin del sueño"
    )
    total_sleep_time = models.DurationField(
        null=True, blank=True, verbose_name="Tiempo total dormido"
    )
    awake_time = models.DurationField(
        null=True, blank=True, verbose_name="Tiempo despierto"
    )
    rem_time = models.DurationField(
        null=True, blank=True, verbose_name="Sueño REM"
    )
    core_time = models.DurationField(
        null=True, blank=True, verbose_name="Sueño Core (ligero)"
    )
    deep_time = models.DurationField(
        null=True, blank=True, verbose_name="Sueño profundo"
    )
    notes = models.TextField(
        null=True, blank=True, verbose_name="Notas"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Registro de sueño"
        verbose_name_plural = "Registros de sueño"
        ordering = ["-date", "-sleep_start"]
        unique_together = [("user", "date")]

    def __str__(self):
        return f"{self.user.username} – {self.date}"

    @property
    def total_seconds(self):
        return int(self.total_sleep_time.total_seconds()) if self.total_sleep_time else 0

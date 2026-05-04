from django.db import models
from django.contrib.auth.models import User

from gym.enums import BodyPartChoices, CardioExerciseNameChoices, UnitChoices


# ── Cardio ─────────────────────────────────────────────────────────────────

class CardioExercise(models.Model):
    name = models.CharField(
        max_length=255,
        verbose_name="Nombre del ejercicio",
        choices=CardioExerciseNameChoices.choices(),
    )
    description = models.TextField(null=True, blank=True, verbose_name="Descripción")
    image_base64 = models.TextField(null=True, blank=True, verbose_name="Imagen")

    class Meta:
        verbose_name = "Ejercicio de cardio"
        verbose_name_plural = "Ejercicios de cardio"

    def __str__(self):
        return self.get_name_display() or self.name


class CardioSession(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="cardio_sessions",
        verbose_name="Usuario",
    )
    exercise = models.ForeignKey(
        CardioExercise,
        on_delete=models.CASCADE,
        related_name="sessions",
        verbose_name="Ejercicio",
        null=True,
        blank=True,
    )
    session_start = models.DateTimeField(
        null=True, blank=True, verbose_name="Fecha y hora de inicio"
    )
    session_end = models.DateTimeField(
        null=True, blank=True, verbose_name="Fecha y hora de fin"
    )
    date = models.DateField(verbose_name="Fecha")
    location = models.CharField(
        max_length=255, null=True, blank=True, verbose_name="Ubicación"
    )
    workout_time = models.DurationField(
        null=True, blank=True, verbose_name="Duración del entrenamiento"
    )
    distance = models.FloatField(null=True, blank=True, verbose_name="Distancia (km)")
    avg_speed = models.FloatField(
        null=True, blank=True, verbose_name="Velocidad promedio (km/h)"
    )
    active_calories = models.IntegerField(
        null=True, blank=True, verbose_name="Calorías activas (kcal)"
    )
    total_calories = models.IntegerField(
        null=True, blank=True, verbose_name="Calorías totales (kcal)"
    )
    elevation_gain = models.IntegerField(
        null=True, blank=True, verbose_name="Ganancia de elevación (m)"
    )
    average_heart_rate = models.IntegerField(
        null=True, blank=True, verbose_name="Frecuencia cardíaca promedio (bpm)"
    )
    workout_image = models.ImageField(
        upload_to="cardio/%Y/%m/",
        null=True,
        blank=True,
        verbose_name="Imagen del entrenamiento",
        help_text="Opcional. Sube una captura o foto del entrenamiento para extraer datos con IA.",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Sesión de cardio"
        verbose_name_plural = "Sesiones de cardio"
        ordering = ["-date", "-session_start"]

    def __str__(self):
        if self.exercise:
            return f"{self.user.username} - {self.exercise.name} - {self.date}"
        return f"{self.user.username} - Sin ejercicio - {self.date}"


# ── Musculación ────────────────────────────────────────────────────────────

class MusculationExercise(models.Model):
    name = models.CharField(max_length=255, verbose_name="Nombre del ejercicio")
    description = models.TextField(null=True, blank=True, verbose_name="Descripción")
    body_part = models.CharField(
        max_length=255,
        choices=BodyPartChoices.choices(),
        null=True,
        blank=True,
        verbose_name="Parte del cuerpo",
    )
    sets = models.IntegerField(null=False, blank=False, verbose_name="Series")
    reps = models.IntegerField(null=False, blank=False, verbose_name="Repeticiones")
    unit = models.CharField(
        max_length=255, verbose_name="Unidad", choices=UnitChoices.choices()
    )
    image_base64 = models.TextField(null=True, blank=True, verbose_name="Imagen")

    class Meta:
        verbose_name = "Ejercicio de musculación"
        verbose_name_plural = "Ejercicios de musculación"

    def __str__(self):
        return self.name


class MusculationRecord(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="musculation_records",
        verbose_name="Usuario",
    )
    exercise = models.ForeignKey(
        MusculationExercise,
        on_delete=models.CASCADE,
        related_name="records",
        verbose_name="Ejercicio",
    )
    sets = models.IntegerField(null=False, blank=False, verbose_name="Series")
    reps = models.IntegerField(null=False, blank=False, verbose_name="Repeticiones")
    weight = models.IntegerField(null=False, blank=False, verbose_name="Peso (kg)")
    tbi = models.BooleanField(null=False, blank=False, verbose_name="To be improved")
    observation = models.TextField(null=True, blank=True, verbose_name="Observación")
    record_date = models.DateTimeField(
        null=True, blank=True, verbose_name="Fecha de registro"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Registro de ejercicio de musculación"


class Routine(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="routines",
        verbose_name="Usuario",
    )
    exercises = models.ManyToManyField(
        MusculationExercise, related_name="routines", verbose_name="Ejercicios"
    )
    exercise_types = models.JSONField(
        default=list,
        null=True,
        blank=True,
        verbose_name="Tipos de ejercicios",
        help_text="Múltiples selecciones de tipos de ejercicios",
    )
    warmup = models.ForeignKey(
        CardioExercise,
        on_delete=models.CASCADE,
        related_name="routines",
        verbose_name="Ejercicio de calentamiento",
        null=True,
        blank=True,
    )
    warmup_duration = models.DurationField(
        null=True, blank=True, verbose_name="Duración de calentamiento"
    )
    duration = models.PositiveIntegerField(
        null=True,
        blank=True,
        verbose_name="Duración de la rutina (semanas)",
        help_text="Duración de la rutina en semanas",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Rutina"
        verbose_name_plural = "Rutinas"
        ordering = ["-created_at"]

    def __str__(self):
        exercise_types_str = ""
        if self.exercise_types:
            exercise_types_str = f" - {', '.join(self.exercise_types)}"
        duration_str = f" - {self.duration} semana(s)" if self.duration else ""
        return f"{exercise_types_str}{duration_str} - {self.user}"


class TrainingSession(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="training_sessions",
        verbose_name="Usuario",
    )
    routine = models.ForeignKey(
        Routine,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="sessions",
        verbose_name="Rutina",
    )
    session_date = models.DateTimeField(
        null=True, blank=True, verbose_name="Fecha y hora de la sesión"
    )
    location = models.CharField(
        max_length=255, verbose_name="Ubicación", null=True, blank=True
    )
    workout_time = models.DurationField(
        null=True, blank=True, verbose_name="Duración de la sesión"
    )
    active_kilocalories = models.IntegerField(
        null=True, blank=True, verbose_name="Kcal activas"
    )
    total_kilocalories = models.IntegerField(
        null=True, blank=True, verbose_name="Kcal totales"
    )
    avg_heart_rate = models.IntegerField(
        null=True, blank=True, verbose_name="FC media (BPM)"
    )
    workout_image = models.ImageField(
        upload_to="gym/%Y/%m/",
        null=True,
        blank=True,
        verbose_name="Imagen del entrenamiento",
        help_text="Opcional. Sube una captura o foto del entrenamiento para extraer datos con IA.",
    )

    class Meta:
        verbose_name = "Sesión de entrenamiento"
        verbose_name_plural = "Sesiones de entrenamiento"

    def __str__(self):
        return f"{self.user} - {self.session_date}"

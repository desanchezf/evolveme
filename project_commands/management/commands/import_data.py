import csv
import logging
import os
from datetime import datetime, timedelta

from django.conf import settings
from django.contrib.auth.models import User
from django.core.management.base import BaseCommand
from django.utils import timezone
from django.utils.dateparse import parse_datetime, parse_duration

from evolveme.models import GymUserProfile, Measure
from nutrition.models import Product
from gym.models import (
    CardioExercise, MusculationExercise, Routine,
    RoutineDay, RoutineDayExercise, Session,
)
from ia.models import OllamaModelConfig, OllamaServer, Promtps

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = "Cargar datos iniciales desde archivos CSV"

    def handle(self, *args, **options):
        if not self.user_data():
            print(" ❌ Error al cargar la información de los usuarios 👤")
            return
        else:
            print(" ✅ Información cargada correctamente 👤")
        if not self.measures_data():
            print(" ❌ Error al cargar las medidas 📏")
            return
        else:
            print(" ✅ Medidas cargadas correctamente 📏")
        if not self.musculation_exercises():
            print(" ❌ Error al cargar los ejercicios de musculación 💪")
            return
        else:
            print(" ✅ Ejercicios de musculación cargados correctamente 💪")
        if not self.cardio_exercises():
            print(" ❌ Error al cargar los ejercicios de cardio 🏃")
            return
        else:
            print(" ✅ Ejercicios de cardio cargados correctamente 🏃")
        if not self.sessions():
            print(" ❌ Error al cargar las sesiones 🏋️")
            return
        else:
            print(" ✅ Sesiones cargadas correctamente 🏋️")
        if not self.food_products():
            print(" ❌ Error al cargar los productos alimentarios 🍎")
            return
        else:
            print(" ✅ Productos alimentarios cargados correctamente 🍎")
        if not self.default_routines():
            print(" ❌ Error al cargar las rutinas por defecto 📋")
            return
        else:
            print(" ✅ Rutinas por defecto cargadas correctamente 📋")
        if not self.prompts_data():
            print(" ❌ Error al cargar los prompts 🤖")
            return
        else:
            print(" ✅ Prompts cargados correctamente 🤖")
        if not self.ollama_models():
            print(" ❌ Error al precargar modelos Ollama 🤖")
            return
        else:
            print(" ✅ Modelos Ollama precargados correctamente 🤖")

    def get_csv_path(self, filename):
        """Obtiene la ruta del archivo CSV en la carpeta csv/"""
        try:
            project_root = settings.BASE_DIR
        except AttributeError:
            project_root = os.path.dirname(
                os.path.dirname(
                    os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
                )
            )
        return os.path.join(project_root, "csv", filename)

    def get_prompt_path(self, filename):
        """Obtiene la ruta del archivo de prompt en la carpeta prompts/"""
        try:
            project_root = settings.BASE_DIR
        except AttributeError:
            project_root = os.path.dirname(
                os.path.dirname(
                    os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
                )
            )
        return os.path.join(project_root, "prompts", filename)

    def parse_datetime_safe(self, value):
        """Parsea un datetime y lo convierte a timezone-aware si es necesario"""
        if not value:
            return None
        parsed = parse_datetime(value)
        if parsed:
            # Convertir a timezone-aware si es naive
            if timezone.is_naive(parsed):
                return timezone.make_aware(parsed)
            return parsed
        return None

    def user_data(self):
        """Crea el usuario 'david' si no existe"""
        logger.info("Cargando información de los usuarios 👤 ...")
        username = "david"
        if not User.objects.filter(username=username).exists():
            User.objects.create_user(
                username=username,
                email="david@example.com",
                password="david123",
            )
            logger.info(f"Usuario {username} creado correctamente ✅")
        else:
            logger.info(f"Usuario {username} ya existe ✅")
        return True

    def measures_data(self):
        """Carga las medidas desde measures.csv"""
        logger.info("Cargando medidas 📏 ...")

        csv_path = self.get_csv_path("measures.csv")
        if not os.path.exists(csv_path):
            logger.error(f"El archivo {csv_path} no existe")
            return False

        def safe_float(value, default=None):
            """Convierte un valor a float de forma segura"""
            if not value or (isinstance(value, str) and value.strip() == ""):
                return default
            try:
                return float(value)
            except (ValueError, TypeError):
                return default

        def safe_int(value, default=None):
            """Convierte un valor a int de forma segura"""
            if not value or (isinstance(value, str) and value.strip() == ""):
                return default
            try:
                return int(float(value))
            except (ValueError, TypeError):
                return default

        with open(csv_path, newline="", encoding="utf-8") as csvfile:
            measures_reader = csv.DictReader(csvfile)
            created_count = 0
            for row in measures_reader:
                username = row.get("user", "david")
                user = User.objects.filter(username=username).first()
                if not user:
                    logger.warning(f"Usuario {username} no encontrado, saltando medida")
                    continue

                if not Measure.objects.filter(user=user, date=row["date"]).exists():
                    Measure.objects.create(
                        user=user,
                        date=row["date"],
                        weight=safe_float(row.get("weight")),
                        arm=safe_float(row.get("arm")),
                        arm_relaxed=safe_float(row.get("arm_relaxed")),
                        chest=safe_float(row.get("chest")),
                        waist=safe_float(row.get("waist")),
                        leg=safe_float(row.get("leg")),
                        leg_relaxed=safe_float(row.get("leg_relaxed")),
                        fat_perc=safe_float(row.get("fat_perc")),
                        muscle_mass=safe_float(row.get("muscle_mass")),
                        bmi=safe_float(row.get("bmi")),
                        body_water_mass=safe_float(row.get("body_water_mass")),
                        body_water_percentage=safe_float(
                            row.get("body_water_percentage")
                        ),
                        fat_mass=safe_float(row.get("fat_mass")),
                        bone_mineral_content=safe_float(
                            row.get("bone_mineral_content")
                        ),
                        bone_mineral_percentage=safe_float(
                            row.get("bone_mineral_percentage")
                        ),
                        protein_mass=safe_float(row.get("protein_mass")),
                        protein_percentage=safe_float(row.get("protein_percentage")),
                        muscle_percentage=safe_float(row.get("muscle_percentage")),
                        skeletal_muscle_mass=safe_float(
                            row.get("skeletal_muscle_mass")
                        ),
                        visceral_fat_rating=safe_float(row.get("visceral_fat_rating")),
                        basal_metabolic_rate=safe_float(
                            row.get("basal_metabolic_rate")
                        ),
                        waist_to_hip_ratio=safe_float(row.get("waist_to_hip_ratio")),
                        body_age=safe_int(row.get("body_age")),
                        fat_free_body_weight=safe_float(
                            row.get("fat_free_body_weight")
                        ),
                    )
                    created_count += 1

        logger.info(f"Medidas cargadas correctamente ✅ ({created_count} creadas)")
        return True

    def musculation_exercises(self):
        """Carga los ejercicios de musculación desde musculation_exercises.csv"""
        logger.info("Cargando ejercicios de musculación 💪 ...")

        csv_path = self.get_csv_path("musculation_exercises.csv")
        if not os.path.exists(csv_path):
            logger.error(f"El archivo {csv_path} no existe")
            return False

        created_count = 0
        with open(csv_path, newline="", encoding="utf-8") as csvfile:
            exercises_reader = csv.DictReader(csvfile)
            for row in exercises_reader:
                if not MusculationExercise.objects.filter(name=row["name"]).exists():
                    MusculationExercise.objects.create(
                        name=row["name"],
                        description=row.get("description", "") or None,
                        body_part=row.get("body_part") or None,
                        sets=int(row["sets"]) if row.get("sets") else 0,
                        reps=int(row["reps"]) if row.get("reps") else 0,
                        unit=row.get("unit", "reps") or "reps",
                        image_base64=row.get("image_base64") or None,
                    )
                    created_count += 1

        logger.info(
            f"Ejercicios de musculación cargados correctamente ✅ "
            f"({created_count} creados)"
        )
        return True

    def cardio_exercises(self):
        """Carga los ejercicios de cardio desde training_session.csv (filas session_type=cardio)"""
        logger.info("Cargando ejercicios de cardio 🏃 ...")

        csv_path = self.get_csv_path("training_session.csv")
        if not os.path.exists(csv_path):
            logger.warning(
                f"El archivo {csv_path} no existe, saltando carga de ejercicios de cardio"
            )
            return True

        created_count = 0
        with open(csv_path, newline="", encoding="utf-8") as csvfile:
            for row in csv.DictReader(csvfile):
                if row.get("session_type") != "cardio":
                    continue
                exercise_name = row.get("name", "").strip()
                if exercise_name and not CardioExercise.objects.filter(name=exercise_name).exists():
                    exercise = CardioExercise.objects.create(
                        name=exercise_name,
                        description="",
                        image_base64=None,
                    )
                    created_count += 1
                    logger.info(
                        f"Ejercicio de cardio creado: {exercise.get_name_display() or exercise.name} ✅"
                    )

        logger.info(
            f"Ejercicios de cardio cargados correctamente ✅ ({created_count} creados)"
        )
        return True

    def sessions(self):
        """Carga todas las sesiones desde training_session.csv al modelo Session unificado."""
        logger.info("Cargando sesiones 🏋️ ...")

        csv_path = self.get_csv_path("training_session.csv")
        if not os.path.exists(csv_path):
            logger.error(f"El archivo {csv_path} no existe")
            return False

        routines_by_user = {}
        created_count = 0

        with open(csv_path, newline="", encoding="utf-8") as csvfile:
            for row in csv.DictReader(csvfile):
                username = row.get("user", "david")
                user = User.objects.filter(username=username).first()
                if not user:
                    logger.warning(f"Usuario {username} no encontrado, saltando sesión")
                    continue

                name = row.get("name", "").strip()
                if not name:
                    continue

                session_start = self.parse_datetime_safe(row.get("session_start"))
                session_end = self.parse_datetime_safe(row.get("session_end"))
                date_str = row.get("date", "")
                try:
                    date_obj = datetime.strptime(date_str, "%Y-%m-%d").date()
                except (ValueError, TypeError):
                    date_obj = session_start.date() if session_start else None
                if not date_obj:
                    continue

                workout_time = (
                    parse_duration(row["workout_time"]) if row.get("workout_time") else None
                )

                # Rutina para sesiones de musculación
                routine = None
                if name == "Musculation":
                    if username not in routines_by_user:
                        r = Routine.objects.filter(user=user).first()
                        if not r:
                            r = Routine.objects.create(user=user)
                        routines_by_user[username] = r
                        profile, _ = GymUserProfile.objects.get_or_create(user=user)
                        if not profile.start_date:
                            profile.start_date = timezone.now().date()
                        if not profile.end_date:
                            profile.end_date = (
                                timezone.now() + timedelta(weeks=6)
                            ).date()
                        if not profile.active_routine:
                            profile.active_routine = r
                        profile.save()
                    routine = routines_by_user.get(username)

                if not Session.objects.filter(user=user, name=name, date=date_obj).exists():
                    Session.objects.create(
                        user=user,
                        name=name,
                        routine=routine,
                        session_start=session_start,
                        session_end=session_end,
                        date=date_obj,
                        location=row.get("location") or None,
                        workout_time=workout_time,
                        distance=float(row["distance"]) if row.get("distance") else None,
                        avg_speed=float(row["avg_speed"]) if row.get("avg_speed") else None,
                        active_calories=int(row["active_calories"]) if row.get("active_calories") else None,
                        total_calories=int(row["total_calories"]) if row.get("total_calories") else None,
                        elevation_gain=int(row["elevation_gain"]) if row.get("elevation_gain") else None,
                        average_heart_rate=int(row["average_heart_rate"]) if row.get("average_heart_rate") else None,
                    )
                    created_count += 1

        logger.info(f"Sesiones cargadas correctamente ✅ ({created_count} creadas)")
        return True

    def food_products(self):
        """Carga los productos alimentarios desde products.csv"""
        logger.info("Cargando productos alimentarios 🍎 ...")

        csv_path = self.get_csv_path("products.csv")
        if not os.path.exists(csv_path):
            logger.error(f"El archivo {csv_path} no existe")
            return False

        def safe_float(value, default=None):
            """Convierte un valor a float de forma segura"""
            if not value or (isinstance(value, str) and value.strip() == ""):
                return default
            try:
                return float(value)
            except (ValueError, TypeError):
                return default

        def safe_str(value, default=""):
            """Convierte un valor a string de forma segura"""
            if not value or (isinstance(value, str) and value.strip() == ""):
                return default
            return str(value).strip()

        created_count = 0
        with open(csv_path, newline="", encoding="utf-8") as csvfile:
            products_reader = csv.DictReader(csvfile)
            for row in products_reader:
                # Saltar si tiene product_id y ya existe
                if row.get("product_id"):
                    try:
                        product_id = int(row["product_id"])
                        if Product.objects.filter(id=product_id).exists():
                            continue
                    except (ValueError, TypeError):
                        pass

                if not Product.objects.filter(name=row["name"]).exists():
                    Product.objects.create(
                        name=row["name"],
                        description=safe_str(row.get("description", "")),
                        barcode=safe_str(row.get("barcode")) or None,
                        market=safe_str(row.get("market", "")),
                        energy_kj_per_100g=safe_float(
                            row.get("energy_kj_per_100g"), None
                        ),
                        calories_per_100g=safe_float(row.get("calories_per_100g"), 0),
                        protein_per_100g=safe_float(row.get("protein_per_100g"), 0),
                        carbs_per_100g=safe_float(row.get("carbs_per_100g"), 0),
                        fat_per_100g=safe_float(row.get("fat_per_100g"), 0),
                        saturated_fat_per_100g=safe_float(
                            row.get("saturated_fat_per_100g"), None
                        ),
                        monounsaturated_fat_per_100g=safe_float(
                            row.get("monounsaturated_fat_per_100g"), None
                        ),
                        polyunsaturated_fat_per_100g=safe_float(
                            row.get("polyunsaturated_fat_per_100g"), None
                        ),
                        sugars_per_100g=safe_float(row.get("sugars_per_100g"), None),
                        polyols_per_100g=safe_float(row.get("polyols_per_100g"), None),
                        fiber_per_100g=safe_float(row.get("fiber_per_100g"), None),
                        salt_per_100g=safe_float(row.get("salt_per_100g"), None),
                        omega3_epa_dha_per_100g=safe_float(
                            row.get("omega3_epa_dha_per_100g"), None
                        ),
                        thiamine_b1_per_100g=safe_float(
                            row.get("thiamine_b1_per_100g"), None
                        ),
                        phosphorus_per_100g=safe_float(
                            row.get("phosphorus_per_100g"), None
                        ),
                        magnesium_per_100g=safe_float(
                            row.get("magnesium_per_100g"), None
                        ),
                        iron_per_100g=safe_float(row.get("iron_per_100g"), None),
                        zinc_per_100g=safe_float(row.get("zinc_per_100g"), None),
                        stock=safe_str(row.get("stock", "no")) or "no",
                    )
                    created_count += 1

        logger.info(
            f"Productos alimentarios cargados correctamente ✅ "
            f"({created_count} creados)"
        )
        return True

    def default_routines(self):
        """Crea las rutinas por defecto si no existen ya (sin usuario asignado)."""
        logger.info("Cargando rutinas por defecto 📋 ...")

        ROUTINES = [
            {
                "name": "Rutina mixta fuerza-calistenia",
                "duration": 6,
                "weekly_structure": "weider",
                "training_focus": "funcional_hibrido",
                "exercise_types": ["push", "pull", "legs", "core", "forearms"],
                "days": [
                    {
                        "day_number": 1, "name": "Push + calistenia de empuje", "is_rest": False,
                        "exercises": [
                            {"name": "Press banca o press inclinado", "sets_reps": "4x6-8", "notes": "Controla la bajada"},
                            {"name": "Press hombros con mancuernas", "sets_reps": "3x8-10", "notes": "Sin arquear la espalda"},
                            {"name": "Fondos en paralelas", "sets_reps": "4x6-10", "notes": "Añade peso si puedes"},
                            {"name": "Flexiones declinadas o pseudo planche push-ups", "sets_reps": "3x8-12", "notes": "Mantén el core fuerte"},
                            {"name": "Extensión de tríceps en polea", "sets_reps": "3x10-12", "notes": "Codos fijos"},
                            {"name": "Plancha con toque de hombros", "sets_reps": "3x30-40s", "notes": "Control total"},
                        ],
                    },
                    {
                        "day_number": 2, "name": "Pull + tirón en calistenia", "is_rest": False,
                        "exercises": [
                            {"name": "Dominadas lastradas o estrictas", "sets_reps": "4x5-8", "notes": "Pecho hacia la barra"},
                            {"name": "Remo con barra o mancuerna", "sets_reps": "3x8-10", "notes": "Tira con la espalda"},
                            {"name": "Chin-ups o dominadas supinas", "sets_reps": "3x6-10", "notes": "Recorrido completo"},
                            {"name": "Face pull", "sets_reps": "3x12-15", "notes": "Para salud de hombro"},
                            {"name": "Curl de bíceps con barra", "sets_reps": "3x8-12", "notes": "Sin balanceo"},
                            {"name": "Dead hang en barra", "sets_reps": "3x20-30s", "notes": "Si puedes, con toalla"},
                        ],
                    },
                    {
                        "day_number": 3, "name": "Piernas + core", "is_rest": False,
                        "exercises": [
                            {"name": "Sentadilla o prensa", "sets_reps": "4x6-8", "notes": "Profundidad controlada"},
                            {"name": "Peso muerto rumano", "sets_reps": "3x8-10", "notes": "Espalda neutra"},
                            {"name": "Zancadas caminando", "sets_reps": "3x10", "notes": "Paso controlado"},
                            {"name": "Sentadilla búlgara", "sets_reps": "3x8-10", "notes": "Muy buena para calistenia"},
                            {"name": "Elevaciones de gemelos", "sets_reps": "4x12-20", "notes": "Pausa arriba"},
                            {"name": "Elevaciones de piernas colgado", "sets_reps": "3x10-15", "notes": "Sin balanceo"},
                        ],
                    },
                    {
                        "day_number": 4, "name": "Calistenia torso + habilidades", "is_rest": False,
                        "exercises": [
                            {"name": "Dominadas pronas", "sets_reps": "4xAMRAP", "notes": "Deja 1-2 reps en reserva"},
                            {"name": "Fondos en paralelas", "sets_reps": "4xAMRAP", "notes": "Controla la bajada"},
                            {"name": "Flexiones archer o diamante", "sets_reps": "3x8-12", "notes": "Buena técnica"},
                            {"name": "Remo invertido en barra/TRX", "sets_reps": "3x10-15", "notes": "Cuerpo recto"},
                            {"name": "Pike push-ups", "sets_reps": "3x6-12", "notes": "Progresión a handstand"},
                            {"name": "Hollow body hold", "sets_reps": "3x20-40s", "notes": "Core muy importante"},
                        ],
                    },
                    {
                        "day_number": 5, "name": "Calistenia piernas + core + agarre", "is_rest": False,
                        "exercises": [
                            {"name": "Sentadilla pistol asistida o a caja", "sets_reps": "3x6-8", "notes": "Control y equilibrio"},
                            {"name": "Step-ups o búlgaras con peso corporal", "sets_reps": "3x10", "notes": "Sin impulso"},
                            {"name": "Nordic curl asistido o curl femoral deslizante", "sets_reps": "3x6-10", "notes": "Muy útil para isquios"},
                            {"name": "Elevaciones de rodillas colgado", "sets_reps": "3x12-15", "notes": "Sin balanceo"},
                            {"name": "L-sit en paralelas o suelo", "sets_reps": "4x10-20s", "notes": "Mantén la postura"},
                            {"name": "Pinch grip con discos", "sets_reps": "3x20s", "notes": "Agarre fuerte y limpio"},
                        ],
                    },
                    {
                        "day_number": 6, "name": "Antebrazos y grip", "is_rest": False,
                        "exercises": [
                            {"name": "Farmer walks pesados", "sets_reps": "4x30-45s", "notes": "Camina recto, hombros bajos"},
                            {"name": "Dead hang en barra", "sets_reps": "4x20-45s", "notes": "Si puedes, con toalla"},
                            {"name": "Curl de muñeca", "sets_reps": "3x15-20", "notes": "Controlado, sin rebotes"},
                            {"name": "Curl de muñeca inverso", "sets_reps": "3x15-20", "notes": "Muy útil para extensores"},
                            {"name": "Reverse curl con barra o mancuernas", "sets_reps": "3x10-12", "notes": "Ayuda mucho al antebrazo"},
                            {"name": "Pronosupinación con mancuerna", "sets_reps": "2-3x12-15", "notes": "Salud de codo y muñeca"},
                        ],
                    },
                    {"day_number": 7, "name": "Descanso", "is_rest": True, "exercises": []},
                ],
            },
            {
                "name": "Rutina PPL (Push-Pull-Legs)",
                "duration": 4,
                "weekly_structure": "push_pull_legs",
                "training_focus": "bodybuilding",
                "exercise_types": ["push", "pull", "legs", "core", "forearms"],
                "days": [
                    {
                        "day_number": 1, "name": "Día Push (Pecho, Hombros, Tríceps)", "is_rest": False,
                        "exercises": [
                            {"name": "Press banca/plano", "sets_reps": "4x8-10", "notes": "Controla bajada"},
                            {"name": "Press hombros mancuernas", "sets_reps": "3x10-12", "notes": "Sin arquear espalda"},
                            {"name": "Fondos pecho o máquina", "sets_reps": "3x10-12", "notes": "Añade peso si puedes"},
                            {"name": "Extensiones tríceps polea", "sets_reps": "3x12", "notes": "Mantén codos fijos"},
                            {"name": "Core: Plancha", "sets_reps": "3x30-45s", "notes": None},
                            {"name": "Antebrazos: Curl muñeca", "sets_reps": "3x15", "notes": "Opcional"},
                        ],
                    },
                    {
                        "day_number": 2, "name": "Día Pull (Espalda, Bíceps)", "is_rest": False,
                        "exercises": [
                            {"name": "Dominadas o jalón pecho", "sets_reps": "4x8-10", "notes": "Aprieta escápulas"},
                            {"name": "Remo mancuerna/barra", "sets_reps": "3x10-12", "notes": "Tira con espalda"},
                            {"name": "Face pull hombros posteriores", "sets_reps": "3x12", "notes": "Para postura"},
                            {"name": "Curl bíceps barra", "sets_reps": "3x10-12", "notes": "Sin balanceo"},
                            {"name": "Core: Elevación de piernas", "sets_reps": "3x12", "notes": None},
                            {"name": "Antebrazos: Giro muñeca inverso", "sets_reps": "3x15", "notes": None},
                        ],
                    },
                    {
                        "day_number": 3, "name": "Día Legs (Piernas)", "is_rest": False,
                        "exercises": [
                            {"name": "Sentadilla/prensa", "sets_reps": "4x8-10", "notes": "Profundidad 90°"},
                            {"name": "Peso muerto rumano", "sets_reps": "3x10-12", "notes": "Protege lumbares"},
                            {"name": "Zancadas caminando", "sets_reps": "3x10", "notes": "Controladas"},
                            {"name": "Elevación de gemelos", "sets_reps": "3x12-15", "notes": "Estira completo"},
                            {"name": "Core: Russian twists", "sets_reps": "3x20", "notes": "Con peso ligero"},
                        ],
                    },
                ],
            },
        ]

        created = 0
        for routine_def in ROUTINES:
            if Routine.objects.filter(user=None, exercise_types=routine_def["exercise_types"]).filter(
                days__day_number=1
            ).exists():
                logger.info(f"Rutina '{routine_def['name']}' ya existe, saltando")
                continue

            routine = Routine.objects.create(
                user=None,
                duration=routine_def.get("duration"),
                weekly_structure=routine_def["weekly_structure"],
                training_focus=routine_def["training_focus"],
                exercise_types=routine_def["exercise_types"],
            )

            for day_def in routine_def["days"]:
                routine_day = RoutineDay.objects.create(
                    routine=routine,
                    day_number=day_def["day_number"],
                    name=day_def["name"],
                    is_rest=day_def["is_rest"],
                )
                for order, ex in enumerate(day_def.get("exercises", [])):
                    library_ex, _ = MusculationExercise.objects.get_or_create(
                        name=ex["name"],
                        defaults={"sets": 0, "reps": 0},
                    )
                    routine.exercises.add(library_ex)
                    RoutineDayExercise.objects.create(
                        day=routine_day,
                        exercise=library_ex,
                        exercise_name=ex["name"],
                        sets_reps=ex.get("sets_reps", ""),
                        notes=ex.get("notes"),
                        order=order,
                    )

            logger.info(f"Rutina '{routine_def['name']}' creada ✅")
            created += 1

        logger.info(f"Rutinas por defecto cargadas ✅ ({created} creadas)")
        return True

    def prompts_data(self):
        """Carga los prompts desde los archivos de texto en la carpeta prompts/"""
        logger.info("Cargando prompts 🤖 ...")

        prompts_config = [
            {"name": "gym", "filename": "gym.txt"},
            {"name": "nutrition", "filename": "nutrition.txt"},
        ]

        created_count = 0
        updated_count = 0

        for prompt_config in prompts_config:
            prompt_name = prompt_config["name"]
            prompt_filename = prompt_config["filename"]
            prompt_path = self.get_prompt_path(prompt_filename)

            if not os.path.exists(prompt_path):
                logger.warning(
                    f"El archivo {prompt_path} no existe, saltando prompt '{prompt_name}'"
                )
                continue

            try:
                # Leer el contenido del archivo
                with open(prompt_path, "r", encoding="utf-8") as f:
                    prompt_content = f.read().strip()

                if not prompt_content:
                    logger.warning(
                        f"El archivo {prompt_path} está vacío, saltando prompt '{prompt_name}'"
                    )
                    continue

                # Buscar o crear el prompt
                prompt_obj, created = Promtps.objects.get_or_create(
                    name=prompt_name,
                    defaults={"prompt": prompt_content},
                )

                if not created:
                    # Si ya existe, actualizar el contenido
                    prompt_obj.prompt = prompt_content
                    prompt_obj.save()
                    updated_count += 1
                    logger.info(f"Prompt '{prompt_name}' actualizado ✅")
                else:
                    created_count += 1
                    logger.info(f"Prompt '{prompt_name}' creado ✅")

            except Exception as e:
                logger.error(
                    f"Error al procesar el prompt '{prompt_name}' desde {prompt_path}: {e}"
                )
                continue

        logger.info(
            f"Prompts cargados correctamente ✅ "
            f"({created_count} creados, {updated_count} actualizados)"
        )
        return True

    def ollama_models(self):
        """Precarga servidor Ollama por defecto y modelos llama3.2-vision:11b y qwen3:8b."""
        logger.info("Precargando servidor y modelos Ollama 🤖 ...")

        import os
        default_ollama_url = os.getenv("OLLAMA_BASE_URL", "http://ollama:11434")

        server, server_created = OllamaServer.objects.get_or_create(
            name="local",
            defaults={
                "base_url": default_ollama_url,
                "enabled": True,
                "api_key": "",
            },
        )
        if server_created:
            logger.info(f"Servidor Ollama 'local' creado ({default_ollama_url}) ✅")

        models_to_load = [
            {
                "model_name": "llama3.2-vision:11b",
                "alias": "llama3.2 vision 11b",
                "proposito": "OCR",
                "description": "Modelo de visión para extracción de datos desde imágenes (cardio, entrenamiento, producto).",
            },
            {
                "model_name": "qwen3:8b",
                "alias": "qwen3 8b",
                "proposito": "Razonamiento del nutricionista",
                "description": "Modelo de chat para conversación y razonamiento (nutrición, rutinas, medidas).",
            },
        ]

        created_count = 0
        for m in models_to_load:
            obj, created = OllamaModelConfig.objects.get_or_create(
                server=server,
                model_name=m["model_name"],
                defaults={
                    "alias": m["alias"],
                    "proposito": m["proposito"],
                    "description": m.get("description", ""),
                    "temperature": 0.7,
                    "top_p": 0.9,
                    "max_tokens": 512,
                    "is_default": False,
                    "deprecated": False,
                    "downloaded": False,
                    "update_available": True,
                },
            )
            if created:
                created_count += 1
                logger.info(f"Modelo Ollama '{m['model_name']}' ({m['proposito']}) creado ✅")

        logger.info(
            f"Modelos Ollama precargados correctamente ✅ ({created_count} nuevos)"
        )
        return True

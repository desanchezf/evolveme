import csv
import logging
import os
from datetime import datetime, timedelta

from django.conf import settings
from django.contrib.auth.models import User
from django.core.management.base import BaseCommand
from django.utils import timezone
from django.utils.dateparse import parse_datetime, parse_duration

from cardio.models import CardioExercise, CardioSession
from evolveme.models import GymUserProfile, Measure
from nutrition.models import Product
from gym.models import MusculationExercise, Routine, TrainingSession
from ia.models import Promtps

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = "Eliminar y recargar datos desde archivos CSV"

    def handle(self, *args, **options):
        self.stdout.write(self.style.WARNING("🗑️  Iniciando eliminación de datos..."))

        # Fase 1: Eliminar datos existentes
        if not self.delete_training_sessions():
            self.stdout.write(
                self.style.ERROR(
                    " ❌ Error al eliminar las sesiones de entrenamiento 💪"
                )
            )
            return
        else:
            self.stdout.write(
                self.style.SUCCESS(
                    " ✅ Sesiones de entrenamiento eliminadas correctamente 💪"
                )
            )

        if not self.delete_food_products():
            self.stdout.write(
                self.style.ERROR(" ❌ Error al eliminar los productos alimentarios 🍎")
            )
            return
        else:
            self.stdout.write(
                self.style.SUCCESS(
                    " ✅ Productos alimentarios eliminados correctamente 🍎"
                )
            )

        if not self.delete_cardio_training_session():
            self.stdout.write(
                self.style.ERROR(" ❌ Error al eliminar las sesiones de cardio 🚴")
            )
            return
        else:
            self.stdout.write(
                self.style.SUCCESS(" ✅ Sesiones de cardio eliminadas correctamente 🚴")
            )

        if not self.delete_musculation_exercises():
            self.stdout.write(
                self.style.ERROR(
                    " ❌ Error al eliminar los ejercicios de musculación 💪"
                )
            )
            return
        else:
            self.stdout.write(
                self.style.SUCCESS(
                    " ✅ Ejercicios de musculación eliminados correctamente 💪"
                )
            )

        if not self.delete_cardio_exercises():
            self.stdout.write(
                self.style.ERROR(" ❌ Error al eliminar los ejercicios de cardio 🏃")
            )
            return
        else:
            self.stdout.write(
                self.style.SUCCESS(
                    " ✅ Ejercicios de cardio eliminados correctamente 🏃"
                )
            )

        if not self.delete_measures_data():
            self.stdout.write(self.style.ERROR(" ❌ Error al eliminar las medidas 📏"))
            return
        else:
            self.stdout.write(
                self.style.SUCCESS(" ✅ Medidas eliminadas correctamente 📏")
            )

        if not self.delete_routines():
            self.stdout.write(self.style.ERROR(" ❌ Error al eliminar las rutinas 💪"))
            return
        else:
            self.stdout.write(
                self.style.SUCCESS(" ✅ Rutinas eliminadas correctamente 💪")
            )

        self.stdout.write(self.style.SUCCESS("\n✅ Fase de eliminación completada\n"))
        self.stdout.write(self.style.WARNING("📥 Iniciando carga de datos...\n"))

        # Fase 2: Importar datos
        if not self.user_data():
            self.stdout.write(
                self.style.ERROR(
                    " ❌ Error al cargar la información de los usuarios 👤"
                )
            )
            return
        else:
            self.stdout.write(
                self.style.SUCCESS(" ✅ Información cargada correctamente 👤")
            )

        if not self.measures_data():
            self.stdout.write(self.style.ERROR(" ❌ Error al cargar las medidas 📏"))
            return
        else:
            self.stdout.write(
                self.style.SUCCESS(" ✅ Medidas cargadas correctamente 📏")
            )

        if not self.musculation_exercises():
            self.stdout.write(
                self.style.ERROR(" ❌ Error al cargar los ejercicios de musculación 💪")
            )
            return
        else:
            self.stdout.write(
                self.style.SUCCESS(
                    " ✅ Ejercicios de musculación cargados correctamente 💪"
                )
            )

        if not self.cardio_exercises():
            self.stdout.write(
                self.style.ERROR(" ❌ Error al cargar los ejercicios de cardio 🏃")
            )
            return
        else:
            self.stdout.write(
                self.style.SUCCESS(" ✅ Ejercicios de cardio cargados correctamente 🏃")
            )

        if not self.cardio_training_session():
            self.stdout.write(
                self.style.ERROR(" ❌ Error al cargar las sesiones de cardio 🚴")
            )
            return
        else:
            self.stdout.write(
                self.style.SUCCESS(" ✅ Sesiones de cardio cargadas correctamente 🚴")
            )

        if not self.food_products():
            self.stdout.write(
                self.style.ERROR(" ❌ Error al cargar los productos alimentarios 🍎")
            )
            return
        else:
            self.stdout.write(
                self.style.SUCCESS(
                    " ✅ Productos alimentarios cargados correctamente 🍎"
                )
            )

        if not self.training_sessions():
            self.stdout.write(
                self.style.ERROR(" ❌ Error al cargar las sesiones de entrenamiento 💪")
            )
            return
        else:
            self.stdout.write(
                self.style.SUCCESS(
                    " ✅ Sesiones de entrenamiento cargadas correctamente 💪"
                )
            )

        if not self.prompts_data():
            self.stdout.write(self.style.ERROR(" ❌ Error al cargar los prompts 🤖"))
            return
        else:
            self.stdout.write(
                self.style.SUCCESS(" ✅ Prompts cargados correctamente 🤖")
            )

        self.stdout.write(
            self.style.SUCCESS(
                "\n✅ Proceso de actualización completado correctamente!"
            )
        )

    # ========== Métodos de eliminación ==========

    def delete_training_sessions(self):
        """Elimina las sesiones de entrenamiento"""
        logger.info("Eliminando sesiones de entrenamiento 💪 ...")
        deleted_count, _ = TrainingSession.objects.all().delete()
        logger.info(
            f"Sesiones de entrenamiento eliminadas correctamente ✅ "
            f"({deleted_count} eliminadas)"
        )
        return True

    def delete_food_products(self):
        """Elimina los productos alimentarios"""
        logger.info("Eliminando productos alimentarios 🍎 ...")
        deleted_count, _ = Product.objects.all().delete()
        logger.info(
            f"Productos alimentarios eliminados correctamente ✅ "
            f"({deleted_count} eliminados)"
        )
        return True

    def delete_cardio_training_session(self):
        """Elimina las sesiones de cardio"""
        logger.info("Eliminando sesiones de cardio 🚴 ...")
        deleted_count, _ = CardioSession.objects.all().delete()
        logger.info(
            f"Sesiones de cardio eliminadas correctamente ✅ "
            f"({deleted_count} eliminadas)"
        )
        return True

    def delete_musculation_exercises(self):
        """Elimina los ejercicios de musculación"""
        logger.info("Eliminando ejercicios de musculación 💪 ...")
        deleted_count, _ = MusculationExercise.objects.all().delete()
        logger.info(
            f"Ejercicios de musculación eliminados correctamente ✅ "
            f"({deleted_count} eliminados)"
        )
        return True

    def delete_cardio_exercises(self):
        """Elimina los ejercicios de cardio"""
        logger.info("Eliminando ejercicios de cardio 🏃 ...")
        deleted_count, _ = CardioExercise.objects.all().delete()
        logger.info(
            f"Ejercicios de cardio eliminados correctamente ✅ "
            f"({deleted_count} eliminados)"
        )
        return True

    def delete_measures_data(self):
        """Elimina las medidas"""
        logger.info("Eliminando medidas 📏 ...")
        deleted_count, _ = Measure.objects.all().delete()
        logger.info(f"Medidas eliminadas correctamente ✅ ({deleted_count} eliminadas)")
        return True

    def delete_routines(self):
        """Elimina las rutinas creadas por el comando de importación"""
        logger.info("Eliminando rutinas 💪 ...")
        deleted_count, _ = Routine.objects.all().delete()
        logger.info(f"Rutinas eliminadas correctamente ✅ ({deleted_count} eliminadas)")
        return True

    # ========== Métodos de importación ==========

    def get_csv_path(self, filename):
        """Obtiene la ruta del archivo CSV en la carpeta data/"""
        try:
            project_root = settings.BASE_DIR
        except AttributeError:
            project_root = os.path.dirname(
                os.path.dirname(
                    os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
                )
            )
        return os.path.join(project_root, "data", filename)

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
        """Carga los ejercicios de cardio desde cardio_exercises.csv"""
        logger.info("Cargando ejercicios de cardio 🏃 ...")

        csv_path = self.get_csv_path("cardio_exercises.csv")
        if not os.path.exists(csv_path):
            logger.warning(
                f"El archivo {csv_path} no existe, saltando carga de ejercicios de cardio"
            )
            return True  # No es crítico si no existe el archivo

        created_count = 0
        with open(csv_path, newline="", encoding="utf-8") as csvfile:
            exercises_reader = csv.DictReader(csvfile)
            for row in exercises_reader:
                exercise_name = row["name"]
                if not CardioExercise.objects.filter(name=exercise_name).exists():
                    exercise = CardioExercise.objects.create(
                        name=exercise_name,
                        description=row.get("description", "") or None,
                        image_base64=row.get("image_base64") or None,
                    )
                    created_count += 1
                    logger.info(
                        f"Ejercicio de cardio creado: {exercise.get_name_display() or exercise.name} ✅"
                    )

        logger.info(
            f"Ejercicios de cardio cargados correctamente ✅ ({created_count} creados)"
        )
        return True

    def cardio_training_session(self):
        """Carga las sesiones de cardio desde cardio_session.csv"""
        logger.info("Cargando sesiones de cardio 🚴 ...")

        csv_path = self.get_csv_path("cardio_session.csv")
        if not os.path.exists(csv_path):
            logger.error(f"El archivo {csv_path} no existe")
            return False

        created_count = 0
        with open(csv_path, newline="", encoding="utf-8") as csvfile:
            cardio_reader = csv.DictReader(csvfile)
            for row in cardio_reader:
                username = row.get("user", "david")
                user = User.objects.filter(username=username).first()
                if not user:
                    logger.warning(f"Usuario {username} no encontrado, saltando sesión")
                    continue

                # Parsear fechas y duraciones
                session_start = self.parse_datetime_safe(row.get("session_start"))
                session_end = self.parse_datetime_safe(row.get("session_end"))
                date_obj = datetime.strptime(row["date"], "%Y-%m-%d").date()
                workout_time = (
                    parse_duration(row["workout_time"])
                    if row.get("workout_time")
                    else None
                )

                # Buscar o crear el ejercicio de cardio
                exercise_name = row.get("name", "").strip()
                if not exercise_name:
                    logger.warning("Nombre de ejercicio vacío, saltando sesión")
                    continue

                exercise, created = CardioExercise.objects.get_or_create(
                    name=exercise_name,
                    defaults={
                        "description": "",
                    },
                )
                if created:
                    logger.info(
                        f"Ejercicio de cardio creado: {exercise.get_name_display() or exercise.name} ✅"
                    )

                # Verificar si ya existe
                if not CardioSession.objects.filter(
                    user=user, exercise=exercise, date=date_obj
                ).exists():
                    CardioSession.objects.create(
                        user=user,
                        exercise=exercise,
                        session_start=session_start,
                        session_end=session_end,
                        date=date_obj,
                        location=row.get("location") or None,
                        workout_time=workout_time,
                        distance=(
                            float(row["distance"]) if row.get("distance") else None
                        ),
                        avg_speed=(
                            float(row["avg_speed"]) if row.get("avg_speed") else None
                        ),
                        active_calories=int(row["active_calories"])
                        if row.get("active_calories")
                        else None,
                        total_calories=int(row["total_calories"])
                        if row.get("total_calories")
                        else None,
                        elevation_gain=int(row["elevation_gain"])
                        if row.get("elevation_gain")
                        else None,
                        average_heart_rate=int(row["average_heart_rate"])
                        if row.get("average_heart_rate")
                        else None,
                    )
                    created_count += 1

        logger.info(
            f"Sesiones de cardio cargadas correctamente ✅ ({created_count} creadas)"
        )
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

    def training_sessions(self):
        """Carga las sesiones de entrenamiento desde trainning_session.csv"""
        logger.info("Cargando sesiones de entrenamiento 💪 ...")

        csv_path = self.get_csv_path("trainning_session.csv")
        if not os.path.exists(csv_path):
            logger.error(f"El archivo {csv_path} no existe")
            return False

        # Crear una sola rutina por usuario antes de procesar las sesiones
        # y actualizar el perfil del usuario con las fechas de inicio y fin
        routines_by_user = {}
        with open(csv_path, newline="", encoding="utf-8") as csvfile:
            sessions_reader = csv.DictReader(csvfile)
            for row in sessions_reader:
                username = row.get("user", "david")
                if username not in routines_by_user:
                    user = User.objects.filter(username=username).first()
                    if user:
                        # Buscar o crear una rutina para este usuario
                        routine = Routine.objects.filter(user=user).first()
                        if not routine:
                            routine = Routine.objects.create(user=user)

                        # Actualizar el perfil del usuario con las fechas de inicio y fin
                        # (6 semanas después de la fecha de inicio)
                        profile, _ = GymUserProfile.objects.get_or_create(user=user)
                        if not profile.start_date:
                            profile.start_date = timezone.now().date()
                        if not profile.end_date:
                            profile.end_date = (
                                timezone.now() + timedelta(weeks=6)
                            ).date()
                        if not profile.active_routine:
                            profile.active_routine = routine
                        profile.save()

                        routines_by_user[username] = routine

        created_count = 0
        with open(csv_path, newline="", encoding="utf-8") as csvfile:
            sessions_reader = csv.DictReader(csvfile)
            for row in sessions_reader:
                username = row.get("user", "david")
                user = User.objects.filter(username=username).first()
                if not user:
                    logger.warning(f"Usuario {username} no encontrado, saltando sesión")
                    continue

                # Usar la rutina creada para este usuario
                routine = routines_by_user.get(username)

                session_date = self.parse_datetime_safe(row.get("session_date"))
                workout_time = (
                    parse_duration(row["workout_time"])
                    if row.get("workout_time")
                    else None
                )

                # Verificar si ya existe
                if not TrainingSession.objects.filter(
                    user=user, session_date=session_date
                ).exists():
                    TrainingSession.objects.create(
                        user=user,
                        routine=routine,
                        session_date=session_date,
                        location=row.get("location") or None,
                        workout_time=workout_time,
                        active_kilocalories=int(row["active_kilocalories"])
                        if row.get("active_kilocalories")
                        else None,
                        total_kilocalories=int(row["total_kilocalories"])
                        if row.get("total_kilocalories")
                        else None,
                        avg_heart_rate=int(row["avg_heart_rate"])
                        if row.get("avg_heart_rate")
                        else None,
                    )
                    created_count += 1

        logger.info(
            f"Sesiones de entrenamiento cargadas correctamente ✅ "
            f"({created_count} creadas)"
        )
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

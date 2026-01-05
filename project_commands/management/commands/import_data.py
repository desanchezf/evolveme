import csv
import logging
import os
from datetime import datetime

from django.conf import settings
from django.contrib.auth.models import User
from django.core.management.base import BaseCommand
from django.utils.dateparse import parse_datetime, parse_duration

from cardio.models import CardioSession
from evolveme.models import Measure
from food.models import Product
from gym.models import MusculationExercise, Routine, TrainingSession

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
        if not self.cardio_training_session():
            print(" ❌ Error al cargar las sesiones de cardio 🚴")
            return
        else:
            print(" ✅ Sesiones de cardio cargadas correctamente 🚴")
        if not self.food_products():
            print(" ❌ Error al cargar los productos alimentarios 🍎")
            return
        else:
            print(" ✅ Productos alimentarios cargados correctamente 🍎")
        if not self.training_sessions():
            print(" ❌ Error al cargar las sesiones de entrenamiento 💪")
            return
        else:
            print(" ✅ Sesiones de entrenamiento cargadas correctamente 💪")

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
                        weight=float(row["weight"]) if row.get("weight") else None,
                        arm=float(row["arm"]) if row.get("arm") else None,
                        chest=float(row["chest"]) if row.get("chest") else None,
                        waist=float(row["waist"]) if row.get("waist") else None,
                        leg=float(row["leg"]) if row.get("leg") else None,
                        fat_perc=float(row["fat_perc"])
                        if row.get("fat_perc")
                        else None,
                        muscle_mass=float(row["muscle_mass"])
                        if row.get("muscle_mass")
                        else None,
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
                        image_base64=row.get("image_base64") or None,
                    )
                    created_count += 1

        logger.info(
            f"Ejercicios de musculación cargados correctamente ✅ "
            f"({created_count} creados)"
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
                session_start = (
                    parse_datetime(row["session_start"])
                    if row.get("session_start")
                    else None
                )
                session_end = (
                    parse_datetime(row["session_end"])
                    if row.get("session_end")
                    else None
                )
                date_obj = datetime.strptime(row["date"], "%Y-%m-%d").date()
                workout_time = (
                    parse_duration(row["workout_time"])
                    if row.get("workout_time")
                    else None
                )

                # Verificar si ya existe
                if not CardioSession.objects.filter(
                    user=user, name=row["name"], date=date_obj
                ).exists():
                    CardioSession.objects.create(
                        user=user,
                        name=row["name"],
                        exercise_type=row.get("exercise_type") or None,
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
                        description=row.get("description", "") or "",
                        market=row.get("market") or "",
                        calories_per_100g=float(row["calories_per_100g"])
                        if row.get("calories_per_100g")
                        else 0,
                        protein_per_100g=float(row["protein_per_100g"])
                        if row.get("protein_per_100g")
                        else 0,
                        carbs_per_100g=float(row["carbs_per_100g"])
                        if row.get("carbs_per_100g")
                        else 0,
                        fat_per_100g=float(row["fat_per_100g"])
                        if row.get("fat_per_100g")
                        else 0,
                        saturated_fat_per_100g=(
                            float(row["saturated_fat_per_100g"])
                            if row.get("saturated_fat_per_100g")
                            else 0
                        ),
                        monounsaturated_fat_per_100g=(
                            float(row["monounsaturated_fat_per_100g"])
                            if row.get("monounsaturated_fat_per_100g")
                            else 0
                        ),
                        polyunsaturated_fat_per_100g=(
                            float(row["polyunsaturated_fat_per_100g"])
                            if row.get("polyunsaturated_fat_per_100g")
                            else 0
                        ),
                        sugars_per_100g=float(row["sugars_per_100g"])
                        if row.get("sugars_per_100g")
                        else 0,
                        polyols_per_100g=float(row["polyols_per_100g"])
                        if row.get("polyols_per_100g")
                        else 0,
                        fiber_per_100g=float(row["fiber_per_100g"])
                        if row.get("fiber_per_100g")
                        else 0,
                        salt_per_100g=float(row["salt_per_100g"])
                        if row.get("salt_per_100g")
                        else 0,
                        stock=row.get("stock", "no") or "no",
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

        created_count = 0
        with open(csv_path, newline="", encoding="utf-8") as csvfile:
            sessions_reader = csv.DictReader(csvfile)
            for row in sessions_reader:
                username = row.get("user", "david")
                user = User.objects.filter(username=username).first()
                if not user:
                    logger.warning(f"Usuario {username} no encontrado, saltando sesión")
                    continue

                # Obtener o crear rutina si se especifica routine_id
                routine = None
                if row.get("routine_id"):
                    try:
                        routine_id = int(row["routine_id"])
                        routine = Routine.objects.filter(id=routine_id).first()
                        if not routine:
                            # Crear rutina básica si no existe
                            routine = Routine.objects.create(
                                user=user,
                                start_date=datetime.now(),
                            )
                    except (ValueError, TypeError):
                        pass

                session_date = (
                    parse_datetime(row["session_date"])
                    if row.get("session_date")
                    else None
                )
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

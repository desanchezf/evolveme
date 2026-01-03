import csv
import logging
import os
from datetime import date

from django.conf import settings
from django.core.management.base import BaseCommand

logger = logging.getLogger(__name__)

from cardio.models import CardioSession
from evolveme.models import Measure, User
from food.models import Food
from gym.models import MusculationExercise


class Command(BaseCommand):
    help = "Addind inittial data"

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

    def user_data(self):
        logger.info("Cargando información de los usuarios 👤 ...")
        if not User.objects.filter(username="usuario_prueba").exists():
            User.objects.create(
                username="usuario_prueba",
                email="usuario@prueba.com",
                password="usuario_prueba@",
            )
            logger.info("Información de los usuarios cargada correctamente ✅")
            return True
        logger.info("Usuario ya existe ✅")
        return True

    def measures_data(self):
        logger.info("Cargando medidas 📏 ...")

        csv_path = os.path.join(os.path.dirname(__file__), "csv", "measures.csv")
        with open(csv_path, newline="", encoding="utf-8") as csvfile:
            measures_reader = csv.DictReader(csvfile)
            for row in measures_reader:
                user = User.objects.first()
                if not user:
                    logger.error("No hay usuarios en la base de datos")
                    return False
                if not Measure.objects.filter(
                    user__username=user.username, date=row["date"]
                ).exists():
                    Measure.objects.create(
                        user=user,
                        date=row["date"],
                        weight=float(row["weight"]) if row["weight"] else None,
                        arm=float(row["arm"]) if row["arm"] else None,
                        chest=float(row["chest"]) if row["chest"] else None,
                        waist=float(row["waist"]) if row["waist"] else None,
                        leg=float(row["leg"]) if row["leg"] else None,
                        fat_perc=float(row["fat_perc"]) if row["fat_perc"] else None,
                        muscle_mass=float(row["muscle_mass"])
                        if row["muscle_mass"]
                        else None,
                    )

        logger.info("Medidas cargadas correctamente ✅")
        return True

    def musculation_exercises(self):
        logger.info("Cargando ejercicios de musculación 💪 ...")

        csv_path = os.path.join(os.path.dirname(__file__), "csv", "exercises.csv")
        with open(csv_path, newline="", encoding="utf-8") as csvfile:
            exercises_reader = csv.DictReader(csvfile)
            for row in exercises_reader:
                if not MusculationExercise.objects.filter(id=row["id"]).exists():
                    MusculationExercise.objects.create(
                        id=row["id"],
                        name=row["name"],
                        description=row["description"] if row["description"] else None,
                        body_part=row["body_part"] if row["body_part"] else None,
                        observation=row["observation"] if row["observation"] else None,
                        image_base64=row["image_base64"]
                        if row["image_base64"]
                        else None,
                    )

        logger.info("Ejercicios de musculación cargados correctamente ✅")
        return True

    def cardio_training_session(self):
        logger.info("Cargando sesiones de cardio 🚴 ...")

        user = User.objects.first()
        if not user:
            logger.error("No hay usuarios en la base de datos")
            return False

        csv_path = os.path.join(os.path.dirname(__file__), "csv", "cardio_sessions.csv")
        with open(csv_path, newline="", encoding="utf-8") as csvfile:
            cardio_reader = csv.DictReader(csvfile)
            for row in cardio_reader:
                # El CSV no tiene fecha, usamos la fecha actual
                # Si ya existe una sesión con la misma fecha y nombre, la saltamos
                if not CardioSession.objects.filter(
                    user=user, name=row["name"], date=date.today()
                ).exists():
                    CardioSession.objects.create(
                        user=user,
                        name=row["name"],
                        date=date.today(),
                        workout_time=int(row["workout_time"]),
                        distance=float(row["distance"]) if row["distance"] else None,
                        active_calories=int(row["active_calories"])
                        if row["active_calories"]
                        else None,
                        total_calories=int(row["total_calories"])
                        if row["total_calories"]
                        else None,
                        elevation_gain=int(row["elevation_gain"])
                        if row["elevation_gain"]
                        else None,
                        average_heart_rate=int(row["average_heart_rate"])
                        if row["average_heart_rate"]
                        else None,
                        avg_speed=float(row["avg_speed"]) if row["avg_speed"] else None,
                    )

        logger.info("Sesiones de cardio cargadas correctamente ✅")
        return True

    def food_products(self):
        logger.info("Cargando productos alimentarios 🍎 ...")

        # Obtener la ruta del archivo food.txt relativa al directorio del proyecto
        # El archivo está en prompts/food.txt desde la raíz del proyecto
        try:
            project_root = settings.BASE_DIR
        except AttributeError:
            # Fallback si BASE_DIR no está disponible
            project_root = os.path.dirname(
                os.path.dirname(
                    os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
                )
            )
        food_file_path = os.path.join(project_root, "prompts", "food.txt")

        if not os.path.exists(food_file_path):
            logger.error(f"El archivo {food_file_path} no existe")
            return False

        with open(food_file_path, "r", encoding="utf-8") as f:
            products = [line.strip() for line in f if line.strip()]

        created_count = 0
        skipped_count = 0

        for product_name in products:
            if not Food.objects.filter(name=product_name).exists():
                Food.objects.create(
                    name=product_name,
                    description="",
                    calories_per_100g=0,
                    protein_per_100g=0,
                    carbs_per_100g=0,
                    fat_per_100g=0,
                )
                created_count += 1
            else:
                skipped_count += 1

        logger.info(
            f"Productos alimentarios cargados correctamente ✅ "
            f"(Creados: {created_count}, Ya existían: {skipped_count})"
        )
        return True

    def daily_meals(self):
        pass
   
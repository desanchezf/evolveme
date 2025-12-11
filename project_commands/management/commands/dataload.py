import csv
import logging

from django.core.management.base import BaseCommand

logger = logging.getLogger(__name__)

from evolveme.models import (CardioExercise, GymUserProfile, Measure,
                             MusculationExercise, User)


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
            print(" ✅ Medidas cargadas correctamente 💪")
        if not self.cardio_training_session():
            print(" ❌ Error al cargar las sesiones de cardio 🚴")
            return
        else:
            print(" ✅ Información cargada correctamente 🚴")

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

        with open('evolveme/csv/measures.csv', newline='') as csvfile:
            measures_reader = csv.DictReader(csvfile)
            for row in measures_reader:
                user = User.objects.first()
                if not Measure.objects.filter(user__username=user.username, date=row['date']).exists():
                    Measure.objects.create(
                        user=user,
                        date=row['date'],
                        weight=row['weight'],
                        arm=row['arm'],
                        chest=row['chest'],
                        waist=row['waist'],
                        leg=row['leg'],
                        fat_perc=row['fat_perc'],
                        muscle_mass=row['muscle_mass']
                    )

        logger.info("Medidas cargadas correctamente ✅")
        return True

    def musculation_exercises(self):
        logger.info("Cargando ejercicios de musculación 💪 ...")

        with open('evolveme/csv/exercises.csv', newline='') as csvfile:
            exercises_reader = csv.DictReader(csvfile)
            for row in exercises_reader:
                if not MusculationExercise.objects.filter(id=row['id']).exists():
                    MusculationExercise.objects.create(
                        id=row['id'],
                        name=row['name'],
                        description=row['description'],
                        body_part=row['body_part'],
                        observation=row['observation'],
                        image_base64=row['image_base64']
                    )

        logger.info("Ejercicios de musculación cargados correctamente ✅")
        return True

    def cardio_training_session(self):
        logger.info("Cargando sesiones de cardio 🚴 ...")

        with open('evolveme/csv/cardio_sessions.csv', newline='') as csvfile:
            cardio_reader = csv.DictReader(csvfile)
            for row in cardio_reader:
                CardioExercise.objects.create(
                    name=row['name'],
                    workout_time=row['workout_time'],
                    distance=row['distance'],
                    active_calories=row['active_calories'],
                    total_calories=row['total_calories'],
                    elevation_gain=row['elevation_gain'],
                    average_heart_rate=row['average_heart_rate'],
                    avg_speed=row['avg_speed']
                )

        logger.info("Sesiones de cardio cargadas correctamente ✅")
        return True

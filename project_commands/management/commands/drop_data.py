import logging

from django.core.management.base import BaseCommand

from cardio.models import CardioSession
from evolveme.models import Measure
from nutrition.models import Product
from gym.models import MusculationExercise, Routine, TrainingSession

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = "Eliminar datos importados desde archivos CSV"

    def handle(self, *args, **options):
        if not self.training_sessions():
            print(" ❌ Error al eliminar las sesiones de entrenamiento 💪")
            return
        else:
            print(" ✅ Sesiones de entrenamiento eliminadas correctamente 💪")
        if not self.food_products():
            print(" ❌ Error al eliminar los productos alimentarios 🍎")
            return
        else:
            print(" ✅ Productos alimentarios eliminados correctamente 🍎")
        if not self.cardio_training_session():
            print(" ❌ Error al eliminar las sesiones de cardio 🚴")
            return
        else:
            print(" ✅ Sesiones de cardio eliminadas correctamente 🚴")
        if not self.musculation_exercises():
            print(" ❌ Error al eliminar los ejercicios de musculación 💪")
            return
        else:
            print(" ✅ Ejercicios de musculación eliminados correctamente 💪")
        if not self.measures_data():
            print(" ❌ Error al eliminar las medidas 📏")
            return
        else:
            print(" ✅ Medidas eliminadas correctamente 📏")
        if not self.routines():
            print(" ❌ Error al eliminar las rutinas 💪")
            return
        else:
            print(" ✅ Rutinas eliminadas correctamente 💪")

    def training_sessions(self):
        """Elimina las sesiones de entrenamiento"""
        logger.info("Eliminando sesiones de entrenamiento 💪 ...")
        deleted_count, _ = TrainingSession.objects.all().delete()
        logger.info(
            f"Sesiones de entrenamiento eliminadas correctamente ✅ "
            f"({deleted_count} eliminadas)"
        )
        return True

    def food_products(self):
        """Elimina los productos alimentarios"""
        logger.info("Eliminando productos alimentarios 🍎 ...")
        deleted_count, _ = Product.objects.all().delete()
        logger.info(
            f"Productos alimentarios eliminados correctamente ✅ "
            f"({deleted_count} eliminados)"
        )
        return True

    def cardio_training_session(self):
        """Elimina las sesiones de cardio"""
        logger.info("Eliminando sesiones de cardio 🚴 ...")
        deleted_count, _ = CardioSession.objects.all().delete()
        logger.info(
            f"Sesiones de cardio eliminadas correctamente ✅ "
            f"({deleted_count} eliminadas)"
        )
        return True

    def musculation_exercises(self):
        """Elimina los ejercicios de musculación"""
        logger.info("Eliminando ejercicios de musculación 💪 ...")
        deleted_count, _ = MusculationExercise.objects.all().delete()
        logger.info(
            f"Ejercicios de musculación eliminados correctamente ✅ "
            f"({deleted_count} eliminados)"
        )
        return True

    def measures_data(self):
        """Elimina las medidas"""
        logger.info("Eliminando medidas 📏 ...")
        deleted_count, _ = Measure.objects.all().delete()
        logger.info(f"Medidas eliminadas correctamente ✅ ({deleted_count} eliminadas)")
        return True

    def routines(self):
        """Elimina las rutinas creadas por el comando de importación"""
        logger.info("Eliminando rutinas 💪 ...")
        deleted_count, _ = Routine.objects.all().delete()
        logger.info(f"Rutinas eliminadas correctamente ✅ ({deleted_count} eliminadas)")
        return True

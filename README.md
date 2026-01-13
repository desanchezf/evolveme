# EvolveMe - Sistema de Gestión de Fitness y Nutrición

![Django](https://img.shields.io/badge/Django-4.2.17-green.svg?style=plastic)
![Python](https://img.shields.io/badge/Python-3.12-blue.svg?style=plastic&logo=python&logoColor=white)
![Docker](https://img.shields.io/badge/Docker-2496ED?style=plastic&logo=docker&logoColor=white)
![Unfold Admin](https://img.shields.io/badge/Unfold-Admin-orange.svg?style=plastic)

Sistema completo de gestión para seguimiento de entrenamientos, nutrición y medidas corporales con integración de IA para generación de rutinas y dietas personalizadas.

---

## 🚀 Características Principales

- **Gestión de Entrenamientos**: Rutinas de musculación, sesiones de cardio y registros de ejercicios
- **Gestión de Nutrición**: Productos alimentarios, dietas diarias y seguimiento de consumo
- **Seguimiento Corporal**: Medidas corporales y composición corporal detallada
- **Integración con IA**: Generación automática de rutinas y dietas mediante prompts
- **Admin Personalizado**: Interfaz moderna con tema Unfold personalizado (naranja DuckDuckGo)
- **Formularios Avanzados**: Formsets para entrada de datos múltiples
- **Importación de Datos**: Comandos para cargar datos desde archivos CSV

---

## 📁 Estructura del Proyecto

### Apps Instaladas

- **evolveme**: App principal con perfiles de usuario y medidas corporales
- **cardio**: Gestión de ejercicios y sesiones de cardio
- **gym**: Gestión de ejercicios de musculación, rutinas y sesiones de entrenamiento
- **nutrition**: Gestión de alimentos, productos y dietas diarias (renombrada desde "food")
- **ia**: Gestión de prompts para integración con modelos de IA
- **project_commands**: Comandos de gestión personalizados

---

## 🎨 Personalización del Admin

El proyecto utiliza **Unfold Admin** con un tema personalizado inspirado en DuckDuckGo:

- **Color primario**: Naranja DuckDuckGo (`#FF6600`)
- **Fondos**: Grises oscuros (`#1a1a1a`, `#2d2d2d`)
- **Resaltes**: Grises claros (`#3d3d3d`, `#4a4a4a`)

La personalización se encuentra en:
- `project/settings.py`: Configuración `UNFOLD`
- `static/css/unfold_custom.css`: Estilos CSS personalizados

---

## 📦 Apps y Modelos

### Evolveme App

**Modelos:**
- **GymUserProfile**: Perfil del usuario del gimnasio
  - Información personal (fecha de nacimiento, género, altura)
  - Objetivos del usuario (perder peso, ganar músculo, etc.)
- **Measure**: Seguimiento de medidas corporales
  - Medidas básicas: peso, brazos, pecho, cintura, piernas
  - Composición corporal: porcentaje de grasa, masa muscular, BMI
  - Métricas avanzadas: agua corporal, masa ósea, proteína, grasa visceral, tasa metabólica basal, etc.

**Enums:**
- `GenderChoices`: Género (Masculino, Femenino, Otro)
- `ObjectiveChoices`: Objetivos (Perder peso, Ganar músculo, Ganar peso, Mejorar salud, Mejorar rendimiento)

**Estado:**
- [x] Perfil del gimnasio (GymUserProfile)
- [x] Seguimiento de medidas corporales (Measure) con métricas avanzadas
- [x] Admin configurado con fieldsets organizados
- [x] Grupos de usuarios y permisos configurados

---

### Cardio App

**Modelos:**
- **CardioSession**: Sesiones de ejercicio cardiovascular
  - Tipo de ejercicio (caminar, ciclismo, elíptica)
  - Tiempo, distancia, calorías
  - Frecuencia cardíaca promedio, velocidad promedio
  - Elevación ganada
  - Fechas de inicio y fin

**Enums:**
- `CardioExerciseChoices`: Tipos de ejercicios de cardio

**Estado:**
- [x] Modelo de sesiones de cardio
- [x] Admin configurado con fieldsets
- [x] Importación desde CSV

---

### Gym App

**Modelos:**
- **MusculationExercise**: Ejercicios de musculación
  - Nombre, descripción, parte del cuerpo
  - Series y repeticiones por defecto
  - Imagen en base64
- **MusculationRecord**: Registros de ejercicios realizados
  - Usuario, ejercicio, fecha
  - Series, repeticiones, peso
  - Flag "To be improved" (TBI)
  - Observaciones
- **Routine**: Rutinas de entrenamiento
  - Usuario, fechas de inicio y fin
  - Tipos de ejercicios (push, pull, legs, core, etc.) - campo JSON
  - Calentamiento (warmup)
  - Ejercicios asociados (ManyToMany)
- **TrainingSession**: Sesiones de entrenamiento
  - Usuario, rutina asociada
  - Fecha y hora, ubicación
  - Tiempo de entrenamiento
  - Calorías activas y totales
  - Frecuencia cardíaca promedio

**Enums:**
- `BodyPartChoices`: Partes del cuerpo (Pecho, Espalda, Piernas, Brazos, Hombros, Abdomen, Antebrazos, Zona media)
- `ExerciseTypesChoices`: Tipos de ejercicios (Push, Pull, Legs, Core, Full Body, Lower Body, Upper Body, Abs, Forearms)

**Formularios:**
- **MusculationRecordFormsetView**: Formulario con formset para registrar múltiples ejercicios en una sesión
- **RoutineJSONView**: Formulario para generar rutinas desde JSON generado por IA

**Templates:**
- `gym/musculation_record_formset.html`: Formulario de registro de entrenamiento
- `gym/routine_json_form.html`: Formulario para generar rutina desde JSON

**Estado:**
- [x] Ejercicios de musculación (MusculationExercise)
- [x] Registros de ejercicios (MusculationRecord)
- [x] Sesiones de entrenamiento (TrainingSession)
- [x] Rutinas (Routine) con tipos de ejercicios y calentamiento
- [x] Admin configurado
- [x] Formularios con formsets
- [x] Generación de rutinas desde JSON

---

### Nutrition App (anteriormente "food")

**Modelos:**
- **Product**: Productos alimentarios
  - Nombre, descripción, código de barras
  - Información nutricional completa por 100g:
    - Valor energético (kJ y kcal)
    - Macronutrientes: proteínas, carbohidratos, grasas (saturadas, monoinsaturadas, poliinsaturadas)
    - Azúcares, polialcoholes, fibra, sal
    - Omega-3 (EPA+DHA)
    - Micronutrientes: tiamina B1, fósforo, magnesio, hierro, zinc
  - Mercado y stock
- **ProductQuantity**: Cantidad de producto
  - Producto, cantidad, unidad de medida
- **DailyDiet**: Dieta diaria
  - Usuario, fecha
  - Productos y cantidades consumidas (ManyToMany con ProductQuantity)
- **MealMetrics**: Métricas nutricionales de una dieta
  - Calorías, proteínas, carbohidratos, grasas

**Enums:**
- `MarketChoices`: Mercados disponibles
- `StockChoices`: Estado de stock (Sí, No, Comprar)

**Formularios:**
- **DailyDietFormsetView**: Formulario con formset para registrar dieta diaria con múltiples productos
- **DietJSONView**: Formulario para generar dieta semanal desde JSON generado por IA

**Templates:**
- `nutrition/daily_diet_formset.html`: Formulario de registro de dieta diaria
- `nutrition/diet_json_form.html`: Formulario para generar dieta semanal desde JSON

**Estado:**
- [x] Productos alimentarios (Product) con información nutricional completa
- [x] Cantidades de productos (ProductQuantity)
- [x] Dietas diarias (DailyDiet)
- [x] Métricas de comida (MealMetrics)
- [x] Admin configurado
- [x] Formularios con formsets
- [x] Generación de dietas semanales desde JSON
- [x] Importación desde CSV

---

### IA App

**Modelos:**
- **Promtps**: Prompts para modelos de IA
  - Nombre del prompt
  - Contenido del prompt (texto completo)
  - Fechas de creación y actualización

**Estado:**
- [x] Modelo de prompts
- [x] Admin configurado
- [x] Importación automática desde archivos de texto

---

## 🤖 Integración con IA

### Prompts Disponibles

El proyecto incluye prompts predefinidos para generar rutinas y dietas:

- **`prompts/gym.txt`**: Prompt para generar rutinas de ejercicios (Push-Pull-Legs)
- **`prompts/nutrition.txt`**: Prompt para generar dietas semanales personalizadas

### Estructuras JSON de Respuesta

El sistema espera respuestas JSON estructuradas de los modelos de IA:

- **`prompts/gym_response.txt`**: Estructura JSON para rutinas de ejercicios
  - Usuario, fechas, tipos de ejercicios, calentamiento
  - Días de la rutina con ejercicios (nombre, descripción, parte del cuerpo, series, repeticiones)

- **`prompts/nutrition_response.txt`**: Estructura JSON para dietas semanales
  - Usuario, fecha de inicio de semana
  - Días de la semana (lunes a sábado) con comidas:
    - Desayuno, media mañana, almuerzo, merienda, cena
    - Productos con nombre, cantidad y unidad

### Generación desde JSON

**Rutinas:**
1. Acceder a `/admin/gym/routine/generate-from-json/`
2. Pegar el JSON generado por la IA
3. El sistema crea automáticamente:
   - La rutina con fechas y tipos de ejercicios
   - Los ejercicios si no existen
   - Asocia los ejercicios a la rutina

**Dietas:**
1. Acceder a `/admin/nutrition/dailydiet/generate-from-json/`
2. Pegar el JSON generado por la IA
3. El sistema crea automáticamente:
   - Dietas diarias para cada día de la semana
   - ProductQuantity para cada producto
   - Busca productos por nombre (case-insensitive)

---

## 📊 Comandos de Gestión

### Importación de Datos

```bash
python manage.py import_data
```

Este comando importa datos desde archivos CSV en la carpeta `data/`:

- **Usuarios**: Crea usuario "david" si no existe
- **Medidas**: Desde `measures.csv`
- **Ejercicios de musculación**: Desde `musculation_exercises.csv`
- **Sesiones de cardio**: Desde `cardio_session.csv`
- **Productos alimentarios**: Desde `products.csv`
- **Sesiones de entrenamiento**: Desde `trainning_session.csv`
- **Rutinas**: Crea automáticamente una rutina por usuario (6 semanas de duración)
- **Prompts**: Desde `prompts/gym.txt` y `prompts/nutrition.txt`

### Eliminación de Datos

```bash
python manage.py drop_data
```

Elimina todos los datos importados por el comando `import_data`.

---

## 🎯 Formularios Avanzados

### Formsets

El proyecto utiliza Django Formsets con Crispy Forms y Unfold Admin:

**MusculationRecordFormset:**
- Permite registrar múltiples ejercicios en una sesión de entrenamiento
- Accesible desde: `/admin/gym/musculationrecord/add-formset/`
- Incluye: usuario, fecha, y múltiples ejercicios con series, repeticiones, peso, TBI y observaciones

**ProductQuantityFormSet:**
- Permite registrar múltiples productos en una dieta diaria
- Accesible desde: `/admin/nutrition/dailydiet/add-formset/`
- Incluye: usuario, fecha, y múltiples productos con cantidad y unidad

---

## 🗂️ Archivos de Datos

Los archivos CSV se encuentran en la carpeta `data/`:

- `measures.csv`: Medidas corporales
- `musculation_exercises.csv`: Ejercicios de musculación
- `cardio_session.csv`: Sesiones de cardio
- `products.csv`: Productos alimentarios
- `trainning_session.csv`: Sesiones de entrenamiento

---

## 🛠️ Configuración

### Variables de Entorno

El proyecto utiliza variables de entorno para configuración sensible:

- `ADMIN_USERNAME`: Usuario administrador
- `ADMIN_PASSWORD`: Contraseña del administrador
- `ADMIN_EMAIL`: Email del administrador
- `ADMIN_GROUPS`: Grupos de usuarios (separados por comas)

### Configuración de Unfold

En `project/settings.py`:

```python
UNFOLD = {
    "PRIMARY_COLOR": "#FF6600",  # Naranja DuckDuckGo
    "SECONDARY_COLOR": "#3d3d3d",  # Gris claro
    "STYLES": [
        "/static/css/unfold_custom.css",
    ],
}
```

### Archivos Estáticos

- `STATIC_URL = "static/"`
- `STATICFILES_DIRS = [BASE_DIR / "static"]`
- `STATIC_ROOT = BASE_DIR / "staticfiles"`

---

## 📝 Tareas Pendientes

### Funcionalidades Futuras
- [ ] API REST con Django REST Framework
- [ ] Documentación Swagger/OpenAPI
- [ ] Integración con Redis y Celery para tareas asíncronas
- [ ] Notificaciones por correo y SMS
- [ ] Dashboard con gráficos y estadísticas
- [ ] Exportación de datos a PDF/Excel
- [ ] Aplicación móvil

---

## 🚀 Instalación y Uso

### Requisitos

- Python 3.12+
- Django 4.2.17
- PostgreSQL
- Docker (opcional)

### Instalación

1. Clonar el repositorio
2. Instalar dependencias: `pip install -r requirements.txt`
3. Configurar variables de entorno
4. Ejecutar migraciones: `python manage.py migrate`
5. Importar datos iniciales: `python manage.py import_data`
6. Crear superusuario: `python manage.py createsuperuser`
7. Ejecutar servidor: `python manage.py runserver`

### Docker

```bash
docker-compose up -d
```

---

## 📄 Licencia

Este proyecto es de uso privado.

---

## 👥 Contribuidores

- David Sánchez

---

## 📞 Soporte

Para más información, consultar la documentación de Django Unfold: https://unfoldadmin.com/

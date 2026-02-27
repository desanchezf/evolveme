# EvolveMe - Sistema de Gestión de Fitness y Nutrición

![Django](https://img.shields.io/badge/Django-4.2.17-green.svg?style=plastic)
![Python](https://img.shields.io/badge/Python-3.12-blue.svg?style=plastic&logo=python&logoColor=white)
![Docker](https://img.shields.io/badge/Docker-2496ED?style=plastic&logo=docker&logoColor=white)
![Jazzmin](https://img.shields.io/badge/Jazzmin-Admin-blue.svg?style=plastic)

Sistema completo de gestión para seguimiento de entrenamientos, nutrición y medidas corporales con integración de IA para generación de rutinas y dietas personalizadas.

---

## 🚀 Características Principales

- **Gestión de Entrenamientos**: Rutinas de musculación, sesiones de cardio y registros de ejercicios
- **Gestión de Nutrición**: Productos alimentarios, dietas diarias y seguimiento de consumo
- **Seguimiento Corporal**: Medidas corporales y composición corporal detallada
- **Integración con IA**: Generación automática de rutinas y dietas mediante prompts
- **Admin Personalizado**: Interfaz moderna con tema Jazzmin
- **Formularios Avanzados**: Formsets para entrada de datos múltiples
- **Importación de Datos**: Comandos para cargar datos desde archivos CSV

---

## 🔗 URLs de Formularios Públicos

Todos los formularios requieren autenticación (`@login_required`). Si el usuario no está autenticado, será redirigido automáticamente a la página de login.

### Página Principal

- **`/`** - Panel principal con tarjetas de acceso a todos los formularios
  - Vista: `IndexView`
  - Requiere autenticación: ✅

### Formularios de Evolveme

- **`/measure/`** - Registrar medidas corporales
  - Vista: `measure_form_view`
  - Formulario: `MeasureForm`
  - Modelo: `Measure`
  - Requiere autenticación: ✅

### Formularios de Cardio

- **`/cardio/cardio-session/`** - Registrar sesión de cardio
  - Vista: `cardio_session_form_view`
  - Formulario: `CardioSessionForm`
  - Modelo: `CardioSession`
  - Requiere autenticación: ✅

### Formularios de Gym

- **`/gym/musculation-record/`** - Registrar sesión de musculación
  - Vista: `musculation_record_form_view`
  - Formulario: `MusculationRecordPublicForm`
  - Modelo: `MusculationRecord`
  - Requiere autenticación: ✅

- **`/gym/training-session/`** - Registrar sesión de entrenamiento
  - Vista: `training_session_form_view`
  - Formulario: `TrainingSessionModelForm`
  - Modelo: `TrainingSession`
  - Requiere autenticación: ✅

### Formularios de Nutrition

- **`/nutrition/product/`** - Registrar producto alimentario
  - Vista: `product_form_view`
  - Formulario: `ProductForm`
  - Modelo: `Product`
  - Requiere autenticación: ✅

- **`/nutrition/daily-diet/`** - Registrar dieta del día
  - Vista: `daily_diet_form_view`
  - Formulario: `DailyDietForm` + `ProductQuantityFormSet`
  - Modelo: `DailyDiet` + `ProductQuantity`
  - Requiere autenticación: ✅

### URLs del Admin

- **`/admin/`** - Panel de administración de Django
- **`/admin/gym/musculationrecord/add-formset/`** - Formset de registros de musculación (admin)
- **`/admin/gym/routine/generate-from-json/`** - Generar rutina desde JSON (admin)
- **`/admin/nutrition/dailydiet/add-formset/`** - Formset de dieta diaria (admin)
- **`/admin/nutrition/dailydiet/generate-from-json/`** - Generar dieta semanal desde JSON (admin)

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

El proyecto utiliza **Jazzmin** como tema del panel de administración de Django. La configuración se encuentra en `project/settings.py` en el diccionario `JAZZMIN_SETTINGS`.

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

El proyecto utiliza Django Formsets con Crispy Forms y Bootstrap 5:

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

### Tema del Admin (Jazzmin)

El tema del panel de administración se configura en `project/settings.py` mediante `JAZZMIN_SETTINGS` (título, cabecera, sidebar, etc.). Consulta la documentación de [django-jazzmin](https://django-jazzmin.readthedocs.io/) para personalizar.

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
## Funciones

### Panel principal

Panel de Administración y Registro con tarjetas de acceso a todos los formularios y al admin.

![Panel principal con tarjetas de acceso](pictures/actions.png)

### Dashboard del administrador

Vista del dashboard de Django con Jazzmin: módulos por aplicación y enlaces a los formularios públicos desde el menú lateral.

![Dashboard del admin](pictures/admin-dashboard.png)

### Formularios de registro

#### Registrar sesión de entrenamiento

Formulario para registrar una sesión completa de entrenamiento (usuario, rutina, fecha, ubicación, duración, kcal, FC media).

![Registrar sesión de entrenamiento](pictures/register-train.png)

#### Registrar sesión de musculación

Formulario para registrar ejercicios de musculación (usuario, ejercicio, series, repeticiones, peso, TBI, observación).

![Registrar sesión de musculación](pictures/register-muscle.png)

#### Registrar sesión de cardio

Formulario para registrar una sesión de cardio (usuario, ejercicio, fechas, ubicación, duración, distancia, velocidad, calorías, elevación, FC).

![Registrar sesión de cardio](pictures/register-cardio-session.png)

#### Registrar medidas corporales

Formulario para registrar medidas corporales (usuario, fecha, peso, brazo, pecho, cintura, pierna, etc.).

![Registrar medidas corporales](pictures/register-measures.png)

#### Registrar producto

Formulario para registrar un producto alimentario con valores nutricionales (nombre, descripción, código de barras, mercado, calorías, proteínas, carbohidratos, grasas por 100 g).

![Registrar producto](pictures/register-product.png)

#### Registrar dieta del día

Formulario para registrar la dieta del día: información de la dieta (usuario, fecha) y productos consumidos (producto, cantidad, unidad).

![Registrar dieta del día](pictures/register-nutrition.png)







---

## 📄 Licencia

Este proyecto es de uso privado.

---

## 👥 Contribuidores

- David Sánchez

---

## 📞 Soporte

Para más información sobre el tema del admin, consultar la documentación de Django Jazzmin: https://django-jazzmin.readthedocs.io/

### Django-sanbox

![Django](https://img.shields.io/badge/Django-5.1.5-green.svg?style=plastic)
![Python](https://img.shields.io/badge/Python-3.12-blue.svg?style=plastic&logo=python&logoColor=white)
![Docker](https://img.shields.io/badge/Docker-2496ED?style=plastic&logo=docker&logoColor=white)
![Code Style - Ruff](https://img.shields.io/badge/code%20style-ruff-30173D.svg?style=plastic)

## Estructura del Proyecto

### APPs Instaladas

- **evolveme**: App principal con perfiles de usuario y medidas corporales
- **cardio**: Gestión de ejercicios y sesiones de cardio
- **gym**: Gestión de ejercicios de musculación, rutinas y sesiones de entrenamiento
- **nutrition**: Gestión de alimentos, suplementos y dietas

---

## APPs y Modelos

### Common
- [x] Login with username and password
- [x] Add [Unfold theme](https://github.com/unfoldadmin/django-unfold)
  - [x] [Installation process](https://dev.to/eshat002/simplify-your-django-admin-with-django-unfold-5g16)
  - [ ] *Corregir fallo en los detalles del modelo Authentication and Authorization*
- [ ] REDIS
- [ ] Celery
- [ ] Swagger
- [ ] Django Rest Framework

---

### Evolveme App

**Modelos:**
- **GymUserProfile**: Perfil del usuario del gimnasio
  - Información personal (fecha de nacimiento, género, altura)
  - Objetivos del usuario (perder peso, ganar músculo, etc.)
- **Measure**: Seguimiento de medidas corporales
  - Peso, brazos, pecho, cintura, piernas
  - Porcentaje de grasa y masa muscular

**Enums:**
- `GenderChoices`: Género (Masculino, Femenino, Otro)
- `ObjectiveChoices`: Objetivos (Perder peso, Ganar músculo, Ganar peso, Mejorar salud, Mejorar rendimiento)

**Estado:**
- [x] Perfil del gimnasio (GymUserProfile)
- [x] Seguimiento de medidas corporales (Measure)
- [x] Añadir admin de los modelos
- [x] Añadir los grupos de usuarios
- [x] Añadir los permisos de los grupos de usuarios
- [x] Añadir variables de entorno

---

### Cardio App

**Modelos:**
- **CardioSession**: Sesiones de ejercicio cardiovascular
  - Tipo de ejercicio (caminar, ciclismo, elíptica)
  - Tiempo, distancia, calorías
  - Frecuencia cardíaca promedio, velocidad promedio
  - Elevación ganada

**Enums:**
- `CardioExerciseChoices`: Tipos de ejercicios de cardio
  - Caminar exterior/cinta
  - Bicicleta exterior/cinta
  - Elíptica cinta

**Estado:**
- [x] Modelo de sesiones de cardio
- [ ] Admin configurado
- [ ] Formularios de registro

---

### Gym App

**Modelos:**
- **MusculationExercise**: Ejercicios de musculación
  - Nombre, descripción, parte del cuerpo
  - Imagen en base64
- **ExerciseSet**: Sets de ejercicios
  - Peso, repeticiones, series
  - Flag "To be improved"
- **TrainingSession**: Sesiones de entrenamiento
  - Combinación de ejercicios de musculación y cardio
  - Fecha y observaciones
- **Routine**: Rutinas de entrenamiento
  - Nombre, fechas de inicio y fin
  - Ejercicios incluidos

**Enums:**
- `BodyPartChoices`: Partes del cuerpo
  - Pecho, Espalda, Piernas, Brazos, Hombros, Abdomen, Antebrazos

**Estado:**
- [x] Ejercicios de musculación (MusculationExercise)
- [x] Sesiones de entrenamiento (TrainingSession)
- [x] Rutina
- [ ] Formulario para rutina
- [ ] Formulario para sesión de musculación
- [ ] Formulario para sesión de entrenamiento

---

### Food App

**Modelos:**
- **Food**: Alimentos
  - Información nutricional por 100g (calorías, proteínas, carbohidratos, grasas)
- **Supplement**: Suplementos
  - Nombre, descripción, unidad de medida
- **Diet**: Dieta completa (2 semanas)
  - Nombre, tipo, fechas de inicio y fin
  - Asociación con usuario
- **DietDay**: Día específico de la dieta (1-14)
  - Número de día y fecha
- **Meal**: Comida del día
  - Tipo de comida (desayuno, almuerzo, cena, etc.)
  - Orden y notas
- **MealFood**: Alimentos en una comida
  - Cantidad en gramos, calorías calculadas automáticamente
- **MealSupplement**: Suplementos en una comida
  - Cantidad y notas
- **EatenFood**: Registro de alimentos consumidos
  - Alimentos realmente consumidos por el usuario
  - Relación opcional con comida planificada
  - Cálculo automático de calorías
- **EatenSupplement**: Registro de suplementos consumidos
  - Suplementos realmente consumidos
  - Fecha y tipo de comida

**Enums:**
- `MealTypeChoices`: Tipos de comida
  - Desayuno, Almuerzo, Snack, Cena, Picoteo

**Estado:**
- [x] Modelo completo de dieta (2 semanas con múltiples comidas y alimentos)
- [x] Registro de consumo real (EatenFood, EatenSupplement)
- [x] Cálculo automático de calorías
- [ ] Admin configurado
- [ ] Generador de dieta (MercaGPT)
- [ ] Formularios de registro

---

## Tareas Pendientes

### Evolveme
- [ ] Volcar datos de prueba
- [ ] Formulario para rutina
- [ ] Formulario para sesión de musculación
- [ ] Formulario para sesión de entrenamiento
- [ ] Generador de dieta (MercaGPT)
- [ ] Permisos para los usuarios

### Cardio
- [ ] Configurar admin
- [ ] Formularios de registro

### Food
- [ ] Configurar admin
- [ ] Generador de dieta (MercaGPT)
- [ ] Formularios de registro

### Finme
- [ ] Movimientos
- [ ] Balances
- [ ] Notificación correo

### Carme
- [ ] Evento
- [ ] Recordatorio
- [ ] Notificación correo
- [ ] Notificación SMS

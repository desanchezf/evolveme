"""
Django settings for project project.

For more information on this file, see
https://docs.djangoproject.com/en/5.2/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/5.2/ref/settings/
"""

import os
from pathlib import Path

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/5.2/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = "django-insecure-vz+du974h9+nba#ix&ggwst-sqs8cgsd%@1txg^sht#d_^fmlt"

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = ["localhost", "127.0.0.1", "0.0.0.0", "backend"]


# Application definition

INSTALLED_APPS = [
    "jazzmin",
    "crispy_forms",
    "crispy_bootstrap5",
    "import_export",
    "django_prometheus",
    # Django apps
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    # Project apps
    "evolveme",
    "cardio",
    "nutrition",
    "gym",
    "ia.apps.IaConfig",
    # Project commands
    "project_commands",
]

MIDDLEWARE = [
    "django_prometheus.middleware.PrometheusBeforeMiddleware",
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "django_prometheus.middleware.PrometheusAfterMiddleware",
]

ROOT_URLCONF = "project.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "project" / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "project.wsgi.application"


# Database (PostgreSQL 16 compatible with Django 5.2)
# https://docs.djangoproject.com/en/5.2/ref/settings/#databases

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": os.getenv("POSTGRES_DB", "django_db"),
        "USER": os.getenv("POSTGRES_USER", "postgres"),
        "PASSWORD": os.getenv("POSTGRES_PASSWORD", "postgres"),
        "HOST": os.getenv("POSTGRES_HOST", "postgres"),
        "PORT": os.getenv("POSTGRES_PORT", "5432"),
        "CONN_MAX_AGE": 60,
        "OPTIONS": {"connect_timeout": 10},
    }
}


# Password validation
# https://docs.djangoproject.com/en/5.2/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]


# Internationalization
# https://docs.djangoproject.com/en/5.2/topics/i18n/

LANGUAGE_CODE = "en-us"
TIME_ZONE = "UTC"
USE_I18N = True
USE_TZ = True

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/5.2/howto/static-files/

STATIC_URL = "static/"

# Auth
LOGIN_URL = "/accounts/login/"
LOGIN_REDIRECT_URL = "/"
LOGOUT_REDIRECT_URL = "/accounts/login/"
STATICFILES_DIRS = [
    BASE_DIR / "static",
]
STATIC_ROOT = BASE_DIR / "staticfiles"

# Media files (uploads)
MEDIA_URL = "media/"
MEDIA_ROOT = BASE_DIR / "media"

# Default primary key field type
# https://docs.djangoproject.com/en/5.2/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# Celery (broker desde REDIS_URL; tarea diaria en project/celery.py)
CELERY_BROKER_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")
CELERY_RESULT_BACKEND = CELERY_BROKER_URL

# Evolveme
ADMIN_USERNAME = os.getenv("ADMIN_USERNAME", "")
ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD", "")
ADMIN_EMAIL = os.getenv("ADMIN_EMAIL", "")

ADMIN_GROUPS = os.getenv("ADMIN_GROUPS", "").split(",")
ROLE_PERMISSIONS = {
    "owner": [
        # Evolveme
        {
            "app_label": "evolveme",
            "model": "gymuserprofile",
            "permissions": ["add", "view", "change", "delete"],
        },
        {
            "app_label": "evolveme",
            "model": "cardio",
            "permissions": ["add", "view", "change", "delete"],
        },
        {
            "app_label": "evolveme",
            "model": "musculationexercise",
            "permissions": ["add", "view", "change", "delete"],
        },
        {
            "app_label": "evolveme",
            "model": "trainingsession",
            "permissions": ["add", "view", "change", "delete"],
        },
        {
            "app_label": "evolveme",
            "model": "diet",
            "permissions": ["add", "view", "change", "delete"],
        },
        {
            "app_label": "evolveme",
            "model": "measure",
            "permissions": ["add", "view", "change", "delete"],
        },
        {
            "app_label": "evolveme",
            "model": "routine",
            "permissions": ["add", "view", "change", "delete"],
        },
        {
            "app_label": "evolveme",
            "model": "dietgenerator",
            "permissions": ["add", "view", "change", "delete"],
        },
        # Finme
        {
            "app_label": "finme",
            "model": "movement",
            "permissions": ["add", "view", "change", "delete"],
        },
        {
            "app_label": "finme",
            "model": "balance",
            "permissions": ["add", "view", "change", "delete"],
        },
    ],
    # Client groups
    "client": [
        {
            "app_label": "evolveme",
            "model": "gymuserprofile",
            "permissions": ["view"],
        },
        {
            "app_label": "evolveme",
            "model": "cardio",
            "permissions": ["add", "view", "change", "delete"],
        },
        {
            "app_label": "evolveme",
            "model": "musculationexercise",
            "permissions": ["view"],
        },
        {
            "app_label": "evolveme",
            "model": "trainingsession",
            "permissions": ["add", "view", "change", "delete"],
        },
        {
            "app_label": "evolveme",
            "model": "diet",
            "permissions": ["view"],
        },
        {
            "app_label": "evolveme",
            "model": "measure",
            "permissions": ["add", "view", "change", "delete"],
        },
        {
            "app_label": "evolveme",
            "model": "routine",
            "permissions": ["view"],
        },
        {
            "app_label": "evolveme",
            "model": "dietgenerator",
            "permissions": ["view"],
        },
    ],
}

CRISPY_ALLOWED_TEMPLATE_PACKS = ["bootstrap5"]
CRISPY_TEMPLATE_PACK = "bootstrap5"

# Jazzmin (admin theme)
JAZZMIN_SETTINGS = {
    "site_title": "EvolveMe",
    "site_header": "EvolveMe",
    "site_brand": "EvolveMe",
    "site_logo": "ico_dark.png",
    "site_icon": "ico_dark.png",
    "login_logo": "ico_dark.png",
    "welcome_sign": "Panel de Administración",
    "show_sidebar": True,
    "navigation_expanded": True,
    # Clase CSS en el <img> del logo para limitar tamaño
    "site_logo_classes": "admin-logo-constrained",
    # Apartados en el menú superior (como Portal EvolveMe)
    "topmenu_links": [
        {"name": "Home", "url": "/admin/", "icon": "fas fa-home"},
        {"name": "Dieta", "url": "/nutrition/daily-diet/", "icon": "fas fa-utensils"},
        {
            "name": "Entrenamiento",
            "url": "/gym/training-session/",
            "icon": "fas fa-calendar-check",
        },
        {"name": "Cardio", "url": "/cardio/cardio-session/", "icon": "fas fa-running"},
        {
            "name": "Musculación",
            "url": "/gym/musculation-record/",
            "icon": "fas fa-dumbbell",
        },
        {
            "name": "Producto",
            "url": "/nutrition/product/",
            "icon": "fas fa-shopping-basket",
        },
        {"name": "IA", "url": "/ia/chat/", "icon": "fas fa-robot"},
    ],
    # Enlaces en el menú lateral a los formularios públicos
    "custom_links": {
        "evolveme": [
            {
                "name": "Registrar medidas",
                "url": "/measure/",
                "icon": "fas fa-ruler-combined",
            },
        ],
        "gym": [
            {
                "name": "Registro de musculación",
                "url": "/gym/musculation-record/",
                "icon": "fas fa-dumbbell",
            },
            {
                "name": "Sesión de entrenamiento",
                "url": "/gym/training-session/",
                "icon": "fas fa-calendar-check",
            },
        ],
        "cardio": [
            {
                "name": "Sesión de cardio",
                "url": "/cardio/cardio-session/",
                "icon": "fas fa-running",
            },
        ],
        "nutrition": [
            {
                "name": "Nuevo producto",
                "url": "/nutrition/product/",
                "icon": "fas fa-shopping-basket",
            },
            {
                "name": "Dieta diaria",
                "url": "/nutrition/daily-diet/",
                "icon": "fas fa-utensils",
            },
        ],
    },
    # Iconos por app y modelo (Font Awesome)
    "icons": {
        # Auth
        "auth.user": "fas fa-user",
        "auth.group": "fas fa-users",
        # Cardio
        "cardio.cardioexercise": "fas fa-heartbeat",
        "cardio.cardiosession": "fas fa-running",
        # Evolveme
        "evolveme.gymuserprofile": "fas fa-id-card",
        "evolveme.measure": "fas fa-ruler-combined",
        # Gym
        "gym.musculationexercise": "fas fa-dumbbell",
        "gym.musculationrecord": "fas fa-clipboard-list",
        "gym.routine": "fas fa-list-ol",
        "gym.trainingsession": "fas fa-calendar-check",
        # IA
        "ia.chatmessage": "fas fa-comment-dots",
        "ia.chatsession": "fas fa-comments",
        "ia.ollamamodelconfig": "fas fa-cube",
        "ia.ollamaserver": "fas fa-server",
        "ia.promtps": "fas fa-robot",
        # Nutrition
        "nutrition.product": "fas fa-shopping-basket",
        "nutrition.productquantity": "fas fa-weight-hanging",
        "nutrition.dailydiet": "fas fa-utensils",
        "nutrition.mealmetrics": "fas fa-chart-pie",
    },
    # CSS personalizado: paleta M3 compartida + estilos propios de EvolveMe
    "custom_css": "admin/css/jazzmin_custom.css",
}

JAZZMIN_UI_TWEAKS = {
    # Sidebar oscura con acento primario (color sobreescrito via CSS)
    "sidebar": "sidebar-dark-primary",
    # Barra de navegación superior clara
    "navbar": "navbar-white navbar-light",
    # Sin borde inferior en la navbar
    "no_navbar_border": True,
    # Botones: mapeo de acciones → clases Bootstrap
    "button_classes": {
        "primary": "btn-primary",
        "secondary": "btn-outline-secondary",
        "info": "btn-info",
        "warning": "btn-warning",
        "danger": "btn-danger",
        "success": "btn-success",
    },
    "actions_sticky_top": False,
}

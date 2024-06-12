import os
from pathlib import Path
from decouple import config

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/5.0/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = config("SECRET_KEY")

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = ["*"]  # Permitir todos os hosts (não recomendado para produção)

APPEND_SLASH = True


# Application definition
INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "app_profile",
    "app_dashboard",
    "app_integracao",
    "app_pedido",
    "app_webhook",
    "app_mensagem",
    "django_celery_results",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "Notiflix.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [os.path.join(BASE_DIR, "templates")],
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

WSGI_APPLICATION = "Notiflix.wsgi.application"

# Database
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",
    }
}

# Password validation
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
LANGUAGE_CODE = "pt-BR"

TIME_ZONE = "America/Sao_Paulo"

USE_I18N = True

USE_TZ = True

# Static files (CSS, JavaScript, Images)
STATIC_URL = "/static/"
STATICFILES_DIRS = (os.path.join(BASE_DIR, "templates/static"),)
STATIC_ROOT = os.path.join(BASE_DIR, "static")

MEDIA_ROOT = os.path.join(BASE_DIR, "templates/media")
MEDIA_URL = "/media/"

# Default primary key field type
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# Logging configuration
"""LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "standard": {"format": "%(asctime)s [%(levelname)s] %(name)s: %(message)s"},
    },
    "handlers": {
        "console": {
            "level": "DEBUG",
            "class": "logging.StreamHandler",
            "formatter": "standard",
        },
        "file": {
            "level": "DEBUG",
            "class": "logging.FileHandler",
            "filename": os.path.join(BASE_DIR, "logs", "app.log"),
            "formatter": "standard",
        },
    },
    "loggers": {
        "django": {
            "handlers": ["console", "file"],
            "level": "DEBUG",
            "propagate": True,
        },
        "app_integracao.middleware": {
            "handlers": ["console", "file"],
            "level": "DEBUG",
            "propagate": True,
        },
        "app_webhook": {
            "handlers": ["console", "file"],
            "level": "DEBUG",
            "propagate": True,
        },
    },
}
"""
import os

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "standard": {"format": "%(asctime)s [%(levelname)s] %(name)s: %(message)s"},
    },
    "handlers": {
        "console": {
            "level": "INFO",
            "class": "logging.StreamHandler",
            "formatter": "standard",
        },
        "file": {
            "level": "INFO",
            "class": "logging.FileHandler",
            "formatter": "standard",
            "filename": os.path.join(os.path.dirname(__file__), "django.log"),
        },
    },
    "loggers": {
        "": {
            "handlers": ["console", "file"],
            "level": "INFO",
            "propagate": False,
        },
        "django": {
            "handlers": ["console", "file"],
            "level": "INFO",
            "propagate": False,
        },
        "app_webhook": {  # Substitua pelo nome do seu aplicativo
            "handlers": ["console", "file"],
            "level": "DEBUG",
            "propagate": False,
        },
        "app_integracao": {  # Substitua pelo nome do seu aplicativo
            "handlers": ["console", "file"],
            "level": "DEBUG",
            "propagate": False,
        },
    },
}


# Celery


# URL do broker do Celery


# Configurações depreciadas (remover ou comentar)
# CELERY_ACCEPT_CONTENT = ["json"]  # Depreciado, use accept_content
# CELERY_TASK_CONTENT = "json"  # Depreciado, ajuste conforme necessário
# CELERY_RESULT_BACKEND = "django-db"  # Depreciado, use result_backend

# settings.py

#CELERY_BROKER_URL = "amqp://admin:Mfcd62!!Mfcd62!!@rabbitmq.lojabibelo.com.br:5672/cloudstore"
CELERY_BROKER_URL = "redis://159.54.139.153:6379/0"
CELERY_RESULT_BACKEND = "redis://159.54.139.153:6379/0"

# Configurações atualizadas para Celery 6.0.0
accept_content = ["json"]
result_backend = "django-db"
broker_connection_retry_on_startup = True  # Novo parâmetro para substituir o deprecated

# Celery
"""CELERY_BROKER_URL = "amqp://admin:Mfcd62!!Mfcd62!!@rabbitmq.lojabibelo.com.br:5672/cloudstore"
CELERY_RESULT_BACKEND = "rpc://"
CELERY_ACCEPT_CONTENT = ["json"]
CELERY_TASK_SERIALIZER = "json"
CELERY_RESULT_SERIALIZER = "json"
CELERY_TIMEZONE = "America/Sao_Paulo"
CELERY_BROKER_CONNECTION_RETRY_ON_STARTUP = True"""

"""

# Celery

# Substitua as configurações do RabbitMQ pelas configurações do Redis
CELERY_BROKER_URL = 'redis://:password@hostname:port/db'
CELERY_RESULT_BACKEND = 'redis://:password@hostname:port/db'

# Exemplo de configuração local sem senha
CELERY_BROKER_URL = 'redis://localhost:6379/0'
CELERY_RESULT_BACKEND = 'redis://localhost:6379/0'

# Exemplo de configuração com senha e servidor remoto
# CELERY_BROKER_URL = 'redis://:sua_senha@redis.exemplo.com:6379/0'
# CELERY_RESULT_BACKEND = 'redis://:sua_senha@redis.exemplo.com:6379/0'

# Configurações adicionais do Celery (opcionais)
CELERY_ACCEPT_CONTENT = ['json']
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'
CELERY_TIMEZONE = 'America/Sao_Paulo'
CELERY_BROKER_CONNECTION_RETRY_ON_STARTUP = True  # Parâmetro atualizado
"""
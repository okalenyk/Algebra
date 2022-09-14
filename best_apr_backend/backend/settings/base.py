"""
Django settings for best_apr_backend project.

Generated by 'django-admin startproject' using Django 3.2.9.

For more information on this file, see
https://docs.djangoproject.com/en/3.2/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/3.2/ref/settings/
"""
import os
from datetime import timedelta
from os import environ
from pathlib import Path

from django.utils import timezone
from kombu import Queue, Exchange

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

DATA_UPLOAD_MAX_MEMORY_SIZE = 52428800
# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/3.2/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = environ.get('BACKEND_SECRET_KEY')
#SECRET_KEY_ID = environ.get('BACKEND_SECRET_KEY_ID')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = int(environ.get('BACKEND_DEBUG_MODE'))

BACKEND_SETTINGS_MODE = str(environ.get('BACKEND_SETTINGS_MODE'))
BACKEND_SETTINGS_TYPE = str(environ.get('BACKEND_SETTINGS_TYPE'))

# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    # 3RD-PARTY EXTENTIONS
    'corsheaders',
    'django_celery_beat',
    'django_extensions',
    'django_filters',
    'drf_spectacular',
    'rest_framework',
    'rangefilter',
    ###

    # APPS
    'best_apr',
    'content',
    'networks',
    'users',
    ###
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'backend.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'backend.wsgi.application'


# Database
# https://docs.djangoproject.com/en/3.2/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': environ.get('DATABASE_NAME'),
        'USER': environ.get('DATABASE_ORIGIN_USER'),
        'PASSWORD': environ.get('DATABASE_ORIGIN_PASS'),
        'HOST': environ.get('DATABASE_HOST'),
        'PORT': environ.get('DATABASE_PORT'),
    }
}


# Password validation
# https://docs.djangoproject.com/en/3.2/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    # {
    #     'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    # },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]


# Internationalization
# https://docs.djangoproject.com/en/3.2/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/3.2/howto/static-files/

STATIC_URL = '/static/'

STATIC_ROOT = '/code/static/'

MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

MEDIA_URL = '/media/'

# Default primary key field type
# https://docs.djangoproject.com/en/3.2/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

AUTH_USER_MODEL = 'users.User'

# CACHING
# CACHE = {
#     'default': {
#         'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
#         'TIMEOUT': int(environ.get('DEFAULT_CACHE_TIMEOUT')),
#         'OPTIONS': {
#             # Максимальное количество элементов в кеше.
#             'MAX_ENTRIES': int(environ.get('MAX_ENTRIES')),
#             # Часть элементов, которые нужно удалить.
#             # Вычисляется по формуле: MAX_ENTRIES / CULL_FREQUENCY.
#             'CULL_FREQUENCY': int(environ.get('CULL_FREQUENCY')),
#         }
#     }
# }

# DEFAULT_VIEW_CACHE_TIMEOUT = int(environ.get('DEFAULT_VIEW_CACHE_TIMEOUT'))

# LOGGING
LOGGING_CURRENT_DATE = timezone.now()

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'console': {
            'format': '%(name)-12s %(levelname)-8s %(message)s'
        },
        'file': {
            'format': '%(asctime)s %(name)-12s %(levelname)-8s %(message)s'
        }
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'console'
        },
        'file': {
            'level': 'DEBUG',
            'class': 'logging.FileHandler',
            'formatter': 'file',
            'filename': '{mode}_{year}_{month}.log'.format(
                mode=environ.get('BACKEND_SETTINGS_MODE'),
                year=LOGGING_CURRENT_DATE.year,
                month=LOGGING_CURRENT_DATE.month
            )
        }
    },
    'loggers': {
        '': {
            'level': 'DEBUG',
            'handlers': ('console', 'file')
        },
        'django.request': {
            'level': 'DEBUG',
            'handlers': ('console', 'file'),
            'propagate': False
        },
        'django.server': {
            'level': 'DEBUG',
            'handlers': ('console', 'file'),
            'propagate': False
        },
    }
}

# BROKER
BROKER_SERVICE_NAME = environ.get('BROKER_SERVICE_NAME')
BROKER_HOST = environ.get('BROKER_HOST')
BROKER_PORT = environ.get('BROKER_PORT')
BROKER_URL = f'redis://{BROKER_HOST}:{BROKER_PORT}/0'
BROKER_TRANSPORT_OPTIONS = {'visibility_timeout': 3600, }

# CELERY
CELERY_DATA_FORMAT = 'json'
CELERY_BROKER_URL = f'redis://{BROKER_SERVICE_NAME}:{BROKER_PORT}/0'
# CELERY_RESULT_BACKEND = f'redis://{BROKER_SERVICE_NAME}:{BROKER_PORT}/0'
CELERY_ACCEPT_CONTENT = [f'application/{CELERY_DATA_FORMAT}', ]
CELERY_TIMEZONE = TIME_ZONE
CELERY_TASK_SERIALIZER = CELERY_DATA_FORMAT
CELERY_RESULT_SERIALIZER = CELERY_DATA_FORMAT

CELERY_BEAT_SCHEDULE = {
    'update_pools_apr_task': {
        'task': 'best_apr.tasks.update_pools_apr_task',
        'schedule': timedelta(minutes=1),
    },
    'update_eternal_farmings_apr_task': {
        'task': 'best_apr.tasks.update_eternal_farmings_apr_task',
        'schedule': timedelta(minutes=1),
    },
    'update_limit_farmings_apr_task': {
        'task': 'best_apr.tasks.update_limit_farmings_apr_task',
        'schedule': timedelta(minutes=1),
    },
}

CELERYD_HIJACK_ROOT_LOGGER = False
CELERYD_LOG_COLOR = True

CELERYD_PREFETCH_MULTIPLIER = 1
CELERYD_CONCURRENCY = int(environ.get('CELERY_CONCURRENCY', 1))

# DRF_SPECTACULAR
# SPECTACULAR_SETTINGS = {
#     'TITLE': 'RUBIC CROSSCHAIN API',
#     'DESCRIPTION': '',
#     'VERSION': '1.0.0',
#     # OTHER SETTINGS
#     'AUTHENTICATION_WHITELIST': [
#         'rest_framework.authentication.BaseAuthentication',
#     ],
# }

# REST_FRAMEWORK
REST_FRAMEWORK = {
    'DEFAULT_SCHEMA_CLASS': 'drf_spectacular.openapi.AutoSchema',
}

#EMAIL
EMAIL_HOST = str(environ.get('EMAIL_HOST'))
EMAIL_PORT = str(environ.get('EMAIL_PORT'))
EMAIL_USE_TLS = False
EMAIL_USE_SSL = True
EMAIL_HOST_USER = str(environ.get('EMAIL_HOST_USER'))
EMAIL_HOST_PASSWORD = str(environ.get('EMAIL_HOST_PASSWORD'))
EMAIL_TO = str(environ.get('EMAIL_TO'))

# # OTHER
BLOCK_DELTA = int(environ.get('BLOCK_DELTA'))
APR_DELTA = int(environ.get('APR_DELTA'))
DEFAULT_TXN_TIMEOUT = int(environ.get('DEFAULT_TXN_TIMEOUT'))
DEFAULT_POLL_LATENCY = int(environ.get('DEFAULT_POLL_LATENCY'))

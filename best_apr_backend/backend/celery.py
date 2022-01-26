from os import environ

from celery import Celery
from django.conf import settings

# Set the default Django settings module for the 'celery' program.
environ.setdefault(
    'DJANGO_SETTINGS_MODULE',
    'backend.settings.{}'.format(
        environ.get('BACKEND_SETTINGS_MODE')
    )
)

app = Celery(
    main='best_apr_backend',
    broker=settings.CELERY_BROKER_URL,
)

# Using a string here means the worker doesn't have to serialize
# the configuration object to child processes.
# - namespace='CELERY' means all celery-related configuration keys
#   should have a `CELERY_` prefix.
app.config_from_object(
    'django.conf:settings',
    namespace='CELERY',
)

# Load task modules from all registered Django app configs.
app.autodiscover_tasks()

from .base import *

ALLOWED_HOSTS = (
    '*',
)

INSTALLED_APPS.append('debug_toolbar')

INTERNAL_IPS = (
    '127.0.0.1',
    '0.0.0.0',
)

MIDDLEWARE.append('debug_toolbar.middleware.DebugToolbarMiddleware')

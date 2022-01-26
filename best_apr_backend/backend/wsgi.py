"""
WSGI config for best_apr_backend project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/3.2/howto/deployment/wsgi/
"""

from os import environ

from django.core.wsgi import get_wsgi_application

environ.setdefault(
    'DJANGO_SETTINGS_MODULE',
    'backend.settings.{}'.format(
        environ.get('BACKEND_SETTINGS_MODE')
    )
)

application = get_wsgi_application()

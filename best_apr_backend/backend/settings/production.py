from corsheaders.defaults import default_headers

from .base import *

ALLOWED_HOSTS = environ.get('BACKEND_ALLOWED_HOSTS').split()

SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')

SECURE_SSL_REDIRECT = True

SESSION_COOKIE_SAMESITE = 'None'

SESSION_COOKIE_SECURE = True

CSRF_COOKIE_SAMESITE = 'None'

CSRF_COOKIE_SECURE = True

CSRF_TRUSTED_ORIGINS = environ.get('BACKEND_CSRF_TRUSTED_ORIGINS').split()

CORS_ALLOWED_ORIGINS = environ.get('CORS_ALLOWED_ORIGINS').split()

CORS_ORIGIN_WHITELIST = environ.get('CORS_ALLOWED_ORIGINS').split()

CORS_ALLOW_CREDENTIALS = bool(int(environ.get('CORS_ALLOW_CREDENTIALS')))

CORS_ALLOW_HEADERS = list(default_headers) + [
    'access-control-allow-headers',
    # 'access-control-allow-credentials',
    'access-control-allow-origin',
    'cache-control',
    'cookie',
    'expires',
    'pragma',
]

CORS_ORIGIN_ALLOW_ALL = bool(int(environ.get('CORS_ORIGIN_ALLOW_ALL')))

CORS_ALLOW_METHODS = environ.get('CORS_ALLOW_METHODS').split()

REST_FRAMEWORK.update(
    {
        'DEFAULT_RENDERER_CLASSES': [
            'rest_framework.renderers.JSONRenderer',
        ],
    }
)
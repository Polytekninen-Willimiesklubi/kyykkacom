# Generate a new SECRET_KEY for production.
# SECRET_KEY = '&clagu7m@fo_*sfr^&i$56r_b-46=$15h83iv68r*^t^5c8r*5'
DEBUG = True
ALLOWED_HOSTS = []
INTERNAL_IPS = ['localhost', '127.0.0.1']
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'nkl',
        'USER': 'root',
        'PASSWORD': 'root',
        'HOST': '127.0.0.1',
        #FOR DOCKER 'HOST': 'DB',
        'PORT': '3306',
        }
}
# If running memcached in Docker
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.memcached.MemcachedCache',
        'LOCATION': 'memcached:11211',
        
    }
}
INSTALLED_APPS = INSTALLED_APPS + ['debug_toolbar']
MIDDLEWARE = ['debug_toolbar.middleware.DebugToolbarMiddleware'] + MIDDLEWARE

CORS_ORIGIN_ALLOW_ALL=True
CORS_ORIGIN_WHITELIST = ["localhost"]

CORS_ALLOW_CREDENTIALS = True

ADMINS = [('Ville', 'ville@rauko.la')]
MAILER_LIST = ['vilde70@gmail.com']
EMAIL_HOST = 'smtp.eu.mailgun.org'
EMAIL_HOST_USER = 'kyykka@mail.rauko.la'
EMAIL_HOST_PASSWORD = ''
EMAIL_PORT = 587
EMAIL_USE_TLS = True
DEFAULT_FROM_EMAIL = 'kyykka@rauko.la'

if DEBUG:
    EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
    CORS_ORIGIN_ALLOW_ALL=True
    CORS_ORIGIN_WHITELIST = ["localhost:8080"]
else:
    EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'

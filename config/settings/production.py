from config.settings.base import *
from datetime import timedelta

# Debug
# https://docs.djangoproject.com/en/dev/ref/settings/#std:setting-DEBUG
DEBUG = get_secret("DEBUG")

# Allowed Hosts
# https://docs.djangoproject.com/en/dev/ref/settings/#allowed-hosts
ALLOWED_HOSTS = get_secret("ALLOWED_HOSTS")

# SECURITY WARNING: keep the secret key used in production secret!
# https://docs.djangoproject.com/en/dev/ref/settings/#std:setting-SECRET_KEY
SECRET_KEY = get_secret("SECRET_KEY")

# Rest Framework
# https://www.django-rest-framework.org/api-guide/settings/
REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": [
        "backend.api.authentication.ExpiringTokenAuthentication"
    ],
    "DEFAULT_PERMISSION_CLASSES": ["rest_framework.permissions.IsAuthenticated"],
}
# This is used by the ExpiringTokenAuthentication which extends from rest's token authentication
TIMEOUT_TIMEDELTA = timedelta(minutes=10)

# Database
# https://docs.djangoproject.com/en/2.1/ref/settings/#databases
DATABASES = {
    "default": {
        "ENGINE": "django_prometheus.db.backends.postgresql",
        "NAME": get_secret("DB_NAME"),
        "USER": get_secret("DB_USER"),
        "PASSWORD": get_secret("DB_PASSWORD"),
        "HOST": get_secret("DB_HOST"),
        "PORT": get_secret("DB_PORT"),
    }
}

# Installed app django-cors-headers
# https://pypi.org/project/django-cors-headers/
CORS_ALLOWED_ORIGINS = [
    # prod
    "https://law-orga.de",
    "http://law-orga.de",
    "http://www.law-orga.de",
    "https://www.law-orga.de",
    "https://d1g37iqegvaqxr.cloudfront.net",
    # dev
    "https://d7pmzq2neb57w.cloudfront.net",
    # test
    "https://d33cushiywgecu.cloudfront.net",
]

# Logging
# https://docs.djangoproject.com/en/dev/topics/logging/
# LOGGING_DIR = os.path.join(BASE_DIR, "tmp/logs")
# LOGGING = {
#     "version": 1,
#     "disable_existing_loggers": False,
#     "handlers": {
#         "file": {
#             "class": "logging.FileHandler",
#             "level": "WARNING",
#             "filename": os.path.join(LOGGING_DIR, "django.log"),
#         },
#     },
#     "loggers": {"": {"handlers": ["file"], "propagate": True, "level": "INFO",},},
# }

# LOGGING = {
#     "version": 1,
#     "disable_existing_loggers": False,
#     "formatters": {"simple": {"format": "%(levelname)s %(message)s"},},
#     "handlers": {
#         "console": {
#             "level": "ERROR",
#             "class": "logging.StreamHandler",
#             "formatter": "simple",
#         },
#         "logstash": {
#             "level": "ERROR",
#             "class": "logstash.TCPLogstashHandler",
#             "host": "logstash",
#             "port": 5959,
#             "version": 1,
#             "message_type": "django",
#             "fqdn": False,
#             "tags": ["django.request", "django", "backend"],
#             "formatter": "simple",
#         },
#     },
#     "loggers": {
#         "django.request": {
#             "handlers": ["logstash"],
#             "level": "ERROR",
#             "propagate": True,
#         },
#         "backend": {
#             "handlers": ["console", "logstash"],
#             "level": "ERROR",
#             "propagate": True,
#         },
#     },
# }

import environs

from .base import *

# Environment
# https://github.com/sloria/environs/blob/master/examples/django_example.py
env = environs.Env()
env.read_env()

# This is used for links in activation emails and so on
MAIN_FRONTEND_URL = "https://www.law-orga.de"
STATISTICS_FRONTEND_URL = "https://statistics.law-orga.de"

# Debug
# https://docs.djangoproject.com/en/dev/ref/settings/#std:setting-DEBUG
DEBUG = False

# Allowed Hosts
# https://docs.djangoproject.com/en/dev/ref/settings/#allowed-hosts
ALLOWED_HOSTS = ["backend.law-orga.de"]

# same site attribute
# https://docs.djangoproject.com/en/4.1/ref/settings/#session-cookie-samesite
SESSION_COOKIE_SAMESITE = "Strict"
CSRF_COOKIE_SAMESITE = "Strict"

# Add the frontend to trusted origins
# https://docs.djangoproject.com/en/4.1/ref/settings/#csrf-trusted-origins
CSRF_TRUSTED_ORIGINS = ["https://*.law-orga.de"]

# session cookie domain
# https://docs.djangoproject.com/en/4.1/ref/settings/#session-cookie-domain
SESSION_COOKIE_DOMAIN = ".law-orga.de"
CSRF_COOKIE_DOMAIN = ".law-orga.de"

# SECURITY WARNING: keep the secret key used in production secret!
# https://docs.djangoproject.com/en/dev/ref/settings/#std:setting-SECRET_KEY
SECRET_KEY = env.str("DJANGO_SECRET_KEY")

# Database
# https://docs.djangoproject.com/en/2.1/ref/settings/#databases
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": env.str("DB_NAME"),
        "USER": env.str("DB_USER"),
        "PASSWORD": env.str("DB_PASSWORD"),
        "HOST": env.str("DB_HOST"),
        "PORT": env.int("DB_PORT"),
        "TEST": {"NAME": "test_{}".format(RUNTIME)},
        "OPTIONS": {
            "sslmode": "verify-full",
            "sslrootcert": os.path.join(
                BASE_DIR, "static/dist/lawandorga-backend-service.cer"
            ),
        },
    }
}

# E-Mail
# https://docs.djangoproject.com/en/dev/topics/email/#smtp-backend
EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"
EMAIL_HOST = env.str("EMAIL_HOST")
DEFAULT_FROM_EMAIL = env.str("EMAIL_ADDRESS")
SERVER_EMAIL = env.str("EMAIL_ADDRESS")
EMAIL_PORT = env.int("EMAIL_PORT")
EMAIL_HOST_USER = env.str("EMAIL_ADDRESS")
EMAIL_HOST_PASSWORD = env.str("EMAIL_PASSWORD")
EMAIL_USE_TLS = True
EMAIL_USE_SSL = False

# Installed app django-cors-headers
# https://pypi.org/project/django-cors-headers/
CORS_ALLOWED_ORIGINS = [MAIN_FRONTEND_URL, STATISTICS_FRONTEND_URL]

# Storage
# https://django-storages.readthedocs.io/en/latest/backends/amazon-S3.html#settings
DEFAULT_FILE_STORAGE = "config.storage.CustomS3Boto3Storage"
AWS_S3_SECRET_ACCESS_KEY = env.str("S3_SECRET_KEY")
AWS_S3_ACCESS_KEY_ID = env.str("S3_ACCESS_KEY")
AWS_STORAGE_BUCKET_NAME = env.str("S3_BUCKET_NAME")
AWS_S3_REGION_NAME = "fr-par"
AWS_S3_ENDPOINT_URL = "https://s3.fr-par.scw.cloud"
AWS_S3_FILE_OVERWRITE = False

# Logging
# https://docs.djangoproject.com/en/dev/topics/logging/
LOGGING_DIR = os.path.join(BASE_DIR, "tmp/logs")
LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "level": "WARNING",
        },
        "mail_admins": {
            "class": "django.utils.log.AdminEmailHandler",
            "level": "ERROR",
        },
        "null": {
            "class": "logging.NullHandler",
        },
    },
    "loggers": {
        "django.security.DisallowedHost": {
            "handlers": ["null"],
            "propagate": False,
        },
        "django": {
            "handlers": ["console", "mail_admins"],
            "propagate": False,
            "level": "INFO",
        },
    },
}

# This is used for ics calendar integration links
CALENDAR_URL = "https://calendar.law-orga.de/api/events/ics/"

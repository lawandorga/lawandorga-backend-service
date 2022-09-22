# type: ignore
from .base import *

# Debug
# https://docs.djangoproject.com/en/dev/ref/settings/#std:setting-DEBUG
DEBUG = False

# Allowed Hosts
# https://docs.djangoproject.com/en/dev/ref/settings/#allowed-hosts
ALLOWED_HOSTS = env.list("ALLOWED_HOSTS")

# SECURITY WARNING: keep the secret key used in production secret!
# https://docs.djangoproject.com/en/dev/ref/settings/#std:setting-SECRET_KEY
SECRET_KEY = env.str("SECRET_KEY")

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
    }
}

# E-Mail
# https://docs.djangoproject.com/en/dev/topics/email/#smtp-backend
EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"
EMAIL_HOST = env.str("EMAIL_HOST")
DEFAULT_FROM_EMAIL = env.str("EMAIL_HOST")
SERVER_EMAIL = env.str("EMAIL_HOST")
EMAIL_PORT = env.int("EMAIL_PORT")
EMAIL_HOST_USER = env.str("EMAIL_HOST")
EMAIL_HOST_PASSWORD = env.str("EMAIL_PASSWORD")
EMAIL_USE_TLS = True
EMAIL_USE_SSL = False

# Installed app django-cors-headers
# https://pypi.org/project/django-cors-headers/
CORS_ALLOWED_ORIGINS = env.list("CORS_ALLOWED_ORIGINS")

# Storage
# https://django-storages.readthedocs.io/en/latest/backends/amazon-S3.html#settings
DEFAULT_FILE_STORAGE = "config.storage.CustomS3Boto3Storage"
AWS_S3_SECRET_ACCESS_KEY = env.str("SCW_SECRET_KEY")
AWS_S3_ACCESS_KEY_ID = env.str("SCW_ACCESS_KEY")
AWS_STORAGE_BUCKET_NAME = env.str("SCW_S3_BUCKET_NAME")
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
        "file": {
            "class": "logging.FileHandler",
            "level": "ERROR",
            "filename": os.path.join(LOGGING_DIR, "django.log"),
        },
        "console": {
            "class": "logging.StreamHandler",
            "level": "ERROR",
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
            "handlers": ["console", "file", "mail_admins"],
            "propagate": False,
            "level": "INFO",
        },
    },
}

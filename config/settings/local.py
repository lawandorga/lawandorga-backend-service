# type: ignore
from .base import *

# Debug
# https://docs.djangoproject.com/en/dev/ref/settings/#std:setting-DEBUG
DEBUG = True

# Allowed Hosts
# https://docs.djangoproject.com/en/dev/ref/settings/#allowed-hosts
ALLOWED_HOSTS = ["*"]

# SECURITY WARNING: keep the secret key used in production secret!
# https://docs.djangoproject.com/en/dev/ref/settings/#std:setting-SECRET_KEY
SECRET_KEY = "srt(vue=+gl&0c_c3pban6a&m2h2iz6mhbx^%^_%9!#-jg0*lz"

# Application definition
# https://docs.djangoproject.com/en/dev/ref/applications/
INSTALLED_APPS += ["debug_toolbar"]

# Middleware
# https://docs.djangoproject.com/en/dev/topics/http/middleware/
MIDDLEWARE += [
    "debug_toolbar.middleware.DebugToolbarMiddleware",
    "config.middleware.custom_debug_toolbar_middleware",
]

# Database
# https://docs.djangoproject.com/en/2.1/ref/settings/#databases
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": os.path.join(BASE_DIR, "tmp/db.sqlite3"),
    }
}

# E-Mail
# https://docs.djangoproject.com/en/dev/topics/email/#smtp-backend
EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"

# Installed app django-cors-headers
# https://pypi.org/project/django-cors-headers/
CORS_ALLOW_ALL_ORIGINS = True

# Django Debug Toolbar
# https://django-debug-toolbar.readthedocs.io/en/latest/installation.html#configuring-internal-ips
INTERNAL_IPS = ["127.0.0.1"]

# Logging
# https://docs.djangoproject.com/en/dev/topics/logging/
LOGGING_DIR = os.path.join(BASE_DIR, "tmp/logs")
LOGGING = {
    "version": 1,
    "disable_existing_loggers": True,
    "formatters": {
        "console": {
            "format": "{levelname:8s}I | {name:14s} | {message}",
            "style": "{",
        }
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "level": "DEBUG",
            "formatter": "console",
        },
    },
    "loggers": {
        "": {"handlers": ["console"], "level": "DEBUG"},
        "uvicorn": {
            "handlers": ["console"],
            "propagate": False,
            "level": "DEBUG",
        },
        "uvicorn.error": {
            "handlers": ["console"],
            "propagate": False,
            "level": "DEBUG",
        },
        "django": {
            "handlers": ["console"],
            "propagate": False,
            "level": "INFO",
        },
        "django.request": {
            "handlers": ["console"],
            "propagate": False,
            "level": "DEBUG",
        },
        "django.server": {
            "handlers": ["console"],
            "propagate": False,
            "level": "DEBUG",
        },
        "django.security": {
            "handlers": ["console"],
            "propagate": False,
            "level": "DEBUG",
        },
    },
}

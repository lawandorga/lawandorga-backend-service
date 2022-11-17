from .base import *

# This is used for links in activation emails and so on
#
MAIN_FRONTEND_URL = "http://127.0.0.1:4200"
STATISTICS_FRONTEND_URL = "http://127.0.0.1:4300"

# This is used for ics calendar integration links
#
CALENDAR_URL = "http://127.0.0.1:8000"

# Debug
# https://docs.djangoproject.com/en/dev/ref/settings/#std:setting-DEBUG
DEBUG = True

# Allowed Hosts
# https://docs.djangoproject.com/en/dev/ref/settings/#allowed-hosts
ALLOWED_HOSTS = ["*"]

# SECURITY WARNING: keep the secret key used in production secret!
# https://docs.djangoproject.com/en/dev/ref/settings/#std:setting-SECRET_KEY
SECRET_KEY = "nosecret"

# Application definition
# https://docs.djangoproject.com/en/dev/ref/applications/
INSTALLED_APPS += ["debug_toolbar"]

# Middleware
# https://docs.djangoproject.com/en/dev/topics/http/middleware/
MIDDLEWARE += [
    "debug_toolbar.middleware.DebugToolbarMiddleware",
    "config.middleware.custom_debug_toolbar_middleware",
]

# same site attribute
# https://docs.djangoproject.com/en/4.1/ref/settings/#session-cookie-samesite
SESSION_COOKIE_SAMESITE = "None"
CSRF_COOKIE_SAMESITE = "None"

# Database
# https://docs.djangoproject.com/en/2.1/ref/settings/#databases
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": os.path.join(BASE_DIR, "tmp/db.sqlite3"),
    },
}

# E-Mail
# https://docs.djangoproject.com/en/dev/topics/email/#smtp-backend
EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"

# Login
# https://docs.djangoproject.com/en/4.1/ref/settings/#login-redirect-url
LOGIN_REDIRECT_URL = MAIN_FRONTEND_URL

# Installed app django-cors-headers
# https://pypi.org/project/django-cors-headers/
CORS_ALLOWED_ORIGINS = [MAIN_FRONTEND_URL, STATISTICS_FRONTEND_URL]

# Add the frontend to trusted origins
# https://docs.djangoproject.com/en/4.1/ref/settings/#csrf-trusted-origins
CSRF_TRUSTED_ORIGINS = [MAIN_FRONTEND_URL, STATISTICS_FRONTEND_URL]

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

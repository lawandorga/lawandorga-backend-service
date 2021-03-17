from config.settings.base import *
from datetime import timedelta

# Debug
# https://docs.djangoproject.com/en/dev/ref/settings/#std:setting-DEBUG
DEBUG = True

# Allowed Hosts
# https://docs.djangoproject.com/en/dev/ref/settings/#allowed-hosts
ALLOWED_HOSTS = ['*']

# SECURITY WARNING: keep the secret key used in production secret!
# https://docs.djangoproject.com/en/dev/ref/settings/#std:setting-SECRET_KEY
SECRET_KEY = "srt(vue=+gl&0c_c3pban6a&m2h2iz6mhbx^%^_%9!#-jg0*lz"

# Authentication Timeout
# TODO: figure out what this is for
TIMEOUT_TIMEDELTA = timedelta(weeks=10)

# Database
# https://docs.djangoproject.com/en/2.1/ref/settings/#databases
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": os.path.join(BASE_DIR, "db.sqlite3"),
    }
}

# E-Mail
# https://docs.djangoproject.com/en/dev/topics/email/#smtp-backend
EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"

# Installed app django-cors-headers
# https://pypi.org/project/django-cors-headers/
CORS_ALLOW_ALL_ORIGINS = True

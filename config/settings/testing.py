from .base import *

# This is used for links in activation emails and so on
#
MAIN_FRONTEND_URL = "http://127.0.0.1:4200"
STATISTICS_FRONTEND_URL = "http://127.0.0.1:4300"

# This is used for ics calendar integration links
#
CALENDAR_URL = "http://127.0.0.1:8000"


# SECURITY WARNING: keep the secret key used in production secret!
# https://docs.djangoproject.com/en/dev/ref/settings/#std:setting-SECRET_KEY
SECRET_KEY = "nosecret"

# Database
# https://docs.djangoproject.com/en/2.1/ref/settings/#databases
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": ":memory:",
    },
}

# E-Mail
# https://docs.djangoproject.com/en/dev/topics/email/#smtp-backend
EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"

# Static Files
# https://docs.djangoproject.com/en/dev/howto/static-files/
MEDIA_ROOT = os.path.join(BASE_DIR, "tmp/media/testing/")

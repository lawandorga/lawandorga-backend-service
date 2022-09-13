import json
import os
from datetime import datetime, timedelta

import pytz
from django.core.exceptions import ImproperlyConfigured

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Secret settings
try:
    with open(os.path.join(BASE_DIR, "tmp/secrets.json")) as f:
        secrets_json = json.loads(f.read())
except FileNotFoundError:
    secrets_json = {}


def get_secret(setting, secrets=secrets_json):
    if setting in secrets:
        var = secrets[setting]
    else:
        var = os.getenv(setting, None)

    if var is not None:
        return var
    else:
        error_msg = "Set the {} environment variable.".format(setting)
        raise ImproperlyConfigured(error_msg)


# Application definition
# https://docs.djangoproject.com/en/dev/ref/applications/
INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "rest_framework",
    "tinymce",
    "apps.core",
    "apps.recordmanagement",
    "storages",
    "corsheaders",
    "solo",
]

# Password validation
# https://docs.djangoproject.com/en/1.11/ref/settings/#auth-password-validators
AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]

# Middleware
# https://docs.djangoproject.com/en/dev/topics/http/middleware/
MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "corsheaders.middleware.CorsMiddleware",
    # "django.middleware.common.CommonMiddleware",
    # "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "config.middleware.TokenAuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    # "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "config.middleware.LoggingMiddleware",
]

# Url conf
# https://docs.djangoproject.com/en/dev/ref/settings/#std:setting-ROOT_URLCONF
ROOT_URLCONF = "config.urls"

# Templates
# https://docs.djangoproject.com/en/dev/topics/templates/#configuration
TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [os.path.join(BASE_DIR, "templates")],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

# WSGI
# https://docs.djangoproject.com/en/dev/ref/settings/#std:setting-WSGI_APPLICATION
WSGI_APPLICATION = "config.wsgi.application"

# Internationalization
# https://docs.djangoproject.com/en/2.1/topics/i18n/
LANGUAGE_CODE = "en-us"
TIME_ZONE = "Europe/Berlin"
USE_I18N = True
USE_L10N = True
USE_TZ = True

# Authentication
# https://docs.djangoproject.com/en/dev/ref/settings/#std:setting-AUTH_USER_MODEL
AUTH_USER_MODEL = "core.UserProfile"

# Static Files Storage
# http://whitenoise.evans.io/en/stable/
STATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage"

# Static Files
# https://docs.djangoproject.com/en/dev/howto/static-files/
STATICFILES_DIRS = [os.path.join(BASE_DIR, "static/dist/")]
STATIC_URL = "static/"
STATIC_ROOT = os.path.join(BASE_DIR, "tmp/static/")
MEDIA_URL = "media/"
MEDIA_ROOT = os.path.join(BASE_DIR, "tmp/media/")

# Installed app django-cors-headers
# https://pypi.org/project/django-cors-headers/
CORS_ALLOW_HEADERS = [
    "accept",
    "accept-encoding",
    "authorization",
    "content-type",
    "dnt",
    "origin",
    "user-agent",
    "x-csrftoken",
    "x-requested-with",
    "private-key",
]

# Rest Framework
# https://www.django-rest-framework.org/api-guide/settings/
REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": [
        "rest_framework_simplejwt.authentication.JWTAuthentication",
        "rest_framework.authentication.SessionAuthentication",
    ],
    "DATE_INPUT_FORMATS": ["%d-%m-%Y", "%Y-%m-%d", "%Y-%m-%dT%H:%M:%S.%fZ"],
    "DATETIME_FORMAT": "%Y-%m-%dT%H:%M",
    "DEFAULT_PERMISSION_CLASSES": [
        "config.authentication.IsAuthenticatedAndEverything"
    ],
}

# JWT Token
# See: https://django-rest-framework-simplejwt.readthedocs.io/en/latest/settings.html
SIMPLE_JWT = {
    "UPDATE_LAST_LOGIN": True,
    "SIGNING_KEY": get_secret("JWT_SIGNING_KEY"),
    "ACCESS_TOKEN_LIFETIME": timedelta(minutes=20),
    "REFRESH_TOKEN_LIFETIME": timedelta(minutes=20),
    "USER_ID_CLAIM": "django_user",
    "ROTATE_REFRESH_TOKENS": True,
}

# Necessary in django 3.2
# https://docs.djangoproject.com/en/3.2/releases/3.2/#customizing-type-of-auto-created-primary-keys
DEFAULT_AUTO_FIELD = "django.db.models.AutoField"

# mail errors to the admins
# See: https://docs.djangoproject.com/en/3.2/ref/settings/#admins
ADMINS = [("Daniel Mössner", "it@law-orga.de")]

# This is used by the ExpiringTokenAuthentication which extends from rest's token authentication
TIMEOUT_TIMEDELTA = timedelta(minutes=30)

# This is used for links in activation emails and so on
FRONTEND_URL = get_secret("FRONTEND_URL")

# Run time is set when django starts
RUNTIME = datetime.now(pytz.timezone("Europe/Berlin")).strftime("%Y-%m-%d--%H:%M:%S")

# The standard password of the dummy user, this is used within get_private_key in UserProfile
# This enables us to do a lot of cool stuff, for example: test the restframework api directly
DUMMY_USER_PASSWORD = "qwe123"

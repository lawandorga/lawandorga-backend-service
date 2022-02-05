from django.core.exceptions import ImproperlyConfigured
from datetime import timedelta, datetime
import pytz
import json
import os

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Secret settings
with open(os.path.join(BASE_DIR, "tmp/secrets.json")) as f:
    secrets_json = json.loads(f.read())


def get_secret(setting, secrets=secrets_json):
    try:
        return secrets[setting]
    except KeyError:
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
    "apps.api",
    "apps.recordmanagement",
    "apps.files",
    "apps.collab",
    "apps.internal",
    "rest_framework.authtoken",
    "storages",
    "corsheaders",
    "solo",
]

# Middleware
# https://docs.djangoproject.com/en/dev/topics/http/middleware/
MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "corsheaders.middleware.CorsMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "apps.static.middleware.LoggingMiddleware",
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
AUTH_USER_MODEL = "api.UserProfile"

# Storage
# https://django-storages.readthedocs.io/en/latest/backends/amazon-S3.html#settings
DEFAULT_FILE_STORAGE = 'config.storage.CustomS3Boto3Storage'
AWS_S3_SECRET_ACCESS_KEY = get_secret("SCW_SECRET_KEY")
AWS_S3_ACCESS_KEY_ID = get_secret("SCW_ACCESS_KEY")
AWS_STORAGE_BUCKET_NAME = get_secret("SCW_S3_BUCKET_NAME")
AWS_S3_REGION_NAME = "fr-par"
AWS_S3_ENDPOINT_URL = "https://s3.fr-par.scw.cloud"
AWS_S3_FILE_OVERWRITE = False

# Static Files
# https://docs.djangoproject.com/en/dev/howto/static-files/
STATICFILES_DIRS = [os.path.join(BASE_DIR, "static/dist/")]
STATIC_URL = "static.py/"
STATIC_ROOT = os.path.join(BASE_DIR, "tmp/static.py/")
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
        "apps.api.authentication.ExpiringTokenAuthentication",
        "rest_framework.authentication.SessionAuthentication",
    ],
    'DATE_INPUT_FORMATS': ["%d-%m-%Y", "%Y-%m-%d", "%Y-%m-%dT%H:%M:%S.%fZ"],
    'DATETIME_FORMAT': "%Y-%m-%dT%H:%M",
    "DEFAULT_PERMISSION_CLASSES": ["rest_framework.permissions.IsAuthenticated"],
}

# Necessary in django 3.2
# https://docs.djangoproject.com/en/3.2/releases/3.2/#customizing-type-of-auto-created-primary-keys
DEFAULT_AUTO_FIELD = 'django.db.models.AutoField'

# mail errors to the admins
# See: https://docs.djangoproject.com/en/3.2/ref/settings/#admins
ADMINS = [('Daniel Mössner', 'it@law-orga.de')]

# This is used by the ExpiringTokenAuthentication which extends from rest's token authentication
TIMEOUT_TIMEDELTA = timedelta(minutes=30)

# Secret keys for s3-storage to save files from 'files' and documents from records
SCW_SECRET_KEY = get_secret("SCW_SECRET_KEY")
SCW_ACCESS_KEY = get_secret("SCW_ACCESS_KEY")
SCW_S3_BUCKET_NAME = get_secret("SCW_S3_BUCKET_NAME")

# This is used for links in activation emails and so on
FRONTEND_URL = get_secret("FRONTEND_URL")

# Run time is set when django starts
RUNTIME = datetime.now(pytz.timezone('Europe/Berlin')).isoformat()

# The standard password of the dummy user, this is used within get_private_key in UserProfile
# This enables us to do a lot of cool stuff, for example: test the restframework api directly
DUMMY_USER_PASSWORD = "qwe123"

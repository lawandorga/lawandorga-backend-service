#  law&orga - record and organization management software for refugee law clinics
#  Copyright (C) 2020  Dominik Walser
#
#  This program is free software: you can redistribute it and/or modify
#  it under the terms of the GNU Affero General Public License as
#  published by the Free Software Foundation, either version 3 of the
#  License, or (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU Affero General Public License for more details.
#
#  You should have received a copy of the GNU Affero General Public License
#  along with this program.  If not, see <https://www.gnu.org/licenses/>
from django.core.exceptions import ImproperlyConfigured
from datetime import timedelta
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
    "backend.api",
    "backend.recordmanagement",
    "backend.files",
    "backend.collab",
    "rest_framework.authtoken",
    "storages",
    "corsheaders",
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
    "backend.static.middleware.LoggingMiddleware",
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

# Static Files
# https://docs.djangoproject.com/en/dev/howto/static-files/
STATICFILES_DIRS = [os.path.join(BASE_DIR, "static/dist/")]
STATIC_URL = "/static/"
STATIC_ROOT = os.path.join(BASE_DIR, "tmp/static/")

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

# This is used by the ExpiringTokenAuthentication which extends from rest's token authentication
TIMEOUT_TIMEDELTA = timedelta(minutes=10)

# Secret keys for s3-storage to save files from 'files' and documents from records
SCW_SECRET_KEY = get_secret("SCW_SECRET_KEY")
SCW_ACCESS_KEY = get_secret("SCW_ACCESS_KEY")
SCW_S3_BUCKET_NAME = get_secret("SCW_S3_BUCKET_NAME")

# This is used for links in activation emails and so on
FRONTEND_URL = get_secret("FRONTEND_URL")

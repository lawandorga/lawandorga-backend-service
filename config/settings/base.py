import os
from datetime import datetime, timedelta

import pytz

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Application definition
# https://docs.djangoproject.com/en/dev/ref/applications/
INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "oidc_provider",
    "rest_framework",
    "tinymce",
    "core",
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

# Password hasher
# https://docs.djangoproject.com/en/4.1/topics/auth/passwords/#using-argon2-with-django
PASSWORD_HASHERS = [
    "django.contrib.auth.hashers.Argon2PasswordHasher",
    "django.contrib.auth.hashers.PBKDF2PasswordHasher",
    "django.contrib.auth.hashers.PBKDF2SHA1PasswordHasher",
    "django.contrib.auth.hashers.BCryptSHA256PasswordHasher",
    "django.contrib.auth.hashers.ScryptPasswordHasher",
]

# Middleware
# https://docs.djangoproject.com/en/dev/topics/http/middleware/
MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "corsheaders.middleware.CorsMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "config.middleware.authentication_middleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "config.middleware.logging_middleware",
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
USE_TZ = True

# Authentication
# https://docs.djangoproject.com/en/dev/ref/settings/#std:setting-AUTH_USER_MODEL
AUTH_USER_MODEL = "core.UserProfile"

# Login
# https://docs.djangoproject.com/en/4.1/ref/settings/#login-url
LOGIN_URL = "/login/"
LOGOUT_REDIRECT_URL = "/login/"

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

# needed for session
# https://pypi.org/project/django-cors-headers/
CORS_ALLOW_CREDENTIALS = True

# same site attribute
# https://docs.djangoproject.com/en/4.1/ref/settings/#session-cookie-samesite
SESSION_COOKIE_SAMESITE = "Strict"
CSRF_COOKIE_SAMESITE = "Strict"

# logout after browser close
# https://docs.djangoproject.com/en/4.1/ref/settings/#session-expire-at-browser-close
SESSION_EXPIRE_AT_BROWSER_CLOSE = True
SESSION_COOKIE_AGE = 60 * 60 * 8

# Rest Framework
# https://www.django-rest-framework.org/api-guide/settings/
REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": [
        "rest_framework.authentication.SessionAuthentication",
    ],
    "DATE_INPUT_FORMATS": ["%d-%m-%Y", "%Y-%m-%d", "%Y-%m-%dT%H:%M:%S.%fZ"],
    "DATETIME_FORMAT": "%Y-%m-%dT%H:%M",
    "DEFAULT_PERMISSION_CLASSES": [
        "config.authentication.IsAuthenticatedAndEverything"
    ],
    "EXCEPTION_HANDLER": "config.authentication.custom_exception_handler",
}

# Necessary in django 3.2
# https://docs.djangoproject.com/en/3.2/releases/3.2/#customizing-type-of-auto-created-primary-keys
DEFAULT_AUTO_FIELD = "django.db.models.AutoField"

# OpenID connect settings
# https://django-oidc-provider.readthedocs.io/en/latest/sections/settings.html
OIDC_USERINFO = "core.auth.oidc_provider_settings.userinfo"
OIDC_EXTRA_SCOPE_CLAIMS = "core.auth.oidc_provider_settings.RlcScopeClaims"
OIDC_IDTOKEN_INCLUDE_CLAIMS = True

# mail errors to the admins
# https://docs.djangoproject.com/en/3.2/ref/settings/#admins
ADMINS = [("Daniel Mössner", "it@law-orga.de")]

# TinyMCE
# https://django-tinymce.readthedocs.io/en/latest/installation.html#configuration
TINYMCE_DEFAULT_CONFIG = {
    "theme": "silver",
    "height": 500,
    "menubar": False,
    "plugins": "advlist,autolink,lists,link,image,charmap,print,preview,anchor,"
    "searchreplace,visualblocks,code,fullscreen,insertdatetime,media,table,paste,"
    "code,help,wordcount",
    "toolbar": "undo redo | formatselect | "
    "bold italic underline | forecolor backcolor | alignleft aligncenter "
    "alignright alignjustify | bullist numlist outdent indent | link",
    "block_formats": "Paragraph=p; Heading=h2; Subheading=h3; Preformatted=pre",
    "valid_classes": "",
    "valid_styles": {
        "*": "color,text-align,padding-left,text-decoration,background-color"
    },
    "advlist_bullet_styles": "default",
    "advlist_number_styles": "default",
}

# custom test runner
# https://pytest-django.readthedocs.io/en/latest/faq.html#how-can-i-use-manage-py-test-with-pytest-django
TEST_RUNNER = "config.test.PytestTestRunner"

# caching
# https://docs.djangoproject.com/en/4.1/topics/cache/#local-memory-caching
CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.locmem.LocMemCache",
        "LOCATION": "unique-snowflake",
    }
}

# This is used by the ExpiringTokenAuthentication which extends from rest's token authentication
TIMEOUT_TIMEDELTA = timedelta(minutes=30)

# This is used for ics calendar integration links
CALENDAR_URL = "http://localhost:8000/api/events/ics/"

# this is used to check the domain settings for the email application
MAIL_MX_RECORD = "mail.law-orga.de."

# General settings displayed on the index page
RUNTIME = datetime.now(pytz.timezone("Europe/Berlin")).strftime("%Y-%m-%d--%H:%M:%S")
IMAGE = os.getenv("PIPELINE_IMAGE", "unknown")
SERVICE = os.getenv("PIPELINE_SERVICE", "unknown")

# The standard password of the dummy user, this is used within get_private_key in UserProfile
# This enables us to do a lot of cool stuff, for example: test the restframework api directly
DUMMY_USER_PASSWORD = "qwe123"

# cronjobs
# those are used within core.cronjobs and imported by string
CRONJOBS = [
    "core.legal.cronjobs.create_legal_requirements_for_users",
    "core.records.cronjobs.update_statistic_fields",
]

# testing
TESTING = os.getenv("TESTING", False)

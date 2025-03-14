from .production import *

# This is used for links in activation emails and so on
#
MAIN_FRONTEND_URL = "http://localhost:4204"
STATISTICS_FRONTEND_URL = "http://localhost:4300"

# This is used internally to access media or similar stuff
#
MAIN_BACKEND_URL = "http://localhost:4205"

# This is used for ics calendar integration links
#
CALENDAR_URL = "http://localhost:4205"

# Debug
# https://docs.djangoproject.com/en/dev/ref/settings/#std:setting-DEBUG
DEBUG = True

# Allowed Hosts
# https://docs.djangoproject.com/en/dev/ref/settings/#allowed-hosts
ALLOWED_HOSTS = ["*"]

# session cookie domain
# https://docs.djangoproject.com/en/4.1/ref/settings/#session-cookie-domain
SESSION_COOKIE_DOMAIN = None
CSRF_COOKIE_DOMAIN = None

# secure attribute
# https://developer.mozilla.org/en-US/docs/Web/HTTP/Cookies?retiredLocale=de#restrict_access_to_cookies
SESSION_COOKIE_SECURE = False
CSRF_COOKIE_SECURE = False

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

# Installed app django-cors-headers
# https://pypi.org/project/django-cors-headers/
CORS_ALLOWED_ORIGINS = [MAIN_FRONTEND_URL, STATISTICS_FRONTEND_URL]

# Add the frontend to trusted origins
# https://docs.djangoproject.com/en/4.1/ref/settings/#csrf-trusted-origins
CSRF_TRUSTED_ORIGINS = [MAIN_FRONTEND_URL, STATISTICS_FRONTEND_URL]

# Storage
# https://django-storages.readthedocs.io/en/latest/backends/amazon-S3.html#settings
STORAGES["default"]["BACKEND"] = "config.storage.CustomS3Boto3Storage"
AWS_S3_SECRET_ACCESS_KEY = env.str("S3_SECRET_KEY")
AWS_S3_ACCESS_KEY_ID = env.str("S3_ACCESS_KEY")
AWS_STORAGE_BUCKET_NAME = env.str("S3_BUCKET_NAME")
AWS_S3_REGION_NAME = "fr-par"
AWS_S3_ENDPOINT_URL = "https://s3.fr-par.scw.cloud"
AWS_S3_FILE_OVERWRITE = False

# E-Mail
# https://docs.djangoproject.com/en/dev/topics/email/#smtp-backend
EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"

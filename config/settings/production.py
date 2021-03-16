from config.settings.base import *
from datetime import timedelta

# Debug
# https://docs.djangoproject.com/en/dev/ref/settings/#std:setting-DEBUG
DEBUG = False

# Allowed Hosts
# https://docs.djangoproject.com/en/dev/ref/settings/#allowed-hosts
ALLOWED_HOSTS = get_secret('ALLOWED_HOSTS')

# SECURITY WARNING: keep the secret key used in production secret!
# https://docs.djangoproject.com/en/dev/ref/settings/#std:setting-SECRET_KEY
SECRET_KEY = get_secret('SECRET_KEY')

# Authentication Timeout
# TODO: figure out what this is
TIMEOUT_TIMEDELTA = timedelta(minutes=10)

# Database
# https://docs.djangoproject.com/en/2.1/ref/settings/#databases
DATABASES = {
    "default": {
        "ENGINE": "django_prometheus.db.backends.postgresql",
        "NAME": get_secret('DB_NAME'),
        "USER": get_secret("DB_USER"),
        "PASSWORD": get_secret("DB_PASSWORD"),
        "HOST": get_secret("DB_HOST"),
        "PORT": get_secret("DB_PORT")
    }
}

# E-Mail
# https://docs.djangoproject.com/en/dev/topics/email/#smtp-backend
EMAIL_HOST = get_secret("EMAIL_HOST")
DEFAULT_FROM_EMAIL = get_secret("EMAIL_ADDRESS")
SERVER_EMAIL = get_secret("EMAIL_ADDRESS")
EMAIL_PORT = get_secret("EMAIL_PORT")
EMAIL_HOST_USER = get_secret("EMAIL_HOST_USER")
EMAIL_HOST_PASSWORD = get_secret("EMAIL_HOST_PASSWORD")
EMAIL_USER_TLS = get_secret("EMAIL_USER_TLS")
EMAIL_USE_SSL = get_secret("EMAIL_USE_SSL")

# Installed app django-cors-headers
# https://pypi.org/project/django-cors-headers/
CORS_ALLOWED_ORIGINS = [
    # prod
    "https://law-orga.de",
    "http://law-orga.de",
    "http://www.law-orga.de",
    "https://www.law-orga.de",
    "https://d1g37iqegvaqxr.cloudfront.net",
    # dev
    "https://d7pmzq2neb57w.cloudfront.net",
    # test
    "https://d33cushiywgecu.cloudfront.net",
]

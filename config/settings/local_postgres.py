# type: ignore

from .local import *

# Database
# https://docs.djangoproject.com/en/2.1/ref/settings/#databases
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": "lawandorga-backend-service",
        "USER": "lawandorga-backend-service",
        "PASSWORD": "pass1234",
        "HOST": "192.168.1.94",
        "PORT": "5432",
        "TEST": {"NAME": "test_{}".format(RUNTIME)},
    }
}

# type: ignore

import environs

from .local import *

# Environment
# https://github.com/sloria/environs/blob/master/examples/django_example.py
env = environs.Env()
env.read_env()

# Database
# https://docs.djangoproject.com/en/2.1/ref/settings/#databases
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": "lawandorga-backend-service",
        "USER": "lawandorga-backend-service",
        "PASSWORD": "pass1234",
        "HOST": "localhost",
        "PORT": "5432",
        "TEST": {"NAME": "test_{}".format(RUNTIME)},
    }
}

# Storage
# https://django-storages.readthedocs.io/en/latest/backends/amazon-S3.html#settings
DEFAULT_FILE_STORAGE = "config.storage.CustomS3Boto3Storage"
AWS_S3_SECRET_ACCESS_KEY = env.str("S3_SECRET_KEY")
AWS_S3_ACCESS_KEY_ID = env.str("S3_ACCESS_KEY")
AWS_STORAGE_BUCKET_NAME = env.str("S3_BUCKET_NAME")
AWS_S3_REGION_NAME = "fr-par"
AWS_S3_ENDPOINT_URL = "https://s3.fr-par.scw.cloud"
AWS_S3_FILE_OVERWRITE = False

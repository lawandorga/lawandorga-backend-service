# type: ignore

import environs

from .local import *

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

# Storage
# https://django-storages.readthedocs.io/en/latest/backends/amazon-S3.html#settings
STORAGES["default"]["BACKEND"] = "config.storage.CustomS3Boto3Storage"
AWS_S3_SECRET_ACCESS_KEY = env.str("S3_SECRET_KEY")
AWS_S3_ACCESS_KEY_ID = env.str("S3_ACCESS_KEY")
AWS_STORAGE_BUCKET_NAME = env.str("S3_BUCKET_NAME")
AWS_S3_REGION_NAME = "fr-par"
AWS_S3_ENDPOINT_URL = "https://s3.fr-par.scw.cloud"
AWS_S3_FILE_OVERWRITE = False

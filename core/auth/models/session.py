from django.contrib.sessions.base_session import AbstractBaseSession
from django.db import models

from config.session import SessionStore


class CustomSession(AbstractBaseSession):
    user_id = models.IntegerField(null=True, db_index=True)

    @classmethod
    def get_session_store_class(cls):
        return SessionStore

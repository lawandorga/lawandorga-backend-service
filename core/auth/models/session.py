from django.contrib.sessions.base_session import AbstractBaseSession
from django.db import models

from config.session import SessionStore


class CustomSession(AbstractBaseSession):
    user_id = models.IntegerField(null=True, db_index=True)

    class Meta:
        verbose_name = "AUTH_CustomSession"
        verbose_name_plural = "AUTH_CustomSessions"

    @classmethod
    def get_session_store_class(cls):
        return SessionStore

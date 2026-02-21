from django.contrib.sessions.backends.db import SessionStore as DBStore


class SessionStore(DBStore):
    @classmethod
    def get_model_class(cls):
        from core.auth.models.session import CustomSession

        return CustomSession

    def create_model_instance(self, data: dict):
        from core.auth.models.session import CustomSession

        obj: CustomSession = super().create_model_instance(data)  # type: ignore
        try:
            user_id = int(data["_auth_user_id"])
        except ValueError, TypeError, KeyError:
            user_id = None
        obj.user_id = user_id
        return obj

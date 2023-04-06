from django.apps import AppConfig


class MessagebusConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "messagebus"

    def ready(self) -> None:
        from messagebus.domain.bus import MessageBus
        from messagebus.impl.repository import DjangoMessageBusRepository

        MessageBus.set_repository(DjangoMessageBusRepository)
        MessageBus.run_checks()

from django.apps import AppConfig


class CoreConfig(AppConfig):
    name = "core"

    def ready(self) -> None:
        import core.folders.handlers  # noqa: F401
        import core.org.handlers  # noqa: F401

from typing import Any, Callable, Literal, Type

from django.db import models, transaction

Handler = Callable[[Any], None]
OnOptions = Literal[
    "pre_save", "on_save", "post_save", "pre_delete", "on_delete", "post_delete"
]


class Addon:
    pre_save: list[Handler] = []
    on_save: list[Handler] = []
    post_save: list[Handler] = []

    pre_delete: list[Handler] = []
    on_delete: list[Handler] = []
    post_delete: list[Handler] = []

    def __init__(self, obj):
        self._obj = obj

    def call(self, on: OnOptions):
        handlers = getattr(self, on)
        for handler in handlers:
            handler()


class Aggregate(models.Model):
    addons: dict[str, Type[Addon]]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for key, addon_class in self.__class__.addons.items():
            assert not hasattr(self, key)
            addon = addon_class(self)
            setattr(self, key, addon)

    def __call_addons(self, on: OnOptions):
        for key in self.addons.keys():
            addon = getattr(self, key)
            addon.call(on)

    def save(self, *args, **kwargs):
        self.__call_addons("pre_save")
        with transaction.atomic():
            self.__call_addons("on_save")
            super().save()
        self.__call_addons("post_save")

    def delete(self, *args, **kwargs):
        self.__call_addons("pre_delete")
        with transaction.atomic():
            self.__call_addons("on_delete")
            super().delete()
        self.__call_addons("post_delete")

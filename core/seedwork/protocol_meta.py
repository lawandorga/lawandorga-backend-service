from typing import Any

from django.db import models

from core.folders.domain.external import IOwner

django_model_type: Any = type(models.Model)
protocol_type: Any = type(IOwner)


class ModelProtocolMeta(django_model_type, protocol_type):
    """
    This technique allows us to use Protocol with
    Django models without metaclass conflict
    """

    pass

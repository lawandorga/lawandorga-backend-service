from django.conf import settings
from django.core.files.storage import FileSystemStorage


class InstanceStorage(FileSystemStorage):
    def __init__(self, **kwargs):
        kwargs.pop('location', None)
        location = settings.MEDIA_ROOT
        super().__init__(location=location, **kwargs)


instance_storage = InstanceStorage()

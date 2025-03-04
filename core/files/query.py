from core.files.models.file import File
from core.org.models.org import Org


def has_org_files(org: Org) -> bool:
    return File.objects.filter(folder__rlc=org).exists()

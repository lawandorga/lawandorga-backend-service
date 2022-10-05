from apps.core.auth.models import RlcUser
from apps.core.rlc.models import Group
from apps.static.use_case_layer import add_mapping

add_mapping(Group, lambda v: Group.objects.get(id=v) if type(v) is int else v)
add_mapping(RlcUser, lambda v: RlcUser.objects.get(id=v) if type(v) is int else v)

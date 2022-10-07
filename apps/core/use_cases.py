from apps.core.auth.models import RlcUser
from apps.core.rlc.models import Group
from apps.recordmanagement.models import QuestionnaireTemplate, Record
from apps.static.use_case_layer import add_mapping

add_mapping(Group, lambda v, actor: Group.objects.get(id=v))
add_mapping(RlcUser, lambda v, actor: RlcUser.objects.get(id=v, org__id=actor.org.id))
add_mapping(
    QuestionnaireTemplate,
    lambda v, actor: QuestionnaireTemplate.objects.get(id=v, rlc__id=actor.org.id),
)
add_mapping(
    Record, lambda v, actor: Record.objects.get(id=v, template__rlc__id=actor.org.id)
)

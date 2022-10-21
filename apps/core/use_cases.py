from apps.core.auth.models import RlcUser
from apps.core.legal.models import LegalRequirementUser
from apps.core.records.models import QuestionnaireTemplate, Record
from apps.core.rlc.models import Group
from apps.core.seedwork.use_case_layer import add_mapping

add_mapping(Group, lambda v, actor: Group.objects.get(id=v, from_rlc__id=actor.org_id))
add_mapping(RlcUser, lambda v, actor: RlcUser.objects.get(id=v, org__id=actor.org_id))
add_mapping(
    QuestionnaireTemplate,
    lambda v, actor: QuestionnaireTemplate.objects.get(id=v, rlc__id=actor.org_id),
)
add_mapping(
    Record, lambda v, actor: Record.objects.get(id=v, template__rlc__id=actor.org_id)
)
add_mapping(
    LegalRequirementUser,
    lambda v, actor: LegalRequirementUser.objects.get(id=v, rlc_user=actor),
)

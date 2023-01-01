from django.db.models import Q

from core.records.models import Record, RecordDeletion, RecordTemplate


def record_from_id(actor, v) -> Record:
    return Record.objects.get(id=v, template__rlc__id=actor.org_id)


def template_from_id(actor, v) -> RecordTemplate:
    return RecordTemplate.objects.get(id=v, rlc_id=actor.org_id)


def deletion_from_id(actor, v) -> RecordDeletion:
    return RecordDeletion.objects.get(
        Q(id=v)
        & (
            Q(requested_by__rlc_user__org_id=actor.org_id)
            | Q(processed_by__rlc_user__org_id=actor.org_id)
            | Q(record__template__rlc_id=actor.org_id)
        )
    )

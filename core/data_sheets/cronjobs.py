from core.data_sheets.models import RecordStatisticField, RecordTemplate


def update_statistic_fields() -> str:
    updated = 0

    update_fields = []
    for meta in RecordTemplate.get_statistic_fields_meta():
        fields = list(RecordStatisticField.objects.filter(name=meta["name"]))
        for field in fields:
            if field.options != meta["options"] or field.helptext != meta["helptext"]:
                field.options = meta["options"]
                field.helptext = meta["helptext"]
                update_fields.append(field)
                updated += 1

    RecordStatisticField.objects.bulk_update(
        update_fields, fields=["options", "helptext"]
    )

    return "Updated {} statistic fields.".format(updated)

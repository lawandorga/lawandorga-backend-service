from core.data_sheets.models.data_sheet import DataSheet


def get_available_datasheet_years(org_id: int) -> set[int]:
    years = set(
        DataSheet.objects.filter(template__rlc_id=org_id)
        .values_list("created__year", flat=True)
        .distinct()
    )
    return years

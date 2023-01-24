# from typing import cast
#
# from django.db import transaction
#
# from core.folders.domain.aggregates.folder import Folder
# from core.folders.domain.repositiories.folder import FolderRepository
# from core.models import FoldersFolder, Record
# from core.seedwork.repository import RepositoryWarehouse
#
# all_records = list(
#     Record.objects.exclude(folder_uuid=None).select_related("template", "template__rlc")
# )
# all_folders = list(FoldersFolder.objects.all())
#
# item_uuids = []
# for folder in all_folders:
#     for item in folder.items:
#         item_uuids.append(item["uuid"])
#
# error_records = []
# for record in all_records:
#     if str(record.uuid) not in item_uuids:
#         error_records.append(record)
#
#
# r = cast(FolderRepository, RepositoryWarehouse.get("FOLDER"))
#
# folders = {}
#
# with transaction.atomic():
#     i = 0
#     for record in error_records:
#         if record.template.rlc_id not in folders:
#             folders[record.template.rlc_id] = r.get_dict(record.template.rlc_id)
#         i += 1
#         folder: Folder = folders[record.template.rlc_id][record.folder_uuid]
#         folder.add_item(record)
#         r.save(folder)

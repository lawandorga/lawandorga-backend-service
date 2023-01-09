# from core.folders.domain.aggregates.folder import Folder
# from core.folders.domain.aggregates.item import Item
# from messagebus import DjangoAggregate
#
#
# class DjangoItem(Item, DjangoAggregate):
#     def set_folder(self, folder: Folder):
#         super().set_folder(folder)
#         self.add_event(
#             "ItemAddedToFolder",
#             data={
#                 "org_pk": self.org_pk,
#                 "uuid": str(self.uuid),
#                 "repository": self.REPOSITORY,
#                 "name": self.name,
#                 "folder_uuid": str(folder.uuid),
#             },
#         )
#
#     def set_name(self, name: str):
#         self.add_event(
#             "ItemRenamed",
#             data={
#                 "org_pk": self.org_pk,
#                 "uuid": str(self.uuid),
#                 "repository": self.REPOSITORY,
#                 "name": self.name,
#                 "folder_uuid": str(self.folder_uuid),
#             },
#         )
#
#     def delete(self, *args, **kwargs):
#         self.add_event(
#             "ItemDeleted",
#             data={
#                 "org_pk": self.org_pk,
#                 "uuid": str(self.uuid),
#                 "repository": self.REPOSITORY,
#                 "name": self.name,
#                 "folder_uuid": str(self.folder_uuid),
#             },
#         )
#         return super().delete(*args, **kwargs)

# from django.core.management.base import BaseCommand

# from core.auth.domain.user_key import UserKey
# from core.auth.models.org_user import OrgUser
# from core.encryption.models import GroupKey, Keyring
# from core.folders.domain.value_objects.asymmetric_key import EncryptedAsymmetricKey
# from core.folders.domain.value_objects.symmetric_key import EncryptedSymmetricKey
# from core.org.models.group import EncryptedGroupKey, Group
# from core.org.models.org import Org


# class Command(BaseCommand):
#     help = "migrates into the new encryption model"

#     def handle(self, *args, **options):
#         Keyring.objects.all().delete()

#         for o in Org.objects.all().order_by("pk"):
#             self.stdout.write("migrating org {}".format(o.pk))

#             for u in (
#                 OrgUser.objects.filter(org=o).select_related("user").order_by("pk")
#             ):
#                 user_key = UserKey.create_from_dict(u.key)
#                 if not isinstance(user_key.key, EncryptedAsymmetricKey):
#                     u.locked = True
#                     u.save()
#                     for ug in u.groups.all():
#                         ug.members.remove(u)
#                     continue
#                 keyring = Keyring.create(user=u, key=user_key)
#                 keyring.store()
#                 self.stdout.write("created keyring for user {}".format(u.pk))

#             for g in (
#                 Group.objects.filter(org=o).prefetch_related("members").order_by("pk")
#             ):
#                 self.stdout.write("migrating group {}".format(g.pk))
#                 for u in g.members.all().order_by("pk").select_related("keyring"):
#                     enc_group_key = g.get_enc_group_key_of_user(u)
#                     assert isinstance(enc_group_key, EncryptedGroupKey)
#                     enc_s_key = enc_group_key.get_key_for_migration()
#                     assert isinstance(enc_s_key, EncryptedSymmetricKey)
#                     group_key = GroupKey(
#                         keyring=u.keyring,
#                         group=g,
#                         key=enc_s_key.as_dict(),
#                     )
#                     group_key.save(force=True)
#                     self.stdout.write("created group key for user {}".format(u.pk))

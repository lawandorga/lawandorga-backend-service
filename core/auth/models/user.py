from datetime import timedelta
from typing import TYPE_CHECKING, Any, Dict, Union

from django.contrib.auth.models import (
    AbstractBaseUser,
    BaseUserManager,
    PermissionsMixin,
)
from django.core.exceptions import ObjectDoesNotExist
from django.db import models, transaction
from django.utils import timezone
from rest_framework.exceptions import ParseError

from core.static import PERMISSION_ADMIN_MANAGE_USERS

if TYPE_CHECKING:
    from core.models import MailUser, MatrixUser, Permission, RlcUser, StatisticUser


class UserProfileManager(BaseUserManager):
    def get_queryset(self):
        return (
            super()
            .get_queryset()
            .select_related("rlc_user", "statistic_user", "internal_user", "mail_user")
        )


class UserProfile(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(max_length=255, unique=True)
    name = models.CharField(max_length=255)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    # custom manager
    objects = UserProfileManager()

    # overwrites abstract base user
    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["name"]

    # mypy stuff
    rlc_user: "RlcUser"
    statistic_user: "StatisticUser"
    matrix_user: "MatrixUser"
    mail_user: "MailUser"

    class Meta:
        verbose_name = "UserProfile"
        verbose_name_plural = "UserProfiles"
        ordering = ["name"]

    def __str__(self):
        return "user: {}; email: {};".format(self.pk, self.email)

    # django intern stuff
    @property
    def is_staff(self):
        return hasattr(self, "internal_user")

    # other stuff
    @property
    def rlc(self):
        return self.rlc_user.org

    def change_password(self, old_password, new_password):
        if not self.check_password(old_password):
            raise ParseError("The password is not correct.")
        rlc_user = self.rlc_user
        self.set_password(new_password)
        rlc_user.change_password_for_keys(new_password)
        with transaction.atomic():
            rlc_user.save()
            self.save()

    def has_permission(self, permission: Union[str, "Permission"]):
        return self.rlc_user.has_permission(permission)

    def get_collab_permissions(self):
        from core.models import PermissionForCollabDocument

        groups = self.rlc_user.groups.all()
        return PermissionForCollabDocument.objects.filter(
            group_has_permission__in=groups
        ).select_related("document")

    def get_own_records(self):
        from core.records.models import Record

        records = Record.objects.filter(template__rlc=self.rlc).prefetch_related(
            "users_entries", "users_entries__value"
        )
        record_pks = []
        for record in list(records):
            users_entries = list(record.users_entries.all())
            if len(users_entries) <= 0:
                continue
            users = list(users_entries[0].value.all())
            if self.rlc_user.id in map(lambda x: x.id, users):
                record_pks.append(record.id)

        return Record.objects.filter(pk__in=record_pks)

    def get_records_information(self):
        from core.records.models import Record

        records = Record.objects.filter(template__rlc=self.rlc).prefetch_related(
            "state_entries", "users_entries", "users_entries__value"
        )
        records_data = []
        for record in list(records):
            state_entries = list(record.state_entries.all())
            users_entries = list(record.users_entries.all())

            if len(users_entries) <= 0 or len(state_entries) <= 0:
                continue
            users = list(users_entries[0].value.all())
            if self.rlc_user.id not in map(lambda x: x.id, users):
                continue
            state = state_entries[0].value
            if state == "Open":
                records_data.append(
                    {
                        "id": record.id,
                        "uuid": record.uuid,
                        "identifier": record.identifier,
                        "state": state,
                    }
                )
        return records_data

    def get_members_information(self):
        from .org_user import RlcUser

        if self.has_permission(PERMISSION_ADMIN_MANAGE_USERS):
            members_data = []
            users = RlcUser.objects.filter(
                org=self.rlc, created__gt=timezone.now() - timedelta(days=14)
            )
            for rlc_user in list(users):
                if rlc_user.groups.all().count() == 0:
                    members_data.append(
                        {
                            "name": rlc_user.user.name,
                            "id": rlc_user.user.id,
                            "rlcuserid": rlc_user.id,
                        }
                    )
            return members_data
        return None

    def get_questionnaire_information(self):
        from core.questionnaires.models.questionnaire import Questionnaire

        questionnaires = Questionnaire.objects.filter(
            template__rlc_id=self.rlc_user.org_id
        ).select_related("template", "record")

        questionnaire_data = []

        for questionnaire in list(questionnaires):
            if (
                not questionnaire.answered
                and questionnaire.folder
                and questionnaire.folder.has_access(self.rlc_user)
            ):
                questionnaire_data.append(
                    {
                        "name": questionnaire.name,
                        "folder_uuid": questionnaire.folder_uuid,
                    }
                )

        return questionnaire_data

    def get_changed_records_information(self):
        records = self.get_own_records()
        records = records.filter(updated__gt=timezone.now() - timedelta(days=10))
        changed_records_data = []
        for record in list(records):
            changed_records_data.append(
                {
                    "id": record.id,
                    "uuid": record.uuid,
                    "identifier": record.identifier,
                    "updated": record.updated,
                }
            )
        return changed_records_data

    def get_information(self) -> Dict[str, Any]:
        return_dict = {}
        # records
        records_data = self.get_records_information()
        if records_data:
            return_dict["records"] = records_data
        # members
        members_data = self.get_members_information()
        if members_data:
            return_dict["members"] = members_data
        # questionnaires
        questionnaire_data = self.get_questionnaire_information()
        if questionnaire_data:
            return_dict["questionnaires"] = questionnaire_data
        # changed records
        changed_records_data = self.get_changed_records_information()
        if changed_records_data:
            return_dict["changed_records"] = changed_records_data
            # return
        return return_dict

    def get_public_key(self) -> bytes:
        return self.rlc_user.get_public_key()

    def get_private_key(self, *args, **kwargs) -> str:
        return self.rlc_user.get_private_key()

    def get_private_key_rlc(self, private_key_user=None, request=None):
        if private_key_user:
            pass
        elif request:
            private_key_user = self.get_private_key(request=request)
        else:
            raise ValueError("You need to pass (private_key_user) or (request).")

        return self.rlc.get_private_key(user=self, private_key_user=private_key_user)

    def get_rlc_aes_key(self, private_key_user=None):
        if private_key_user:
            return self.rlc.get_aes_key(user=self, private_key_user=private_key_user)
        else:
            raise ValueError("You need to set (private_key_user).")

    def test_all_keys(self, private_key_user):
        from core.records.models import RecordEncryptionNew

        for key in RecordEncryptionNew.objects.filter(user=self.rlc_user):
            key.test(private_key_user)
        self.users_rlc_keys.first().test(private_key_user)

    def __get_all_keys_raw(self):
        from core.records.models import RecordEncryptionNew

        ret = {
            "record_keys": list(
                RecordEncryptionNew.objects.filter(user=self.rlc_user).select_related(
                    "record"
                )
            ),
            "rlc_keys": self.users_rlc_keys.select_related("rlc").all(),
        }

        return ret

    def check_all_keys_correct(self):
        keys = self.get_all_keys()
        for key in keys:
            if not key["correct"]:
                return False
        return True

    def get_all_keys(self):
        keys = self.__get_all_keys_raw()
        all_keys = []

        for key in keys["record_keys"]:
            d = {
                "id": key.id,
                "correct": key.correct,
                "source": "RECORD",
                "information": "{}".format(key.record.identifier),
            }
            all_keys.append(d)
        for key in keys["rlc_keys"]:
            d = {
                "id": key.id,
                "correct": key.correct,
                "source": "RLC",
                "information": "{}".format(key.rlc.name),
            }
            all_keys.append(d)

        return all_keys

    def generate_keys_for_user(self, private_key_self, user_to_unlock):
        """
        this method assumes that a valid public key exists for user_to_unlock
        """
        from core.models import OrgEncryption
        from core.records.models import RecordEncryptionNew

        # check if all keys can be handed over
        success = True

        # generate new rlc key - this always works
        user_to_unlock.users_rlc_keys.all().delete()
        aes_key_rlc = self.rlc.get_aes_key(user=self, private_key_user=private_key_self)
        new_keys = OrgEncryption(
            user=user_to_unlock, rlc=user_to_unlock.rlc, encrypted_key=aes_key_rlc
        )
        new_keys.encrypt(user_to_unlock.get_public_key())
        new_keys.save()

        # generate new record encryption
        record_encryptions = user_to_unlock.rlc_user.recordencryptions.filter(
            correct=False
        )

        for old_keys in list(record_encryptions):
            # change the keys to the new keys
            try:
                encryption = RecordEncryptionNew.objects.get(
                    user=self.rlc_user, record=old_keys.record
                )
            except ObjectDoesNotExist:
                success = False
                continue
            encryption.decrypt(private_key_user=private_key_self)
            old_keys.key = encryption.key
            old_keys.encrypt(user_to_unlock.get_public_key())
            old_keys.save()

        # return true if everything worked as expected return false otherwise
        return success

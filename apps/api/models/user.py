from datetime import timedelta

import jwt
from django.conf import settings
from django.contrib.auth.models import (
    AbstractBaseUser,
    BaseUserManager,
    PermissionsMixin,
)
from django.core.exceptions import ObjectDoesNotExist
from django.db import models, transaction
from django.utils import timezone
from rest_framework.exceptions import AuthenticationFailed, ParseError

from apps.api.models.has_permission import HasPermission
from apps.api.models.permission import Permission
from apps.api.static import PERMISSION_ADMIN_MANAGE_USERS
from apps.static.encryption import RSAEncryption
from rest_framework_simplejwt.settings import api_settings as jwt_settings


class UserProfileManager(BaseUserManager):
    def get_queryset(self):
        return super().get_queryset().select_related("rlc_user")

    @staticmethod
    def get_users_with_special_permission(permission, from_rlc=None, for_rlc=None):
        if isinstance(permission, str):
            permission = Permission.objects.get(name=permission).id

        users = (
            HasPermission.objects.filter(
                permission=permission,
                group_has_permission=None,
            )
                .values("user_has_permission")
                .distinct()
        )

        user_ids = [has_permission["user_has_permission"] for has_permission in users]
        result = UserProfile.objects.filter(id__in=user_ids).distinct()
        if from_rlc is not None:
            result = result.filter(rlc=from_rlc)

        groups = HasPermission.objects.filter(
            permission=permission,
            user_has_permission=None,
        ).values("group_has_permission")
        group_ids = [
            has_permission["group_has_permission"] for has_permission in groups
        ]
        result = result | UserProfile.objects.filter(rlcgroups__in=group_ids).distinct()
        if from_rlc is not None:
            result = result.filter(rlc=from_rlc)

        if from_rlc is not None:
            result = result.filter(rlc=from_rlc)

        return result


class UserProfile(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(max_length=255, unique=True)
    name = models.CharField(max_length=255)
    rlc = models.ForeignKey(
        "Rlc",
        related_name="rlc_members",
        on_delete=models.PROTECT,
        blank=True,
        null=True,
    )
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    # custom manager
    objects = UserProfileManager()

    # overwrites abstract base user
    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["name"]

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
    def change_password(self, old_password, new_password):
        if not self.check_password(old_password):
            raise ParseError("The password is not correct.")
        keys = self.encryption_keys
        keys.decrypt(old_password)
        keys.encrypt(new_password)
        self.set_password(new_password)
        with transaction.atomic():
            keys.save()
            self.save()

    def __get_as_user_permissions(self):
        """
        Returns: all HasPermissions the user itself has as list
        """
        return [
            has_permission.permission.name
            for has_permission in HasPermission.objects.filter(
                user_has_permission=self.pk
            )
        ]

    def __get_as_group_member_permissions(self):
        """
        Returns: all HasPermissions the groups in which the user is member of have as list
        """
        groups = [groups["id"] for groups in list(self.rlcgroups.values("id"))]
        return [
            has_permission.permission.name
            for has_permission in HasPermission.objects.filter(
                group_has_permission_id__in=groups
            )
        ]

    def get_all_user_permissions(self):
        """
        Returns: all HasPermissions which the user has direct and
                    indirect (through membership in a group or rlc) as list
        """
        return (
            self.__get_as_user_permissions() + self.__get_as_group_member_permissions()
        )

    def __has_as_user_permission(self, permission):
        return HasPermission.objects.filter(
            user_has_permission=self.pk, permission=permission
        ).exists()

    def __has_as_group_member_permission(self, permission):
        groups = [group.pk for group in self.rlcgroups.all()]
        return HasPermission.objects.filter(
            group_has_permission__pk__in=groups, permission=permission
        ).exists()

    def has_permission(self, permission, for_user=None, for_group=None, for_rlc=None):
        if isinstance(permission, str):
            try:
                permission = Permission.objects.get(name=permission)
            except ObjectDoesNotExist:
                return False

        as_user = self.__has_as_user_permission(permission)
        as_group = self.__has_as_group_member_permission(permission)

        return as_user or as_group

    def get_collab_permissions(self):
        from apps.collab.models import PermissionForCollabDocument

        groups = self.rlcgroups.all()
        return PermissionForCollabDocument.objects.filter(
            group_has_permission__in=groups
        ).select_related("document")

    def get_own_records(self):
        from apps.recordmanagement.models.record import Record

        records = Record.objects.filter(template__rlc=self.rlc).prefetch_related(
            "users_entries", "users_entries__value"
        )
        record_pks = []
        for record in list(records):
            users_entries = list(record.users_entries.all())
            if len(users_entries) <= 0:
                continue
            users = list(users_entries[0].value.all())
            if self.id in map(lambda x: x.id, users):
                record_pks.append(record.id)

        return Record.objects.filter(pk__in=record_pks)

    def get_records_information(self):
        from apps.recordmanagement.models.record import Record

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
            if self.id not in map(lambda x: x.id, users):
                continue
            state = state_entries[0].value
            if state == "Open":
                records_data.append(
                    {
                        "id": record.id,
                        "identifier": record.identifier,
                        "state": state,
                    }
                )
        return records_data

    def get_members_information(self):
        if self.has_permission(PERMISSION_ADMIN_MANAGE_USERS):
            members_data = []
            users = UserProfile.objects.filter(
                rlc=self.rlc, rlc_user__created__gt=timezone.now() - timedelta(days=14)
            ).select_related("rlc_user")
            for user in list(users):
                if user.rlcgroups.all().count() == 0:
                    members_data.append(
                        {
                            "name": user.name,
                            "id": user.id,
                            "rlcuserid": user.rlc_user.id,
                        }
                    )
            return members_data
        return None

    def get_questionnaire_information(self):
        from apps.recordmanagement.models.questionnaire import Questionnaire

        questionnaires = Questionnaire.objects.filter(
            record__in=self.get_own_records()
        ).select_related("template", "record")

        questionnaire_data = []

        for questionnaire in list(questionnaires):
            if not questionnaire.answered:
                questionnaire_data.append(
                    {
                        "name": questionnaire.template.name,
                        "record": questionnaire.record.identifier,
                        "record_id": questionnaire.record.id,
                    }
                )

        return questionnaire_data

    def get_changed_records_information(self):
        records = self.get_own_records().filter(
            updated__gt=timezone.now() - timedelta(days=10)
        )
        changed_records_data = []
        for record in list(records):
            changed_records_data.append(
                {
                    "id": record.id,
                    "identifier": record.identifier,
                    "updated": record.updated,
                }
            )
        return changed_records_data

    def get_information(self):
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

    def get_public_key(self) -> str:
        """
        gets the public key of the user from the database
        :return: public key of user (PEM)
        """
        if not hasattr(self, "encryption_keys"):
            self.generate_new_user_encryption_keys()
        return self.encryption_keys.public_key

    def get_private_key(self, password_user=None, request=None):
        if not hasattr(self, "encryption_keys"):
            self.generate_new_user_encryption_keys()

        if password_user and not request:
            self.encryption_keys.decrypt(password_user)
            private_key = self.encryption_keys.private_key

        elif request and not password_user:
            try:
                if hasattr(request, 'META') and 'HTTP_AUTHORIZATION' in request.META:
                    token = request.META['HTTP_AUTHORIZATION'].replace('Bearer ', '')
                    payload = jwt.decode(token, jwt_settings.SIGNING_KEY, [jwt_settings.ALGORITHM])
                    private_key = payload['key']
                else:
                    private_key = request.auth.payload["key"]
            except AttributeError:
                # enable direct testing of the rest framework
                if self.email == "dummy@law-orga.de" and settings.DUMMY_USER_PASSWORD:
                    self.encryption_keys.decrypt(settings.DUMMY_USER_PASSWORD)
                    return self.encryption_keys.private_key
                else:
                    raise AuthenticationFailed(
                        "No token or no private key provided within the token."
                    )
            # private_key = private_key.replace("\\n", "\n").replace("<linebreak>", "\n")

        else:
            raise ValueError("You need to pass (password_user) or (request).")

        return private_key

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
        from apps.recordmanagement.models import RecordEncryptionNew

        for key in RecordEncryptionNew.objects.filter(user=self):
            key.test(private_key_user)
        self.users_rlc_keys.first().test(private_key_user)

    def __get_all_keys_raw(self):
        from apps.recordmanagement.models import RecordEncryptionNew

        ret = {
            "record_keys": list(
                RecordEncryptionNew.objects.filter(user=self).select_related("record")
            ),
            "rlc_keys": self.users_rlc_keys.select_related("rlc").all(),
        }

        return ret

    def check_all_keys_correct(self):
        keys = self.get_all_keys()
        for key in keys:
            if not key['correct']:
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

    def generate_new_user_encryption_keys(self):
        from apps.api.models.user_encryption_keys import UserEncryptionKeys

        UserEncryptionKeys.objects.filter(user=self).delete()
        private, public = RSAEncryption.generate_keys()
        user_keys = UserEncryptionKeys(
            user=self, private_key=private, public_key=public
        )
        user_keys.save()

    def generate_keys_for_user(self, private_key_self, user_to_unlock):
        """
        this method assumes that a valid public key exists for user_to_unlock
        """
        from apps.api.models import UsersRlcKeys
        from apps.recordmanagement.models import RecordEncryptionNew

        # check if all keys can be handed over
        success = True

        # generate new rlc key - this always works
        user_to_unlock.users_rlc_keys.all().delete()
        aes_key_rlc = self.rlc.get_aes_key(user=self, private_key_user=private_key_self)
        new_keys = UsersRlcKeys(user=user_to_unlock, rlc=user_to_unlock.rlc, encrypted_key=aes_key_rlc)
        new_keys.encrypt(user_to_unlock.get_public_key())
        new_keys.save()

        # generate new record encryption
        record_encryptions = user_to_unlock.recordencryptions.filter(correct=False)

        for old_keys in list(record_encryptions):
            # change the keys to the new keys
            try:
                encryption = RecordEncryptionNew.objects.get(user=self, record=old_keys.record)
            except ObjectDoesNotExist:
                success = False
                continue
            encryption.decrypt(private_key_user=private_key_self)
            old_keys.key = encryption.key
            old_keys.encrypt(user_to_unlock.get_public_key())
            old_keys.save()

        # return true if everything worked as expected return false otherwise
        return success

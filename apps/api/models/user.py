from apps.api.models.has_permission import HasPermission
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from apps.api.models.permission import Permission
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from rest_framework.exceptions import ParseError, AuthenticationFailed
from django.core.exceptions import ObjectDoesNotExist
from apps.static.encryption import RSAEncryption
from django.core.mail import send_mail
from apps.api.static import PERMISSION_ADMIN_MANAGE_USERS
from django.template import loader
from django.utils import timezone
from django.conf import settings
from django.db import models, transaction
from datetime import timedelta
import jwt


class UserProfileManager(BaseUserManager):
    def get_queryset(self):
        return super().get_queryset().select_related('rlc_user')

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
        result = (
            result | UserProfile.objects.filter(rlcgroups__in=group_ids).distinct()
        )
        if from_rlc is not None:
            result = result.filter(rlc=from_rlc)

        if from_rlc is not None:
            result = result.filter(rlc=from_rlc)

        return result


class UserProfile(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(max_length=255, unique=True)
    name = models.CharField(max_length=255)
    rlc = models.ForeignKey("Rlc", related_name="rlc_members", on_delete=models.PROTECT, blank=True, null=True)
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
        return hasattr(self, 'internal_user')

    # other stuff
    def change_password(self, old_password, new_password):
        if not self.check_password(old_password):
            raise ParseError('The password is not correct.')
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
        return [has_permission.permission.name for has_permission in
                HasPermission.objects.filter(user_has_permission=self.pk)]

    def __get_as_group_member_permissions(self):
        """
        Returns: all HasPermissions the groups in which the user is member of have as list
        """
        groups = [groups["id"] for groups in list(self.rlcgroups.values("id"))]
        return [has_permission.permission.name for has_permission in
                HasPermission.objects.filter(group_has_permission_id__in=groups)]

    def get_all_user_permissions(self):
        """
        Returns: all HasPermissions which the user has direct and
                    indirect (through membership in a group or rlc) as list
        """
        return (
            self.__get_as_user_permissions()
            + self.__get_as_group_member_permissions()
        )

    def __has_as_user_permission(self, permission):
        return HasPermission.objects.filter(user_has_permission=self.pk, permission=permission).exists()

    def __has_as_group_member_permission(self, permission):
        groups = [group.pk for group in self.rlcgroups.all()]
        return HasPermission.objects.filter(group_has_permission__pk__in=groups, permission=permission).exists()

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
        return PermissionForCollabDocument.objects.filter(group_has_permission__in=groups).select_related('document')

    def get_own_records(self):
        from apps.recordmanagement.models.record import Record
        records = Record.objects.filter(template__rlc=self.rlc).prefetch_related('users_entries',
                                                                                 'users_entries__value')
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
        records = Record.objects.filter(template__rlc=self.rlc).prefetch_related('state_entries', 'users_entries',
                                                                                 'users_entries__value')
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
            if state == 'Open':
                records_data.append({
                    'id': record.id,
                    'identifier': record.identifier,
                    'state': state,
                })
        return records_data

    def get_members_information(self):
        if self.has_permission(PERMISSION_ADMIN_MANAGE_USERS):
            members_data = []
            users = UserProfile.objects \
                .filter(rlc=self.rlc, rlc_user__created__gt=timezone.now() - timedelta(days=14)) \
                .select_related('rlc_user')
            for user in list(users):
                if user.rlcgroups.all().count() == 0:
                    members_data.append({'name': user.name, 'id': user.id, 'rlcuserid': user.rlc_user.id})
            return members_data
        return None

    def get_questionnaire_information(self):
        from apps.recordmanagement.models.questionnaire import Questionnaire

        questionnaires = Questionnaire.objects.filter(record__in=self.get_own_records()) \
            .select_related('template', 'record')

        questionnaire_data = []

        for questionnaire in list(questionnaires):
            if not questionnaire.answered:
                questionnaire_data.append({
                    'name': questionnaire.template.name,
                    'record': questionnaire.record.identifier,
                    'record_id': questionnaire.record.id,
                })

        return questionnaire_data

    def get_changed_records_information(self):
        records = self.get_own_records().filter(updated__gt=timezone.now() - timedelta(days=10))
        changed_records_data = []
        for record in list(records):
            changed_records_data.append({
                'id': record.id,
                'identifier': record.identifier,
                'updated': record.updated
            })
        return changed_records_data

    def get_information(self):
        return_dict = {}
        # records
        records_data = self.get_records_information()
        if records_data:
            return_dict['records'] = records_data
        # members
        members_data = self.get_members_information()
        if members_data:
            return_dict['members'] = members_data
        # questionnaires
        questionnaire_data = self.get_questionnaire_information()
        if questionnaire_data:
            return_dict['questionnaires'] = questionnaire_data
        # changed records
        changed_records_data = self.get_changed_records_information()
        if changed_records_data:
            return_dict['changed_records'] = changed_records_data
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
                private_key = request.auth.payload['key']
            except AttributeError:
                # enable direct testing of the rest framework
                if self.email == "dummy@law-orga.de" and settings.DUMMY_USER_PASSWORD:
                    self.encryption_keys.decrypt(settings.DUMMY_USER_PASSWORD)
                    return self.encryption_keys.private_key
                else:
                    raise AuthenticationFailed('No private key within the token.')
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
            raise ValueError('You need to set (private_key_user).')

    def generate_new_user_encryption_keys(self):
        from apps.api.models.user_encryption_keys import UserEncryptionKeys

        UserEncryptionKeys.objects.filter(user=self).delete()
        private, public = RSAEncryption.generate_keys()
        user_keys = UserEncryptionKeys(user=self, private_key=private, public_key=public)
        user_keys.save()

    def generate_keys_for_user(self, private_key_self, user_to_unlock):
        """
        this method assumes that a valid public key exists for user_to_unlock
        """
        from apps.api.models import UsersRlcKeys
        from apps.recordmanagement.models import RecordEncryption

        # this variable checks if all keys that the user needed were generated
        keys_missing = False

        # generate new rlc key - this works always
        user_to_unlock.users_rlc_keys.all().delete()
        aes_key_rlc = self.rlc.get_aes_key(user=self, private_key_user=private_key_self)
        new_keys = UsersRlcKeys(
            user=user_to_unlock, rlc=user_to_unlock.rlc, encrypted_key=aes_key_rlc
        )
        new_keys.encrypt(user_to_unlock.get_public_key())
        new_keys.save()

        # generate new record encryption
        record_encryptions = user_to_unlock.record_encryptions.all()

        for old_keys in list(record_encryptions):
            # check if the user has the needed keys if not just skip
            try:
                encryption = RecordEncryption.objects.get(user=self, record=old_keys.record)
            except ObjectDoesNotExist:
                keys_missing = True
                continue
            # change the keys to the new keys
            encryption.decrypt(private_key_user=private_key_self)
            old_keys.encrypted_key = encryption.encrypted_key
            old_keys.encrypt(user_to_unlock.get_public_key())
            old_keys.save()

        # return true if everything worked as expected return false otherwise
        return not keys_missing


class RlcUser(models.Model):
    user = models.OneToOneField(UserProfile, on_delete=models.CASCADE, related_name='rlc_user')
    # rlc = models.ForeignKey("Rlc", related_name="users", on_delete=models.PROTECT, blank=True, null=True)
    # blocker
    email_confirmed = models.BooleanField(default=True)
    accepted = models.BooleanField(default=False)
    locked = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    # more info
    note = models.TextField(blank=True)
    birthday = models.DateField(null=True, blank=True)
    phone_number = models.CharField(max_length=17, null=True, default=None, blank=True)
    street = models.CharField(max_length=255, default=None, null=True, blank=True)
    city = models.CharField(max_length=255, default=None, null=True, blank=True)
    postal_code = models.CharField(max_length=255, default=None, null=True, blank=True)
    # other
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'RlcUser'
        verbose_name_plural = 'RlcUsers'
        ordering = ['accepted', 'locked', 'is_active', 'user__name']

    def __str__(self):
        return 'rlcUser: {}; email: {};'.format(self.pk, self.user.email)

    def delete(self, *args, **kwargs):
        user = self.user
        super().delete(*args, **kwargs)
        user.delete()

    def check_delete_is_safe(self):
        from apps.recordmanagement.models import RecordEncryptionNew
        for encryption in self.user.recordencryptions.all():
            if RecordEncryptionNew.objects.filter(record=encryption.record).count() <= 2:
                return False
        return True

    def get_email_confirmation_token(self):
        token = AccountActivationTokenGenerator().make_token(self)
        return token

    def get_email_confirmation_link(self):
        token = self.get_email_confirmation_token()
        link = "{}user/email-confirm/{}/{}/".format(settings.FRONTEND_URL, self.id, token)
        return link

    def send_email_confirmation_email(self):
        link = self.get_email_confirmation_link()
        subject = "Law & Orga Registration"
        message = "Law & Orga - Activate your account here: {}".format(link)
        html_message = loader.render_to_string(
            "email_templates/activate_account.html", {"url": link}
        )
        send_mail(
            subject=subject,
            html_message=html_message,
            message=message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[self.user.email],
        )

    def get_password_reset_token(self):
        token = PasswordResetTokenGenerator().make_token(self.user)
        return token

    def get_password_reset_link(self):
        token = self.get_password_reset_token()
        link = "{}user/password-reset-confirm/{}/{}/".format(settings.FRONTEND_URL, self.id, token)
        return link

    def send_password_reset_email(self):
        link = self.get_password_reset_link()
        subject = "Law & Orga Account Password reset"
        message = "Law & Orga - Reset your password here: {}".format(link)
        html_message = loader.render_to_string(
            "email_templates/reset_password.html", {"link": link}
        )
        send_mail(
            subject=subject,
            html_message=html_message,
            message=message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[self.user.email],
        )

    def grant(self, permission_name):
        permission = Permission.objects.get(name=permission_name)
        HasPermission.objects.create(user_has_permission=self.user, permission=permission)


# this is used on signup
class AccountActivationTokenGenerator(PasswordResetTokenGenerator):
    def _make_hash_value(self, rlc_user, timestamp):
        login_timestamp = (
            ""
            if rlc_user.user.last_login is None
            else rlc_user.user.last_login.replace(microsecond=0, tzinfo=None)
        )
        super_make_hash_value = (
            str(rlc_user.pk) + rlc_user.user.password + str(login_timestamp) + str(timestamp)
        )
        additional_hash_value = str(rlc_user.email_confirmed)
        return super_make_hash_value + additional_hash_value

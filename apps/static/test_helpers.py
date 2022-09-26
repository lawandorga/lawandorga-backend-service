from typing import List

from django.conf import settings

from apps.core.auth.models import StatisticUser
from apps.core.models import RlcUser, UserProfile
from apps.recordmanagement.models import Record, RecordEncryptionNew
from apps.static.encryption import AESEncryption


def create_statistics_user(email="dummy@law-orga.de", name="Dummy 1"):
    user = UserProfile.objects.create(email=email, name=name)
    user.set_password(settings.DUMMY_USER_PASSWORD)
    user.save()
    statistics_user = StatisticUser.objects.create(user=user)
    return {
        "user": user,
        "username": user.email,
        "email": user.email,
        "password": settings.DUMMY_USER_PASSWORD,
        "statistics_user": statistics_user,
    }


def create_rlc_user(email="dummy@law-orga.de", name="Dummy 1", rlc=None):
    user = UserProfile.objects.create(email=email, name=name)
    user.set_password(settings.DUMMY_USER_PASSWORD)
    user.save()
    rlc_user = RlcUser.objects.create(
        user=user, email_confirmed=True, accepted=True, org=rlc
    )
    private_key = user.get_private_key(password_user=settings.DUMMY_USER_PASSWORD)
    return {
        "user": user,
        "username": user.email,
        "email": user.email,
        "password": settings.DUMMY_USER_PASSWORD,
        "rlc_user": rlc_user,
        "private_key": private_key,
        "public_key": user.get_public_key(),
    }


def create_record(template=None, users: List[UserProfile] = None):
    record = Record.objects.create(template=template)
    aes_key_record = AESEncryption.generate_secure_key()
    for user in users if users else []:
        public_key_user = user.get_public_key()
        encryption = RecordEncryptionNew(record=record, user=user, key=aes_key_record)
        encryption.encrypt(public_key_user=public_key_user)
        encryption.save()
    return {"record": record, "aes_key": aes_key_record}

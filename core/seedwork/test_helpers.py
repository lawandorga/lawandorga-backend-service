from typing import List, Optional, cast

from django.conf import settings

from core.auth.domain.user_key import UserKey
from core.auth.models import StatisticUser
from core.folders.domain.aggregates.folder import Folder
from core.folders.domain.repositiories.folder import FolderRepository
from core.models import RlcUser, UserProfile
from core.records.models import Record, RecordTemplate
from core.rlc.models import Org
from core.seedwork.repository import RepositoryWarehouse


def create_folder(name="Test Folder", user: RlcUser | None = None):
    assert user is not None

    folder = Folder.create(name=name, org_pk=user.org_id)
    folder.grant_access(to=user)
    r = cast(FolderRepository, RepositoryWarehouse.get(FolderRepository))
    r.save(folder)
    return {"folder": folder}


def create_org(name="Dummy RLC"):
    org = Org.objects.create(name=name)
    return org


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


def create_user(email="dummy@law-orga.de", name="Mr. Dummy"):
    user = UserProfile.objects.create(email=email, name=name)
    user.set_password(settings.DUMMY_USER_PASSWORD)
    user.save()
    return user


def create_rlc_user(
    email="dummy@law-orga.de",
    name="Dummy 1",
    rlc=None,
    accepted=True,
    password=settings.DUMMY_USER_PASSWORD,
):
    user = UserProfile.objects.create(email=email, name=name)
    user.set_password(password)
    user.save()
    rlc_user = RlcUser(user=user, email_confirmed=True, accepted=accepted, org=rlc)
    rlc_user.generate_keys(password)
    rlc_user.save()
    private_key = (
        UserKey.create_from_dict(rlc_user.key)
        .decrypt_self(password)
        .key.get_private_key()
        .decode("utf-8")
    )
    return {
        "user": user,
        "username": user.email,
        "email": user.email,
        "password": settings.DUMMY_USER_PASSWORD,
        "rlc_user": rlc_user,
        "private_key": private_key,
        "public_key": user.get_public_key(),
    }


def create_record_template(org=None):
    template = RecordTemplate.objects.create(rlc=org, name="Record Template")
    return {"template": template}


def create_record(template=None, users: Optional[List[UserProfile]] = None):
    assert users and len(users) > 0
    if template is None:
        template = RecordTemplate.objects.create(
            rlc=users[0].rlc, name="Record Template"
        )
    user = users[0].rlc_user
    folder = create_folder(user=user)["folder"]

    record = Record(template=template)
    record.set_folder(folder)
    record.generate_key(user)
    record.save()

    for u in users[1:]:
        record.grant_access(u.rlc_user, user)

    return {"record": record}

from django.conf import settings

from apps.core.models import RlcUser, UserProfile


def create_rlc_user(email="dummy@law-orga.de", name="Dummy 1", rlc=None):
    user = UserProfile.objects.create(email=email, name=name, rlc=rlc)
    user.set_password(settings.DUMMY_USER_PASSWORD)
    user.save()
    rlc_user = RlcUser.objects.create(user=user, email_confirmed=True, accepted=True)
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

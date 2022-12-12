import re

from django.conf import settings
from django.contrib.auth.forms import PasswordResetForm, SetPasswordForm
from django.contrib.auth.views import (
    LoginView,
    PasswordResetCompleteView,
    PasswordResetConfirmView,
    PasswordResetDoneView,
    PasswordResetView,
)
from django.db import transaction

from core.auth.domain.user_key import UserKey
from core.auth.models import RlcUser, UserProfile


def strip_scheme(url: str):
    return re.sub(r"^https?:\/\/", "", url)


class CustomLoginView(LoginView):
    redirect_url = settings.MAIN_FRONTEND_URL
    success_url_allowed_hosts = {
        strip_scheme(settings.MAIN_FRONTEND_URL),
        strip_scheme(settings.STATISTICS_FRONTEND_URL),
    }
    redirect_authenticated_user = True

    def form_valid(self, form):
        response = super().form_valid(form)
        user = self.request.user
        if hasattr(user, "rlc_user"):
            rlc_user: RlcUser = user.rlc_user  # type: ignore
            # generate if not existent
            if rlc_user.key is None:
                rlc_user.generate_keys(form.data["password"])
                rlc_user.save()
            # check if encrypted
            u1 = UserKey.create_from_dict(rlc_user.key)
            if not u1.is_encrypted:
                u2 = u1.encrypt_self(form.data["password"])
                rlc_user.key = u2.as_dict()
                rlc_user.save()
            # get and decrypt the key
            u4 = rlc_user.get_decrypted_key_from_password(form.data["password"])
            self.request.session["private_key"] = u4.key.get_private_key().decode(
                "utf-8"
            )
        return response


class CustomPasswordResetForm(PasswordResetForm):
    def get_users(self, email):
        """Given an email, return matching user(s) who should receive a reset.

        This allows subclasses to more easily customize the default policies
        that prevent inactive users and users with unusable passwords from
        resetting their password.
        """
        email_field_name = UserProfile.get_email_field_name()
        active_users = UserProfile._default_manager.filter(
            **{
                "%s__iexact" % email_field_name: email,
            }
        )
        return (u for u in active_users if u.has_usable_password())


class CustomPasswordResetView(PasswordResetView):
    form_class = CustomPasswordResetForm


class CustomPasswordResetDoneView(PasswordResetDoneView):
    pass


class CustomSetPasswordForm(SetPasswordForm):
    def save(self, commit=True):
        with transaction.atomic():
            user = super().save(commit)
            if hasattr(user, "rlc_user"):
                rlc_user = user.rlc_user
                rlc_user.generate_keys(self.cleaned_data["new_password1"])
                rlc_user.lock()
                rlc_user.save()
        return user


class CustomPasswordResetConfirmView(PasswordResetConfirmView):
    form_class = CustomSetPasswordForm


class CustomPasswordResetCompleteView(PasswordResetCompleteView):
    pass

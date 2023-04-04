import re

from django.conf import settings
from django.contrib.auth.forms import PasswordResetForm, SetPasswordForm
from django.contrib.auth.views import (
    LoginView,
    LogoutView,
    PasswordResetCompleteView,
    PasswordResetConfirmView,
    PasswordResetDoneView,
    PasswordResetView,
)
from django.http import HttpResponseRedirect
from django.urls import reverse_lazy
from django.utils.decorators import method_decorator
from django.utils.http import url_has_allowed_host_and_scheme
from django.views.decorators.csrf import ensure_csrf_cookie
from django.views.generic import RedirectView

from core.auth.models import UserProfile
from core.auth.use_cases.user import run_user_login_checks, set_password_of_myself


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
        user: UserProfile = form.get_user()  # type: ignore

        if hasattr(user, "rlc_user"):
            run_user_login_checks(user, form.data["password"])
            uk = user.rlc_user.get_decrypted_key_from_password(form.data["password"])
            self.request.session["user_key"] = uk.as_unsafe_dict()

        if (
            hasattr(user, "rlc_user")
            and hasattr(user.rlc_user, "mfa_secret")
            and user.rlc_user.mfa_secret.enabled
        ):
            self.request.session["user_pk"] = user.pk
            url = f"{reverse_lazy('mfa_login')}"
            next_param = self.request.GET.get("next")
            if next_param:
                url += f"?next={next_param}"
            return HttpResponseRedirect(url)

        return super().form_valid(form)


class CustomLogoutView(LogoutView):
    pass


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
        if not commit:
            raise ValueError("Why would this set password form not commit?")
        user = set_password_of_myself(self.user, self.cleaned_data["new_password1"])
        return user


class CustomPasswordResetConfirmView(PasswordResetConfirmView):
    form_class = CustomSetPasswordForm


class CustomPasswordResetCompleteView(PasswordResetCompleteView):
    pass


class CustomRedirectView(RedirectView):
    """used to set cookies"""

    url = settings.MAIN_FRONTEND_URL
    success_url_allowed_hosts = {
        strip_scheme(settings.MAIN_FRONTEND_URL),
        strip_scheme(settings.STATISTICS_FRONTEND_URL),
    }

    def get_success_url_allowed_hosts(self):
        return {self.request.get_host(), *self.success_url_allowed_hosts}

    def get_redirect_url(self, *args, **kwargs):
        """Return the user-originating redirect URL if it's safe."""
        redirect_to = self.request.GET.get("next")
        url_is_safe = url_has_allowed_host_and_scheme(
            url=redirect_to,
            allowed_hosts=self.get_success_url_allowed_hosts(),
            require_https=self.request.is_secure(),
        )
        return redirect_to if url_is_safe else self.url

    @method_decorator(ensure_csrf_cookie)
    def get(self, request, *args, **kwargs):
        """Return a empty response with the token CSRF.

        Returns
        -------
        Response
            The response with the token CSRF as a cookie.
        """
        return super().get(request, *args, **kwargs)

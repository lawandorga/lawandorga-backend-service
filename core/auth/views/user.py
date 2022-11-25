import re

from django.conf import settings
from django.contrib.auth.views import LoginView

from core.auth.domain.user_key import UserKey


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
            rlc_user = user.rlc_user
            u1 = UserKey.create_from_dict(rlc_user.key)
            if not u1.is_encrypted:
                u2 = u1.encrypt_self(form.data["password"])
                rlc_user.key = u2.as_dict()
                rlc_user.save()
            u3 = UserKey.create_from_dict(rlc_user.key)
            u4 = u3.decrypt_self(form.data["password"])
            self.request.session["private_key"] = u4.key.get_private_key().decode(
                "utf-8"
            )
        return response

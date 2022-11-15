import re

from django.conf import settings
from django.contrib.auth.views import LoginView


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
            self.request.session["private_key"] = user.rlc_user.get_private_key(
                password_user=form.data["password"]
            )
        return response

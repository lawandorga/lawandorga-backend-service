from django.conf import settings
from django.contrib.auth import login
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import RedirectURLMixin  # type: ignore
from django.http import Http404, HttpRequest, HttpResponseRedirect
from django.urls import reverse_lazy
from django.views import generic

from core.auth.forms.mfa import CheckMfaForm, MfaAuthenticationForm, SetupMfaForm
from core.auth.models.user import UserProfile
from core.auth.use_cases.mfa import (
    create_mfa_secret,
    delete_mfa_secret,
    enable_mfa_secret,
)
from core.auth.views.user import strip_scheme


class GetUserMixin:
    request: HttpRequest

    def get_user(self) -> "UserProfile":
        if not hasattr(self.request, "user"):
            raise Http404()
        return self.request.user  # type: ignore


class MfaStatusView(LoginRequiredMixin, GetUserMixin, generic.TemplateView):
    template_name = "mfa/status.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.get_user()
        if not hasattr(user, "rlc_user"):
            context["mfa_impossible"] = True
            return context
        context["mfa_setup"] = hasattr(user.org_user, "mfa_secret")
        context["mfa_enabled"] = (
            context["mfa_setup"] and user.org_user.mfa_secret.enabled
        )
        context["frontend_url"] = settings.MAIN_FRONTEND_URL
        if hasattr(user.org_user, "mfa_secret"):
            context["mfa_secret"] = user.org_user.mfa_secret
        return context


class MfaSetupView(LoginRequiredMixin, GetUserMixin, generic.FormView):
    template_name = "mfa/setup.html"
    form_class = SetupMfaForm

    def get_form(self, form_class=None):
        return SetupMfaForm(self.get_user(), **self.get_form_kwargs())

    def form_valid(self, form):
        create_mfa_secret(self.get_user().rlc_user)
        url = reverse_lazy("mfa_enable")
        return HttpResponseRedirect(url)


class MfaEnableView(LoginRequiredMixin, GetUserMixin, generic.FormView):
    template_name = "mfa/enable.html"
    success_url = reverse_lazy("mfa_status")

    def get_context_data(self, **kwargs):
        if not hasattr(self.request.user, "rlc_user") or not hasattr(
            self.get_user().rlc_user, "mfa_secret"
        ):
            raise Http404()
        context = super().get_context_data(**kwargs)
        context["object"] = self.get_user().rlc_user.mfa_secret
        return context

    def get_form(self, form_class=None):
        return CheckMfaForm(self.get_user(), **self.get_form_kwargs())

    def form_valid(self, form):
        enable_mfa_secret(self.get_user().rlc_user)
        return HttpResponseRedirect(self.get_success_url())


class MfaDisableView(LoginRequiredMixin, GetUserMixin, generic.FormView):
    template_name = "mfa/disable.html"
    success_url = reverse_lazy("mfa_status")

    def get_context_data(self, **kwargs):
        if not hasattr(self.request.user, "rlc_user"):
            raise Http404()
        return super().get_context_data(**kwargs)

    def get_form(self, form_class=None):
        return CheckMfaForm(self.get_user(), **self.get_form_kwargs())

    def form_valid(self, form):
        delete_mfa_secret(self.get_user().rlc_user)
        return HttpResponseRedirect(self.get_success_url())


class MfaLoginView(RedirectURLMixin, generic.FormView):
    template_name = "mfa/login.html"
    form_class = MfaAuthenticationForm
    next_page = settings.MAIN_FRONTEND_URL
    success_url_allowed_hosts = {
        strip_scheme(settings.MAIN_FRONTEND_URL),
        strip_scheme(settings.STATISTICS_FRONTEND_URL),
    }

    def get_form(self, form_class=None):
        if form_class is None:
            form_class = self.get_form_class()
        return form_class(
            self.request.session["user_pk"],
            self.request.session["user_key"],
            **self.get_form_kwargs(),
        )

    def form_valid(self, form):
        login(self.request, form.get_user())
        return HttpResponseRedirect(self.get_success_url())

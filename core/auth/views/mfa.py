from django import views
from django.conf import settings
from django.contrib.auth import login
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponseRedirect
from django.urls import reverse_lazy

from core.auth.forms.mfa import (
    CheckMfaForm,
    EnableMfaForm,
    MfaAuthenticationForm,
    SetupMfaForm,
)
from core.auth.models.mfa import MultiFactorAuthenticationSecret
from core.auth.use_cases.mfa import delete_mfa_secret
from core.auth.views.user import strip_scheme


class MfaStatusView(LoginRequiredMixin, views.generic.TemplateView):
    template_name = "mfa/status.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        context["mfa_setup"] = hasattr(user.rlc_user, "mfa_secret")
        context["mfa_enabled"] = (
            context["mfa_setup"] and user.rlc_user.mfa_secret.enabled
        )
        context["frontend_url"] = settings.MAIN_FRONTEND_URL
        if hasattr(user.rlc_user, "mfa_secret"):
            context["mfa_secret"] = user.rlc_user.mfa_secret
        return context


class MfaSetupView(LoginRequiredMixin, views.generic.CreateView):
    template_name = "mfa/setup.html"
    form_class = SetupMfaForm

    def get_success_url(self):
        return reverse_lazy("mfa_enable", args=[self.object.uuid])

    def get_form(self, form_class=None):
        if form_class is None:
            form_class = self.get_form_class()
        return form_class(self.request.user, **self.get_form_kwargs())


class MfaEnableView(LoginRequiredMixin, views.generic.UpdateView):
    template_name = "mfa/enable.html"
    form_class = EnableMfaForm
    success_url = reverse_lazy("mfa_status")
    slug_url_kwarg = "uuid"
    slug_field = "uuid"
    queryset = MultiFactorAuthenticationSecret.objects.none()

    def get_queryset(self):
        user = self.request.user
        if hasattr(user, "rlc_user"):
            return MultiFactorAuthenticationSecret.objects.filter(user=user.rlc_user)
        return super().get_queryset()

    def get_form(self, form_class=None):
        if form_class is None:
            form_class = self.get_form_class()
        return form_class(self.request.user, **self.get_form_kwargs())

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        url = self.object.url
        context["uri"] = url
        return context


class MfaLoginView(views.generic.FormView):
    template_name = "mfa/login.html"
    form_class = MfaAuthenticationForm
    success_url = settings.MAIN_FRONTEND_URL
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
            **self.get_form_kwargs()
        )

    def form_valid(self, form):
        login(self.request, form.get_user())
        return HttpResponseRedirect(self.get_success_url())


class MfaDisableView(LoginRequiredMixin, views.generic.DeleteView):
    template_name = "mfa/disable.html"
    form_class = CheckMfaForm
    success_url = reverse_lazy("mfa_status")
    slug_url_kwarg = "uuid"
    slug_field = "uuid"
    queryset = MultiFactorAuthenticationSecret.objects.none()
    object: MultiFactorAuthenticationSecret

    def get_queryset(self):
        user = self.request.user
        if hasattr(user, "rlc_user"):
            return MultiFactorAuthenticationSecret.objects.filter(user=user.rlc_user)
        return super().get_queryset()

    def get_form(self, form_class=None):
        if form_class is None:
            form_class = self.get_form_class()
        return form_class(self.request.user, **self.get_form_kwargs())

    def form_valid(self, form):
        delete_mfa_secret(self.request.user.rlc_user)
        return HttpResponseRedirect(self.get_success_url())

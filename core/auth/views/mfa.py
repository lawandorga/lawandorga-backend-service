from django import views
from django.urls import reverse_lazy

from core.auth.forms.mfa import EnableMfaForm, SetupMfaForm
from django.contrib.auth.mixins import LoginRequiredMixin

from core.auth.models.mfa import MultiFactorAuthenticationSecret

class MfaStatusView(LoginRequiredMixin, views.generic.TemplateView):
    template_name = "mfa/status.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['mfa_setup'] = hasattr(self.request.user.rlc_user, 'mfa_secret')
        context['mfa_enabled'] = context['mfa_setup'] and self.request.user.rlc_user.mfa_secret.enabled
        return context


class MfaSetupView(LoginRequiredMixin, views.generic.CreateView):
    template_name = 'mfa/setup.html'
    form_class = SetupMfaForm
    success_url = reverse_lazy('mfa_enable', args=[0])
    
    def get_form(self, form_class=None):
        if form_class is None:
            form_class = self.get_form_class()
        return form_class(self.request.user, **self.get_form_kwargs())


class MfaEnableView(LoginRequiredMixin, views.generic.UpdateView):
    template_name = 'mfa/enable.html'
    form_class = EnableMfaForm
    queryset = MultiFactorAuthenticationSecret.objects.none()
    success_url = reverse_lazy('mfa_status')

    def get_form(self, form_class=None):
        if form_class is None:
            form_class = self.get_form_class()
        return form_class(self.request.user, **self.get_form_kwargs())

    def get_object(self, queryset=None):
        return self.request.user.rlc_user.mfa_secret

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        url = self.object.url
        context['uri'] = url
        return context

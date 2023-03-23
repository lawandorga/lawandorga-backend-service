from typing import Any
from django import forms

from core.auth.models.mfa import MultiFactorAuthenticationSecret
from core.auth.models.org_user import RlcUser
from core.auth.models.user import UserProfile
from core.auth.use_cases.mfa import create_mfa_secret, enable_mfa_secret


class SetupMfaForm(forms.ModelForm):
    class Meta:
        model = MultiFactorAuthenticationSecret
        fields: list[str] = []

    def __init__(self, user: UserProfile, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.user = user

    def clean(self):
        if not hasattr(self.user, 'rlc_user'):
            raise forms.ValidationError('You need to have the Rlc User Role to setup MfA.')
        if hasattr(self.user.rlc_user, 'mfa_secret'):
            raise forms.ValidationError('You already have MfA setup.')
        return super().clean()

    def save(self, commit: bool = True) -> MultiFactorAuthenticationSecret:
        if not commit:
            raise ValueError("This form does not support commit=False")
        create_mfa_secret(self.user.rlc_user)
        return self.user.rlc_user.mfa_secret


class EnableMfaForm(forms.ModelForm):
    code = forms.IntegerField()
    
    class Meta:
        model = MultiFactorAuthenticationSecret
        fields = ["code"]

    def __init__(self, user: UserProfile, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.user = user

    def clean(self):
        attrs = super().clean()
        code = attrs["code"]
        if str(code) != self.user.rlc_user.mfa_secret.get_code():
            raise forms.ValidationError('The code is not valid.')
        return attrs

    def save(self, commit: bool = True) -> MultiFactorAuthenticationSecret:
        if not commit:
            raise ValueError("This form does not support commit=False")
        enable_mfa_secret(self.user.rlc_user)
        return self.user.rlc_user.mfa_secret

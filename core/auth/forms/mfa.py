from django import forms
from django.contrib.auth import get_user_model

from core.auth.domain.user_key import UserKey
from core.auth.models.user import UserProfile

from seedwork.types import JsonDict


class SetupMfaForm(forms.Form):
    def __init__(self, user: UserProfile, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.user = user

    def clean(self):
        if not hasattr(self.user, "org_user"):
            raise forms.ValidationError(
                "You need to have the Org User Role to setup MfA."
            )
        if hasattr(self.user.org_user, "mfa_secret"):
            raise forms.ValidationError("You already have MfA setup.")
        return super().clean()


class CheckMfaForm(forms.Form):
    code = forms.IntegerField(required=True)

    def __init__(self, user: UserProfile, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.user = user

    def clean(self):
        attrs = super().clean()
        if "code" not in attrs:
            return attrs
        code = attrs["code"]
        if not hasattr(self.user, "org_user"):
            raise forms.ValidationError("You need the Org User Role.")
        if not hasattr(self.user.org_user, "mfa_secret"):
            raise forms.ValidationError(
                "You have no Multi-factor Authentication setup."
            )
        if str(code) != self.user.org_user.mfa_secret.get_code():
            raise forms.ValidationError("The code is not valid.")
        return attrs


class MfaAuthenticationForm(forms.Form):
    code = forms.IntegerField(label="MfA Code")

    def __init__(self, user_pk: int, user_key: JsonDict, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.user: UserProfile = get_user_model().objects.get(pk=user_pk)
        self.key = UserKey.create_from_unsafe_dict(user_key)

    def clean(self):
        attrs = super().clean()
        code = attrs["code"]
        if str(code) != self.user.org_user.mfa_secret.get_code_with_key(self.key.key):
            raise forms.ValidationError("The code is not valid.")
        return attrs

    def get_user(self):
        return self.user

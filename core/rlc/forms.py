from django import forms
from django.core.exceptions import ValidationError
from django.db import transaction

from core.data_sheets.fixtures import create_default_record_template
from core.models import RlcUser, UserProfile
from core.static import get_all_permission_strings


class OrgAdminForm(forms.ModelForm):
    user_name = forms.CharField(label="Name")
    user_email = forms.EmailField(label="E-Mail")
    user_password = forms.CharField(label="Password", widget=forms.PasswordInput())

    class Meta:
        fields = ["name", "user_name", "user_email", "user_password"]

    def clean_user_email(self):
        email = self.cleaned_data["user_email"]
        if UserProfile.objects.filter(email=email).exists():
            raise ValidationError(
                "A user with this email exists already. Choose another email."
            )
        return email

    def save(self, commit=True):
        with transaction.atomic():
            # save
            rlc = super().save()
            create_default_record_template(rlc)
            # create user
            user = UserProfile.objects.create(
                email=self.cleaned_data["user_email"],
                name=self.cleaned_data["user_name"],
            )
            user.set_password(self.cleaned_data["user_password"])
            user.save()
            # and rlc user
            rlc_user = RlcUser(accepted=True, email_confirmed=True, user=user, org=rlc)
            rlc_user.generate_keys(self.cleaned_data["user_password"])
            rlc_user.save()
            # grant permissions
            for permission in get_all_permission_strings():
                rlc_user.grant(permission)
        # return
        return rlc

    def save_m2m(self):
        pass

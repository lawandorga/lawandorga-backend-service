from django.core.exceptions import ValidationError

from apps.recordmanagement.fixtures import create_default_record_template
from apps.api.static import get_all_permission_strings
from apps.api.models import UserProfile, RlcUser
from django import forms


class RlcAdminForm(forms.ModelForm):
    user_name = forms.CharField(label='Name')
    user_email = forms.EmailField(label='E-Mail')
    user_password = forms.CharField(label='Password', widget=forms.PasswordInput())

    class Meta:
        fields = ['name', 'user_name', 'user_email', 'user_password']

    def clean_user_email(self):
        email = self.cleaned_data['user_email']
        if UserProfile.objects.filter(email=email).exists():
            raise ValidationError('A user with this email exists already. Choose another email.')
        return email

    def save(self, commit=True):
        # save
        rlc = super().save()
        create_default_record_template(rlc)
        # create user
        user = UserProfile.objects.create(email=self.cleaned_data['user_email'], name=self.cleaned_data['user_name'],
                                          rlc=rlc)
        user.set_password(self.cleaned_data['user_password'])
        user.save()
        # and rlc user
        rlc_user = RlcUser.objects.create(accepted=True, email_confirmed=True, user=user)
        # grant permissions
        for permission in get_all_permission_strings():
            rlc_user.grant(permission)
        # return
        return rlc

    def save_m2m(self):
        pass

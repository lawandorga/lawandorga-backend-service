from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.db.models import Q

from core.auth.models.org_user import RlcUser
from core.auth.models.user import UserProfile
from core.auth.use_cases.rlc_user import register_rlc_user
from core.legal.models.legal_requirement import LegalRequirement
from core.rlc.models.org import Org


class OrgModelChoiceField(forms.ModelChoiceField):
    def label_from_instance(self, obj: Org):  # type: ignore
        return obj.name


class LegalRequirementField(forms.ModelMultipleChoiceField):
    widget = forms.CheckboxSelectMultiple

    def label_from_instance(self, obj: LegalRequirement):  # type: ignore
        return obj.title


class CustomUserCreationForm(UserCreationForm):
    org = OrgModelChoiceField(queryset=Org.objects.order_by("name"))
    lrs = LegalRequirementField(
        queryset=LegalRequirement.objects.filter(
            Q(accept_required=True) | Q(show_on_register=True)
        ),
        label="Accept Legal Requirements",
    )

    class Meta:
        model = UserProfile
        fields = ("org", "name", "email", "password1", "password2", "lrs")

    def save(self, commit=True):
        if not commit:
            raise NotImplementedError(
                "can't create rlc_user and user without commit equal to true"
            )
        register_rlc_user(
            None,
            self.cleaned_data["email"],
            self.cleaned_data["password1"],
            self.cleaned_data["name"],
            self.cleaned_data["lrs"].values_list("pk", flat=True),
            self.cleaned_data["org"].pk,
        )
        return RlcUser.objects.get(user__email=self.cleaned_data["email"])

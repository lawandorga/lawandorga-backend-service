from django.conf import settings

from core.auth.domain.user_key import UserKey
from core.data_sheets.models import DataSheetTemplate
from core.models import Org, OrgUser, UserProfile
from core.tests.data_sheet_fixtures import create_default_record_template


class UserUnitUserBase:
    def setUp(self):
        self.org = Org.objects.create(name="Test RLC")
        self.user1, self.org_user1 = self.create_user(
            "dummy@law-orga.de", "Dummy", settings.DUMMY_USER_PASSWORD
        )
        self.user2, self.org_user2 = self.create_user(
            "tester@law-orga.de", "Tester", settings.DUMMY_USER_PASSWORD
        )
        self.org.generate_keys()
        self.user1 = self.get_user(self.user1.pk)
        self.user2 = self.get_user(self.user2.pk)
        self.private_key1 = (
            UserKey.create_from_dict(self.user1.org_user.key)
            .decrypt_self(settings.DUMMY_USER_PASSWORD)
            .key.get_private_key()
            .decode("utf-8")
        )
        self.private_key2 = (
            UserKey.create_from_dict(self.user2.org_user.key)
            .decrypt_self(settings.DUMMY_USER_PASSWORD)
            .key.get_private_key()
            .decode("utf-8")
        )

        create_default_record_template(self.org)
        self.template = DataSheetTemplate.objects.filter(rlc=self.org).first()

    def get_user(self, pk):
        return UserProfile.objects.get(pk=pk)

    def create_user(self, email, name, password):
        user = UserProfile.objects.create(email=email, name=name)
        user.set_password(password)
        user.save()
        org_user = OrgUser(user=user, email_confirmed=True, accepted=True, org=self.org)
        org_user.generate_keys(password)
        org_user.save()
        return user, org_user

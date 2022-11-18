from django.db.models import Q

from core.auth.models import UserProfile
from core.mail.api import schemas
from core.mail.models import MailDomain
from core.seedwork.api_layer import ApiError, Router

router = Router()


@router.get(url="page/mail/", output_schema=schemas.OutputPageMail)
def query__page_mail(user: UserProfile):
    if hasattr(user, "mail_user"):
        mail_user = user.mail_user

        available_domains = MailDomain.objects.filter(
            Q(org=mail_user.org) | Q(org=None)
        )

        return {"user": mail_user, "available_domains": available_domains}

    raise ApiError("No mail account", status=444)


@router.get(url="page/admin/mail/")
def query__page_admin_mail():
    pass

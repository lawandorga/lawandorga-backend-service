from core.auth.models import UserProfile
from core.mail.api import schemas
from core.mail.models import MailAddress, MailDomain
from core.seedwork.api_layer import ApiError, Router

router = Router()


@router.get(url="page/mail/", output_schema=schemas.OutputPageMail)
def query__page_mail(user: UserProfile):
    if hasattr(user, "mail_user"):
        mail_user = user.mail_user

        available_domains = list(MailDomain.objects.filter(org=mail_user.org))
        domain = available_domains[0] if len(available_domains) else None
        addresses = MailAddress.objects.filter(domain__org=mail_user.org)

        return {
            "user": mail_user,
            "available_domains": available_domains,
            "domain": domain,
            "addresses": addresses,
        }

    raise ApiError("No mail account", status=444)

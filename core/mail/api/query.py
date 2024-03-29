from django.core.exceptions import ObjectDoesNotExist

from core.auth.models import UserProfile
from core.mail.api import schemas
from core.mail.models import MailDomain, MailUser
from core.mail.models.group import MailGroup
from core.seedwork.api_layer import ApiError, Router

router = Router()


@router.get(url="page/dashboard/", output_schema=schemas.OutputPageMail)
def query__page_dashboard(user: UserProfile):
    if hasattr(user, "mail_user"):
        mail_user = user.mail_user

        mail_user_account_data = {
            "addresses": list(mail_user.account.addresses.all()),
        }

        mail_user_data = {
            "uuid": mail_user.uuid,
            "email": mail_user.email,
            "account": mail_user_account_data,
            "aliases": mail_user.aliases,
            "groups": list(mail_user.groups.all()),
        }

        available_domains = list(MailDomain.objects.filter(org=mail_user.org))
        domain = MailDomain.objects.filter(org=mail_user.org).first()
        users = list(
            MailUser.objects.filter(org=mail_user.org).select_related("account")
        )
        groups = list(
            MailGroup.objects.filter(org=mail_user.org).select_related("account")
        )

        return {
            "user": mail_user_data,
            "available_domains": available_domains,
            "domain": domain,
            "users": users,
            "groups": groups,
        }

    raise ApiError("No mail account", status=444)


@router.get(
    url="page/group/<uuid:group>/",
    output_schema=schemas.OutputPageGroup,
)
def query__page_group(mail_user: MailUser, data: schemas.InputPageGroup):
    try:
        group = MailGroup.objects.get(org=mail_user.org, uuid=data.group)
    except ObjectDoesNotExist:
        raise ApiError("Group was not found.")

    available_domains = MailDomain.objects.filter(org=mail_user.org)
    addresses = group.account.addresses.all()
    members = group.members.all()
    available_users = MailUser.objects.filter(org=mail_user.org).exclude(
        pk__in=members.values_list("pk", flat=True)
    )

    return {
        "addresses": list(addresses),
        "available_domains": list(available_domains),
        "members": list(members),
        "available_users": available_users,
    }


@router.get(
    url="page/user/<uuid:user>/",
    output_schema=schemas.OutputPageUser,
)
def query__page_user(mail_user: MailUser, data: schemas.InputPageUser):
    try:
        user = MailUser.objects.get(org=mail_user.org, uuid=data.user)
    except ObjectDoesNotExist:
        raise ApiError("User was not found.")

    available_domains = MailDomain.objects.filter(org=mail_user.org)
    addresses = user.account.addresses.all()

    return {"addresses": list(addresses), "available_domains": list(available_domains)}

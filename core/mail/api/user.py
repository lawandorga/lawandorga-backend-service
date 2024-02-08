from core.mail.api import schemas
from core.mail.models import MailUser
from core.seedwork.api_layer import Router

router = Router()


@router.post(url="regenerate_password/", output_schema=schemas.OutputPassword)
def command__regenerate_password(mail_user: MailUser):
    password = mail_user.generate_random_password()
    mail_user.set_password(password)
    mail_user.save()
    return {"password": password}

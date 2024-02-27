import datetime
from uuid import UUID

from pydantic import BaseModel

from core.auth.models.org_user import OrgUser
from core.seedwork.api_layer import Router

router = Router()


class InputQueryFolderMails(BaseModel):
    group: UUID


class OutputMail(BaseModel):
    uuid: UUID


@router.get(url="folder_mails/<uuid:group>/", output_schema=list[OutputMail])
def query__folder_mails(user: OrgUser, data: InputQueryFolderMails):
    # query the mail import model from models.py
    # optional return the cc-email of the folder as well
    return [
        {
            "uuid": "123",
            "sender": "hello@gmail.com",
            "bcc": "",
            "subject": "First email",
            "content": "Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat. Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id est laborum.",
            "sending_datetime": datetime.datetime.now(),
            "is_read": True,
            "is_pinned": False,
        },
        {
            "uuid": "234",
            "sender": "hello@gmail.com",
            "bcc": "",
            "subject": "Second email",
            "content": "Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat. Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id est laborum.",
            "sending_datetime": datetime.datetime.now(),
            "is_read": True,
            "is_pinned": True,
        },
        {
            "uuid": "345",
            "sender": "hello@gmail.com",
            "bcc": "",
            "subject": "Third email",
            "content": "Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat. Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id est laborum.",
            "sending_datetime": datetime.datetime.now(),
            "is_read": False,
            "is_pinned": False,
        },
    ]

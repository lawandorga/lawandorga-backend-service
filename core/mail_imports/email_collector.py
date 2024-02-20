# TODO: gets the credentials and returns a list of email objects
# Open Question: how to check if email is alrdy imported should it even check here?

from pydantic import BaseModel


class EmailObj(BaseModel):
    text: str
    subject: str
    sender: str
    receiver: list[str]

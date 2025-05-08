from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm

from pydantic import BaseModel


class GroupForm(BaseModel):
    chat_id: str
    name_group: str
    is_notify: bool
    kyrs: int
    forma_obychenia: str

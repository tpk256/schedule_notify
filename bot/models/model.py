from pydantic import BaseModel


class Group(BaseModel):
    chat_id: str
    name_group: str
    is_notify: bool
    activated: bool
    code: str
    file_type: int

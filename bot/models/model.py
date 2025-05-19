from pydantic import BaseModel


class Group(BaseModel):
    chat_id: int
    tg_group_name: str
    is_notify: bool
    is_activated: bool
    code_: str

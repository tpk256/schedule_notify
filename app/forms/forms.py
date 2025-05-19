from pydantic import BaseModel


class GroupForm(BaseModel):
    chat_id: int
    group_name: str
    is_notify: bool
    list_id_edu_group: list[int]


class MessageForm(BaseModel):
    text: str
    is_send: bool

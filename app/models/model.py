from datetime import datetime

from pydantic import BaseModel


class Code(BaseModel):
    id: int
    code: str


class EduGroup(BaseModel):
    id: int
    course: int
    edu_form: int
    edu_group_name: str


class TelegramGroup(BaseModel):
    chat_id: int
    tg_group_name: str
    is_notify: bool
    is_activated: bool
    code_: str
    data_created: datetime = None


class User(BaseModel):
    id: int
    username: str
    hashed_password: str
    email: str = None
    isActive: bool = None


class Token(BaseModel):
    access_token: str
    token_type: str

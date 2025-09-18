from pydantic import BaseModel


class Schedule(BaseModel):
    id: int

    course_id: int
    parity: int
    hash_excel: str
    url: str
    files_id: list[str]

    count_updates: int
    date_updated: int
    date_created: int


class Subscribe(BaseModel):
    id: int
    tg_chat_id: int
    course_id: int
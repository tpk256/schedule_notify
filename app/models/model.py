from enum import Enum


from pydantic import BaseModel


class FormaObychenia(Enum):
    OCHNO = "ochnaya"
    ZA_OCHNO = "zaochnaya"
    OCHNO_AND_ZA_OCHNO = "och_zaoch"


class FileType(BaseModel):
    id: int
    forma_obucheniya: str
    kurs: int

    @staticmethod
    def get_file_type(forma_obychenia, kyrs) -> int:
        if forma_obychenia == FormaObychenia.OCHNO.value:
            return 10 + kyrs
        elif forma_obychenia == FormaObychenia.ZA_OCHNO.value:
            return 20 + kyrs

        elif forma_obychenia == FormaObychenia.OCHNO_AND_ZA_OCHNO.value:
            return 30 + kyrs


class Group(BaseModel):
    chat_id: str
    name_group: str
    is_notify: bool
    activated: bool
    code: str


class User(BaseModel):
    id: int
    username: str
    hashed_password: str
    email: str | None = None
    isActive: bool | None = None


class Token(BaseModel):
    access_token: str
    token_type: str

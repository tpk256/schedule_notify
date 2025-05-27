from enum import Enum
from typing import Optional
from datetime import datetime
import re

from pydantic import BaseModel


class SubGroup(BaseModel):
    number: int = -1
    subject: str = ""
    aud: str = ""

    def __eq__(self, other):
        if isinstance(other, SubGroup):
            return self.number == other.number and self.subject == other.subject and self.aud == other.aud

        else:
            raise ValueError

    def __ne__(self, other):
        return not self.__eq__(other)


class Pair(BaseModel):
    number: int
    time: str
    sub_groups: tuple[SubGroup | None, SubGroup | None]  # 2 подгруппы


class Day(BaseModel):
    date: datetime
    name: str
    pairs: tuple[
        Pair | None,
        Pair | None,
        Pair | None,
        Pair | None,
        Pair | None,
        Pair | None,
        Pair | None
    ]


class Schedule(BaseModel):
    days: tuple[
        Day | None | str,
        Day | None | str, Day | None | str, Day | None | str, Day | None | str, Day | None | str]  # 6 дней


class Group(BaseModel):
    name: str
    schedule: Optional[Schedule]


class Table(BaseModel):
    groups: list[Group]
    flag_parity: bool
    hash: str  # хэш от файла таблицы, чтобы понимать парсить или нет


class Data(BaseModel):
    # _id: int     # формат  <<номер курса><номер формы обучения>>
    tables: list[Table]

    # форма обучения и курс уже будут учтены в id
    # number: int
    # forma_obychenia: Optional[int]  # на будущее, ибо не только для очников это будет


class FormaObychenia(Enum):
    OCHNO = "ochnaya"
    ZA_OCHNO = "zaochnaya"
    OCHNO_AND_ZA_OCHNO = "och_zaoch"


class Link:
    url: str
    forma: str
    kyrs: int

    def __init__(self, url: str, forma: str = None, kyrs: int = None):
        self.url = url
        self.forma = forma
        self.kyrs = kyrs

    def __repr__(self):
        return f"link: {self.url}, forma: {self.forma}, kyrs: {self.kyrs}"

    @property
    def file_type(self):
        if not (self.forma and self.kyrs):
            raise ValueError("Отсутствуют данные по форме или курсу")
        if self.forma == FormaObychenia.OCHNO.value:
            return self.kyrs + 10
        elif self.forma == FormaObychenia.ZA_OCHNO.value:
            return self.kyrs + 20

        elif self.forma == FormaObychenia.OCHNO_AND_ZA_OCHNO.value:
            return self.kyrs + 30


class File:
    path: str
    hash: str
    link: Link
    updated: bool
    file_id: str = None

    def __init__(self, path: str, _hash: str, link: Link, updated: bool = False):
        self.path = path
        self.hash = _hash
        self.link = link
        self.updated = updated

    def set_file_id(self, file_id):
        self.file_id = file_id

    def __repr__(self):
        return f"{'t' if self.file_id is not None else ''}File: {self.path}, hash: {self.hash} {f'file_id: {self.file_id}' if self.file_id is not None else ''}"

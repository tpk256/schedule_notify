from enum import Enum
from typing import Optional
from datetime import datetime
import re

from pydantic import BaseModel


class FormaObychenia(Enum):
    OCHNO = "ochnaya"
    ZA_OCHNO = "zaochnaya"
    OCHNO_AND_ZA_OCHNO = "och_zaoch"


class Link:
    url: str
    forma: str
    kyrs: int
    parity: int

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
            return self.kyrs

        elif self.forma == FormaObychenia.ZA_OCHNO.value:
            return self.kyrs

        elif self.forma == FormaObychenia.OCHNO_AND_ZA_OCHNO.value:
            return self.kyrs


class File:
    path: str
    hash: str
    link: Link

    def __init__(self, path: str, _hash: str, link: Link):
        self.path = path
        self.hash = _hash
        self.link = link


    def __repr__(self):
        return f"{self.path}, {self.hash}"


class Event(BaseModel):
    type: str
    course: int
    parity: int


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



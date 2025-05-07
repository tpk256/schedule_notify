from enum import Enum


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
            return None

        match self.forma:
            case FormaObychenia.OCHNO.value:
                return 10 + self.kyrs
            case FormaObychenia.ZA_OCHNO.value:
                return 20 + self.kyrs
            case FormaObychenia.OCHNO_AND_ZA_OCHNO.value:
                return 30 + self.kyrs


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

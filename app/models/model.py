from pydantic import BaseModel


class FileType(BaseModel):
    id: int
    forma_obucheniya: str
    kurs: int
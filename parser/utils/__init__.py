import hashlib

from pydantic import BaseModel

from .links import *

from .formatter import *


class GroupNotify(BaseModel):
    chat_id: str
    file_id: str


def file_hash(path: str, chunk_size: int = 8192) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(chunk_size), b""):
            h.update(chunk)
    return h.hexdigest()
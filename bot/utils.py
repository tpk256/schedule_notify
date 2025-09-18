import hashlib
import datetime

from openpyxl import load_workbook
from openpyxl.utils import get_column_letter


def file_hash(path: str, chunk_size: int = 8192) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(chunk_size), b""):
            h.update(chunk)
    return h.hexdigest()


def get_current_parity() -> int:
    # TODO в новый год говно будет
    current_week = datetime.date.today().isocalendar().week
    return (current_week - 1) % 2




import os
from datetime import datetime, timedelta, timezone, date


from dotenv import load_dotenv

import jwt

load_dotenv()
ALGORITHM = os.getenv('ALGORITHM')
SECRET_KEY = os.getenv('SECRET_KEY')


def create_access_token(data: dict, expires_delta: timedelta | None = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def even_week(on_date: date = None) -> bool:
    """
    Возвращает True, если ISO-номер недели чётный, иначе False.
    Если on_date не передан, берётся сегодня.
    """
    d = on_date or date.today()
    week_number = d.isocalendar()[1]
    return week_number % 2 == 0
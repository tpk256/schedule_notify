import sqlite3
import os
from typing import Annotated


from fastapi.security import OAuth2PasswordBearer
from fastapi import Depends, HTTPException, status
from passlib.context import CryptContext
from jwt.exceptions import InvalidTokenError
from aiogram import Bot
import jwt
import dotenv

from db import get_user_by_username

dotenv.load_dotenv()

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/v1/token")
ALGORITHM = os.getenv('ALGORITHM')
SECRET_KEY = os.getenv('SECRET_KEY')
BOT_TOKEN = os.environ['BOT_TOKEN']


async def get_bot() -> Bot:
    bot = Bot(token=BOT_TOKEN)
    try:
        yield bot
    finally:
        if bot:
            await bot.close()


def get_conn() -> sqlite3.Connection:
    conn = sqlite3.Connection(os.environ['DATABASE'], check_same_thread=False)

    try:
        yield conn

    finally:
        conn.commit()
        conn.close()


def verify_password(plain_password, hashed_password) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def authenticate_user(db_conn, username: str, password: str):
    user = get_user_by_username(db_conn, username)
    if not user:
        return False
    if not verify_password(password, user.hashed_password):
        return False
    return user


async def get_current_user(
        db_conn: Annotated[sqlite3.Connection, Depends(get_conn)],
        token: Annotated[str, Depends(oauth2_scheme)]
):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username = payload.get("sub")
        if username is None:
            raise credentials_exception
    except InvalidTokenError:
        raise credentials_exception

    user = get_user_by_username(db_conn, username=username)
    if user is None:
        raise credentials_exception
    if not user.isActive:
        raise credentials_exception

    return user

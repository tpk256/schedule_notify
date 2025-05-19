import sqlite3
import os
from typing import Annotated
from datetime import timedelta
import asyncio


from fastapi.security import OAuth2PasswordRequestForm
from fastapi import Depends,  HTTPException, status, APIRouter, Body, Response
from fastapi.responses import JSONResponse
from aiogram import Bot

from utils import create_access_token
from models import model
from forms import MessageForm
from depend import get_conn, authenticate_user, get_current_user, get_bot
from db import get_tg_groups, save_message

ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv('ACCESS_TOKEN_EXPIRE_MINUTES'))

router = APIRouter()


@router.post('', name="create_message")
async def create_message(
        db_conn: Annotated[sqlite3.Connection, Depends(get_conn)],
        _: Annotated[tuple[model.User, sqlite3.Connection], Depends(get_current_user)],
        message_form: Annotated[MessageForm, Body()],
        bot: Annotated[Bot, Depends(get_bot)],
):
    if message_form.is_send:
        groups = get_tg_groups(db_conn)
        for group in groups:
            await bot.send_message(
                chat_id=group.chat_id,
                text=message_form.text
            )
            await asyncio.sleep(2)

    save_message(db_conn, message_form)

    return JSONResponse({}, status_code=200)


@router.patch('', name="send_message")
async def send_message(
        _: Annotated[tuple[model.User, sqlite3.Connection], Depends(get_current_user)],
):
    return JSONResponse({}, status_code=400)

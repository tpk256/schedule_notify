import asyncio
import json
from uuid import uuid4
import logging
import os
from datetime import datetime

from aiogram import Bot, Dispatcher
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.types import InlineQueryResultCachedDocument
from aiogram.types import (
    InlineQueryResultArticle,
    InputTextMessageContent,
    InlineQueryResultDocument,
    InlineQuery
)
from pymongo import MongoClient
from pymongo.synchronous.collection import Collection
from dotenv import load_dotenv

from models import model
from filters.chat_type import ChatTypeFilter
from middleware import middleware
from db import activate_group, DbConnection, get_edu_groups_id_by_chat_id
from keyboards import keyboard

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
load_dotenv()

bot = Bot(token=os.environ['BOT_TOKEN'])
client = MongoClient(os.environ['HOST_MONGO'], int(os.environ['PORT_MONGO']))
dp = Dispatcher()
BASE_URL = os.environ['BASE_URL_TG']


@dp.message(
    ChatTypeFilter(chat_type=["group", "supergroup"]),
    Command(commands=["activate"])
)
async def activate_code(
        message: Message,
        group: model.Group
):
    if group is None:
        await message.answer(text="Данной группы нет в базе")
        return

    values = message.text.split()
    if group.is_activated:
        await message.answer(text="Группа уже активирована!")
        return

    if len(values) == 2:
        code = values[-1]
    else:
        await message.answer(text="Код активации неверный")
        return

    if code == group.code_:
        with DbConnection() as db_conn:
            activate_group(db_conn, group.chat_id)
        await message.answer(text="Активация группы была успешной!")
        return
    else:
        await message.answer(text="Код активации неверный")
        return


@dp.message(
    ChatTypeFilter(chat_type=["group", "supergroup"]),
    Command(commands=["schedule"])
)
async def get_schedule(
        message: Message,
        group: model.Group
):
    if group is None:
        await message.answer(text="Данной группы нет в базе")
        return

    if group.is_activated:
        # получить все edu_group_id, к которым привязан наш чат
        with DbConnection() as db_conn:
            edu_g = get_edu_groups_id_by_chat_id(db_conn, tg_chat_id=message.chat.id)
        kb = keyboard.schedule_keyboard(BASE_URL, chat_id=message.chat.id, edu_groups=edu_g)
        await message.answer(
            text='Актуальное расписание',
            reply_markup=kb
        )

    else:
        await message.answer(text="Группа не активирована")
        return


middleware_cached = middleware.GroupMiddleware()


async def main() -> None:
    dp.message.middleware(middleware_cached)
    try:
        await dp.start_polling(bot)
    finally:
        await bot.session.close()

if __name__ == '__main__':

    asyncio.run(main())

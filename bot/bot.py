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
from dotenv import load_dotenv

from models import model
from filters.chat_type import ChatTypeFilter
from middleware import middleware
from db import activate_group, DbConnection, get_file_id_for_group

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
load_dotenv()

bot = Bot(token=os.environ['BOT_TOKEN'])
dp = Dispatcher()


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
    if group.activated:
        await message.answer(text="Группа уже активирована!")
        return

    if len(values) == 2:
        code = values[-1]
    else:
        await message.answer(text="Код активации неверный")
        return

    if code == group.code:
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

    if group.activated:
        with DbConnection() as db_conn:

            file_id = get_file_id_for_group(db_conn, group.file_type)

            await message.answer_document(
                document=file_id,
                caption='Актуальное расписание'
            )

    else:
        await message.answer(text="Группа не активирована")
        return



async def main() -> None:
    dp.message.middleware(middleware.GroupMiddleware())
    try:
        await dp.start_polling(bot)
    finally:
        await bot.session.close()

if __name__ == '__main__':

    asyncio.run(main())

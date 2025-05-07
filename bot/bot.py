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

from dotenv import load_dotenv

from aiogram.types import (
    InlineQueryResultArticle,
    InputTextMessageContent,
    InlineQueryResultDocument,
    InlineQuery
)

os.chdir(r"/")


DOWNLOAD_DIR = "../parser/parser/downloads"
HASH_DB_FILE = "file_hashes.json"
DOWNLOAD_DB_FILE = "download_db.json"

# Настроим логирование
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
load_dotenv()

bot = Bot(token=os.environ['BOT_TOKEN'])
dp = Dispatcher()


def get_file_id_for_course(course: str) -> str:

    with open(HASH_DB_FILE, mode='r', encoding='utf-8') as f:
        db_file = json.load(f)
    files_key = filter(lambda arg: arg.startswith(f"{course}k"), db_file)

    ans_key = None
    for key in files_key:
        if ans_key is None:
            ans_key = key
        else:
            if datetime.fromisoformat(db_file[key]['date']) > datetime.fromisoformat(db_file[ans_key]['date']):
                ans_key = key

    if ans_key is None:
        return ""

    return db_file[ans_key]['file_id']


async def schedule_command_handler(message: Message) -> None:
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text='1 курс', callback_data='sched_1'),
            InlineKeyboardButton(text='2 курс', callback_data='sched_2'),
        ],
        [
            InlineKeyboardButton(text='3 курс', callback_data='sched_3'),
            InlineKeyboardButton(text='4 курс', callback_data='sched_4'),
        ],
    ])
    await message.answer(
        'Выберите курс для получения расписания:',
        reply_markup=keyboard
    )


async def schedule_callback_handler(callback: CallbackQuery) -> None:
    course = callback.data.split('_')[1]
    file_id = get_file_id_for_course(course)
    await callback.answer()
    if file_id:
        await callback.message.answer_document(
            file_id,
            caption=f'Расписание для {course}-го курса'
        )
    else:
        await callback.message.answer(f'Файл с расписанием для {course}-го курса не найден.')


@dp.inline_query()
async def inline_query_handler(query: InlineQuery, bot: Bot):
    if query.query:
        return
    results = []
    for i in range(1, 4 + 1):
        file_id = get_file_id_for_course(str(i))
        if not file_id:
            continue

        results.append(
            InlineQueryResultCachedDocument(
                id=str(uuid4()),
                title=f"Расписание для {i}-го курса",
                document_file_id=file_id,
                description="Скачать расписание",
                thumb_url="https://avatars.mds.yandex.net/get-yapic/65952/FqxdgtAP9HtAFRnNSvXP8suw4r4-1/islands-68",
                thumb_width=68,
                thumb_height=68
            )
        )

    await bot.answer_inline_query(
        inline_query_id=query.id,
        results=results,
        cache_time=120
    )


# Точка входа
async def main() -> None:

    dp.message.register(
        schedule_command_handler,
        Command(commands=['schedule']),
        lambda msg: msg.chat.type in ("group", "supergroup")
    )

    dp.callback_query.register(
        schedule_callback_handler,
        lambda c: c.data and c.data.startswith('sched_')
    )


    try:
        await dp.start_polling(bot)
    finally:
        await bot.session.close()

if __name__ == '__main__':

    asyncio.run(main())

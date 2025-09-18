import logging

from aiogram.filters import Command, StateFilter
from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.context import FSMContext
from aiogram import Bot, Dispatcher
from aiogram.filters import Command, CommandObject
from aiogram.types import Message, InputFile, InputMediaPhoto
from aiogram import Bot, Dispatcher, Router, BaseMiddleware, F
from aiogram.utils.media_group import MediaGroupBuilder

from keyboards import menu_keyboard , choice_course_keyboard, choice_parity_keyboard
from fsm import ScheduleChoice
from utils import get_current_parity
from db import get_schedule_info, DbConnection


router = Router()

@router.message(
    Command(commands=["start"])
)
async def start(
        message: Message,
        state: FSMContext
):
    await state.clear()
    await state.set_state(ScheduleChoice.menu)
    await message.answer(
        text="Добро пожаловать в бота расписания НФ НИТУ МИСИС!",
        reply_markup=menu_keyboard
    )
    logging.info(f"message_from first_name: {message.from_user.first_name}, username: {message.from_user.username}")



@router.message(
    lambda f: f.text == 'Помощь'
)
async def help(
        message: Message,
):

    await message.answer(
        text="Обратитесь за помощью к https://t.me/uuuuwxj",
    )


@router.message(
)
async def any_message(
        message: Message,
):

    await message.answer(
        text="не понимаю вас, попробуйте /start",
    )
    logging.info(f"message_from first_name: {message.from_user.first_name}, username: {message.from_user.username}")

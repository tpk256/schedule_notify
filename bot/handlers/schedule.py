import logging

from aiogram.filters import Command, StateFilter
from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.context import FSMContext
from aiogram import Bot, Dispatcher
from aiogram.filters import Command
from aiogram.types import Message, InputFile, InputMediaPhoto
from aiogram import Bot, Dispatcher, Router, BaseMiddleware, F
from aiogram.utils.media_group import MediaGroupBuilder

from keyboards import menu_keyboard , choice_course_keyboard, choice_parity_keyboard
from fsm import ScheduleChoice
from utils import get_current_parity
from db import get_schedule_info, DbConnection


router = Router()


@router.message(
    StateFilter(ScheduleChoice.menu),
    lambda f: f.text == 'Расписание'
)
async def schedule_choice_course(
        message: Message,
        state: FSMContext
):

    await state.set_state(ScheduleChoice.choice_course)
    await message.answer(
        text="Выберите, пожалуйста, курс!",
        reply_markup=choice_course_keyboard
    )
    logging.info(f"message_from first_name: {message.from_user.first_name}, username: {message.from_user.username}")

@router.message(
    StateFilter(ScheduleChoice.choice_course),
    lambda f: f.text in ('1 курс', "2 курс", "3 курс", "4 курс")
)
async def schedule_choice_parity(
        message: Message,
        state: FSMContext
):

    await state.update_data(
        {
            "course": ('1 курс', "2 курс", "3 курс", "4 курс").index(message.text) + 1
        }
    )

    await state.set_state(ScheduleChoice.choice_parity)

    await message.answer(
        text="Выберите, "
             "пожалуйста, какой четности расписание вас интересует, "
             f"сейчас: {'ЧЕТНАЯ НЕДЕЛЯ' if get_current_parity() == 0 else 'НЕЧЕТНАЯ НЕДЕЛЯ'}",
        reply_markup=choice_parity_keyboard
    )
    logging.info(f"message_from first_name: {message.from_user.first_name}, username: {message.from_user.username}")


async def create_media_group(caption: str, files_id: list[str]):

    # В медиа группу я добавил, ибо мне так удобно ;9
    media_group = MediaGroupBuilder(caption=caption)

    for file_id in files_id:
        media_group.add_photo(media=file_id)

    return media_group.build()


@router.message(
    StateFilter(ScheduleChoice.choice_parity),
    lambda f: f.text in ("Четная неделя", "Нечетная неделя")
)
async def get_schedule(
        message: Message,
        state: FSMContext
):

    course = await state.get_value("course")
    parity = 0

    if message.text == "Нечетная неделя":
        parity = 1

    with DbConnection() as db_conn:
        try:
            cursor = db_conn.cursor()
            schedule = get_schedule_info(course, parity=parity, cur=cursor)
            if not schedule:
                await message.answer(
                    text="Сейчас расписания с такой четности нет",
                )
                return

            await message.answer_media_group(
                media=await create_media_group(caption=f"Расписание {course} курс", files_id=schedule.files_id)
            )
        finally:
            cursor.close()
    logging.info(f"message_from first_name: {message.from_user.first_name}, username: {message.from_user.username}")


@router.message(
    StateFilter(ScheduleChoice.choice_course),
    lambda f: f.text == 'Назад'
)
async def cancel_schedule_choice_course(
        message: Message,
        state: FSMContext
):
    await state.clear()

    await state.set_state(ScheduleChoice.menu)
    await message.answer(
        text="Вы в главном меню",
        reply_markup=menu_keyboard
    )
    logging.info(f"message_from first_name: {message.from_user.first_name}, username: {message.from_user.username}")


@router.message(
    StateFilter(ScheduleChoice.choice_parity),
    lambda f: f.text in ('Назад к выбору курса', 'Назад в меню')
)
async def cancel_schedule_choice_parity(
        message: Message,
        state: FSMContext
):

    await state.clear()

    if message.text == 'Назад в меню':
        await state.set_state(ScheduleChoice.menu)
        await message.answer(
            text='Вы в главном меню.',
            reply_markup=menu_keyboard
        )
        return

    await state.set_state(ScheduleChoice.choice_course)
    await message.answer(
        text="Выберите, пожалуйста, курс!",
        reply_markup=choice_course_keyboard
    )
    logging.info(f"message_from first_name: {message.from_user.first_name}, username: {message.from_user.username}")

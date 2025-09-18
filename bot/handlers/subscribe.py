import logging

from aiogram.filters import Command, StateFilter
from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.context import FSMContext
from aiogram import Bot, Dispatcher
from aiogram.filters import Command
from aiogram.types import Message, InputFile, InputMediaPhoto
from aiogram import Bot, Dispatcher, Router, BaseMiddleware, F
from aiogram.utils.media_group import MediaGroupBuilder

from keyboards import menu_keyboard , choice_course_keyboard, choice_parity_keyboard, unsubscribe_keyboard, subscribe_keyboard, create_course_keyboard
from fsm import ScheduleChoice, SubscribeChoice
from utils import get_current_parity
from db import get_schedule_info, DbConnection, get_subscribe, create_subscribe, delete_subscribe
from models import Schedule, Subscribe


router = Router()


@router.message(
    lambda f: f.text == 'Рассылка',
    StateFilter(ScheduleChoice.menu)
)
async def subscribe(
        message: Message,
        state: FSMContext
):
    sub = None
    with DbConnection() as conn:
        try:
            cur = conn.cursor()
            sub = get_subscribe(message.chat.id, cur)
        finally:
            cur.close()

    if sub:
        # работа с подпиской
        await state.set_state(SubscribeChoice.remove_sub)
        await state.update_data(
            {
                "sub": sub
            }
        )
        await message.answer(
            text=f"Вы подписаны на рассылку расписания {sub.course_id} курса",
            reply_markup=unsubscribe_keyboard
        )
    else:
        # оформление подписки
        await state.set_state(SubscribeChoice.add_sub)

        await message.answer(
            text=f"Вы ещё не подписаны на рассылку расписания, может хотите подписаться?",
            reply_markup=subscribe_keyboard
        )

    logging.info(f"message_from first_name: {message.from_user.first_name}, username: {message.from_user.username}")


@router.message(
    lambda f: f.text == 'Подписаться',
    StateFilter(SubscribeChoice.add_sub)
)
async def subscribe_add(
        message: Message,
        state: FSMContext
):
    await state.set_state(SubscribeChoice.choice_course_sub)
    await message.answer(
        text="Выберите курс, на который хотите подписаться",
        reply_markup=choice_course_keyboard

    )
    logging.info(f"message_from first_name: {message.from_user.first_name}, username: {message.from_user.username}")


@router.message(
    lambda f: f.text in ('1 курс', "2 курс", "3 курс", "4 курс"),
    StateFilter(SubscribeChoice.choice_course_sub)
)
async def subscribe_create(
        message: Message,
        state: FSMContext
):
    num_course = ('1 курс', "2 курс", "3 курс", "4 курс").index(message.text) + 1

    with DbConnection() as conn:
        try:
            cur = conn.cursor()
            create_subscribe(
                message.chat.id,
                num_course,
                cur
            )
            conn.commit()


        finally:
            cur.close()

    await message.answer(
        text=f"Вы успешно подписали на рассылку расписания {num_course} курса",
        reply_markup=menu_keyboard

    )
    await state.clear()
    await state.set_state(ScheduleChoice.menu)
    logging.info(f"message_from first_name: {message.from_user.first_name}, username: {message.from_user.username}")



@router.message(
    lambda f: f.text == "Отписаться",
    StateFilter(SubscribeChoice.remove_sub)
)
async def subscribe_remove(
        message: Message,
        state: FSMContext
):

    sub: Subscribe  = await state.get_value('sub')
    with DbConnection() as conn:
        try:

            cur = conn.cursor()
            delete_subscribe(
                sub.id,
                sub.tg_chat_id,
                cur
            )
            conn.commit()


        finally:
            cur.close()
    await message.answer(
        text=f"Вы успешно отписались.",
        reply_markup=menu_keyboard

    )
    await state.clear()
    await state.set_state(ScheduleChoice.menu)
    logging.info(f"message_from first_name: {message.from_user.first_name}, username: {message.from_user.username}")





@router.message(
    lambda f: f.text == 'Назад' or f.text == 'Вернуться в меню',
    StateFilter(SubscribeChoice.remove_sub, SubscribeChoice.add_sub, SubscribeChoice.choice_course_sub)
)
async def cancel_subscribe(
        message: Message,
        state: FSMContext
):
    await state.clear()
    await state.set_state(ScheduleChoice.menu)
    await message.answer(
        text=f"Вы вернулись в меню",
        reply_markup=menu_keyboard
    )


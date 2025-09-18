from aiogram.types import ReplyKeyboardMarkup, WebAppInfo, InlineKeyboardMarkup, KeyboardButton
from aiogram.utils.keyboard import ReplyKeyboardBuilder, InlineKeyboardBuilder


def create_menu_keyboard():
    kb = [
        [KeyboardButton(text="Расписание"), KeyboardButton(text="Помощь")],
        [KeyboardButton(text="Рассылка")]
    ]
    keyboard = ReplyKeyboardMarkup(keyboard=kb, resize_keyboard=True)

    return keyboard


def create_course_keyboard():
    kb = [
        [KeyboardButton(text="1 курс"), KeyboardButton(text="2 курс")],
        [KeyboardButton(text="3 курс"), KeyboardButton(text="4 курс")],
        [KeyboardButton(text="Назад")]
    ]
    keyboard = ReplyKeyboardMarkup(keyboard=kb, resize_keyboard=True)

    return keyboard


def create_parity_keyboard():
    kb = [
        [KeyboardButton(text="Четная неделя"), KeyboardButton(text="Нечетная неделя")],
        [KeyboardButton(text="Назад к выбору курса"), KeyboardButton(text="Назад в меню")]
    ]
    keyboard = ReplyKeyboardMarkup(keyboard=kb, resize_keyboard=True)

    return keyboard


def create_unsubscribe_keyboard():
    kb = [
        [KeyboardButton(text="Назад"), KeyboardButton(text="Отписаться")],
    ]
    keyboard = ReplyKeyboardMarkup(keyboard=kb, resize_keyboard=True)

    return keyboard


def create_subscribe_keyboard():
    kb = [
        [KeyboardButton(text="Назад"), KeyboardButton(text="Подписаться")],
    ]
    keyboard = ReplyKeyboardMarkup(keyboard=kb, resize_keyboard=True)

    return keyboard


subscribe_keyboard = create_subscribe_keyboard()
unsubscribe_keyboard = create_unsubscribe_keyboard()
menu_keyboard = create_menu_keyboard()
choice_course_keyboard  = create_course_keyboard()
choice_parity_keyboard  = create_parity_keyboard()
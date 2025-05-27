from aiogram.types import ReplyKeyboardMarkup, WebAppInfo, InlineKeyboardMarkup
from aiogram.utils.keyboard import ReplyKeyboardBuilder, InlineKeyboardBuilder


def schedule_keyboard(url: str, chat_id: int, edu_groups: list[tuple[int, str]]) -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()

    for edu_id, edu_name in edu_groups:
        kb.button(text=f"Расписание {edu_name}", url=f"{url}/schedule/{chat_id}/{edu_id}")
    kb.adjust(1)
    return kb.as_markup()